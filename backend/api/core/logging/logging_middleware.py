import json
import time
from typing import Callable
from urllib.parse import parse_qsl, urlencode

from fastapi import Request, Response, UploadFile
from starlette.middleware.base import BaseHTTPMiddleware

from api.core.logging.logger_config import logger

MAX_BODY_LOG_SIZE = 10 * 1024 * 1024


class LoggingMiddleware(BaseHTTPMiddleware):
    SECRET_FIELDS = {
        "password",
        "token",
        "access_token",
        "refresh_token",
        "api_key",
        "apikey",
        "secret",
        "authorization",
        "csrftoken",
        "client_secret",
    }

    def mask_secrets(self, obj):
        """Recursively replaces all secret fields with '********'"""
        if isinstance(obj, dict):
            return {
                k: (
                    "********"
                    if any(secret in k.lower() for secret in self.SECRET_FIELDS)
                    else self.mask_secrets(v)
                )
                for k, v in obj.items()
            }
        elif isinstance(obj, list):
            return [self.mask_secrets(i) for i in obj]
        return obj

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        try:
            body_bytes = await request.body()
            content_type = request.headers.get("content-type", "")

            if "multipart/form-data" in content_type:
                body_summary = {}
                form = await request.form()
                for key, value in form.multi_items():
                    if isinstance(value, UploadFile):
                        body_summary[key] = {
                            "filename": value.filename,
                            "content_type": value.content_type,
                        }
                    else:
                        body_summary[key] = value
                body = self.mask_secrets(body_summary)

            elif "application/x-www-form-urlencoded" in content_type:
                text = body_bytes.decode("utf-8", errors="ignore")
                form_dict = dict(parse_qsl(text))
                masked_form = self.mask_secrets(form_dict)
                body = urlencode(masked_form)

            else:
                text = body_bytes.decode("utf-8", errors="ignore")
                if len(text) > MAX_BODY_LOG_SIZE:
                    body = f"<text too long: {len(text)} bytes>"
                else:
                    try:
                        body_json = json.loads(text)
                        body = self.mask_secrets(body_json)
                    except Exception:
                        body = text

            async def receive() -> dict:
                return {"type": "http.request", "body": body_bytes}

            request._receive = receive

        except Exception:
            body = "<cannot read body>"

        response = await call_next(request)

        resp_body = b""
        async for chunk in response.body_iterator:
            resp_body += chunk

        async def new_body_iterator():
            yield resp_body

        response.body_iterator = new_body_iterator()

        try:
            resp_content = resp_body.decode("utf-8", errors="ignore")
            if len(resp_content) > MAX_BODY_LOG_SIZE:
                resp_content = f"<response too long: {len(resp_content)} bytes>"
            else:
                try:
                    resp_content = json.loads(resp_content)
                except Exception:
                    pass
        except Exception:
            resp_content = "<cannot decode response>"

        process_time = time.time() - start_time
        client_host = request.client.host if request.client else "unknown"

        log_data = {
            "method": request.method,
            "status_code": response.status_code,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client": client_host,
            "process_time_s": round(process_time, 3),
            "request_body": body,
            "response_body": resp_content,
            "headers": dict(request.headers),
        }

        logger.info(json.dumps(log_data, ensure_ascii=False))
        return response

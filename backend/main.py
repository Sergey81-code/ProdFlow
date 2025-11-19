from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn


from api.core.config import get_settings
from api.core.logging.logging_middleware import LoggingMiddleware
from api.core.routers import router
from api.core.logging.handlers import log_router

settings = get_settings()

app = FastAPI(title=settings.PROJECT_NAME)


app.include_router(router)
app.include_router(log_router)

app.openapi_schema = app.openapi()
app.openapi_schema["components"]["securitySchemes"] = {
    "HTTPBearer": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }
}
app.openapi_schema["security"] = [{"HTTPBearer": []}]

origins = settings.FRONTEND_ORIGINS.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LoggingMiddleware)


@app.get("/")
async def ping():
    return {"Success": True}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=settings.APP_PORT, reload=True)

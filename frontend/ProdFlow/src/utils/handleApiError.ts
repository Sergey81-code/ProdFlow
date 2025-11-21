import { message } from "antd";

export const handleApiError = (err: any) => {
  const status = err?.response?.status;
  const detail = err?.response?.data?.detail || err?.message || "Ошибка";
  const serverMessage = status ? `[${status}] ${detail}` : detail;
  message.error(serverMessage);
};

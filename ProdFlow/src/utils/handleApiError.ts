import { message } from 'antd';

export const handleApiError = (err: any) => {
  const status = err?.response?.status;
  const data = err?.response?.data;

  if (Array.isArray(data?.detail)) {
    const errors = data.detail.map((e: any) => {
      const field = e.loc?.slice(1).join('.') || 'Поле';
      return `${field}: ${e.msg}`;
    });
    message.error(errors.join('\n'));
    return;
  }

  const detail = data?.detail || data?.message || err?.message || 'Ошибка';
  const serverMessage = status ? `[${status}] ${detail}` : detail;
  message.error(serverMessage);
};

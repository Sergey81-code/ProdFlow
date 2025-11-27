import { LockOutlined,UserOutlined } from '@ant-design/icons';
import { Button, Card, Form, Input, message } from 'antd';
import React from 'react';
import { useNavigate } from 'react-router-dom';

import { login } from '../api/index';

const LoginPage: React.FC = () => {
  const navigate = useNavigate();

  const onFinish = async (values: { username: string; password: string }) => {
    try {
      const data = await login(values.username, values.password);

      localStorage.setItem('token', data.access_token);
      message.success('Успешный вход!');
      navigate('/');
    } catch {
      message.error('Неверный логин или пароль');
    }
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
      }}
    >
      <Card title="Авторизация" style={{ width: 320, textAlign: 'center' }}>
        <Form name="login" onFinish={onFinish}>
          <Form.Item
            name="username"
            rules={[{ required: true, message: 'Введите имя пользователя!' }]}
          >
            <Input prefix={<UserOutlined />} placeholder="Имя пользователя" />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: 'Введите пароль!' }]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="Пароль" />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              block
              style={{
                background: 'linear-gradient(90deg, #FFD8A8 0%, #FFB347 100%)',
                border: 'none',
                color: '#333',
                fontWeight: 500,
              }}
            >
              Войти
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default LoginPage;

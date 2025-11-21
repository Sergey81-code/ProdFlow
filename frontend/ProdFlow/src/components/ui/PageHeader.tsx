import { MenuOutlined } from '@ant-design/icons';
import { Button,Layout, Space, Typography } from 'antd';
import React from 'react';
import { useNavigate } from 'react-router-dom';

const { Header } = Layout;
const { Title } = Typography;

interface Props {
  title?: string;
  onMenuClick?: () => void;
}

const PageHeader: React.FC<Props> = ({
  title = 'ProdFlow Admin',
  onMenuClick,
}) => {
  const navigate = useNavigate();

  return (
    <Header
      style={{
        background: 'linear-gradient(90deg, #FFD8A8 0%, #FFB347 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 24px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      }}
    >
      <Space align="center">
        {onMenuClick && (
          <Button
            type="text"
            icon={<MenuOutlined />}
            onClick={onMenuClick}
            style={{ fontSize: 20 }}
          />
        )}
        <Title
          level={4}
          style={{ margin: 0, color: '#333', cursor: 'pointer' }}
          onClick={() => navigate('/')}
        >
          {title}
        </Title>
      </Space>
    </Header>
  );
};

export default PageHeader;

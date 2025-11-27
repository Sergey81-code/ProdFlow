import { Layout } from 'antd';
import React from 'react';

import ProdFlowButton from '../../components/ui/Button';

const { Footer } = Layout;

interface Props {
  onShowLogs: () => void;
}

const PageFooter: React.FC<Props> = ({ onShowLogs }) => {
  return (
    <Footer
      style={{
        display: 'flex',
        justifyContent: 'flex-end',
        alignItems: 'center',
        padding: '12px 24px',
        background: 'linear-gradient(90deg, #FFD8A8 0%, #FFB347 100%)',
        boxShadow: '0 -2px 8px rgba(0,0,0,0.08)',
        flexWrap: 'wrap',
        gap: 8,
      }}
    >
      <ProdFlowButton
        text="Показать логи"
        onClick={onShowLogs}
        style={{
          padding: '6px 16px',
          fontWeight: 600,
          fontSize: 14,
          background: '#fff',
        }}
      />
    </Footer>
  );
};

export default PageFooter;

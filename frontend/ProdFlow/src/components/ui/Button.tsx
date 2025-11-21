import { Button, ButtonProps } from 'antd';
import React from 'react';

interface ProdFlowButtonProps
  extends Omit<ButtonProps, 'type' | 'style' | 'children'> {
  text?: string;
  icon?: React.ReactNode;
  style?: React.CSSProperties;
}

const ProdFlowButton: React.FC<ProdFlowButtonProps> = ({
  text,
  icon,
  style,
  onClick,
  ...rest
}) => {
  return (
    <Button
      type="primary"
      icon={icon}
      onClick={onClick}
      style={{
        background: 'linear-gradient(90deg, #FFD8A8 0%, #FFB347 100%)',
        border: 'none',
        color: '#333',
        fontWeight: 500,
        ...style,
      }}
      {...rest}
    >
      {text}
    </Button>
  );
};

export default ProdFlowButton;

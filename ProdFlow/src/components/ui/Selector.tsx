import { DownOutlined } from '@ant-design/icons';
import { Button,Dropdown } from 'antd';
import React from 'react';

export interface SelectorItem {
  label: string;
  value: string;
  icon?: React.ReactNode;
}

interface SelectorProps {
  items: SelectorItem[];
  value: string;
  onChange: (value: string) => void;
}

export const Selector: React.FC<SelectorProps> = ({
  items,
  value,
  onChange,
}) => {
  const menuItems = items.map((i) => ({
    key: i.value,
    icon: i.icon,
    label: i.label,
    onClick: () => onChange(i.value),
  }));

  const current = items.find((i) => i.value === value);

  return (
    <Dropdown menu={{ items: menuItems }} trigger={['click']}>
      <Button style={{ width: '100%' }}>
        {current?.label || 'Выбрать'} <DownOutlined />
      </Button>
    </Dropdown>
  );
};

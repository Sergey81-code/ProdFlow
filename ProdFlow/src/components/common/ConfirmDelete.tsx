import { Modal } from 'antd';
import React from 'react';

interface Props {
  title?: string;
  visible: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export const ConfirmDelete: React.FC<Props> = ({
  title = 'Удалить?',
  visible,
  onConfirm,
  onCancel,
}) => {
  return (
    <Modal
      title={title}
      open={visible}
      onOk={onConfirm}
      onCancel={onCancel}
      okText="Удалить"
      cancelText="Отмена"
      okButtonProps={{ danger: true }}
    />
  );
};

import { Button, Form,Modal } from 'antd';
import React, { useEffect } from 'react';

import { RoleCreateDto,RoleDto } from '../../types/role';
import RoleForm from '../forms/RoleForm';
import ProdFlowButton from '../ui/Button';

interface Props {
  visible: boolean;
  onClose: () => void;
  onSubmit: (vals: RoleCreateDto) => void;
  editingRole?: RoleDto | null;
}

export const RoleModal: React.FC<Props> = ({
  visible,
  onClose,
  onSubmit,
  editingRole,
}) => {
  const [form] = Form.useForm();

  useEffect(() => {
    if (visible) {
      if (editingRole) {
        form.setFieldsValue(editingRole);
      } else {
        form.resetFields();
      }
    }
  }, [visible, editingRole, form]);

  const handleClose = () => {
    form.resetFields();
    onClose();
  };

  const handleFinish = async (vals: RoleCreateDto) => {
    await onSubmit(vals);
    form.resetFields();
    onClose();
  };

  return (
    <Modal
      title={editingRole ? 'Редактировать роль' : 'Добавить роль'}
      open={visible}
      onCancel={handleClose}
      footer={null}
      forceRender
    >
      <RoleForm form={form} onFinish={handleFinish} />
      <div style={{ marginTop: 16, textAlign: 'right' }}>
        <Button onClick={handleClose} style={{ marginRight: 8 }}>
          Отмена
        </Button>
        <ProdFlowButton text="Сохранить" onClick={() => form.submit()} />
      </div>
    </Modal>
  );
};

import { Button, Form,Modal } from 'antd';
import React, { useEffect } from 'react';

import { RoleDto } from '../../types/role';
import { UserCreateDto,UserDto } from '../../types/user';
import UserForm from '../forms/UserForm';
import ProdFlowButton from '../ui/Button';

interface Props {
  visible: boolean;
  onClose: () => void;
  onSubmit: (vals: UserCreateDto) => void;
  editingUser?: UserDto | null;
  roles: RoleDto[];
}

export const UserModal: React.FC<Props> = ({
  visible,
  onClose,
  onSubmit,
  editingUser,
  roles,
}) => {
  const [form] = Form.useForm();

  useEffect(() => {
    if (visible) {
      if (editingUser) {
        form.setFieldsValue(editingUser);
      } else {
        form.resetFields();
      }
    }
  }, [visible, editingUser, form]);

  const handleClose = () => {
    form.resetFields();
    onClose();
  };

  const handleFinish = async (vals: UserCreateDto) => {
    await onSubmit(vals);
    form.resetFields();
    onClose();
  };

  return (
    <Modal
      title={
        editingUser ? 'Редактировать пользователя' : 'Добавить пользователя'
      }
      open={visible}
      onCancel={handleClose}
      footer={null}
      forceRender
    >
      <UserForm form={form} roles={roles} onFinish={handleFinish} />
      <div style={{ marginTop: 16, textAlign: 'right' }}>
        <Button onClick={handleClose} style={{ marginRight: 8 }}>
          Отмена
        </Button>
        <ProdFlowButton text="Сохранить" onClick={() => form.submit()} />
      </div>
    </Modal>
  );
};

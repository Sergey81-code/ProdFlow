import { Button, Form,Modal } from 'antd';
import React, { useEffect } from 'react';

import { DeviceCreateDto,DeviceDto } from '../../types/device';
import DeviceForm from '../forms/DeviceForm';
import ProdFlowButton from '../ui/Button';

interface Props {
  visible: boolean;
  onClose: () => void;
  onSubmit: (vals: DeviceCreateDto) => void;
  editingDevice?: DeviceDto | null;
}

export const DeviceModal: React.FC<Props> = ({
  visible,
  onClose,
  onSubmit,
  editingDevice,
}) => {
  const [form] = Form.useForm();

  useEffect(() => {
    if (visible) {
      if (editingDevice) {
        form.setFieldsValue(editingDevice);
      } else {
        form.resetFields();
      }
    }
  }, [visible, editingDevice, form]);

  const handleClose = () => {
    form.resetFields();
    onClose();
  };

  const handleFinish = async (vals: DeviceCreateDto) => {
    await onSubmit(vals);
    form.resetFields();
    onClose();
  };

  return (
    <Modal
      title={editingDevice ? 'Редактировать устройство' : 'Добавить устройство'}
      open={visible}
      onCancel={handleClose}
      footer={null}
      forceRender
    >
      <DeviceForm form={form} onFinish={handleFinish} />
      <div style={{ marginTop: 16, textAlign: 'right' }}>
        <Button onClick={handleClose} style={{ marginRight: 8 }}>
          Отмена
        </Button>
        <ProdFlowButton text="Сохранить" onClick={() => form.submit()} />
      </div>
    </Modal>
  );
};

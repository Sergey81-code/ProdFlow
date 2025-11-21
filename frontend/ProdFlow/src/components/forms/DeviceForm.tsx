import React from "react";
import { Form, Input, FormInstance } from "antd";
import { DeviceCreateDto } from "../../types/device";

interface Props {
  initial?: Partial<DeviceCreateDto>;
  onFinish: (vals: DeviceCreateDto) => void;
  form?: FormInstance<any>;
}

const DeviceForm: React.FC<Props> = ({ initial, onFinish, form }) => {
  return (
    <Form layout="vertical" form={form} initialValues={initial} onFinish={onFinish}>
      <Form.Item
        name="name"
        label="Название"
        rules={[{ required: true, message: "Введите название устройства" }]}
      >
        <Input />
      </Form.Item>

      <Form.Item
        name="android_id"
        label="Android ID"
        rules={[{ required: true, message: "Введите Android ID" }]}
      >
        <Input />
      </Form.Item>
    </Form>
  );
};

export default DeviceForm;

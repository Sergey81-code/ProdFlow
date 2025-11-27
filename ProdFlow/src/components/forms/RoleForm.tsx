import { Form, FormInstance, Input, Select, Spin } from 'antd';
import React, { useEffect, useState } from 'react';

import { getPermissions } from '../../api/index';
import { RoleCreateDto } from '../../types/role';

interface Props {
  initial?: RoleCreateDto;
  onFinish: (vals: RoleCreateDto) => void;
  form?: FormInstance<any>;
}

const RoleForm: React.FC<Props> = ({ initial, onFinish, form }) => {
  const [availablePermissions, setAvailablePermissions] = useState<string[]>(
    []
  );
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    getPermissions()
      .then((perms) => setAvailablePermissions(perms))
      .finally(() => setLoading(false));
  }, []);

  return (
    <Form
      layout="vertical"
      form={form}
      initialValues={initial}
      onFinish={onFinish}
    >
      <Form.Item
        name="name"
        label="Название роли"
        rules={[{ required: true, message: 'Введите название роли' }]}
      >
        <Input />
      </Form.Item>

      <Form.Item name="permissions" label="Permissions">
        {loading ? (
          <Spin />
        ) : (
          <Select
            mode="tags"
            placeholder="Введите разрешения"
            tokenSeparators={[',']}
            options={availablePermissions.map((p) => ({ label: p, value: p }))}
          />
        )}
      </Form.Item>
    </Form>
  );
};

export default RoleForm;

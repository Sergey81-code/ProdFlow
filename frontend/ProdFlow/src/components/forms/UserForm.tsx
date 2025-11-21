import { Form, FormInstance,Input, Select } from 'antd';

import { RoleDto } from '../../types/role';
import { UserCreateDto } from '../../types/user';

interface Props {
  initial?: Partial<UserCreateDto>;
  roles: RoleDto[];
  onFinish: (vals: UserCreateDto) => void;
  form?: FormInstance<any>;
}

const UserForm: React.FC<Props> = ({ initial, roles, onFinish, form }) => {
  return (
    <Form
      layout="vertical"
      form={form}
      initialValues={initial}
      onFinish={onFinish}
    >
      <Form.Item
        name="username"
        label="Имя пользователя"
        rules={[{ required: true }]}
      >
        <Input />
      </Form.Item>
      <Form.Item name="first_name" label="Имя" rules={[{ required: true }]}>
        <Input />
      </Form.Item>
      <Form.Item name="last_name" label="Фамилия" rules={[{ required: true }]}>
        <Input />
      </Form.Item>
      <Form.Item name="patronymic" label="Отчество">
        <Input />
      </Form.Item>
      <Form.Item
        name="password"
        label="Пароль"
        rules={initial ? [] : [{ required: false }]}
      >
        <Input />
      </Form.Item>
      <Form.Item name="role_ids" label="Роли">
        <Select
          mode="multiple"
          allowClear
          options={roles.map((r) => ({ label: r.name, value: r.id }))}
        />
      </Form.Item>
    </Form>
  );
};

export default UserForm;

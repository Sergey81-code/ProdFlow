import { MoreOutlined } from '@ant-design/icons';
import { Button, Dropdown,Space, Table } from 'antd';
import React, { useEffect,useMemo, useState } from 'react';

import { RoleDto } from '../../types/role';
import { UserDto } from '../../types/user';

interface Props {
  data: UserDto[];
  loading: boolean;
  roles: RoleDto[];
  onEdit: (user: UserDto) => void;
  onDelete: (user: UserDto) => void;
}

export const UsersTable: React.FC<Props> = ({
  data,
  loading,
  roles,
  onEdit,
  onDelete,
}) => {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 530);
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const columns = useMemo(
    () => [
      {
        title: 'Username',
        dataIndex: 'username',
        key: 'username',
        width: isMobile ? 100 : undefined,
      },
      {
        title: 'Name',
        dataIndex: 'first_name',
        key: 'name',
        render: (_: any, rec: UserDto) =>
          `${rec.last_name} ${rec.first_name}${rec.patronymic ? ` ${rec.patronymic}` : ''}`,
        width: isMobile ? 120 : undefined,
      },
      {
        title: 'Roles',
        dataIndex: 'role_ids',
        key: 'roles',
        render: (ids: string[]) =>
          (ids || [])
            .map((id) => roles.find((r) => r.id === id)?.name ?? id)
            .join(', '),
        width: isMobile ? 100 : undefined,
      },
      {
        title: 'Actions',
        key: 'actions',
        render: (_: any, record: UserDto) =>
          isMobile ? (
            <Dropdown
              menu={{
                items: [
                  {
                    key: 'edit',
                    label: 'Edit',
                    onClick: () => onEdit(record),
                  },
                  {
                    key: 'delete',
                    label: 'Delete',
                    danger: true,
                    onClick: () => onDelete(record),
                  },
                ],
              }}
              trigger={['click']}
            >
              <Button icon={<MoreOutlined />} />
            </Dropdown>
          ) : (
            <Space>
              <Button onClick={() => onEdit(record)} size="small">
                Edit
              </Button>
              <Button danger onClick={() => onDelete(record)} size="small">
                Delete
              </Button>
            </Space>
          ),
        width: isMobile ? 50 : undefined,
      },
    ],
    [roles, isMobile]
  );

  return (
    <Table
      pagination={false}
      dataSource={data}
      columns={columns}
      rowKey="id"
      loading={loading}
      size={isMobile ? 'small' : 'middle'}
    />
  );
};

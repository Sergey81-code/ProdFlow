import { MoreOutlined } from '@ant-design/icons';
import { Button, Dropdown,Space, Table } from 'antd';
import React, { useEffect,useMemo, useState } from 'react';

import { DeviceDto } from '../../types/device';

interface Props {
  data: DeviceDto[];
  loading: boolean;
  onEdit: (device: DeviceDto) => void;
  onDelete: (device: DeviceDto) => void;
}

export const DevicesTable: React.FC<Props> = ({
  data,
  loading,
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
        title: 'Name',
        dataIndex: 'name',
        key: 'name',
        width: isMobile ? 100 : undefined,
      },
      {
        title: 'Android ID',
        dataIndex: 'android_id',
        key: 'android_id',
        width: isMobile ? 120 : undefined,
      },
      {
        title: 'Actions',
        key: 'actions',
        render: (_: any, record: DeviceDto) =>
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
    [isMobile]
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

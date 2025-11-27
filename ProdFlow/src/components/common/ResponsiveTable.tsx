import { Table } from 'antd';
import React from 'react';

interface Props<T> {
  data: T[];
  columns: any;
  rowKey?: string;
  loading?: boolean;
}

export function ResponsiveTable<T>({
  data,
  columns,
  rowKey = 'id',
  loading,
}: Props<T>) {
  return (
    <Table
      columns={columns}
      dataSource={data}
      rowKey={rowKey}
      loading={loading}
      pagination={{ pageSize: 10 }}
    />
  );
}

import React, { useMemo, useState, useEffect } from "react";
import { Table, Space, Button, Dropdown } from "antd";
import { MoreOutlined } from "@ant-design/icons";
import { RoleDto } from "../../types/role";

interface Props {
  data: RoleDto[];
  loading: boolean;
  onEdit: (role: RoleDto) => void;
  onDelete: (role: RoleDto) => void;
}

export const RolesTable: React.FC<Props> = ({ data, loading, onEdit, onDelete }) => {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 530);
    handleResize();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const columns = useMemo(() => [
    { title: "Name", dataIndex: "name", key: "name", width: isMobile ? 100 : undefined },
    {
      title: "Permissions",
      dataIndex: "permissions",
      key: "permissions",
      render: (p: string[]) => (p || []).join(", "),
      width: isMobile ? 120 : undefined,
    },
    {
      title: "Actions",
      key: "actions",
      render: (_: any, record: RoleDto) =>
        isMobile ? (
          <Dropdown
            menu={{
              items: [
                {
                  key: "edit",
                  label: "Edit",
                  onClick: () => onEdit(record),
                },
                {
                  key: "delete",
                  label: "Delete",
                  danger: true,
                  onClick: () => onDelete(record),
                },
              ],
            }}
            trigger={["click"]}
          >
            <Button icon={<MoreOutlined />} />
          </Dropdown>
        ) : (
          <Space>
            <Button onClick={() => onEdit(record)} size="small">Edit</Button>
            <Button danger onClick={() => onDelete(record)} size="small">Delete</Button>
          </Space>
        ),
      width: isMobile ? 50 : undefined,
    },
  ], [isMobile]);

  return (
    <Table
      pagination={false}
      dataSource={data}
      columns={columns}
      rowKey="id"
      loading={loading}
      size={isMobile ? "small" : "middle"}
    />
  );
};

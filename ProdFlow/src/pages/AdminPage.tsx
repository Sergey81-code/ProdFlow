import { MobileOutlined,TableOutlined, TeamOutlined } from '@ant-design/icons';
import { Card,Col, Row } from 'antd';
import React from 'react';

import { ConfirmDelete } from '../components/common/ConfirmDelete';
import { DeviceModal } from '../components/modals/DeviceModal';
import { RoleModal } from '../components/modals/RoleModal';
import { UserModal } from '../components/modals/UserModal';
import { DevicesTable } from '../components/tables/DevicesTable';
import { RolesTable } from '../components/tables/RolesTable';
import { UsersTable } from '../components/tables/UsersTable';
import ProdFlowButton from '../components/ui/Button';
import { Selector } from '../components/ui/Selector';
import { useAdminLogic } from '../hooks/useAdminLogic';

const modeItems = [
  { label: 'Пользователи', value: 'users', icon: <TeamOutlined /> },
  { label: 'Роли', value: 'roles', icon: <TableOutlined /> },
  { label: 'Устройства', value: 'devices', icon: <MobileOutlined /> },
];

const AdminPage: React.FC = () => {
  const logic = useAdminLogic();

  return (
    <>
      <Row gutter={[16, 16]} style={{ marginBottom: 16, alignItems: 'center' }}>
        <Col xs={24} sm={12} md={6}>
          <div style={{ maxWidth: 220 }}>
            <Selector
              items={modeItems}
              value={logic.mode}
              onChange={(v) => logic.setMode(v as any)}
            />
          </div>
        </Col>

        <Col xs={24} sm={12} md={18} style={{ textAlign: 'right' }}>
          <ProdFlowButton text="Добавить" onClick={logic.handleCreateClick} />
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Card variant="borderless">
            {logic.mode === 'users' && (
              <UsersTable
                data={logic.usersQuery.data ?? []}
                loading={logic.usersQuery.isLoading}
                roles={logic.rolesQuery.data ?? []}
                onEdit={logic.setEditingUser}
                onDelete={(u) => {
                  logic.setDeleteTarget({ id: u.id, type: 'user' });
                  logic.setDeleteVisible(true);
                }}
              />
            )}

            {logic.mode === 'roles' && (
              <RolesTable
                data={logic.rolesQuery.data ?? []}
                loading={logic.rolesQuery.isLoading}
                onEdit={logic.setEditingRole}
                onDelete={(r) => {
                  logic.setDeleteTarget({ id: r.id, type: 'role' });
                  logic.setDeleteVisible(true);
                }}
              />
            )}

            {logic.mode === 'devices' && (
              <DevicesTable
                data={logic.devicesQuery.data ?? []}
                loading={logic.devicesQuery.isLoading}
                onEdit={logic.setEditingDevice}
                onDelete={(d) => {
                  logic.setDeleteTarget({ id: d.id, type: 'device' });
                  logic.setDeleteVisible(true);
                }}
              />
            )}
          </Card>
        </Col>
      </Row>

      <UserModal
        visible={!!logic.editingUser}
        onClose={() => logic.setEditingUser(null)}
        onSubmit={logic.handleUserSubmit}
        editingUser={logic.editingUser}
        roles={logic.rolesQuery.data ?? []}
      />

      <RoleModal
        visible={!!logic.editingRole}
        onClose={() => logic.setEditingRole(null)}
        onSubmit={logic.handleRoleSubmit}
        editingRole={logic.editingRole}
      />

      <DeviceModal
        visible={!!logic.editingDevice}
        onClose={() => logic.setEditingDevice(null)}
        onSubmit={logic.handleDeviceSubmit}
        editingDevice={logic.editingDevice}
      />

      <ConfirmDelete
        visible={logic.deleteVisible}
        title="Вы уверены?"
        onConfirm={logic.handleDeleteConfirm}
        onCancel={() => logic.setDeleteVisible(false)}
      />
    </>
  );
};

export default AdminPage;

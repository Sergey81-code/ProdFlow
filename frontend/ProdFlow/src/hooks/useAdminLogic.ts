import { message } from 'antd';
import { useState } from 'react';

import { handleApiError } from '../utils/handleApiError';
import { useDevices } from './useDevices';
import { useRoles } from './useRoles';
import { useUsers } from './useUsers';

export const useAdminLogic = () => {
  const usersQuery = useUsers();
  const rolesQuery = useRoles();
  const devicesQuery = useDevices();

  const [mode, setMode] = useState<'users' | 'roles' | 'devices'>('users');

  const [editingUser, setEditingUser] = useState<any | null>(null);
  const [editingRole, setEditingRole] = useState<any | null>(null);
  const [editingDevice, setEditingDevice] = useState<any | null>(null);

  const [deleteVisible, setDeleteVisible] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<{
    id: string;
    type: 'user' | 'role' | 'device';
  } | null>(null);

  const handleCreateClick = () => {
    if (mode === 'users') setEditingUser({});
    else if (mode === 'roles') setEditingRole({});
    else setEditingDevice({});
  };

  const handleUserSubmit = async (vals: any) => {
    try {
      if (editingUser?.id) {
        await usersQuery.update.mutateAsync({
          id: editingUser.id,
          payload: vals,
        });
      } else {
        await usersQuery.create.mutateAsync(vals);
      }
      setEditingUser(null);
    } catch (err) {
      handleApiError(err);
    }
  };

  const handleRoleSubmit = async (vals: any) => {
    try {
      if (editingRole?.id) {
        await rolesQuery.update.mutateAsync({
          id: editingRole.id,
          payload: vals,
        });
      } else {
        await rolesQuery.create.mutateAsync(vals);
      }
      setEditingRole(null);
    } catch (err) {
      handleApiError(err);
    }
  };

  const handleDeviceSubmit = async (vals: any) => {
    try {
      if (editingDevice?.id) {
        await devicesQuery.update.mutateAsync({
          id: editingDevice.id,
          payload: vals,
        });
      } else {
        await devicesQuery.create.mutateAsync(vals);
      }
      setEditingDevice(null);
    } catch (err) {
      handleApiError(err);
    }
  };

  const handleDeleteConfirm = async () => {
    if (!deleteTarget) return;

    const { id, type } = deleteTarget;

    try {
      if (type === 'user') await usersQuery.remove.mutateAsync(id);
      else if (type === 'role') await rolesQuery.remove.mutateAsync(id);
      else await devicesQuery.remove.mutateAsync(id);

      message.success('Удалено');
    } catch (err) {
      handleApiError(err);
    } finally {
      setDeleteVisible(false);
      setDeleteTarget(null);
    }
  };

  return {
    usersQuery,
    rolesQuery,
    devicesQuery,

    mode,
    setMode,

    editingUser,
    editingRole,
    editingDevice,
    setEditingUser,
    setEditingRole,
    setEditingDevice,

    deleteVisible,
    deleteTarget,
    setDeleteVisible,
    setDeleteTarget,

    handleCreateClick,
    handleUserSubmit,
    handleRoleSubmit,
    handleDeviceSubmit,
    handleDeleteConfirm,
  };
};

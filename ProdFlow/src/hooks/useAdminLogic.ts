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

  const handleSubmit = async (
    type: 'user' | 'role' | 'device',
    vals: any
  ): Promise<boolean> => {
    try {
      if (type === 'user') {
        if (editingUser?.id) {
          await usersQuery.update.mutateAsync({
            id: editingUser.id,
            payload: vals,
          });
        } else {
          await usersQuery.create.mutateAsync(vals);
        }
        setEditingUser(null);
      } else if (type === 'role') {
        if (editingRole?.id) {
          await rolesQuery.update.mutateAsync({
            id: editingRole.id,
            payload: vals,
          });
        } else {
          await rolesQuery.create.mutateAsync(vals);
        }
        setEditingRole(null);
      } else if (type === 'device') {
        if (editingDevice?.id) {
          await devicesQuery.update.mutateAsync({
            id: editingDevice.id,
            payload: vals,
          });
        } else {
          await devicesQuery.create.mutateAsync(vals);
        }
        setEditingDevice(null);
      }
      return true;
    } catch (err) {
      handleApiError(err);
      return false;
    }
  };

  const handleUserSubmit = async (vals: any): Promise<boolean> =>
    handleSubmit('user', vals);

  const handleRoleSubmit = async (vals: any): Promise<boolean> =>
    handleSubmit('role', vals);

  const handleDeviceSubmit = async (vals: any): Promise<boolean> =>
    handleSubmit('device', vals);

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

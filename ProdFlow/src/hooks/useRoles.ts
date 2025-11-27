import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { createRole, deleteRole,getRoles, updateRole } from '../api';
import { RoleCreateDto, RoleDto } from '../types/role';

const ROLES_KEY = ['roles'];

export const useRoles = () => {
  const qc = useQueryClient();

  const query = useQuery<RoleDto[]>({
    queryKey: ROLES_KEY,
    queryFn: getRoles,
    staleTime: 1000 * 60,
  });

  const create = useMutation({
    mutationFn: (payload: RoleCreateDto) => createRole(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ROLES_KEY }),
  });

  const update = useMutation({
    mutationFn: ({
      id,
      payload,
    }: {
      id: string;
      payload: Partial<RoleCreateDto>;
    }) => updateRole(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ROLES_KEY }),
  });

  const remove = useMutation({
    mutationFn: (id: string) => deleteRole(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ROLES_KEY }),
  });

  return { ...query, create, update, remove };
};

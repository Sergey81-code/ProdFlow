import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getUsers, createUser, updateUser, deleteUser } from "../api";
import { UserCreateDto, UserDto } from "../types/user";

const USERS_KEY = ["users"];

export const useUsers = () => {
  const qc = useQueryClient();

  const query = useQuery<UserDto[]>({
    queryKey: USERS_KEY,
    queryFn: getUsers,
    staleTime: 1000 * 60,
  });

  const create = useMutation({
    mutationFn: (payload: UserCreateDto) => createUser(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: USERS_KEY }),
  });

  const update = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Partial<UserCreateDto> }) =>
      updateUser(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: USERS_KEY }),
  });

  const remove = useMutation({
    mutationFn: (id: string) => deleteUser(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: USERS_KEY }),
  });

  return { ...query, create, update, remove };
};

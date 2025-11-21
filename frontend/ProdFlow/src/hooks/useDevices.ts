import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getDevices, createDevice, updateDevice, deleteDevice } from "../api";
import { DeviceCreateDto, DeviceDto } from "../types/device";

const DEVICES_KEY = ["devices"];

export const useDevices = () => {
  const qc = useQueryClient();

  const query = useQuery<DeviceDto[]>({
    queryKey: DEVICES_KEY,
    queryFn: getDevices,
    staleTime: 1000 * 60,
  });

  const create = useMutation({
    mutationFn: (payload: DeviceCreateDto) => createDevice(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: DEVICES_KEY }),
  });

  const update = useMutation({
    mutationFn: ({
      id,
      payload,
    }: {
      id: string;
      payload: Partial<DeviceCreateDto>;
    }) => updateDevice(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: DEVICES_KEY }),
  });

  const remove = useMutation({
    mutationFn: (id: string) => deleteDevice(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: DEVICES_KEY }),
  });

  return { ...query, create, update, remove };
};

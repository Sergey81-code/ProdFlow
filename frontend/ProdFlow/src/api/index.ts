import axios from "axios";
import { UserCreateDto, UserDto } from "../types/user";
import { RoleCreateDto, RoleDto } from "../types/role";
import { DeviceCreateDto, DeviceDto } from "../types/device";
import apiBase from "./apiBase";

const VERSION_URL = "/v1" as const;

export const apiV1 = {
  get: (url: string, cfg?: any) => apiBase.get(`${VERSION_URL}${url}`, cfg),
  post: (url: string, data?: any, cfg?: any) => apiBase.post(`${VERSION_URL}${url}`, data, cfg),
  patch: (url: string, data?: any, cfg?: any) => apiBase.patch(`${VERSION_URL}${url}`, data, cfg),
  delete: (url: string, cfg?: any) => apiBase.delete(`${VERSION_URL}${url}`, cfg),
};

export const apiRaw = {
  get: (url: string, cfg?: any) => apiBase.get(url, cfg),
  post: (url: string, data?: any, cfg?: any) => apiBase.post(url, data, cfg),
};


export const login = async (username: string, password: string) => {
  const params = new URLSearchParams();
  params.append("username", username);
  params.append("password", password);

  const { data } = await axios.post(
    "http://127.0.0.1:8000/v1/auth/",
    params,
    { headers: { "Content-Type": "application/x-www-form-urlencoded" } }
  );
  return data;
};

export const getUsers = async (): Promise<UserDto[]> => {
  const { data } = await apiV1.get("/users");
  return data;
};

export const createUser = async (payload: UserCreateDto) => {
  const { data } = await apiV1.post("/users", payload);
  return data as UserDto;
};

export const updateUser = async (id: string, payload: Partial<UserCreateDto>) => {
  const { data } = await apiV1.patch(`/users/${id}`, payload);
  return data as UserDto;
};

export const deleteUser = async (id: string) => {
  await apiV1.delete(`/users/${id}`);
};

export const getRoles = async (): Promise<RoleDto[]> => {
  const { data } = await apiV1.get("/roles");
  return data;
};

export const createRole = async (payload: RoleCreateDto) => {
  const { data } = await apiV1.post("/roles", payload);
  return data as RoleDto;
};

export const updateRole = async (id: string, payload: Partial<RoleCreateDto>) => {
  const { data } = await apiV1.patch(`/roles/${id}`, payload);
  return data as RoleDto;
};

export const deleteRole = async (id: string) => {
  await apiV1.delete(`/roles/${id}`);
};

export const getDevices = async (): Promise<DeviceDto[]> => {
  const { data } = await apiV1.get("/devices");
  return data;
};

export const createDevice = async (payload: DeviceCreateDto) => {
  const { data } = await apiV1.post("/devices", payload);
  return data as DeviceDto;
};

export const updateDevice = async (id: string, payload: Partial<DeviceCreateDto>) => {
  const { data } = await apiV1.patch(`/devices/${id}`, payload);
  return data as DeviceDto;
};

export const deleteDevice = async (id: string) => {
  await apiV1.delete(`/devices/${id}`);
};

export const getPermissions = async (): Promise<string[]> => {
  const { data } = await apiV1.get("/roles/permissions");
  return data;
};

export const getLogs = async () => {
  const { data } = await apiRaw.get("/logs");
  return data;
};

export const getLogFile = async (filename: string): Promise<Blob> => {
  const response = await apiRaw.get(`/logs/${filename}`, {
    responseType: "blob",
  });
  return response.data;
};

export default apiV1;

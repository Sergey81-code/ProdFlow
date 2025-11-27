export interface RoleCreateDto {
  name: string;
  permissions: string[];
}

export interface RoleDto {
  id: string;
  name: string;
  permissions: string[];
}

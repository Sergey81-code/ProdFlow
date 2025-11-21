export interface UserCreateDto {
  username: string;
  first_name: string;
  last_name: string;
  patronymic?: string;
  password?: string;
  finger_token?: string;
  role_ids?: string[];
}

export interface UserDto {
  id: string;
  username: string;
  first_name: string;
  last_name: string;
  patronymic?: string;
  finger_token?: string;
  role_ids: string[];
}

import { apiV1 } from '../clients'

export const getRole = (roleId: string) =>
  apiV1.get(`/roles/${roleId}`)

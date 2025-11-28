import { apiV1 } from '../clients'

export const getMe = () => apiV1.get('/users/me')

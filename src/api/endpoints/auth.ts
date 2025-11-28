import { apiV1 } from '../clients'

export const login = (username: string, password: string) => {
  const form = new URLSearchParams()
  form.append('username', username)
  form.append('password', password)

  return apiV1.post('/auth/', form, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  })
}

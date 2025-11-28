import axios from 'axios'
import SecureStore from '../storage/secureStore'
import { AxiosHeaders } from 'axios'

export function createBaseClient(baseURL?: string) {
  const client = axios.create({
    baseURL,
    timeout: 20000,
    headers: new AxiosHeaders({
      'Content-Type': 'application/json',
      Accept: 'application/json'
    })
  })

  client.interceptors.request.use(async (cfg) => {
    const token = await SecureStore.getToken()

    if (token) {
      if (!cfg.headers) cfg.headers = new AxiosHeaders()
      cfg.headers.set('Authorization', `Bearer ${token}`)
    }

    return cfg
  })

  return client
}

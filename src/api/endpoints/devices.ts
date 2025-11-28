import { apiV1 } from '../clients'

export const getDevicesByAndroidId = (androidId: string) =>
  apiV1.get(`/devices/android/${androidId}`)

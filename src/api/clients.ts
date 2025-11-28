import { createBaseClient } from './client'
import { API_BASE, API_V1_BASE } from '../constants/config'

export const apiRaw = createBaseClient(API_BASE)
export const apiV1 = createBaseClient(API_V1_BASE)

import * as Application from 'expo-application'
import SecureStore from '../storage/secureStore'
import { getDevicesByAndroidId } from '../api/endpoints/devices'

const ANDROID_KEY = 'prodflow_android_id'

export async function getAndroidId(): Promise<string> {
  const stored = await SecureStore.getItem(ANDROID_KEY)
  if (stored) return stored

  try {
    const androidId = await Application.getAndroidId()
    if (androidId) {
      await SecureStore.saveItem(ANDROID_KEY, androidId)
      return androidId
    }
  } catch (e) {
    console.warn('Не удалось получить AndroidId:', e)
  }

  const fallback = 'prodflow-' + (Date.now().toString(36) + Math.random().toString(36).slice(2, 8))
  await SecureStore.saveItem(ANDROID_KEY, fallback)
  return fallback
}

export async function sendAndroidId(androidId: string) {
  return await getDevicesByAndroidId(androidId)
}

export async function getSavedAndroidId() {
  return await SecureStore.getItem(ANDROID_KEY)
}

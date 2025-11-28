import * as SecureStoreNative from 'expo-secure-store'

const SecureStore = {
  saveToken: async (token: string) => {
    await SecureStoreNative.setItemAsync('prodflow_token', token, {
      keychainAccessible: SecureStoreNative.WHEN_UNLOCKED,
    })
  },

  getToken: async (): Promise<string | null> => {
    return await SecureStoreNative.getItemAsync('prodflow_token')
  },

  deleteToken: async () => {
    await SecureStoreNative.deleteItemAsync('prodflow_token')
  },

  saveCredentials: async (value: { username: string; password: string }) => {
    await SecureStoreNative.setItemAsync('prodflow_credentials', JSON.stringify(value))
  },

  getCredentials: async (): Promise<{ username: string; password: string } | null> => {
    const item = await SecureStoreNative.getItemAsync('prodflow_credentials')
    if (!item) return null
    return JSON.parse(item)
  },

  deleteCredentials: async () => {
    await SecureStoreNative.deleteItemAsync('prodflow_credentials')
  },

  savePendingCredentials: async (value: { username: string; password: string }) => {
    await SecureStoreNative.setItemAsync('prodflow_pending_credentials', JSON.stringify(value))
  },

  getPendingCredentials: async (): Promise<{ username: string; password: string } | null> => {
    const item = await SecureStoreNative.getItemAsync('prodflow_pending_credentials')
    if (!item) return null
    return JSON.parse(item)
  },

  clearPendingCredentials: async () => {
    await SecureStoreNative.deleteItemAsync('prodflow_pending_credentials')
  },

  saveItem: async (key: string, value: string) => {
    await SecureStoreNative.setItemAsync(key, value)
  },

  getItem: async (key: string): Promise<string | null> => {
    return await SecureStoreNative.getItemAsync(key)
  },

  deleteItem: async (key: string) => {
    await SecureStoreNative.deleteItemAsync(key)
  },
}

export default SecureStore

import React, { createContext, useState, useEffect } from 'react'
import SecureStore from '../storage/secureStore'
import { getMe } from '../api/endpoints/users'

type User = {
  id: string
  username: string
  first_name: string
  last_name: string
  patronymic?: string | null
  finger_token?: string | null
  role_ids?: string[]
  roles: Record<string, string[]> | null
} | null

export const UserContext = createContext({
  user: null as User,
  setUser: (u: User) => {},
  logout: async () => {}
})

export const UserProvider: React.FC<{children: React.ReactNode}> = ({ children }) => {
  const [user, setUser] = useState<User>(null)

  useEffect(() => {
    (async () => {
      const token = await SecureStore.getToken()
      if (token) {
        try {
          const res = await getMe()
          setUser(res.data)
        } catch {
          await SecureStore.deleteToken()
          setUser(null)
        }
      }
    })()
  }, [])

  const logout = async () => {
    await SecureStore.deleteToken()
    await SecureStore.deleteCredentials()
    setUser(null)
  }

  return <UserContext.Provider value={{ user, setUser, logout }}>{children}</UserContext.Provider>
}

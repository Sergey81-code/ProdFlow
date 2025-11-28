import React, { useState, useContext } from 'react'
import { View, Text, TextInput, StyleSheet, ViewStyle, TextStyle } from 'react-native'
import { login } from '../../src/api/endpoints/auth'
import SecureStore from '../../src/storage/secureStore'
import { useRouter } from 'expo-router'
import { UserContext } from '../../src/contexts/UserContext'
import { getMe } from '../../src/api/endpoints/users'
import Button from '../../src/components/ui/Button'
import { useTheme, Theme } from '../../src/constants/theme'
import axios from 'axios'
import { getRole } from '../../src/api/endpoints/roles'

export default function AuthScreen() {
  const theme = useTheme()
  const s = createStyles(theme)

  const [loginValue, setLoginValue] = useState('')
  const [password, setPassword] = useState('')
  const [errors, setErrors] = useState<{ login?: string; password?: string; server?: string }>({})

  const router = useRouter()
  const { setUser } = useContext(UserContext)

  const doLogin = async () => {
    const newErrors: typeof errors = {}
    if (!loginValue.trim()) newErrors.login = 'Поле "Логин" обязательно'
    if (!password.trim()) newErrors.password = 'Поле "Пароль" обязательно'

    setErrors(newErrors)
    if (Object.keys(newErrors).length > 0) return

    try {
      setErrors({})
      const { data } = await login(loginValue, password)
      await SecureStore.saveToken(data.access_token)

      const me = await getMe()


      const roles: Record<string, string[]> = {}

      if (me.data.role_ids?.length) {
        const roleResponses = await Promise.all(
          me.data.role_ids.map((roleId: string) => getRole(roleId))
        )

        roleResponses.forEach((res) => {
          const role = res.data
          roles[role.name] = role.permissions
        })
      }
      setUser({
        ...me.data,
        roles,
      })

      router.replace('/home')
    } catch (err: any) {
      if (axios.isAxiosError(err)) {
        if (err.response?.status === 401 || err.response?.status === 403) {
          setErrors({ server: 'Неправильный логин или пароль' })
        } else {
          setErrors({ server: 'Ошибка сервера' })
        }
      } else {
        setErrors({ server: 'Произошла неизвестная ошибка' })
      }
    }
  }

  return (
    <View style={s.container}>
      <Text style={s.title}>Вход</Text>

      {errors.server && <Text style={s.serverError}>{errors.server}</Text>}

      <TextInput
        placeholder="Логин"
        value={loginValue}
        onChangeText={(text) => setLoginValue(text)}
        style={s.input}
        placeholderTextColor={theme.colors.muted}
      />
      {errors.login && <Text style={s.error}>{errors.login}</Text>}

      <TextInput
        placeholder="Пароль"
        value={password}
        onChangeText={(text) => setPassword(text)}
        secureTextEntry
        style={s.input}
        placeholderTextColor={theme.colors.muted}
      />
      {errors.password && <Text style={s.error}>{errors.password}</Text>}

      <Button title="Войти" onPress={doLogin} />
    </View>
  )
}

const createStyles = (theme: Theme) =>
  StyleSheet.create({
    container: {
      flex: 1,
      justifyContent: 'center',
      padding: theme.spacing(3),
      backgroundColor: theme.colors.background
    } as ViewStyle,
    title: {
      fontSize: 20,
      color: theme.colors.text,
      marginBottom: theme.spacing(2)
    } as TextStyle,
    input: {
      borderWidth: 1,
      borderColor: theme.colors.primary,
      borderRadius: theme.radii.m,
      padding: theme.spacing(1.5),
      marginBottom: theme.spacing(2),
      color: theme.colors.text
    } as TextStyle,
    error: {
      color: 'red',
      marginBottom: theme.spacing(1)
    } as TextStyle,
    serverError: {
      color: 'red',
      marginBottom: theme.spacing(2),
      textAlign: 'center'
    } as TextStyle
  })

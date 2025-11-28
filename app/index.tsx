import React, { useEffect, useState } from 'react'
import { View, Text, Modal, StyleSheet, ViewStyle, TextStyle } from 'react-native'
import { useRouter } from 'expo-router'
import Loader from '../src/components/ui/Loader'
import { initDb } from '../src/storage/sqlite'
import { registerBackgroundTask } from '../src/tasks/backgroundTask'
import { getAndroidId, sendAndroidId } from '../src/services/deviceService'
import Button from '../src/components/ui/Button'
import { useTheme, Theme } from '../src/constants/theme'

export default function Index() {
  const theme = useTheme()
  const router = useRouter()

  const [loading, setLoading] = useState(true)
  const [androidId, setAndroidId] = useState<string | null>(null)
  const [notFound, setNotFound] = useState(false)
  const [connecting, setConnecting] = useState(false)

  const tryConnect = async (id: string) => {
    try {
      setConnecting(true)
      const res = await sendAndroidId(id)
      if (res.status === 200) {
        router.replace('/auth')
      }
    } catch (e: any) {
      if (e?.response?.status === 404) {
        setNotFound(true)
      }
    } finally {
      setConnecting(false)
      setLoading(false)
    }
  }

  useEffect(() => {
    (async () => {
      await initDb()
      await registerBackgroundTask()
      const id = await getAndroidId()
      setAndroidId(id)
      await tryConnect(id)
    })()
  }, [])

  if (loading) return <Loader />

  const styles = createStyles(theme)

  return (
    <View style={styles.container}>
      <Modal visible={notFound} transparent animationType="slide">
        <View style={styles.overlay}>
          <View style={styles.modal}>
            <Text style={styles.modalTitle}>Устройство не прикреплено</Text>
            <Text style={styles.modalText}>
              AndroidId: {androidId || 'Загрузка...'}
            </Text>
            <Button
              title={connecting ? 'Connecting...' : 'Connect'}
              disabled={connecting}
              onPress={() => {
                if (androidId) tryConnect(androidId)
              }}
            />
          </View>
        </View>
      </Modal>

      <Text style={styles.logo}>ProdFlowMobile</Text>
    </View>
  )
}

const createStyles = (theme: Theme) =>
  StyleSheet.create({
    container: {
      flex: 1,
      justifyContent: 'center',
      alignItems: 'center',
      backgroundColor: theme.colors.background
    } as ViewStyle,
    overlay: {
      flex: 1,
      backgroundColor: 'rgba(0,0,0,0.5)',
      justifyContent: 'center',
      alignItems: 'center'
    } as ViewStyle,
    modal: {
      width: 320,
      padding: theme.spacing(2),
      backgroundColor: theme.colors.surface,
      borderRadius: theme.radii.m
    } as ViewStyle,
    modalTitle: {
      fontSize: 16,
      marginBottom: theme.spacing(1),
      color: theme.colors.text
    } as TextStyle,
    modalText: {
      marginBottom: theme.spacing(2),
      color: theme.colors.muted
    } as TextStyle,
    logo: {
      fontSize: 20,
      color: theme.colors.primary
    } as TextStyle
  })

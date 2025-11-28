import { Slot, Stack } from 'expo-router'
import { SafeAreaProvider } from 'react-native-safe-area-context'
import { ThemeProvider } from '../src/constants/theme'
import { UserProvider } from '../src/contexts/UserContext'

export default function Layout() {

  return (
    <SafeAreaProvider>
      <ThemeProvider>
        <UserProvider>
          <Stack screenOptions={{ headerShown: false }}>
            <Slot />
          </Stack>
        </UserProvider>
      </ThemeProvider>
    </SafeAreaProvider>
  )
}

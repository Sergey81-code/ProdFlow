import React from 'react'
import { View, ScrollView } from 'react-native'

export default function ScreenContainer({ children }: { children: React.ReactNode }) {
  return (
    <ScrollView contentContainerStyle={{ flexGrow:1 }}>
      <View style={{ flex:1, padding:16 }}>{children}</View>
    </ScrollView>
  )
}

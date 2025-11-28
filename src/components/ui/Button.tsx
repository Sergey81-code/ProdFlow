import React from 'react'
import { Pressable, Text, ViewStyle, TextStyle, StyleSheet } from 'react-native'
import { useTheme, Theme } from '../../constants/theme'

type Props = {
  title: string
  onPress: () => void
  variant?: 'solid' | 'ghost',
  disabled?: boolean
}

export default function Button({ title, onPress, variant = 'solid', disabled }: Props) {
  const theme = useTheme()
  const s = createStyles(theme, variant)

  return (
    <Pressable onPress={onPress} style={s.button} disabled={disabled}>
      <Text style={s.text}>{title}</Text>
    </Pressable>
  )
}

const createStyles = (theme: Theme, variant: 'solid' | 'ghost') =>
  StyleSheet.create({
    button: {
      padding: theme.spacing(1.5),
      borderRadius: theme.radii.m,
      backgroundColor: variant === 'solid' ? theme.colors.primary : 'transparent',
      borderWidth: variant === 'ghost' ? 1 : 0,
      borderColor: theme.colors.primary,
      alignItems: 'center' as ViewStyle['alignItems'],
      justifyContent: 'center' as ViewStyle['justifyContent'],
      marginVertical: theme.spacing(1)
    },
    text: {
      color: variant === 'solid' ? '#fff' : theme.colors.primary,
      fontSize: 16
    } as TextStyle
  })

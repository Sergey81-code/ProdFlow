import React, { createContext, useContext, ReactNode, FC } from 'react'

export interface Theme {
  colors: {
    primary: string
    primaryLight: string
    background: string
    surface: string
    text: string
    muted: string
    danger: string
  }
  spacing: (n: number) => number
  fonts: {
    regular: string
    medium: string
    large: number
  }
  radii: {
    s: number
    m: number
    lg: number
  }
}

export const THEME: Theme = {
  colors: {
    primary: '#FF8A33',
    primaryLight: '#FFD7B3',
    background: '#FFFFFF',
    surface: '#FFF7F2',
    text: '#222222',
    muted: '#7A7A7A',
    danger: '#E94E3A'
  },
  spacing: (n: number) => n * 8,
  fonts: {
    regular: 'System',
    medium: 'System',
    large: 18
  },
  radii: {
    s: 6,
    m: 12,
    lg: 20
  }
}

const ThemeContext = createContext<Theme>(THEME)

export const ThemeProvider: FC<{ children: ReactNode }> = ({ children }) => {
  return <ThemeContext.Provider value={THEME}>{children}</ThemeContext.Provider>
}

export const useTheme = (): Theme => useContext(ThemeContext)

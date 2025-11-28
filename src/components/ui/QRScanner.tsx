import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { CameraView, useCameraPermissions, BarcodeScanningResult } from 'expo-camera';
import { Theme, useTheme } from '../../constants/theme';

type Props = {
  onScanned: (data: string) => void;
  onCancel?: () => void;
};

export default function QRScanner({ onScanned, onCancel }: Props) {
  const theme = useTheme();
  const s = createStyles(theme);
  const [permission, requestPermission] = useCameraPermissions();
  const [scanned, setScanned] = useState(false);

  useEffect(() => {
    if (!permission) {
      requestPermission();
    }
  }, [permission]);

  if (!permission || !permission.granted) {
    return (
      <View style={s.container}>
        <Text style={s.text}>Нужен доступ к камере...</Text>
        <TouchableOpacity onPress={requestPermission}>
          <Text style={s.text}>Разрешить</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={s.container}>
      <View style={s.scannerWrapper}>
        <CameraView
          style={StyleSheet.absoluteFillObject}
          facing="back"
          onBarcodeScanned={scanned ? undefined : (result: BarcodeScanningResult) => {
            setScanned(true);
            onScanned(result.data);
          }}
          barcodeScannerSettings={{
            barcodeTypes: ['qr'],
          }}
        />
      </View>

      <View style={s.controls}>
        <TouchableOpacity style={s.button} onPress={() => setScanned(false)}>
          <Text style={s.btnText}>Сканировать снова</Text>
        </TouchableOpacity>
        {onCancel && (
          <TouchableOpacity style={[s.button, s.cancel]} onPress={onCancel}>
            <Text style={s.btnText}>Отмена</Text>
          </TouchableOpacity>
        )}
      </View>
    </View>
  );
}

const createStyles = (theme: Theme) =>
  StyleSheet.create({
    container: {
      flex: 1,
      alignItems: 'center',
      justifyContent: 'center',
      backgroundColor: theme.colors.background,
      padding: theme.spacing(2),
    },
    scannerWrapper: {
      width: '100%',
      height: 380,
      overflow: 'hidden',
      borderRadius: theme.radii.m,
      backgroundColor: '#000',
    },
    controls: {
      flexDirection: 'row',
      marginTop: theme.spacing(2),
      gap: theme.spacing(1),
    },
    button: {
      paddingVertical: theme.spacing(1),
      paddingHorizontal: theme.spacing(2),
      borderRadius: theme.radii.s,
      borderWidth: 1,
      borderColor: theme.colors.primary,
    },
    cancel: {
      borderColor: theme.colors.muted,
    },
    btnText: {
      color: theme.colors.text,
    },
    text: {
      color: theme.colors.text,
    },
  });

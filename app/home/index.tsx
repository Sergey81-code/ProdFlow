import React, { useContext, useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { UserContext } from '../../src/contexts/UserContext';
import { useRouter } from 'expo-router';
import Button from '../../src/components/ui/Button';
import { useTheme } from '../../src/constants/theme';
import QRScanner from '../../src/components/ui/QRScanner';
import * as sqlite from '../../src/storage/sqlite';
import QueueDebugScreen from './queue-debug';

export default function Home() {
  const { user, logout } = useContext(UserContext);
  const router = useRouter();
  const theme = useTheme();
  const s = createStyles(theme);

  const [scanning, setScanning] = useState(false);
  const [queue, setQueue] = useState<any[]>([]);

  async function refreshQueue() {
    const all = await sqlite.getAllQueue();
const parsed = all.map(item => ({
  ...item,
  body: item.body ? JSON.parse(item.body) : null,
  headers: item.headers ? JSON.parse(item.headers) : null,
}));
setQueue(parsed);
  }

  useEffect(() => {
    (async () => {
      await sqlite.initDb();
      await refreshQueue();
    })();
  }, []);


async function handleScanned(data: string) {
  setScanning(false);
  try {
    const payload = JSON.parse(data);
await sqlite.addToQueue({
  ...payload,
  body: payload.body ? JSON.stringify(payload.body) : null,
  headers: payload.headers ? JSON.stringify(payload.headers) : null,
});
    await refreshQueue();
    alert('QR добавлен в очередь!');
  } catch (e: unknown) {
    let msg = 'Неизвестная ошибка';
    if (e instanceof Error) msg = e.message;
    alert('Некорректный QR: ' + msg);
  }
}

  if (scanning) {
    return <QRScanner onScanned={handleScanned} onCancel={() => setScanning(false)} />;
  }

  return (
    <View style={s.root}>
      {/* HEADER */}
      <View style={s.header}>
        <Text style={s.name}>
          {user ? `${user.last_name} ${user.first_name} ${user.patronymic ?? ''}` : '---'}
        </Text>
        <Text style={s.username}>Username: {user?.username}</Text>
        {user?.roles && (
          <Text style={s.rolesText}>
            Роли: {Object.keys(user.roles).join(', ')}
          </Text>
        )}


        <Button
          title="Выйти"
          onPress={async () => {
            await logout();
            router.replace('/auth');
          }}
        />

        <Button title="Сканировать QR" onPress={() => setScanning(true)} />
      </View>

      {/* BODY — СКРОЛЛ */}
      <ScrollView style={s.body} contentContainerStyle={{ paddingBottom: 80 }}>
        {/* Очередь */}
        <View style={s.section}>
          <Text style={s.sectionTitle}>Очередь задач</Text>
          {queue.length === 0 && <Text style={s.empty}>Очередь пуста</Text>}
          {queue.map((item) => (
            <View key={item.id} style={s.queueItem}>
              <Text>ID: {item.id}</Text>
              <Text>{item.method} | {item.path}</Text>
              <Text>Статус: {item.status} | attempts: {item.attempts}</Text>
            </View>
          ))}
        </View>

        {/* DEBUG ФОРМА */}
        <View style={s.debugBlock}>
          <Text style={s.debugTitle}>DEV: Queue Debug</Text>
          <View style={s.debugInner}>
            <QueueDebugScreen />
          </View>
        </View>
      </ScrollView>
    </View>
  );
}

const createStyles = (theme: any) =>
  StyleSheet.create({
    root: {
      flex: 1,
      backgroundColor: theme.colors.background,
    },
    header: {
      padding: theme.spacing(3),
      borderBottomWidth: 1,
      borderColor: theme.colors.muted,
      backgroundColor: theme.colors.background,
    },
    name: {
      fontSize: 20,
      fontWeight: '700',
      color: theme.colors.text,
      marginBottom: 4,
    },
    username: {
      color: theme.colors.muted,
      marginBottom: 12,
    },
    body: {
      flex: 1,
      paddingHorizontal: theme.spacing(3),
    },
    section: {
      marginTop: 20,
    },
    sectionTitle: {
      fontSize: 16,
      fontWeight: '700',
      marginBottom: 12,
      color: theme.colors.text,
    },
    empty: {
      color: theme.colors.muted,
      fontStyle: 'italic',
    },
    queueItem: {
      padding: 10,
      borderRadius: 8,
      borderWidth: 1,
      borderColor: theme.colors.muted,
      marginBottom: 10,
      backgroundColor: theme.colors.surface ?? 'transparent',
    },
    debugBlock: {
      marginTop: 30,
      padding: 12,
      borderRadius: 10,
      borderWidth: 2,
      borderColor: theme.colors.primary,
      backgroundColor: theme.colors.surface ?? 'transparent',
    },
    debugTitle: {
      fontSize: 16,
      fontWeight: '700',
      marginBottom: 10,
      color: theme.colors.primary,
    },
    debugInner: {
      paddingVertical: 4,
    },
    rolesText: {
      fontSize: 14,
      color: theme.colors.muted,
      marginTop: theme.spacing(0.5),
    },

  });

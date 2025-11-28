import React, { useEffect, useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ScrollView } from 'react-native';
import * as sqlite from '../../src/storage/sqlite';
import { useTheme } from '../../src/constants/theme';
import { processQueueTick, forceProcessItem } from '../../src/services/queueService';
import { QueueItem } from '../../src/types/queue';
import { makeId, makeUniqueKey } from '../../src/utils/uid'

export default function QueueDebugScreen() {
  const theme = useTheme();
  const s = createStyles(theme);

  const [method, setMethod] = useState('POST');
  const [path, setPath] = useState('https://httpbin.org/post');
  const [body, setBody] = useState('{"hello":"world"}');
  const [list, setList] = useState<any[]>([]);
  const [stats, setStats] = useState<any>({});

  async function refresh() {
    const all = await sqlite.getAllQueue();
    const parsed = all.map(item => ({
      ...item,
      body: item.body ? JSON.parse(item.body) : null,
      headers: item.headers ? JSON.parse(item.headers) : null,
    }));
    const st = await sqlite.getStats();
    setList(parsed);
    setStats(st);
  }

  useEffect(() => {
    (async () => {
      await sqlite.initDb();
      await refresh();
    })();
  }, []);



async function onAdd() {
  let parsedBody: any = null;
  try { parsedBody = body ? JSON.parse(body) : null } catch { parsedBody = body }

  const id = await makeId();
  const uniq_key = await makeId(); // можно заменить на makeUniqueKey(...) если нужен стабильный ключ

  const newItem: QueueItem = {
    id: id as `${string}-${string}-${string}-${string}-${string}`,
    uniq_key: uniq_key as `${string}-${string}-${string}-${string}-${string}`,
    username: null,
    method,
    path,
    body: parsedBody ? JSON.stringify(parsedBody) : undefined,
    headers: undefined,
    created_at: Date.now(),
    attempts: 0,
    next_retry_at: Date.now(),
    ttl: 0,
    status: 'pending', // TS поймёт как QueueStatus
  };

  await sqlite.addToQueue(newItem);
  await refresh();
}


  async function onProcessAll() {
    await processQueueTick();
    await refresh();
  }

  async function onForce(itemId: string) {
    await forceProcessItem(itemId);
    await refresh();
  }

  async function onPurgeFailed() {
    await sqlite.purgeFailed();
    await refresh();
  }

  return (
    <ScrollView style={s.container} contentContainerStyle={{ paddingBottom: 60 }}>
      <Text style={s.title}>DEV: Queue Debug (DEV ONLY)</Text>

      <View style={s.form}>
        <Text style={s.label}>Метод</Text>
        <TextInput value={method} onChangeText={setMethod} style={s.input} />

        <Text style={s.label}>URL</Text>
        <TextInput value={path} onChangeText={setPath} style={s.input} />

        <Text style={s.label}>Body (JSON)</Text>
        <TextInput
          value={body}
          onChangeText={setBody}
          style={[s.input, { height: 100 }]}
          multiline
        />

        <TouchableOpacity style={s.btn} onPress={onAdd}>
          <Text style={s.btnText}>Добавить в очередь</Text>
        </TouchableOpacity>

        <TouchableOpacity style={s.btn} onPress={onProcessAll}>
          <Text style={s.btnText}>Запустить обработку очереди</Text>
        </TouchableOpacity>

        <TouchableOpacity style={[s.btn, s.danger]} onPress={onPurgeFailed}>
          <Text style={s.btnText}>Удалить все failed</Text>
        </TouchableOpacity>
      </View>

      <View style={s.stats}>
        <Text style={s.statsTitle}>Статистика:</Text>
        <Text>Всего: {stats.total ?? 0}</Text>
        <Text>Pending: {stats.pending ?? 0}</Text>
        <Text>Sent: {stats.sent ?? 0}</Text>
        <Text>Failed: {stats.failed ?? 0}</Text>
      </View>

      <Text style={s.sectionTitle}>Очередь (последние):</Text>
      {list.length === 0 && <Text style={s.empty}>Очередь пуста</Text>}
      {list.map((item) => (
        <View key={item.id} style={s.item}>
          <Text>ID: {item.id}</Text>
          <Text>Метод: {item.method} | {item.path}</Text>
          <Text>Статус: {item.status} | attempts: {item.attempts}</Text>
          <Text>Next retry: {new Date(item.next_retry_at).toLocaleString()}</Text>
          <Text>response_code: {item.response_code ?? '-'}</Text>
          <Text numberOfLines={2}>response_body: {item.response_body ?? '-'}</Text>
          <TouchableOpacity style={s.smallBtn} onPress={() => onForce(item.id)}>
            <Text>Force</Text>
          </TouchableOpacity>
        </View>
      ))}
    </ScrollView>
  );
}

const createStyles = (theme: any) => StyleSheet.create({
  container: { flex: 1, backgroundColor: theme.colors.background, padding: 16 },
  title: { fontSize: 18, fontWeight: '700', marginBottom: 16, color: theme.colors.text },
  form: { marginBottom: 20, padding: 12, borderRadius: 8, borderWidth: 1, borderColor: theme.colors.muted, backgroundColor: theme.colors.surface ?? 'transparent' },
  label: { marginBottom: 4, fontWeight: '600', color: theme.colors.text },
  input: { borderWidth: 1, borderColor: theme.colors.muted, borderRadius: 6, padding: 8, marginBottom: 12, color: theme.colors.text },
  btn: { padding: 12, borderRadius: 6, borderWidth: 1, borderColor: theme.colors.primary, marginBottom: 8, alignItems: 'center', backgroundColor: theme.colors.primaryLight ?? 'transparent' },
  btnText: { color: theme.colors.text, fontWeight: '600' },
  danger: { borderColor: 'red' },
  stats: { marginBottom: 20, padding: 12, borderRadius: 8, borderWidth: 1, borderColor: theme.colors.muted, backgroundColor: theme.colors.surface ?? 'transparent' },
  statsTitle: { fontWeight: '700', marginBottom: 8 },
  sectionTitle: { fontWeight: '700', marginBottom: 12, fontSize: 16 },
  empty: { fontStyle: 'italic', color: theme.colors.muted },
  item: { padding: 10, borderRadius: 6, borderWidth: 1, borderColor: theme.colors.muted, marginBottom: 10, backgroundColor: theme.colors.surface ?? 'transparent' },
  smallBtn: { marginTop: 6, padding: 6, borderRadius: 4, borderWidth: 1, borderColor: theme.colors.primary, alignItems: 'center' },
});

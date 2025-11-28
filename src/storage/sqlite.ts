import * as SQLite from 'expo-sqlite'
import { QueueItem, QueueStatusRow } from '../types/queue'

let db: SQLite.SQLiteDatabase | null = null

export async function initDb() {
  if (db) {
    console.log('DB already initialized')
    return db
  }

  console.log('Opening database...')

  db = await SQLite.openDatabaseAsync('prodflow.db')

  await db.execAsync(`
    CREATE TABLE IF NOT EXISTS request_queue (
      id TEXT PRIMARY KEY NOT NULL,
      uniq_key TEXT,
      username TEXT,
      method TEXT,
      path TEXT,
      body TEXT,
      headers TEXT,
      created_at INTEGER,
      attempts INTEGER DEFAULT 0,
      last_attempt_at INTEGER,
      next_retry_at INTEGER,
      ttl INTEGER,
      status TEXT
    );
  `)

  try {
    await db.execAsync(`ALTER TABLE request_queue ADD COLUMN response_code INTEGER;`)
  } catch {}
  try {
    await db.execAsync(`ALTER TABLE request_queue ADD COLUMN response_body TEXT;`)
  } catch {}
  try {
    await db.execAsync(`ALTER TABLE request_queue ADD COLUMN status TEXT;`)
  } catch {}

  return db
}

function getDb(): SQLite.SQLiteDatabase {
  if (!db) {
    throw new Error('❌ DB is not initialized. Call initDb() first.')
  }
  return db
}

export async function addToQueue(item: QueueItem) {
  const db = getDb()

  await db.runAsync(
    `INSERT OR REPLACE INTO request_queue
     (id, uniq_key, username, method, path, body, headers, created_at, attempts, next_retry_at, ttl, status)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
    [
      item.id,
      item.uniq_key,
      item.username ?? null,
      item.method,
      item.path,
      item.body ?? null,
      item.headers ?? null,
      item.created_at,
      item.attempts ?? 0,
      item.next_retry_at ?? item.created_at,
      item.ttl ?? 0,
      item.status ?? 'pending'
    ]
  )
}

export async function getDue(): Promise<any[]> {
  const db = getDb()

  const rows = await db.getAllAsync(
    `SELECT * FROM request_queue 
     WHERE status = 'pending' 
     AND next_retry_at <= ?`,
    [Date.now()]
  )

  return rows
}

export async function incrementAttempts(
  id: string,
  nextRetryAt: number
) {
  const db = getDb()

  await db.runAsync(
    `UPDATE request_queue
     SET attempts = attempts + 1,
         last_attempt_at = ?,
         next_retry_at = ?
     WHERE id = ?`,
    [Date.now(), nextRetryAt, id]
  )
}


export async function markSent(id: string) {
  const db = getDb()

  await db.runAsync(
    `UPDATE request_queue 
     SET status = 'sent' 
     WHERE id = ?`,
    [id]
  )
}

export async function markFailed(id: string) {
  const db = getDb()

  await db.runAsync(
    `UPDATE request_queue 
     SET status = 'failed' 
     WHERE id = ?`,
    [id]
  )
}




export async function getAllQueue(): Promise<any[]> {
  const db = getDb()
  const rows = await db.getAllAsync(
    `SELECT * FROM request_queue ORDER BY created_at DESC`
  )
  return rows
}

export async function getById(id: string) {
  const db = getDb()
  const rows = await db.getAllAsync(`SELECT * FROM request_queue WHERE id = ?`, [id])
  return rows.length ? rows[0] : null
}


export async function getByUniqKey(uniq_key: string): Promise<QueueItem | null> {
  const db = getDb()
  const rows = await db.getAllAsync<QueueItem>(
    `SELECT * FROM request_queue WHERE uniq_key = ?`,
    [uniq_key]
  )

  return rows.length ? rows[0] : null
}


export async function setNextRetry(id: string, nextRetryAt: number) {
  const db = getDb()
  await db.runAsync(
    `UPDATE request_queue SET next_retry_at = ? WHERE id = ?`,
    [nextRetryAt, id]
  )
}


export async function updateResponse(id: string, payload: { status_code?: number; response_body?: string; last_attempt_at?: number }) {
  const db = getDb()
  await db.runAsync(
    `UPDATE request_queue SET response_code = ?, response_body = ?, last_attempt_at = ? WHERE id = ?`,
    [payload.status_code ?? null, payload.response_body ?? null, payload.last_attempt_at ?? Date.now(), id]
  )
}


export async function getStats() {
  const db = getDb()
  const rows = await db.getAllAsync<QueueStatusRow>(
    `SELECT status, COUNT(*) as cnt FROM request_queue GROUP BY status`
  )
  const out: Record<string, number> = { total: 0, pending: 0, sent: 0, failed: 0 }
  for (const r of rows) {
    out[r.status] = r.cnt
    out.total += r.cnt
  }
  if (out.total === 0) {
    const all = await db.getAllAsync<{ cnt: number }>(`SELECT COUNT(*) as cnt FROM request_queue`)
    out.total = all[0]?.cnt ?? 0
  }
  return out
}

export async function purgeFailed() {
  const db = getDb()
  await db.runAsync(`DELETE FROM request_queue WHERE status = 'failed'`)
}
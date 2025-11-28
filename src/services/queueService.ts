// src/services/queueService.ts
import * as sqlite from '../storage/sqlite'
import { makeId, makeUniqueKey } from '../utils/uid'
import { apiV1 } from '../api/clients'
import { QUEUE_MAX_ATTEMPTS, QUEUE_RETRY_BASE_MS, QUEUE_TTL_MS } from '../constants/config'
import SecureStore from '../storage/secureStore'

export async function enqueueRequest(params: {
  username?: string | null
  method: string
  path: string
  body?: any
  headers?: any
  ttlMs?: number
  force?: boolean
}) {
  const id = makeId()
  const androidId = await SecureStore.getItem('prodflow_android_id')

  const timestamp = Date.now()

  const uniqKey = await makeUniqueKey(
    params.username ?? null,
    params.method,
    params.path,
    androidId ?? null,
    timestamp
  )

  if (!params.force) {
    const exists = await sqlite.getByUniqKey(uniqKey)
    if (exists) {
      return exists.id
    }
  }

  await sqlite.addToQueue({
    id,
    uniq_key: uniqKey,
    username: params.username || null,
    method: params.method,
    path: params.path,
    body: params.body ? JSON.stringify(params.body) : '',
    headers: params.headers ? JSON.stringify(params.headers) : '',
    created_at: timestamp,
    attempts: 0,
    next_retry_at: timestamp,
    ttl: params.ttlMs ?? QUEUE_TTL_MS,
    status: 'pending'
  })

  return id
}

function calcNextRetry(attempts: number) {
  const base = Math.pow(2, attempts) * QUEUE_RETRY_BASE_MS
  const jitter = Math.floor(Math.random() * Math.min(base, 1000))
  return Date.now() + base + jitter
}

export async function processQueueTick() {
  const rows = await sqlite.getDue()
  const results: Array<any> = []

  for (const r of rows) {
    try {
      if (r.ttl && Date.now() - r.created_at > r.ttl) {
        await sqlite.markFailed(r.id)
        results.push({ id: r.id, ok: false, status: 'ttl_exceeded' })
        continue
      }

      if ((r.attempts || 0) >= QUEUE_MAX_ATTEMPTS) {
        await sqlite.markFailed(r.id)
        results.push({ id: r.id, ok: false, status: 'max_attempts' })
        continue
      }

      let body: any = undefined
      if (r.body) {
        try { body = JSON.parse(r.body) } catch { body = r.body }
      }

      let headers: Record<string, any> = {}
      if (r.headers) {
        try { headers = JSON.parse(r.headers) } catch { headers = {} }
      }

      const response = await apiV1.request({
        url: r.path,
        method: r.method,
        data: body,
        headers
      })

      await sqlite.updateResponse(r.id, {
        status_code: response.status,
        response_body: JSON.stringify(response.data),
        last_attempt_at: Date.now()
      })

      await sqlite.markSent(r.id)

      results.push({ id: r.id, ok: true, status: 'sent', code: response.status })
    } catch (e: any) {
      const next = calcNextRetry(r.attempts || 0)

      await sqlite.incrementAttempts(r.id, next)

      results.push({
        id: r.id,
        ok: false,
        status: 'retry_scheduled',
        attempts: (r.attempts || 0) + 1,
        next_retry_at: next,
        error: e?.message ?? String(e)
      })
    }
  }

  return results
}

// Обертка для совместимости
export async function processQueueOnce() {
  return processQueueTick()
}

/* Админ / отладка */
export async function getQueueStats() {
  return sqlite.getStats()
}

export async function getAllQueue() {
  return sqlite.getAllQueue()
}

export async function forceProcessItem(id: string) {
  const row = await sqlite.getById(id)
  if (!row) throw new Error('Not found')

  await sqlite.setNextRetry(id, Date.now() - 1)

  const res = await processQueueTick()
  return res.find((r) => r.id === id) ?? null
}

export async function testEnqueue({
  method,
  path,
  body
}: {
  method: string
  path: string
  body?: any
}) {
  return enqueueRequest({ method, path, body, force: true })
}

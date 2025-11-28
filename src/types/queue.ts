export type QueueStatus = 'pending' | 'sent' | 'failed'

export interface QueueItem {
  id: string
  uniq_key: string
  username?: string | null
  method: string
  path: string
  body?: string
  headers?: string
  created_at: number
  attempts: number
  next_retry_at: number
  ttl: number
  status: QueueStatus
}


export interface QueueStatusRow {
  status: string
  cnt: number
}
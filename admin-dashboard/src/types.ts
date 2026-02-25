export const IST_EMAIL_SUFFIX = '@ist.edu.pk'

export interface User {
  email: string
  role: 'admin' | 'user'
  password: string
}

export interface CallLogEntry {
  id: string
  sessionId: string
  userEmail: string
  durationSec: number
  sttTime: number
  llmTime: number
  ttsTime: number
  e2eTime: number
  confidenceScore: number | null
  timestamp: string
  transcript?: string
  aiResponse?: string
}

export interface KnowledgeDoc {
  id: string
  title: string
  content: string
  lastUpdated: string
  version: number
}

export interface LoginHistoryEntry {
  email: string
  timestamp: string
  success: boolean
}

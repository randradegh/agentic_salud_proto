export interface Message {
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
  metadata?: Record<string, any>
}

export interface ChatRequest {
  message: string
  session_id?: string
  metadata?: Record<string, any>
}

export interface ChatResponse {
  response: string
  session_id: string
  actions: Array<Record<string, any>>
  metadata?: Record<string, any>
}

export interface Session {
  session_id: string
  created_at: string
  expires_at: string
}

import { ChatRequest, ChatResponse, Session } from '@/types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function createSession(): Promise<Session> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/sessions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    
    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`Error creando sesión: ${response.status} ${errorText}`)
    }
    
    return response.json()
  } catch (error) {
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error(`No se pudo conectar con el servidor. Verifica que el backend esté corriendo en ${API_BASE_URL}`)
    }
    throw error
  }
}

export async function sendMessage(request: ChatRequest): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  })
  
  if (!response.ok) {
    throw new Error('Error enviando mensaje')
  }
  
  return response.json()
}

export async function* streamMessage(request: ChatRequest): AsyncGenerator<string, void, unknown> {
  const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  })
  
  if (!response.ok) {
    const errorBody = await response.text()
    let detail = ''
    try {
      const j = JSON.parse(errorBody)
      detail = j.detail || j.message || errorBody
    } catch {
      detail = errorBody || `HTTP ${response.status}`
    }
    throw new Error(detail)
  }
  
  const reader = response.body?.getReader()
  const decoder = new TextDecoder()
  
  if (!reader) {
    throw new Error('No se pudo obtener el stream')
  }
  
  let buffer = ''
  
  while (true) {
    const { done, value } = await reader.read()
    
    if (done) break
    
    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() || ''
    
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const data = JSON.parse(line.slice(6))
          if (data.type === 'token') {
            if (data.content != null) yield String(data.content)
          } else if (data.type === 'done') {
            return
          } else if (data.type === 'error') {
            throw new Error(data.content)
          }
        } catch (e) {
          // Ignorar errores de parsing
        }
      }
    }
  }
}

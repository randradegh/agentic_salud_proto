'use client'

import { useState, useEffect, useRef } from 'react'
import { Message } from '@/types'
import { MessageList } from './MessageList'
import { MessageInput } from './MessageInput'
import { sendMessage, streamMessage, createSession } from '@/lib/api'

export function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([])
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [connectionError, setConnectionError] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Crear sesión al montar
    setConnectionError(null)
    createSession()
      .then((session) => {
        setSessionId(session.session_id)
        setConnectionError(null)
      })
      .catch((error) => {
        console.error('Error creando sesión:', error)
        setConnectionError(error.message)
        // Mostrar mensaje de error al usuario
        const errorMessage: Message = {
          role: 'assistant',
          content: `Error al conectar con el servidor: ${error.message}. Por favor, verifica que el backend esté corriendo en http://localhost:8000`,
          timestamp: new Date().toISOString(),
        }
        setMessages([errorMessage])
      })
  }, [])

  useEffect(() => {
    // Scroll automático al final
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  const handleSend = async (content: string) => {
    if (!sessionId) return

    // Añadir mensaje del usuario
    const userMessage: Message = {
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
    }
    setMessages((prev) => [...prev, userMessage])
    setIsLoading(true)

    try {
      // Usar streaming
      const assistantMessage: Message = {
        role: 'assistant',
        content: '',
        timestamp: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, assistantMessage])

      let fullResponse = ''
      for await (const token of streamMessage({
        message: content,
        session_id: sessionId,
      })) {
        fullResponse += token
        setMessages((prev) => {
          const updated = [...prev]
          updated[updated.length - 1] = {
            ...assistantMessage,
            content: fullResponse,
          }
          return updated
        })
      }
    } catch (error) {
      console.error('Error enviando mensaje:', error)
      const errorMsg = error instanceof Error ? error.message : 'Error desconocido'
      const errorMessage: Message = {
        role: 'assistant',
        content: `Lo siento, hubo un error: ${errorMsg}. Comprueba que Ollama esté corriendo (ollama serve) y que el modelo llama3.1:8b esté instalado.`,
        timestamp: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-[600px] max-h-[80vh] border rounded-lg bg-card shadow-lg">
      <div className="border-b p-4 bg-muted/50">
        <h2 className="text-lg font-semibold">Consultorio Dental</h2>
        <p className="text-sm text-muted-foreground">
          Pregúntame sobre servicios, precios o agenda tu cita en la Ciudad de México
        </p>
        {connectionError && (
          <p className="text-sm text-red-500 mt-2">
            ⚠️ {connectionError}
          </p>
        )}
      </div>
      
      <div className="flex-1 overflow-hidden">
        <MessageList messages={messages} isLoading={isLoading} />
        <div ref={messagesEndRef} />
      </div>
      
      <MessageInput onSend={handleSend} disabled={isLoading || !sessionId} />
    </div>
  )
}

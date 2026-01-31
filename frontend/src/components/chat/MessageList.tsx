'use client'

import { Message } from '@/types'
import { formatTime } from '@/lib/utils'
import { TypingIndicator } from './TypingIndicator'

interface MessageListProps {
  messages: Message[]
  isLoading?: boolean
}

export function MessageList({ messages, isLoading }: MessageListProps) {
  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.length === 0 && (
        <div className="text-center text-muted-foreground mt-8">
          <p className="text-lg font-medium">¡Hola! 👋</p>
          <p className="mt-2">Soy tu asistente virtual. ¿En qué puedo ayudarte hoy?</p>
        </div>
      )}
      
      {messages.map((message, index) => (
        <div
          key={index}
          className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
        >
          <div
            className={`max-w-[80%] rounded-lg px-4 py-2 ${
              message.role === 'user'
                ? 'bg-primary text-primary-foreground'
                : 'bg-muted text-muted-foreground'
            }`}
          >
            <p className="text-sm whitespace-pre-wrap">{message.content}</p>
            <p className="text-xs opacity-70 mt-1">
              {formatTime(message.timestamp)}
            </p>
          </div>
        </div>
      ))}
      
      {isLoading && <TypingIndicator />}
    </div>
  )
}

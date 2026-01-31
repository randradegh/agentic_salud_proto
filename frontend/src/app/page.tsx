'use client'

import { ChatWindow } from '@/components/chat/ChatWindow'

export default function Home() {
  return (
    <main className="min-h-screen p-4 md:p-8 flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="w-full max-w-4xl">
        <div className="mb-6 text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Consultorio Dental CDMX
          </h1>
          <p className="text-gray-600">
            Asistente virtual: servicios, precios y citas en la Ciudad de México
          </p>
        </div>
        <ChatWindow />
      </div>
    </main>
  )
}

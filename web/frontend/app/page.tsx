'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, BookOpen, ChevronDown, ChevronUp, User, FileText } from 'lucide-react'

// =============================================================================
// Types
// =============================================================================

interface Source {
  reference: string
  page: number
  chapter?: string
  part?: string
  section?: string
  snippet: string
}

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  references?: string[]
  sources?: Source[]
}

// =============================================================================
// Example Questions
// =============================================================================

const EXAMPLE_QUESTIONS = [
  "What is the VAT rate in Nigeria?",
  "What are the penalties for tax evasion?",
  "How is company income tax calculated?",
  "What are the exemptions for capital gains tax?",
]

// =============================================================================
// Source Card Component
// =============================================================================

function SourceCard({ source, index }: { source: Source; index: number }) {
  return (
    <div className="rounded-lg bg-[#1a1a1a] border border-[#2a2a2a] overflow-hidden">
      <div className="flex items-center gap-2 px-3 py-2 bg-[#141414] border-b border-[#2a2a2a]">
        <FileText className="w-3.5 h-3.5 text-nigeria-green" />
        <span className="text-xs font-medium text-[#ededed]">
          Source {index}: {source.reference}
        </span>
        <span className="text-xs text-[#737373] ml-auto">Page {source.page}</span>
      </div>
      <div className="px-3 py-2">
        <p className="text-xs text-[#a3a3a3] leading-relaxed line-clamp-3">
          {source.snippet}
        </p>
      </div>
      <div className="flex gap-2 px-3 py-2 border-t border-[#2a2a2a]">
        {source.chapter && (
          <span className="text-xs px-1.5 py-0.5 rounded bg-[#2a2a2a] text-[#737373]">
            {source.chapter}
          </span>
        )}
        {source.part && (
          <span className="text-xs px-1.5 py-0.5 rounded bg-[#2a2a2a] text-[#737373]">
            {source.part}
          </span>
        )}
        {source.section && (
          <span className="text-xs px-1.5 py-0.5 rounded bg-[#2a2a2a] text-[#737373]">
            Section {source.section}
          </span>
        )}
      </div>
    </div>
  )
}

// =============================================================================
// Chat Message Component
// =============================================================================

function ChatMessage({ message }: { message: Message }) {
  const [showSources, setShowSources] = useState(false)
  const isUser = message.role === 'user'

  return (
    <div className={`flex gap-3 message-animate ${isUser ? 'flex-row-reverse' : ''}`}>
      <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
        isUser ? 'bg-[#2a2a2a]' : 'bg-nigeria-green'
      }`}>
        {isUser ? (
          <User className="w-4 h-4 text-[#ededed]" />
        ) : (
          <BookOpen className="w-4 h-4 text-white" />
        )}
      </div>

      <div className={`flex flex-col max-w-[80%] ${isUser ? 'items-end' : 'items-start'}`}>
        <div className={`px-4 py-3 rounded-lg ${
          isUser
            ? 'bg-nigeria-green text-white'
            : 'bg-[#141414] border border-[#2a2a2a] text-[#ededed]'
        }`}>
          <p className="whitespace-pre-wrap text-sm leading-relaxed">{message.content}</p>
        </div>

        {!isUser && message.references && message.references.length > 0 && (
          <div className="mt-3 w-full">
            <div className="flex flex-wrap gap-2 mb-2">
              {message.references.slice(0, 3).map((ref, index) => (
                <span
                  key={index}
                  className="text-xs px-2 py-1 rounded bg-nigeria-green/10 text-nigeria-green border border-nigeria-green/20"
                >
                  {ref}
                </span>
              ))}
              {message.references.length > 3 && (
                <span className="text-xs px-2 py-1 rounded bg-[#2a2a2a] text-[#737373]">
                  +{message.references.length - 3} more
                </span>
              )}
            </div>

            {message.sources && message.sources.length > 0 && (
              <>
                <button
                  onClick={() => setShowSources(!showSources)}
                  className="flex items-center gap-1 text-xs text-[#737373] hover:text-nigeria-green transition-colors"
                >
                  {showSources ? (
                    <><ChevronUp className="w-3 h-3" /> Hide sources</>
                  ) : (
                    <><ChevronDown className="w-3 h-3" /> View {message.sources.length} sources</>
                  )}
                </button>

                {showSources && (
                  <div className="mt-3 space-y-2">
                    {message.sources.map((source, index) => (
                      <SourceCard key={index} source={source} index={index + 1} />
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

// =============================================================================
// Main Page Component
// =============================================================================

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async (query: string) => {
    if (!query.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: query,
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, k: 10 }),
      })

      if (!response.ok) throw new Error('Failed to get response')

      const data = await response.json()

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.answer,
        references: data.references,
        sources: data.sources,
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    sendMessage(input)
  }

  return (
    <main className="flex flex-col h-screen bg-[#0a0a0a]">
      {/* Header */}
      <header className="flex-shrink-0 border-b border-[#2a2a2a] bg-[#0a0a0a]">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-nigeria-green flex items-center justify-center">
              <BookOpen className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-white">Nigeria Tax Act 2025</h1>
              <p className="text-sm text-[#737373]">AI-Powered Legal Assistant</p>
            </div>
          </div>
        </div>
      </header>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-4 py-6">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
              <div className="w-16 h-16 rounded-2xl bg-nigeria-green/10 flex items-center justify-center mb-6">
                <BookOpen className="w-8 h-8 text-nigeria-green" />
              </div>
              <h2 className="text-2xl font-semibold text-white mb-2">
                Nigeria Tax Act 2025 Assistant
              </h2>
              <p className="text-[#737373] mb-8 max-w-md">
                Ask questions about Nigerian tax law and get accurate answers with citations from the official Tax Act.
              </p>

              <div className="w-full max-w-lg">
                <p className="text-sm text-[#737373] mb-3">Try asking:</p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {EXAMPLE_QUESTIONS.map((question, index) => (
                    <button
                      key={index}
                      onClick={() => sendMessage(question)}
                      className="text-left px-4 py-3 rounded-lg bg-[#141414] border border-[#2a2a2a] hover:border-nigeria-green/50 hover:bg-[#1a1a1a] transition-colors text-sm text-[#ededed]"
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}

              {isLoading && (
                <div className="flex gap-3 message-animate">
                  <div className="w-8 h-8 rounded-lg bg-nigeria-green flex items-center justify-center flex-shrink-0">
                    <BookOpen className="w-4 h-4 text-white" />
                  </div>
                  <div className="flex items-center gap-1 px-4 py-3 rounded-lg bg-[#141414]">
                    <div className="w-2 h-2 rounded-full bg-nigeria-green loading-dot"></div>
                    <div className="w-2 h-2 rounded-full bg-nigeria-green loading-dot"></div>
                    <div className="w-2 h-2 rounded-full bg-nigeria-green loading-dot"></div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </div>

      {/* Input Area */}
      <div className="flex-shrink-0 border-t border-[#2a2a2a] bg-[#0a0a0a]">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <form onSubmit={handleSubmit} className="flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about Nigerian tax law..."
              disabled={isLoading}
              className="flex-1 px-4 py-3 rounded-lg bg-[#141414] border border-[#2a2a2a] focus:border-nigeria-green focus:outline-none text-white placeholder-[#737373] disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="px-4 py-3 rounded-lg bg-nigeria-green hover:bg-nigeria-green-dark disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Send className="w-5 h-5 text-white" />
            </button>
          </form>
          <p className="text-xs text-[#737373] mt-2 text-center">
            Responses are generated from the Nigeria Tax Act 2025. Always verify with official sources.
          </p>
        </div>
      </div>
    </main>
  )
}

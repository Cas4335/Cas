import React, { useState, useRef, useEffect, FormEvent } from 'react'
import CitationCard from '../components/CitationCard'

interface Citation {
  chunk_id: string
  source_id: string
  source_path: string
  title: string
  department: string
  doc_type: string
  score: number
  excerpt: string
}

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  citations?: Citation[]
  grounded?: boolean
  loading?: boolean
}

interface Props {
  token: string
  userName: string
  roles: string[]
  onLogout: () => void
}

const API_BASE = import.meta.env.VITE_API_URL || '/api'

const styles: Record<string, React.CSSProperties> = {
  layout: {
    display: 'flex',
    flexDirection: 'column',
    height: '100vh',
    background: '#f5f5f5',
  },
  header: {
    background: '#1e3a5f',
    color: '#fff',
    padding: '12px 20px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    flexShrink: 0,
  },
  headerTitle: { fontSize: 16, fontWeight: 700 },
  headerUser: { fontSize: 13, opacity: 0.8 },
  logoutBtn: {
    background: 'transparent',
    border: '1px solid rgba(255,255,255,0.4)',
    color: '#fff',
    padding: '5px 12px',
    borderRadius: 4,
    cursor: 'pointer',
    fontSize: 12,
  },
  messages: {
    flex: 1,
    overflowY: 'auto',
    padding: '20px',
    display: 'flex',
    flexDirection: 'column',
    gap: 16,
  },
  messageUser: {
    alignSelf: 'flex-end',
    background: '#2563eb',
    color: '#fff',
    borderRadius: '12px 12px 2px 12px',
    padding: '10px 16px',
    maxWidth: '70%',
    fontSize: 14,
    lineHeight: 1.5,
  },
  messageAssistant: {
    alignSelf: 'flex-start',
    background: '#fff',
    border: '1px solid #e5e7eb',
    borderRadius: '12px 12px 12px 2px',
    padding: '14px 16px',
    maxWidth: '80%',
    fontSize: 14,
    lineHeight: 1.6,
  },
  ungroundedBadge: {
    display: 'inline-block',
    background: '#fef9c3',
    color: '#854d0e',
    fontSize: 11,
    padding: '2px 8px',
    borderRadius: 4,
    marginBottom: 8,
  },
  citationsSection: { marginTop: 12 },
  citationsLabel: { fontSize: 12, fontWeight: 600, color: '#666', marginBottom: 6 },
  inputArea: {
    padding: '16px 20px',
    background: '#fff',
    borderTop: '1px solid #e5e7eb',
    flexShrink: 0,
  },
  form: { display: 'flex', gap: 10 },
  input: {
    flex: 1,
    padding: '10px 14px',
    border: '1px solid #d1d5db',
    borderRadius: 8,
    fontSize: 14,
    outline: 'none',
  },
  sendBtn: {
    background: '#2563eb',
    color: '#fff',
    border: 'none',
    borderRadius: 8,
    padding: '10px 20px',
    fontSize: 14,
    fontWeight: 600,
    cursor: 'pointer',
  },
  sendBtnDisabled: { background: '#93c5fd', cursor: 'not-allowed' },
  loadingDots: { color: '#888', fontSize: 20, letterSpacing: 4 },
  roles: { fontSize: 11, color: 'rgba(255,255,255,0.6)', marginTop: 2 },
}

export default function ChatPage({ token, userName, roles, onLogout }: Props) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: 'Hello! I can answer questions based on your company\'s approved documents. Ask me anything.',
    },
  ])
  const [query, setQuery] = useState('')
  const [sending, setSending] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const q = query.trim()
    if (!q || sending) return

    setQuery('')
    setSending(true)

    const userMsg: Message = { id: Date.now().toString(), role: 'user', content: q }
    const loadingMsg: Message = { id: 'loading', role: 'assistant', content: '', loading: true }
    setMessages(prev => [...prev, userMsg, loadingMsg])

    try {
      const res = await fetch(`${API_BASE}/chat/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ query: q }),
      })

      if (!res.ok) {
        throw new Error(`API error: ${res.status}`)
      }

      const data = await res.json()
      const assistantMsg: Message = {
        id: Date.now().toString() + '-a',
        role: 'assistant',
        content: data.answer,
        citations: data.citations,
        grounded: data.grounded,
      }

      setMessages(prev => prev.filter(m => m.id !== 'loading').concat(assistantMsg))
    } catch (err) {
      const errMsg: Message = {
        id: Date.now().toString() + '-err',
        role: 'assistant',
        content: 'Sorry, there was an error processing your request. Please try again.',
      }
      setMessages(prev => prev.filter(m => m.id !== 'loading').concat(errMsg))
    } finally {
      setSending(false)
    }
  }

  return (
    <div style={styles.layout}>
      <div style={styles.header}>
        <div>
          <div style={styles.headerTitle}>PHX Knowledge</div>
          <div style={styles.roles}>Roles: {roles.join(', ')}</div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <span style={styles.headerUser}>{userName}</span>
          <button style={styles.logoutBtn} onClick={onLogout}>Sign out</button>
        </div>
      </div>

      <div style={styles.messages}>
        {messages.map(msg => (
          <div key={msg.id}>
            {msg.role === 'user' ? (
              <div style={styles.messageUser}>{msg.content}</div>
            ) : (
              <div style={styles.messageAssistant}>
                {msg.loading ? (
                  <span style={styles.loadingDots}>···</span>
                ) : (
                  <>
                    {msg.grounded === false && (
                      <div style={styles.ungroundedBadge}>
                        No matching documents found
                      </div>
                    )}
                    <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
                    {msg.citations && msg.citations.length > 0 && (
                      <div style={styles.citationsSection}>
                        <div style={styles.citationsLabel}>
                          Sources ({msg.citations.length})
                        </div>
                        {msg.citations.map((c, i) => (
                          <CitationCard key={c.chunk_id} citation={c} index={i} />
                        ))}
                      </div>
                    )}
                  </>
                )}
              </div>
            )}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      <div style={styles.inputArea}>
        <form style={styles.form} onSubmit={handleSubmit}>
          <input
            style={styles.input}
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="Ask a question about your company's documents..."
            disabled={sending}
          />
          <button
            type="submit"
            style={{ ...styles.sendBtn, ...(sending ? styles.sendBtnDisabled : {}) }}
            disabled={sending}
          >
            {sending ? '...' : 'Send'}
          </button>
        </form>
      </div>
    </div>
  )
}

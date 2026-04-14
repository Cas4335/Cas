import React, { useState } from 'react'

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

interface Props {
  citation: Citation
  index: number
}

const styles: Record<string, React.CSSProperties> = {
  card: {
    border: '1px solid #e5e7eb',
    borderRadius: 6,
    padding: '10px 14px',
    marginBottom: 8,
    background: '#fafafa',
    cursor: 'pointer',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  title: {
    fontSize: 13,
    fontWeight: 600,
    color: '#1d4ed8',
    flex: 1,
  },
  badge: {
    fontSize: 11,
    background: '#e0e7ff',
    color: '#3730a3',
    borderRadius: 4,
    padding: '2px 7px',
    marginLeft: 8,
    flexShrink: 0,
  },
  meta: {
    fontSize: 11,
    color: '#888',
    marginTop: 3,
  },
  excerpt: {
    fontSize: 12,
    color: '#444',
    marginTop: 8,
    lineHeight: 1.5,
    borderLeft: '3px solid #d1d5db',
    paddingLeft: 10,
  },
}

export default function CitationCard({ citation, index }: Props) {
  const [expanded, setExpanded] = useState(false)
  const score = Math.round(citation.score * 100)

  return (
    <div style={styles.card} onClick={() => setExpanded(!expanded)}>
      <div style={styles.header}>
        <div style={styles.title}>[{index + 1}] {citation.title}</div>
        <div style={styles.badge}>{score}% match</div>
      </div>
      <div style={styles.meta}>
        {citation.department} · {citation.doc_type} · {citation.source_path}
      </div>
      {expanded && (
        <div style={styles.excerpt}>{citation.excerpt}</div>
      )}
    </div>
  )
}

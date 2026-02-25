import { useState, useMemo } from 'react'
import { getCallLogs } from '../data/mockCallLogs'
import type { CallLogEntry } from '../types'
import './CallLogs.css'

export function CallLogs() {
  const [logs] = useState<CallLogEntry[]>(() => getCallLogs())
  const [search, setSearch] = useState('')
  const [selected, setSelected] = useState<CallLogEntry | null>(null)

  const filtered = useMemo(() => {
    if (!search.trim()) return logs
    const s = search.toLowerCase()
    return logs.filter(
      l =>
        l.sessionId.toLowerCase().includes(s) ||
        l.userEmail.toLowerCase().includes(s) ||
        l.timestamp.toLowerCase().includes(s)
    )
  }, [logs, search])

  return (
    <div className="calllogs-page">
      <h2 className="page-heading">Call Logs</h2>
      <div className="card">
        <div className="calllogs-toolbar">
          <input
            type="search"
            placeholder="Search by session ID, email, or timestamp..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="calllogs-search"
          />
        </div>
        <div className="table-wrap">
          <table className="calllogs-table">
            <thead>
              <tr>
                <th>Session ID</th>
                <th>User Email</th>
                <th>Duration</th>
                <th>STT (s)</th>
                <th>LLM (s)</th>
                <th>TTS (s)</th>
                <th>E2E (s)</th>
                <th>Confidence</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(log => (
                <tr key={log.id} onClick={() => setSelected(log)} className="calllogs-row">
                  <td>{log.sessionId}</td>
                  <td>{log.userEmail}</td>
                  <td>{log.durationSec}s</td>
                  <td>{log.sttTime.toFixed(2)}</td>
                  <td>{log.llmTime.toFixed(2)}</td>
                  <td>{log.ttsTime.toFixed(2)}</td>
                  <td>{log.e2eTime.toFixed(2)}</td>
                  <td>{log.confidenceScore != null ? (log.confidenceScore * 100).toFixed(0) + '%' : '—'}</td>
                  <td>{new Date(log.timestamp).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {filtered.length === 0 && <p className="calllogs-empty">No logs match your search.</p>}
      </div>

      {selected && (
        <div className="modal-overlay" onClick={() => setSelected(null)}>
          <div className="modal card" onClick={e => e.stopPropagation()}>
            <h3 className="card-title">Call details</h3>
            <p><strong>Session:</strong> {selected.sessionId}</p>
            <p><strong>Timestamp:</strong> {new Date(selected.timestamp).toLocaleString()}</p>
            <p><strong>Transcript:</strong></p>
            <div className="modal-transcript">{selected.transcript || '—'}</div>
            <p><strong>AI Response:</strong></p>
            <div className="modal-response">{selected.aiResponse || '—'}</div>
            <button type="button" className="btn btn-primary" onClick={() => setSelected(null)}>Close</button>
          </div>
        </div>
      )}
    </div>
  )
}

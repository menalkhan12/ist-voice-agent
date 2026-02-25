import { useMemo } from 'react'
import { getCallLogs } from '../data/mockCallLogs'
import './Reports.css'

export function Reports() {
  const logs = useMemo(() => getCallLogs(), [])
  const totalCalls = logs.length
  const successfulResponses = logs.filter(l => l.confidenceScore != null && l.confidenceScore >= 0.7).length
  const lowConfidenceCalls = logs.filter(l => l.confidenceScore != null && l.confidenceScore < 0.7).length
  const avgConfidence = totalCalls
    ? logs.reduce((a, l) => a + (l.confidenceScore ?? 0), 0) / totalCalls
    : 0
  const aiAccuracy = totalCalls ? (successfulResponses / totalCalls) * 100 : 0

  const metrics = [
    { label: 'Total Calls', value: totalCalls, accent: true },
    { label: 'Successful Responses', value: successfulResponses, accent: true },
    { label: 'Low Confidence Calls', value: lowConfidenceCalls, accent: false },
    { label: 'AI Accuracy', value: `${aiAccuracy.toFixed(1)}%`, accent: true },
  ]

  return (
    <div className="reports-page">
      <h2 className="page-heading">Reports & Analytics</h2>
      <div className="reports-grid">
        {metrics.map(m => (
          <div key={m.label} className={`card reports-card ${m.accent ? 'accent' : ''}`}>
            <span className="reports-card-label">{m.label}</span>
            <span className="reports-card-value">{m.value}</span>
          </div>
        ))}
      </div>
      <div className="card reports-chart-card">
        <h3 className="card-title">AI Performance Trends</h3>
        <p className="reports-chart-desc">STT time, LLM time, TTS time, and end-to-end latency over time.</p>
        <div className="reports-chart-placeholder">
          <span>Chart placeholder — integrate with backend API for live metrics</span>
        </div>
      </div>
    </div>
  )
}

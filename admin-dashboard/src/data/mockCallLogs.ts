import type { CallLogEntry } from '../types'

const now = new Date().toISOString()

export function getCallLogs(): CallLogEntry[] {
  try {
    const raw = localStorage.getItem('ist_call_logs')
    if (raw) return JSON.parse(raw)
  } catch {}
  return [
    {
      id: '1',
      sessionId: 'sess-a1b2c3',
      userEmail: 'admin@ist.edu.pk',
      durationSec: 45,
      sttTime: 0.8,
      llmTime: 1.2,
      ttsTime: 2.1,
      e2eTime: 4.5,
      confidenceScore: 0.92,
      timestamp: new Date(Date.now() - 3600000).toISOString(),
      transcript: 'User asked about hostel fee.',
      aiResponse: 'IST has hostels for boys and girls. Fee is approximately 45,000 to 60,000 per semester.',
    },
    {
      id: '2',
      sessionId: 'sess-d4e5f6',
      userEmail: 'admissions@ist.edu.pk',
      durationSec: 120,
      sttTime: 0.9,
      llmTime: 1.5,
      ttsTime: 2.3,
      e2eTime: 5.1,
      confidenceScore: 0.88,
      timestamp: new Date(Date.now() - 7200000).toISOString(),
      transcript: 'When do admissions open?',
      aiResponse: 'Admissions usually open in March or April for the Fall semester.',
    },
  ]
}

export function setCallLogs(logs: CallLogEntry[]) {
  localStorage.setItem('ist_call_logs', JSON.stringify(logs))
}

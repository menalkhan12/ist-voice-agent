import type { KnowledgeDoc } from '../types'

const STORAGE_KEY = 'ist_knowledge_docs'

export function getKnowledgeDocs(): KnowledgeDoc[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) return JSON.parse(raw)
  } catch {}
  return [
    {
      id: '1',
      title: 'Admission FAQs',
      content: 'Sample knowledge content. Upload or edit documents here. Changes will be reflected in the AI voice agent after backend integration.',
      lastUpdated: new Date().toISOString(),
      version: 1,
    },
  ]
}

export function saveKnowledgeDoc(doc: KnowledgeDoc) {
  const docs = getKnowledgeDocs()
  const idx = docs.findIndex(d => d.id === doc.id)
  const nextVersion = idx >= 0 ? docs[idx].version + 1 : 1
  const updated: KnowledgeDoc = { ...doc, lastUpdated: new Date().toISOString(), version: nextVersion }
  if (idx >= 0) docs[idx] = updated
  else docs.push(updated)
  localStorage.setItem(STORAGE_KEY, JSON.stringify(docs))
  return updated
}

export function deleteKnowledgeDoc(id: string) {
  const docs = getKnowledgeDocs().filter(d => d.id !== id)
  localStorage.setItem(STORAGE_KEY, JSON.stringify(docs))
}

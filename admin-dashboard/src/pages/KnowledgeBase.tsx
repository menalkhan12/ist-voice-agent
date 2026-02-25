import { useState, useEffect } from 'react'
import { getKnowledgeDocs, saveKnowledgeDoc } from '../data/mockKnowledge'
import type { KnowledgeDoc } from '../types'
import './KnowledgeBase.css'

export function KnowledgeBase() {
  const [docs, setDocs] = useState<KnowledgeDoc[]>(() => getKnowledgeDocs())
  const [editing, setEditing] = useState<KnowledgeDoc | null>(null)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    setDocs(getKnowledgeDocs())
  }, [editing])

  function handleSave() {
    if (!editing) return
    const updated = saveKnowledgeDoc(editing)
    setDocs(prev => prev.map(d => d.id === updated.id ? updated : d))
    setEditing(null)
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  function handleAdd() {
    const newDoc: KnowledgeDoc = {
      id: Date.now().toString(),
      title: 'New Document',
      content: '',
      lastUpdated: new Date().toISOString(),
      version: 1,
    }
    setEditing(newDoc)
  }

  return (
    <div className="kb-page">
      <h2 className="page-heading">Database (Knowledge Base)</h2>
      <div className="card">
        <div className="kb-toolbar">
          <p className="kb-desc">Upload, edit, and manage AI knowledge content. Changes will sync to the voice agent when backend is connected.</p>
          <button type="button" className="btn btn-primary" onClick={handleAdd}>Add Document</button>
        </div>
        {saved && <p className="kb-saved">Changes saved.</p>}
        {editing ? (
          <div className="kb-editor card">
            <h3 className="card-title">Edit document</h3>
            <label>Title</label>
            <input
              value={editing.title}
              onChange={e => setEditing({ ...editing, title: e.target.value })}
              className="kb-input"
            />
            <label>Content</label>
            <textarea
              value={editing.content}
              onChange={e => setEditing({ ...editing, content: e.target.value })}
              className="kb-textarea"
              rows={12}
            />
            <p className="kb-meta">Last updated: {new Date(editing.lastUpdated).toLocaleString()} — Version {editing.version}</p>
            <div className="kb-editor-actions">
              <button type="button" className="btn btn-outline" onClick={() => setEditing(null)}>Cancel</button>
              <button type="button" className="btn btn-primary" onClick={handleSave}>Save</button>
            </div>
          </div>
        ) : (
          <div className="kb-list">
            {docs.map(doc => (
              <div key={doc.id} className="kb-item card">
                <div className="kb-item-head">
                  <h4>{doc.title}</h4>
                  <span className="kb-item-meta">v{doc.version} · {new Date(doc.lastUpdated).toLocaleString()}</span>
                </div>
                <p className="kb-item-preview">{doc.content.slice(0, 120)}{doc.content.length > 120 ? '…' : ''}</p>
                <button type="button" className="btn btn-outline btn-sm" onClick={() => setEditing(doc)}>Edit</button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

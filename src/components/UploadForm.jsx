import { useState } from 'react'
import { Upload, X } from 'lucide-react'
import { request } from '../api'

export default function UploadForm({ onClose, onCreated }) {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [video, setVideo] = useState(null)
  const [thumbnail, setThumbnail] = useState(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function submit(event) {
    event.preventDefault()
    setError('')
    if (!video) return setError('Selecciona un video MP4.')
    if (video.size > 100 * 1024 * 1024) return setError('El video supera el límite de 100 MB.')
    if (thumbnail && thumbnail.size > 10 * 1024 * 1024) return setError('La miniatura supera el límite de 10 MB.')
    const body = new FormData()
    body.append('title', title)
    body.append('description', description)
    body.append('video_file', video)
    if (thumbnail) body.append('thumbnail_file', thumbnail)
    setBusy(true)
    try {
      await request('/videos', { method: 'POST', body })
      onCreated()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="modal-backdrop" role="presentation" onMouseDown={(event) => event.target === event.currentTarget && onClose()}>
      <section className="upload-modal" role="dialog" aria-modal="true" aria-labelledby="upload-title">
        <div className="modal-heading"><div><p className="eyebrow">TU PRÓXIMO ESTRENO</p><h2 id="upload-title">Publica un video</h2></div><button className="icon-button" onClick={onClose} aria-label="Cerrar"><X size={20} /></button></div>
        <form className="upload-form" onSubmit={submit}>
          <label>Título<input value={title} onChange={(event) => setTitle(event.target.value)} required minLength={2} maxLength={140} placeholder="Ponle nombre a tu historia" /></label>
          <label>Descripción<textarea value={description} onChange={(event) => setDescription(event.target.value)} rows={3} maxLength={5000} placeholder="¿Qué debería saber quien lo vea?" /></label>
          <label className="file-drop"><Upload size={21} /><span>{video?.name || 'Elige tu video MP4'}</span><small>Hasta 100 MB</small><input type="file" accept="video/mp4,.mp4" onChange={(event) => setVideo(event.target.files?.[0] || null)} required /></label>
          <label className="file-line">Miniatura (opcional)<input type="file" accept="image/jpeg,image/png,.jpg,.jpeg,.png" onChange={(event) => setThumbnail(event.target.files?.[0] || null)} /></label>
          {error && <p className="form-error" role="alert">{error}</p>}
          <button className="button button-accent upload-submit" disabled={busy}>{busy ? 'Subiendo...' : 'Publicar video'}<Upload size={17} /></button>
        </form>
      </section>
    </div>
  )
}

import { useEffect, useState } from 'react'
import { ArrowUpRight, Clapperboard, Eye, Pencil, Plus, Trash2 } from 'lucide-react'
import { request } from '../api'
import VideoCard from './VideoCard'

export default function ProfileView({ user, onOpenVideo, onUpload, refreshKey }) {
  const [profile, setProfile] = useState(null)
  const [editing, setEditing] = useState(null)
  const [error, setError] = useState('')

  async function load() {
    try { setProfile(await request(`/users/${user.id}`)) } catch (err) { setError(err.message) }
  }
  useEffect(() => { load() }, [user.id, refreshKey])

  async function remove(video) {
    if (!window.confirm(`¿Eliminar “${video.title}”? Esta acción no se puede deshacer.`)) return
    try { await request(`/videos/${video.id}`, { method: 'DELETE' }); await load() } catch (err) { setError(err.message) }
  }

  async function saveEdit(event) {
    event.preventDefault()
    const body = new FormData()
    body.append('title', editing.title)
    body.append('description', editing.description)
    try {
      await request(`/videos/${editing.id}`, { method: 'PUT', body })
      setEditing(null)
      await load()
    } catch (err) { setError(err.message) }
  }

  return (
    <main className="profile-page page-enter">
      <section className="profile-banner"><div className="profile-identity"><div className="avatar avatar-large">{user.name.slice(0, 1).toUpperCase()}</div><div><p className="eyebrow">PERFIL DE CREADOR</p><h1>{user.name}</h1><p>{user.email}</p></div></div><button className="button button-accent" onClick={onUpload}><Plus size={17} /> Publicar video</button></section>
      {error && <p className="form-error">{error}</p>}
      <section className="profile-stats"><div><span>VIDEOS PUBLICADOS</span><strong>{profile?.video_count ?? '—'}</strong></div><div><span>VISTAS TOTALES</span><strong>{profile?.videos.reduce((sum, item) => sum + item.views, 0) ?? '—'}</strong></div><div><span>EN MIMI DESDE</span><strong>{profile ? new Date(user.created_at || Date.now()).getFullYear() : '—'}</strong></div></section>
      <section className="my-videos"><div className="section-heading"><div><p className="eyebrow">TU COLECCIÓN</p><h2>Mis videos <span>{profile?.video_count ?? 0}</span></h2></div><Clapperboard size={20} /></div>
        {profile?.videos.length ? <div className="profile-video-grid">{profile.videos.map((video, index) => <div className="owned-video" key={video.id}><VideoCard video={video} onOpen={onOpenVideo} index={index} /><div className="video-actions"><span><Eye size={14} /> {video.views} vistas</span><button title="Editar video" onClick={() => setEditing({ id: video.id, title: video.title, description: video.description })}><Pencil size={15} /></button><button title="Eliminar video" onClick={() => remove(video)}><Trash2 size={15} /></button></div></div>)}</div> : <div className="empty-profile"><span className="empty-mark">F.</span><div><h3>Tu canal empieza aquí.</h3><p>Publica un video y dale forma a tu colección.</p></div><button className="button button-dark" onClick={onUpload}>Subir el primero <ArrowUpRight size={16} /></button></div>}
      </section>
      {editing && <div className="modal-backdrop"><form className="upload-modal upload-form" onSubmit={saveEdit}><div className="modal-heading"><div><p className="eyebrow">ACTUALIZA TU HISTORIA</p><h2>Editar video</h2></div><button className="icon-button" type="button" onClick={() => setEditing(null)}>×</button></div><label>Título<input value={editing.title} onChange={(event) => setEditing({ ...editing, title: event.target.value })} required maxLength={140} /></label><label>Descripción<textarea value={editing.description} onChange={(event) => setEditing({ ...editing, description: event.target.value })} rows={4} maxLength={5000} /></label><button className="button button-accent upload-submit">Guardar cambios</button></form></div>}
    </main>
  )
}

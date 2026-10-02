import { useEffect, useState } from 'react'
import { ArrowLeft, ArrowUpRight, MessageCircle, Play, Send, Eye } from 'lucide-react'
import { mediaUrl, request } from '../api'
import VideoCard from './VideoCard'

export default function PlayerView({ videoId, onBack, onOpenVideo, user }) {
  const [video, setVideo] = useState(null)
  const [comments, setComments] = useState([])
  const [recommended, setRecommended] = useState([])
  const [comment, setComment] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    Promise.all([request(`/videos/${videoId}`), request(`/videos/${videoId}/comments`), request(`/videos/${videoId}/recommendations`)]).then(([nextVideo, nextComments, nextRecommended]) => {
      if (!active) return
      setVideo(nextVideo)
      setComments(nextComments)
      setRecommended(nextRecommended)
    }).catch((err) => active && setError(err.message))
    return () => { active = false }
  }, [videoId])

  async function postComment(event) {
    event.preventDefault()
    if (!comment.trim()) return
    try {
      const created = await request(`/videos/${videoId}/comments`, { method: 'POST', body: JSON.stringify({ content: comment.trim() }) })
      setComments((existing) => [created, ...existing])
      setComment('')
      setError('')
    } catch (err) { setError(err.message) }
  }

  if (error && !video) return <div className="notice-state">{error}<button onClick={onBack}>Volver</button></div>
  if (!video) return <div className="notice-state">Cargando video...</div>

  return (
    <main className="player-page page-enter">
      <button className="back-link" onClick={onBack}><ArrowLeft size={16} /> Volver al catálogo</button>
      <div className="player-layout">
        <section className="player-main">
          <div className="player-frame"><video src={mediaUrl(video.video_url)} controls playsInline autoPlay poster={mediaUrl(video.thumbnail_url)}><track kind="captions" /></video></div>
          <div className="player-title-row"><div><p className="eyebrow">REPRODUCIENDO AHORA</p><h1>{video.title}</h1></div><span className="player-views"><Eye size={15} /> {video.views} vistas</span></div>
          <div className="creator-strip"><div className="avatar avatar-small">{video.user_name.slice(0, 1).toUpperCase()}</div><div><strong>{video.user_name}</strong><span>Publicado el {new Date(video.created_at).toLocaleDateString('es-EC', { day: 'numeric', month: 'long', year: 'numeric' })}</span></div><span className="creator-note">MIMI ORIGINAL</span></div>
          <p className="video-description">{video.description || 'Sin descripción.'}</p>
          <section className="comments-section"><div className="section-heading"><h2><MessageCircle size={18} /> Comentarios</h2><span>{comments.length}</span></div>
            <form className="comment-form" onSubmit={postComment}><div className="avatar avatar-small">{user.name.slice(0, 1).toUpperCase()}</div><input value={comment} onChange={(event) => setComment(event.target.value)} placeholder="Deja una impresión..." maxLength={2000} /><button className="icon-button send-button" aria-label="Enviar comentario" disabled={!comment.trim()}><Send size={17} /></button></form>
            {error && <p className="form-error">{error}</p>}
            <div className="comment-list">{comments.length ? comments.map((item) => <article className="comment-item" key={item.id}><div className="avatar avatar-small">{item.user_name.slice(0, 1).toUpperCase()}</div><div><strong>{item.user_name}</strong><p>{item.content}</p><time>{new Date(item.created_at).toLocaleDateString('es-EC', { day: 'numeric', month: 'short' })}</time></div></article>) : <p className="empty-inline">Todavía no hay comentarios. Abre la conversación.</p>}</div>
          </section>
        </section>
        <aside className="recommendations"><div className="section-heading"><h2>También en Mimi</h2><ArrowUpRight size={17} /></div>{recommended.length ? recommended.map((item, index) => <VideoCard key={item.id} video={item} onOpen={onOpenVideo} index={index} />) : <div className="recommend-empty"><Play size={19} /><p>Aún no hay más videos.<br />El próximo puede ser tuyo.</p></div>}</aside>
      </div>
    </main>
  )
}

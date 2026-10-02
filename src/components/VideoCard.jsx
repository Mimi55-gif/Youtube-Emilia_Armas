import { Play, MoreVertical } from 'lucide-react'
import { mediaUrl } from '../api'

export default function VideoCard({ video, onOpen, index = 0 }) {
  return (
    <button className="video-card" onClick={() => onOpen(video.id)} style={{ '--card-order': index }}>
      <div className="video-poster">
        {video.thumbnail_url ? <img src={mediaUrl(video.thumbnail_url)} alt="" loading="lazy" /> : <div className={`poster-art poster-art-${video.id % 5}`}><span>F<span className="poster-dot">.</span></span></div>}
          <span className="poster-play"><Play size={15} fill="currentColor" /></span>
          <span className="poster-duration">HD</span>
      </div>
        <div className="video-card-copy">
          <span className="avatar video-avatar">{video.user_name.slice(0, 1).toUpperCase()}</span>
          <div className="video-card-meta"><h3>{video.title}</h3><p>{video.user_name}</p><p className="video-stat-line">{video.views} vistas · {new Date(video.created_at).toLocaleDateString('es-EC', { day: 'numeric', month: 'short' })}</p></div>
          <MoreVertical className="card-more" size={18} />
      </div>
    </button>
  )
}

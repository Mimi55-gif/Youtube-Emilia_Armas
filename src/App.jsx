import { useEffect, useMemo, useState } from 'react'
import { Clapperboard, CircleUserRound, House, LogOut, Plus, Search } from 'lucide-react'
import { getToken, request } from './api'
import AuthView from './components/AuthView'
import PlayerView from './components/PlayerView'
import ProfileView from './components/ProfileView'
import UploadForm from './components/UploadForm'
import VideoCard from './components/VideoCard'

const categories = ['Todos', 'Videojuegos', 'Música', 'En vivo', 'Tecnología', 'Educación', 'Viajes', 'Cine']

export default function App() {
  const [user, setUser] = useState(() => JSON.parse(localStorage.getItem('frame_user') || 'null'))
  const [page, setPage] = useState('home')
  const [videoId, setVideoId] = useState(null)
  const [videos, setVideos] = useState([])
  const [query, setQuery] = useState('')
  const [activeCategory, setActiveCategory] = useState('Todos')
  const [error, setError] = useState('')
  const [showUpload, setShowUpload] = useState(false)
  const [refreshKey, setRefreshKey] = useState(0)

  useEffect(() => {
    if (!getToken()) return
    request('/videos').then(setVideos).catch((err) => setError(err.message))
  }, [refreshKey])

  function login(result) {
    localStorage.setItem('frame_token', result.access_token)
    localStorage.setItem('frame_user', JSON.stringify(result.user))
    setUser(result.user)
    setPage('home')
  }

  function logout() {
    localStorage.removeItem('frame_token')
    localStorage.removeItem('frame_user')
    setUser(null)
    setPage('home')
    setVideoId(null)
  }

  const filteredVideos = useMemo(() => {
    const term = query.trim().toLocaleLowerCase()
    return videos.filter((video) => {
      const searchable = `${video.title} ${video.user_name} ${video.description}`.toLocaleLowerCase()
      const matchesSearch = !term || searchable.includes(term)
      const matchesCategory = activeCategory === 'Todos' || searchable.includes(activeCategory.toLocaleLowerCase())
      return matchesSearch && matchesCategory
    })
  }, [videos, query, activeCategory])

  if (!user) return <AuthView onLogin={login} />

  return (
    <div className="app-shell watch-app">
      <header className="topbar watch-topbar">
        <button className="brand" onClick={() => { setPage('home'); setVideoId(null) }} aria-label="Mimi, inicio"><Clapperboard size={22} strokeWidth={2.4} /> Mimi</button>
        <label className="watch-search"><input value={query} onChange={(event) => setQuery(event.target.value)} onKeyDown={(event) => event.key === 'Enter' && setPage('home')} placeholder="Buscar" aria-label="Buscar videos" /><button type="button" aria-label="Buscar"><Search size={19} /></button></label>
        <div className="topbar-actions"><button className="button button-accent top-upload" onClick={() => setShowUpload(true)}><Plus size={19} /><span>Crear</span></button><button className="account-button" onClick={() => { setPage('profile'); setVideoId(null) }} title="Abrir perfil"><span className="avatar avatar-nav">{user.name.slice(0, 1).toUpperCase()}</span><span className="account-name">{user.name.split(' ')[0]}</span></button><button className="icon-button logout-button" onClick={logout} title="Cerrar sesión" aria-label="Cerrar sesión"><LogOut size={17} /></button></div>
      </header>
      <aside className="watch-sidebar" aria-label="Navegación principal">
        <button className={`side-link ${page === 'home' && !videoId ? 'selected' : ''}`} onClick={() => { setPage('home'); setVideoId(null) }}><House size={20} /><span>Principal</span></button>
        <button className={`side-link ${page === 'profile' ? 'selected' : ''}`} onClick={() => { setPage('profile'); setVideoId(null) }}><CircleUserRound size={20} /><span>Mi perfil</span></button>
        <div className="side-divider" />
        <p className="side-label">TU CANAL</p>
        <button className="side-user" onClick={() => { setPage('profile'); setVideoId(null) }}><span className="avatar avatar-nav">{user.name.slice(0, 1).toUpperCase()}</span><span>{user.name}</span></button>
        <button className="side-link side-create" onClick={() => setShowUpload(true)}><Plus size={19} /><span>Subir un video</span></button>
      </aside>
      <nav className="mobile-nav" aria-label="Navegación móvil"><button onClick={() => { setPage('home'); setVideoId(null) }}><House size={20} /><span>Inicio</span></button><button onClick={() => setShowUpload(true)}><Plus size={20} /><span>Crear</span></button><button onClick={() => { setPage('profile'); setVideoId(null) }}><CircleUserRound size={20} /><span>Perfil</span></button></nav>
      <div className="watch-main">
        {videoId ? <div className="watch-content page-enter"><PlayerView key={videoId} videoId={videoId} user={user} onBack={() => setVideoId(null)} onOpenVideo={setVideoId} /></div> : page === 'profile' ? <div className="watch-content page-enter"><ProfileView user={user} onOpenVideo={setVideoId} onUpload={() => setShowUpload(true)} refreshKey={refreshKey} /></div> : <main className="watch-content page-enter">
          <nav className="category-bar" aria-label="Categorías">{categories.map((category) => <button key={category} className={activeCategory === category ? 'active' : ''} onClick={() => setActiveCategory(category)}>{category}</button>)}</nav>
          {error && <div className="notice-state">{error}<button onClick={() => setRefreshKey((value) => value + 1)}>Reintentar</button></div>}
          {filteredVideos.length ? <section className="video-grid" aria-label="Videos">{filteredVideos.map((video, index) => <VideoCard key={video.id} video={video} onOpen={setVideoId} index={index} />)}</section> : !error && <section className="empty-catalog"><div className="empty-mark">F.</div><div><p className="eyebrow">{query || activeCategory !== 'Todos' ? 'SIN RESULTADOS' : 'TU INICIO'}</p><h3>{query || activeCategory !== 'Todos' ? 'No encontramos videos.' : 'Todavía no hay videos publicados.'}</h3><p>{query || activeCategory !== 'Todos' ? 'Prueba otra búsqueda o categoría.' : 'Cuando alguien publique, los videos aparecerán aquí.'}</p></div>{!query && activeCategory === 'Todos' && <button className="button button-accent" onClick={() => setShowUpload(true)}><Plus size={17} /> Publicar video</button>}</section>}
          <footer className="site-footer"><span>MIMI VIDEO</span><span>DESCUBRE Y COMPARTE.</span><span>2026</span></footer>
        </main>}
      </div>
      {showUpload && <UploadForm onClose={() => setShowUpload(false)} onCreated={() => { setShowUpload(false); setError(''); setRefreshKey((value) => value + 1); setPage('home'); setVideoId(null) }} />}
    </div>
  )
}

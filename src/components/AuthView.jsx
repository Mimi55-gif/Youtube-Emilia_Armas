import { useState } from 'react'
import { ArrowUpRight, Clapperboard } from 'lucide-react'
import { request } from '../api'

export default function AuthView({ onLogin }) {
  const [mode, setMode] = useState('login')
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function submit(event) {
    event.preventDefault()
    setError('')
    setBusy(true)
    try {
      const result = await request(mode === 'login' ? '/login' : '/users', {
        method: 'POST',
        body: JSON.stringify(mode === 'login' ? { email, password } : { name, email, password }),
      })
      onLogin(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <main className="auth-layout auth-centered">
      <section className="auth-panel">
        <div className="auth-form-wrap">
          <a className="brand auth-brand" href="/"><Clapperboard size={21} strokeWidth={2.4} /> Mimi</a>
          <h2>{mode === 'login' ? 'Inicia sesión' : 'Crea tu cuenta'}</h2>
          <form onSubmit={submit} className="auth-form">
            {mode === 'register' && <label>Nombre<input autoComplete="name" value={name} onChange={(event) => setName(event.target.value)} placeholder="Cómo te llamas" required minLength={2} /></label>}
            <label>Correo electrónico<input type="email" autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="tu@correo.com" required /></label>
            <label>Contraseña<input type="password" autoComplete={mode === 'login' ? 'current-password' : 'new-password'} value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Mínimo 8 caracteres" required minLength={8} /></label>
            {error && <p className="form-error" role="alert">{error}</p>}
            <button className="button button-dark auth-submit" disabled={busy}>{busy ? 'Un momento...' : mode === 'login' ? 'Entrar' : 'Crear cuenta'}<ArrowUpRight size={17} /></button>
          </form>
          <p className="auth-switch">{mode === 'login' ? '¿Todavía no tienes cuenta?' : '¿Ya tienes una cuenta?'} <button onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError('') }}>{mode === 'login' ? 'Regístrate' : 'Inicia sesión'}</button></p>
        </div>
      </section>
    </main>
  )
}

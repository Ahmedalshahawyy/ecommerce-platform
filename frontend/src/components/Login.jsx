import React from 'react'

export default function Login({username, password, setUsername, setPassword, register, login, logout, token}){
  const canSubmit = username.trim() !== '' && password.trim() !== ''
  return (
    <div className="login" role="group" aria-label="Authentication form">
      <input 
        aria-label="username" 
        placeholder="username" 
        value={username} 
        onChange={e=>setUsername(e.target.value)}
        onKeyPress={e => e.key === 'Enter' && canSubmit && login()}
      />
      <input 
        aria-label="password" 
        placeholder="password" 
        type="password" 
        value={password} 
        onChange={e=>setPassword(e.target.value)}
        onKeyPress={e => e.key === 'Enter' && canSubmit && login()}
      />
      <button type="button" onClick={register} disabled={!canSubmit} aria-disabled={!canSubmit}>Register</button>
      <button type="button" onClick={login} disabled={!canSubmit} aria-disabled={!canSubmit}>Login</button>
      <button type="button" onClick={logout} disabled={!token} aria-disabled={!token}>Logout</button>
    </div>
  )
}

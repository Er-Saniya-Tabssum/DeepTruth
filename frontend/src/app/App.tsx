import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { AuthProvider } from './providers'
import routes from './routes'

export default function App(){
  return (
    <AuthProvider>
      <Routes>
        {routes.map(r => (
          <Route key={r.path} path={r.path} element={r.element} />
        ))}
      </Routes>
    </AuthProvider>
  )
}

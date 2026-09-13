import React from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../../app/providers'
import AppShell from './AppShell'

export default function ProtectedRoute({children}:{children:React.ReactNode}) {
  const auth = useAuth()
  if (auth.isLoading) return <div className="min-h-screen grid place-items-center text-slate-400">Loading DeepTruth…</div>
  if (!auth.isAuthenticated) return <Navigate to="/login" replace />
  return <AppShell>{children}</AppShell>
}

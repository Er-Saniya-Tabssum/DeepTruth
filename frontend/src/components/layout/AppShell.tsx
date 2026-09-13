import React from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../../app/providers'

const links = [
  {to:'/dashboard', label:'Overview'},
  {to:'/analyze', label:'Analyze'},
  {to:'/history', label:'History'},
]

export default function AppShell({children}:{children:React.ReactNode}) {
  const auth = useAuth()
  const navigate = useNavigate()
  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-30 border-b border-white/10 bg-[#080b14]/80 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-5 h-16 flex items-center justify-between">
          <button onClick={()=>navigate('/dashboard')} className="flex items-center gap-3">
            <span className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-cyan-400 grid place-items-center font-black text-white">D</span>
            <span className="font-bold tracking-tight text-white">Deep<span className="text-cyan-300">Truth</span></span>
          </button>
          <nav className="hidden md:flex items-center gap-1">
            {links.map(link => <NavLink key={link.to} to={link.to} className={({isActive})=>`px-4 py-2 rounded-lg text-sm ${isActive?'bg-white/10 text-white':'text-slate-400 hover:text-white hover:bg-white/5'}`}>{link.label}</NavLink>)}
          </nav>
          <div className="flex items-center gap-3">
            <span className="hidden sm:block text-xs text-slate-500">{auth.user?.email}</span>
            <button onClick={async()=>{await auth.logout();navigate('/')}} className="text-sm text-slate-300 hover:text-white px-3 py-2 rounded-lg hover:bg-white/5">Sign out</button>
          </div>
        </div>
      </header>
      <main>{children}</main>
    </div>
  )
}

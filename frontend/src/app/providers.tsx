import React, { createContext, useContext, useEffect, useState } from 'react'
import { api } from '../lib/api'
import type { User } from '../types/api'

type AuthState = {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
}

type AuthContextValue = AuthState & {
  login: (email: string, password: string) => Promise<void>
  register: (name:string,email: string, password: string) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export const AuthProvider: React.FC<{children:React.ReactNode}> = ({children}) =>{
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(()=>{
    const init = async ()=>{
      const token = localStorage.getItem('dt_token')
      if(!token){ setIsLoading(false); return }
      api.setToken(token)
      try{
        const res = await api.auth.me()
        setUser(res.user)
      }catch(err){
        setUser(null)
        api.clearToken()
      }finally{ setIsLoading(false) }
    }
    init()
  },[])

  const login = async (email:string, password:string)=>{
    const res = await api.auth.login({email,password})
    localStorage.setItem('dt_token', res.access_token)
    api.setToken(res.access_token)
    setUser(res.user)
  }

  const register = async (name:string,email:string,password:string)=>{
    const res = await api.auth.register({name,email,password})
    localStorage.setItem('dt_token', res.access_token)
    api.setToken(res.access_token)
    setUser(res.user)
  }

  const logout = async ()=>{
    try{ await api.auth.logout() }catch(e){}
    localStorage.removeItem('dt_token')
    api.clearToken()
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{user,isAuthenticated:!!user,isLoading,login,register,logout}}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(){
  const ctx = useContext(AuthContext)
  if(!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}

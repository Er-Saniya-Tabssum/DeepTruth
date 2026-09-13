const API_BASE = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '')

type ApiEnvelope<T> = {
  success: boolean
  data?: T
  error?: { code: string; message: string; details?: unknown } | null
}

class ApiClient {
  private token: string | null = null

  setToken(token: string) { this.token = token }
  clearToken() { this.token = null }

  private async request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const headers = new Headers(options.headers)
    if (!(options.body instanceof FormData)) headers.set('Content-Type', 'application/json')
    if (this.token) headers.set('Authorization', `Bearer ${this.token}`)

    const response = await fetch(`${API_BASE}${path}`, { ...options, headers })
    let payload: ApiEnvelope<T>
    try { payload = await response.json() } catch {
      throw new Error(`Server returned ${response.status}`)
    }

    if (!response.ok || !payload.success) {
      throw new Error(payload.error?.message || `Request failed (${response.status})`)
    }
    return payload.data as T
  }

  auth = {
    login: (body: {email: string; password: string}) =>
      this.request<{user: any; access_token: string; token_type: string; expires_in: number}>('/auth/login', {method:'POST', body: JSON.stringify(body)}),
    register: (body: {name: string; email: string; password: string}) =>
      this.request<{user: any; access_token: string; token_type: string; expires_in: number}>('/auth/register', {method:'POST', body: JSON.stringify(body)}),
    me: () => this.request<{user: any}>('/auth/me'),
    logout: () => this.request<{message: string}>('/auth/logout', {method:'POST'}),
  }

  analysis = {
    upload: (form: FormData) =>
      this.request<{analysis_id: string; filename: string; media_type: string; file_size: number; status: string; inference_mode: string; created_at: string}>('/analysis/upload', {method:'POST', body: form}),
    run: (id: string) => this.request<{analysis_id: string; status: string}>(`/analysis/${id}/run`, {method:'POST'}),
    get: (id: string) => this.request<any>(`/analysis/${id}`),
    history: (page=1, limit=20) => this.request<any>(`/analysis/history?page=${page}&limit=${limit}`),
    stats: () => this.request<any>('/analysis/stats'),
    delete: (id: string) => this.request<any>(`/analysis/${id}`, {method:'DELETE'}),
  }

  removal = {
    removeText: (form: FormData) =>
      this.request<any>('/removal/text', {method:'POST', body: form}),
    removeObject: (form: FormData) =>
      this.request<any>('/removal/object', {method:'POST', body: form}),
    detectText: (form: FormData) =>
      this.request<any>('/removal/detect-text', {method:'POST', body: form}),
    get: (id: string) => this.request<any>(`/removal/${id}`),
  }

  tracking = {
    available: () => this.request<any>('/tracking/available'),
    create: (payload: {analysis_id?: string; source_url?: string}) => {
      const qs = new URLSearchParams()
      if (payload.analysis_id) qs.set('analysis_id', payload.analysis_id)
      if (payload.source_url) qs.set('source_url', payload.source_url)
      return this.request<any>(`/tracking?${qs.toString()}`, {method:'POST'})
    },
    list: (page=1, limit=20) => this.request<any>(`/tracking?page=${page}&limit=${limit}`),
    get: (id: string) => this.request<any>(`/tracking/${id}`),
  }

  async downloadRemoval(id: string): Promise<Blob> {
    const headers = new Headers()
    if (this.token) headers.set('Authorization', `Bearer ${this.token}`)
    const response = await fetch(`${API_BASE}/removal/${id}/cleaned`, {headers})
    if (!response.ok) throw new Error('Unable to download cleaned image')
    return response.blob()
  }

  async downloadReport(id: string): Promise<Blob> {
    const headers = new Headers()
    if (this.token) headers.set('Authorization', `Bearer ${this.token}`)
    const response = await fetch(`${API_BASE}/analysis/${id}/report`, {headers})
    if (!response.ok) throw new Error('Unable to generate report')
    return response.blob()
  }
}

export const api = new ApiClient()

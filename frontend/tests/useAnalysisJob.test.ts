import { describe, it, expect, vi } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useAnalysisJob } from '../src/hooks/useAnalysisJob'
import { api } from '../src/lib/api'

vi.mock('../src/lib/api', ()=>({
  api: {
    analysis: {
      upload: vi.fn(),
      run: vi.fn(),
      get: vi.fn()
    }
  }
}))

describe('useAnalysisJob', ()=>{
  it('handles upload and polling flow', async ()=>{
    const { result } = renderHook(()=> useAnalysisJob())
    // mock file
    const file = new File(['hello'], 'test.png', { type: 'image/png' })
    await act(async ()=>{
      result.current.selectFile(file)
    })
    expect(result.current.state).toBe('SELECTED')
    // mock upload response
    (api.analysis.upload as any).mockResolvedValue({ analysis_id: 'a1' })
    (api.analysis.run as any).mockResolvedValue({ analysis_id: 'a1', status: 'QUEUED' })
    (api.analysis.get as any).mockResolvedValue({ analysis_id: 'a1', status: 'COMPLETED', progress:100, current_stage:'FINAL_ASSESSMENT' })

    await act(async ()=>{
      await result.current.uploadAndStart()
      // allow polling to run once
      await new Promise(r=>setTimeout(r, 10))
    })

    expect(result.current.state).toBe('COMPLETED')
    expect(result.current.analysis?.analysis_id).toBe('a1')
  })
})

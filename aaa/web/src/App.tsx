import { useEffect, useMemo, useState } from 'react'

type Nav = 'Home' | 'Assets' | 'Work' | 'Agents' | 'Research' | 'Validation' | 'Decisions' | 'History'

type StatusPayload = {
  project: string
  short_name: string
  repository: string
  aaa_role: string
  canonical_authority: string
  llm_required_for_control_plane: boolean
  current_state: {
    version: string | null
    status: string | null
    identity: { path: string; sha256: string; byte_size: number }
  }
}

type DiscrepancyComparison = {
  key: string
  authoritative: unknown
  shadow: unknown
  status: 'MATCH' | 'MISMATCH' | 'UNKNOWN'
}

type DiscrepancyPayload = {
  status: 'MATCH' | 'MISMATCH' | 'STALE' | 'UNKNOWN'
  projection_scope: string
  report_sha256: string
  event_ledger: { path: string; latest_event_id: string | null; latest_event_timestamp: string | null }
  comparisons: DiscrepancyComparison[]
}

const navItems: Nav[] = ['Home', 'Assets', 'Work', 'Agents', 'Research', 'Validation', 'Decisions', 'History']
const API = 'http://127.0.0.1:8765/api/aaa'

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section style={{ background: '#111827', border: '1px solid #263244', borderRadius: 12, padding: 18 }}>
      <h3 style={{ margin: '0 0 12px', fontSize: 15, color: '#d1d5db' }}>{title}</h3>
      {children}
    </section>
  )
}

function Pill({ children }: { children: React.ReactNode }) {
  return <span style={{ background: '#1f2937', borderRadius: 999, padding: '7px 11px', color: '#bfdbfe' }}>{children}</span>
}

function statusColor(value: string) {
  if (value === 'MATCH') return '#86efac'
  if (value === 'UNKNOWN') return '#fcd34d'
  return '#fca5a5'
}

export default function App() {
  const [active, setActive] = useState<Nav>('Home')
  const [status, setStatus] = useState<StatusPayload | null>(null)
  const [discrepancy, setDiscrepancy] = useState<DiscrepancyPayload | null>(null)
  const [workCount, setWorkCount] = useState<number | null>(null)
  const [gates, setGates] = useState<string[]>([])
  const [apiState, setApiState] = useState<'LOADING' | 'ONLINE' | 'OFFLINE'>('LOADING')

  useEffect(() => {
    const load = async () => {
      try {
        const [statusResponse, workResponse, gateResponse, discrepancyResponse] = await Promise.all([
          fetch(`${API}/status`, { cache: 'no-store' }),
          fetch(`${API}/work`, { cache: 'no-store' }),
          fetch(`${API}/gates`, { cache: 'no-store' }),
          fetch(`${API}/state/compare`, { cache: 'no-store' }),
        ])
        if (!statusResponse.ok || !workResponse.ok || !gateResponse.ok || !discrepancyResponse.ok) throw new Error('AAA_API_READ_FAILED')
        const statusPayload = await statusResponse.json() as StatusPayload
        const workPayload = await workResponse.json() as { items: unknown[] }
        const gatePayload = await gateResponse.json() as { items: string[] }
        const discrepancyPayload = await discrepancyResponse.json() as DiscrepancyPayload
        setStatus(statusPayload)
        setWorkCount(workPayload.items.length)
        setGates(gatePayload.items)
        setDiscrepancy(discrepancyPayload)
        setApiState('ONLINE')
      } catch {
        setApiState('OFFLINE')
      }
    }
    void load()
  }, [])

  const content = useMemo(() => {
    if (active === 'Validation') {
      return (
        <div style={{ display: 'grid', gap: 16 }}>
          <Card title="Shadow discrepancy">
            <strong style={{ color: statusColor(discrepancy?.status ?? 'UNKNOWN') }}>{discrepancy?.status ?? 'UNAVAILABLE'}</strong>
            <div style={{ marginTop: 8, color: '#64748b', fontSize: 12 }}>{discrepancy?.projection_scope ?? 'API not connected'}</div>
          </Card>
          <Card title="Anchor comparisons">
            <div style={{ display: 'grid', gap: 8 }}>
              {discrepancy?.comparisons.map((row) => (
                <div key={row.key} style={{ display: 'grid', gridTemplateColumns: 'minmax(180px, 1fr) auto', gap: 12, padding: '8px 0', borderBottom: '1px solid #1f2937' }}>
                  <span style={{ color: '#d1d5db' }}>{row.key}</span>
                  <strong style={{ color: statusColor(row.status) }}>{row.status}</strong>
                </div>
              )) ?? <span style={{ color: '#9ca3af' }}>No discrepancy data loaded.</span>}
            </div>
          </Card>
        </div>
      )
    }

    if (active !== 'Home') {
      return (
        <Card title={active}>
          <p style={{ margin: 0, color: '#9ca3af' }}>
            Deterministic read-only view. Mutation surfaces remain disabled during shadow operation.
          </p>
        </Card>
      )
    }

    const currentState = status?.current_state.version ?? 'UNAVAILABLE'
    const controlStatus = status?.current_state.status ?? 'READ_ONLY_API_NOT_CONNECTED'
    const mode = status?.aaa_role ?? 'SHADOW_NONAUTHORITATIVE'

    return (
      <div style={{ display: 'grid', gap: 16 }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16 }}>
          <Card title="Current State">
            <strong>{currentState}</strong>
            <div style={{ marginTop: 8, color: '#93c5fd' }}>{mode}</div>
          </Card>
          <Card title="Shadow State Match">
            <strong style={{ color: statusColor(discrepancy?.status ?? 'UNKNOWN') }}>{discrepancy?.status ?? 'UNAVAILABLE'}</strong>
            <div style={{ marginTop: 8, color: '#9ca3af' }}>{discrepancy?.event_ledger.latest_event_id ?? 'No ledger anchor loaded'}</div>
          </Card>
          <Card title="Work Orders">
            <strong>{workCount ?? '—'}</strong>
            <span style={{ color: '#9ca3af' }}> versioned records</span>
          </Card>
          <Card title="Canonical Write">
            <strong style={{ color: '#fca5a5' }}>PROHIBITED</strong>
            <div style={{ marginTop: 8, color: '#9ca3af' }}>{status?.canonical_authority ?? 'Existing SEMI Control Plane'}</div>
          </Card>
          <Card title="LLM Dependency">
            <strong style={{ color: '#86efac' }}>{status?.llm_required_for_control_plane === false ? 'NOT REQUIRED' : 'NOT CONNECTED'}</strong>
            <div style={{ marginTop: 8, color: '#9ca3af' }}>Deterministic control views remain available.</div>
          </Card>
        </div>
        <Card title="Control status">
          <div style={{ color: '#d1d5db', wordBreak: 'break-word' }}>{controlStatus}</div>
          {status?.current_state.identity && (
            <div style={{ marginTop: 10, color: '#64748b', fontSize: 12 }}>
              {status.current_state.identity.path} · {status.current_state.identity.sha256.slice(0, 16)}… · {status.current_state.identity.byte_size} bytes
            </div>
          )}
        </Card>
        <Card title="Validation gates">
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
            {gates.length > 0 ? gates.map((gate) => <Pill key={gate}>{gate}</Pill>) : <span style={{ color: '#9ca3af' }}>No gate data loaded.</span>}
          </div>
        </Card>
      </div>
    )
  }, [active, discrepancy, gates, status, workCount])

  return (
    <div style={{ minHeight: '100vh', background: '#0b1020', color: '#f9fafb', fontFamily: 'Inter, ui-sans-serif, system-ui, sans-serif' }}>
      <header style={{ padding: '20px 28px', borderBottom: '1px solid #1f2937', display: 'flex', justifyContent: 'space-between', gap: 16, alignItems: 'center' }}>
        <div>
          <div style={{ fontWeight: 800, letterSpacing: '-0.02em', fontSize: 22 }}>Asset Agent ASA</div>
          <div style={{ color: '#64748b', fontSize: 13 }}>AAA Owner Console · deterministic-first</div>
        </div>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <span style={{ fontSize: 12, padding: '6px 10px', border: '1px solid #334155', borderRadius: 999, color: apiState === 'ONLINE' ? '#86efac' : '#fca5a5' }}>API {apiState}</span>
          <span style={{ fontSize: 12, padding: '6px 10px', border: '1px solid #334155', borderRadius: 999, color: '#cbd5e1' }}>SHADOW / READ-ONLY</span>
        </div>
      </header>
      <div style={{ display: 'grid', gridTemplateColumns: '220px minmax(0, 1fr)', minHeight: 'calc(100vh - 82px)' }}>
        <nav style={{ borderRight: '1px solid #1f2937', padding: 16 }}>
          {navItems.map((item) => (
            <button
              key={item}
              type="button"
              onClick={() => setActive(item)}
              style={{
                width: '100%', textAlign: 'left', marginBottom: 5, padding: '10px 12px', borderRadius: 8,
                border: 'none', cursor: 'pointer', color: active === item ? '#ffffff' : '#94a3b8',
                background: active === item ? '#1e293b' : 'transparent', fontWeight: active === item ? 700 : 500,
              }}
            >
              {item}
            </button>
          ))}
        </nav>
        <main style={{ padding: 28, maxWidth: 1200, width: '100%', boxSizing: 'border-box' }}>
          <div style={{ marginBottom: 20 }}>
            <h1 style={{ margin: 0, fontSize: 26 }}>{active}</h1>
            <p style={{ color: '#64748b', marginTop: 6 }}>Owner-visible state without requiring an LLM connection.</p>
          </div>
          {content}
        </main>
      </div>
    </div>
  )
}

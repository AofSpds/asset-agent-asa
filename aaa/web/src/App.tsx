import { useMemo, useState } from 'react'

type Nav = 'Home' | 'Assets' | 'Work' | 'Agents' | 'Research' | 'Validation' | 'Decisions' | 'History'

const navItems: Nav[] = ['Home', 'Assets', 'Work', 'Agents', 'Research', 'Validation', 'Decisions', 'History']

const seedState = {
  project: 'Asset Agent ASA',
  shortName: 'AAA',
  mode: 'SHADOW / NON-CANONICAL',
  currentState: 'SEMI-CURRENT-STATE v2.10',
  blockers: [
    'Independent delta preflight',
    'Production KRX trading calendar identity',
    'U127 persistence and canonical machine release',
    'Price official readiness / CA closure',
  ],
  activeWork: [
    'AAA-T01 Contracts',
    'AAA-T04 Owner Console',
    'AAA-T08 Validation Harness',
  ],
}

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section style={{ background: '#111827', border: '1px solid #263244', borderRadius: 12, padding: 18 }}>
      <h3 style={{ margin: '0 0 12px', fontSize: 15, color: '#d1d5db' }}>{title}</h3>
      {children}
    </section>
  )
}

export default function App() {
  const [active, setActive] = useState<Nav>('Home')
  const content = useMemo(() => {
    if (active !== 'Home') {
      return (
        <Card title={active}>
          <p style={{ margin: 0, color: '#9ca3af' }}>
            Deterministic read-only view scaffold. Data adapter wiring is intentionally deferred to the AAA API track.
          </p>
        </Card>
      )
    }
    return (
      <div style={{ display: 'grid', gap: 16 }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16 }}>
          <Card title="Current State">
            <strong>{seedState.currentState}</strong>
            <div style={{ marginTop: 8, color: '#93c5fd' }}>{seedState.mode}</div>
          </Card>
          <Card title="Active Work">
            <strong>{seedState.activeWork.length}</strong>
            <span style={{ color: '#9ca3af' }}> parallel tracks</span>
          </Card>
          <Card title="Canonical Write">
            <strong style={{ color: '#fca5a5' }}>PROHIBITED</strong>
            <div style={{ marginTop: 8, color: '#9ca3af' }}>Shadow-first build phase</div>
          </Card>
        </div>
        <Card title="Highest-priority blockers">
          <ol style={{ margin: 0, paddingLeft: 20, color: '#d1d5db' }}>
            {seedState.blockers.map((item) => <li key={item} style={{ margin: '7px 0' }}>{item}</li>)}
          </ol>
        </Card>
        <Card title="Parallel build wave">
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
            {seedState.activeWork.map((item) => (
              <span key={item} style={{ background: '#1f2937', borderRadius: 999, padding: '7px 11px', color: '#bfdbfe' }}>{item}</span>
            ))}
          </div>
        </Card>
      </div>
    )
  }, [active])

  return (
    <div style={{ minHeight: '100vh', background: '#0b1020', color: '#f9fafb', fontFamily: 'Inter, ui-sans-serif, system-ui, sans-serif' }}>
      <header style={{ padding: '20px 28px', borderBottom: '1px solid #1f2937', display: 'flex', justifyContent: 'space-between', gap: 16, alignItems: 'center' }}>
        <div>
          <div style={{ fontWeight: 800, letterSpacing: '-0.02em', fontSize: 22 }}>{seedState.project}</div>
          <div style={{ color: '#64748b', fontSize: 13 }}>AAA Owner Console · deterministic-first</div>
        </div>
        <div style={{ fontSize: 12, padding: '6px 10px', border: '1px solid #334155', borderRadius: 999, color: '#cbd5e1' }}>{seedState.mode}</div>
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

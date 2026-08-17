import { useEffect, useMemo, useState } from 'react'

type Nav = 'Home' | 'Structure' | 'Operations' | 'Assets' | 'Work' | 'Agents' | 'Research' | 'Validation' | 'Decisions' | 'History'
type RunState = 'READY_NOT_DISPATCHED' | 'DISPATCHED_AWAITING_ACK' | 'RUNNING_CONFIRMED' | 'BLOCKED' | 'STALE_UNKNOWN' | 'COMPLETED_PASS' | 'COMPLETED_FAIL' | 'COMPLETED_WITH_FINDINGS'
type StatusPayload = { project: string; short_name: string; aaa_role: string; canonical_authority: string; llm_required_for_control_plane: boolean; current_state: { version: string | null; status: string | null; identity: { path: string; sha256: string; byte_size: number } } }
type DiscrepancyPayload = { status: 'MATCH' | 'MISMATCH' | 'STALE' | 'UNKNOWN'; projection_scope: string; event_ledger: { latest_event_id: string | null }; comparisons: { key: string; status: 'MATCH' | 'MISMATCH' | 'UNKNOWN' }[] }
type RunPayload = { run_id: string; process_id: string; responsible_persona: string; state: RunState; effective_state: RunState; exact_base_commit: string; branch: string; last_heartbeat_at: string | null }
type PersonaPayload = { persona: string; state: RunState | 'IDLE_OR_UNREGISTERED'; run_id: string | null; process_id: string | null }
type WorkerPayload = { worker_id: string; worker_type: string; runtime_version: string; host_identity: string; enabled: boolean; last_seen_at: string | null; capabilities: string[]; authorized_personas: string[] }
type TaskPayload = { task_id: string; run_id: string; execution_profile_id: string; required_persona: string; state: string; effective_task_state: string; claimed_by: string | null; lease_epoch: number | null; acknowledged_at_db: string | null; started_at_db: string | null; last_heartbeat_at: string | null; lease_expires_at: string | null }

type StructureSource = { availability: string; path: string | null; sha256?: string; byte_size?: number; as_of?: string | null; declared_status?: string | null }
type StructurePersona = {
  persona_id: string
  formal_name: string
  korean_name: string
  alias: string | null
  domain: string
  status: string
  active_channel_binding_state: string
  active_channels: { channel_instance_id: string; display_name: string; channel_type: string; status: string }[]
  manifest_or_state_ref: string | null
  last_update: string | null
}
type StructureChannel = {
  channel_instance_id: string
  display_name: string
  channel_type: string
  persona_binding: string | null
  status: string
  raw_status: string
  role: string | null
  authority_relation: string | null
  current_workstream: string | null
  source_ref: string | null
}
type StructureWorkstream = {
  workstream_id: string
  display_name: string
  domain_owner: string
  status: string
  current_stage?: string
  current_gate?: string
  current_activity?: string | boolean | null
  exact_target?: string | null
  latest_validated_target?: string | null
  latest_validation_state?: string | null
  source_ref?: string | null
}
type RoadmapStage = { id: string; name: string; display_state: string; gate?: string | null; notes?: string | null }
type HistoricalRun = { run_id: string; historical_state: string; current_disposition: string; started_at?: string | null; last_heartbeat_at?: string | null; terminal_result?: unknown; source?: unknown }
type OperatingStructurePayload = {
  project: string
  short_name: string
  projection: {
    status: string
    current_as_of: string | null
    generated_at: string
    source: string
    source_state_id: string
    conflicts: unknown[]
    sources: Record<string, StructureSource>
  }
  authority: {
    authority_holder: { authority_id: string; display_name: string; responsibilities: string[]; source_ref: string | null }
    operational_flags: Record<string, boolean | null>
  }
  formal_personas: StructurePersona[]
  active_channels: StructureChannel[]
  inactive_channels: StructureChannel[]
  relationships: { edge_types: string[] }
  workstreams: StructureWorkstream[]
  roadmap: {
    roadmap_id: string | null
    version: string | null
    status: string | null
    current_stage: string
    current_gate: string
    current_stage_state: string
    stages: RoadmapStage[]
    validator_modifications: unknown[]
    source_ref: string | null
  }
  historical_runs: HistoricalRun[]
}

type DetailSelection = { title: string; kind: string; payload: unknown }

const navItems: Nav[] = ['Home', 'Structure', 'Operations', 'Assets', 'Work', 'Agents', 'Research', 'Validation', 'Decisions', 'History']
const API = 'http://127.0.0.1:8765/api/aaa'
const STRUCTURE_REFRESH_MS = 15000

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return <section style={{ background: '#111827', border: '1px solid #263244', borderRadius: 12, padding: 18 }}><h3 style={{ margin: '0 0 12px', fontSize: 15, color: '#d1d5db' }}>{title}</h3>{children}</section>
}
function Pill({ children }: { children: React.ReactNode }) {
  return <span style={{ background: '#1f2937', borderRadius: 999, padding: '7px 11px', color: '#bfdbfe', fontSize: 12 }}>{children}</span>
}
function statusColor(value: string) {
  if (['MATCH', 'CURRENT', 'COMPLETED_PASS', 'RUNNING_CONFIRMED', 'RUNNING', 'TERMINAL', 'ACTIVE', 'COMPLETED', 'AVAILABLE'].includes(value)) return '#86efac'
  if (['UNKNOWN', 'READY_NOT_DISPATCHED', 'DISPATCHED_AWAITING_ACK', 'IDLE_OR_UNREGISTERED', 'AWAITING_DISPATCH', 'AWAITING_VALIDATION', 'NOT_INSTANTIATED', 'INACTIVE', 'CLAIMED', 'ACKNOWLEDGED'].includes(value)) return '#fcd34d'
  if (['COMPLETED_WITH_FINDINGS', 'STALE_UNKNOWN', 'STALE'].includes(value)) return '#fdba74'
  return '#fca5a5'
}
function shortPersona(value: string) {
  if (value === 'SEMI-CONTROL-ARCHITECT') return 'Control Architect'
  if (value === 'SEMI-MODEL-VALIDATION-DESIGN-ARCHITECT') return 'Model Validation / Design'
  if (value === 'SEMI-RESEARCH-ORCHESTRATOR') return 'Research Orchestrator'
  if (value === 'SEMI-VALIDATION-AUDITOR') return 'Validation Auditor'
  return value
}
function truthLabel(value: boolean | null) {
  if (value === true) return 'TRUE'
  if (value === false) return 'FALSE'
  return 'UNKNOWN'
}
function nodeButtonStyle(accent = '#334155'): React.CSSProperties {
  return {
    width: '100%',
    textAlign: 'left',
    cursor: 'pointer',
    background: '#0f172a',
    color: '#f8fafc',
    border: `1px solid ${accent}`,
    borderRadius: 12,
    padding: 14,
  }
}
function DetailPanel({ selection }: { selection: DetailSelection | null }) {
  if (!selection) return <Card title="Detail"><div style={{ color: '#64748b' }}>Select a Persona, Channel, Workstream or Stage to inspect governed details.</div></Card>
  return <Card title={`${selection.kind} · ${selection.title}`}><pre style={{ margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-word', color: '#cbd5e1', fontSize: 12, lineHeight: 1.55 }}>{JSON.stringify(selection.payload, null, 2)}</pre></Card>
}

export default function App() {
  const [active, setActive] = useState<Nav>('Home')
  const [status, setStatus] = useState<StatusPayload | null>(null)
  const [discrepancy, setDiscrepancy] = useState<DiscrepancyPayload | null>(null)
  const [workCount, setWorkCount] = useState<number | null>(null)
  const [gates, setGates] = useState<string[]>([])
  const [runs, setRuns] = useState<RunPayload[]>([])
  const [personas, setPersonas] = useState<PersonaPayload[]>([])
  const [workers, setWorkers] = useState<WorkerPayload[]>([])
  const [tasks, setTasks] = useState<TaskPayload[]>([])
  const [structure, setStructure] = useState<OperatingStructurePayload | null>(null)
  const [structureRefreshState, setStructureRefreshState] = useState<'CURRENT' | 'STALE' | 'UNAVAILABLE'>('UNAVAILABLE')
  const [selectedDetail, setSelectedDetail] = useState<DetailSelection | null>(null)
  const [executionProjectionConnected, setExecutionProjectionConnected] = useState(false)
  const [apiState, setApiState] = useState<'LOADING' | 'ONLINE' | 'OFFLINE'>('LOADING')

  useEffect(() => {
    let cancelled = false
    const loadStructure = async () => {
      try {
        const response = await fetch(`${API}/operating-structure`, { cache: 'no-store' })
        if (!response.ok) throw new Error('AAA_STRUCTURE_READ_FAILED')
        const payload = await response.json() as OperatingStructurePayload
        if (!cancelled) {
          setStructure(payload)
          setStructureRefreshState(payload.projection.status === 'STALE' ? 'STALE' : 'CURRENT')
        }
      } catch {
        if (!cancelled) setStructureRefreshState((current) => current === 'UNAVAILABLE' ? 'UNAVAILABLE' : 'STALE')
      }
    }
    const load = async () => {
      try {
        const responses = await Promise.all([
          fetch(`${API}/status`, { cache: 'no-store' }),
          fetch(`${API}/work`, { cache: 'no-store' }),
          fetch(`${API}/gates`, { cache: 'no-store' }),
          fetch(`${API}/state/compare`, { cache: 'no-store' }),
          fetch(`${API}/runs`, { cache: 'no-store' }),
          fetch(`${API}/personas`, { cache: 'no-store' }),
          fetch(`${API}/workers`, { cache: 'no-store' }),
          fetch(`${API}/tasks`, { cache: 'no-store' }),
          fetch(`${API}/operating-structure`, { cache: 'no-store' }),
        ])
        if (responses.some((response) => !response.ok)) throw new Error('AAA_API_READ_FAILED')
        const [statusPayload, workPayload, gatePayload, discrepancyPayload, runPayload, personaPayload, workerPayload, taskPayload, structurePayload] = await Promise.all(responses.map((response) => response.json()))
        if (cancelled) return
        setStatus(statusPayload as StatusPayload)
        setWorkCount((workPayload as { items: unknown[] }).items.length)
        setGates((gatePayload as { items: string[] }).items)
        setDiscrepancy(discrepancyPayload as DiscrepancyPayload)
        setRuns((runPayload as { items: RunPayload[] }).items)
        setPersonas((personaPayload as { items: PersonaPayload[] }).items)
        setWorkers((workerPayload as { items: WorkerPayload[] }).items)
        setTasks((taskPayload as { items: TaskPayload[] }).items)
        setExecutionProjectionConnected(Boolean((workerPayload as { postgres_projection_connected?: boolean }).postgres_projection_connected))
        const operating = structurePayload as OperatingStructurePayload
        setStructure(operating)
        setStructureRefreshState(operating.projection.status === 'STALE' ? 'STALE' : 'CURRENT')
        setApiState('ONLINE')
      } catch {
        if (!cancelled) {
          setApiState('OFFLINE')
          setStructureRefreshState((current) => current === 'UNAVAILABLE' ? 'UNAVAILABLE' : 'STALE')
        }
      }
    }
    void load()
    const timer = window.setInterval(() => { void loadStructure() }, STRUCTURE_REFRESH_MS)
    return () => { cancelled = true; window.clearInterval(timer) }
  }, [])

  const structureView = useMemo(() => {
    if (!structure) return <Card title="Current Operating Structure · 현재 실무 구조"><div style={{ color: '#fca5a5' }}>UNAVAILABLE · Persistent Control Plane projection could not be loaded.</div></Card>
    const projectionStatus = structureRefreshState === 'STALE' ? 'STALE' : structure.projection.status
    return <div style={{ display: 'grid', gap: 16 }}>
      <Card title="Projection freshness / provenance">
        <div className="aaa-flex-row">
          <strong style={{ color: statusColor(projectionStatus) }}>{projectionStatus}</strong>
          <span style={{ color: '#94a3b8' }}>CURRENT AS OF {structure.projection.current_as_of ?? 'UNKNOWN'}</span>
          <span style={{ color: '#64748b' }}>STATE {structure.projection.source_state_id.slice(0, 16)}…</span>
        </div>
        <div style={{ marginTop: 8, color: '#64748b', fontSize: 12 }}>{structure.projection.source}</div>
      </Card>

      <Card title="Relationship legend">
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
          <Pill>AUTHORITY / APPROVAL</Pill>
          <Pill>PERSONA RESPONSIBILITY</Pill>
          <Pill>CHANNEL ↔ PERSONA BINDING</Pill>
          <Pill>EXECUTION / WORKSTREAM</Pill>
          <Pill>VALIDATION / AUDIT</Pill>
          <Pill>ADVISORY</Pill>
        </div>
      </Card>

      <Card title="Layer 1 · Authority">
        <button type="button" style={nodeButtonStyle('#7c3aed')} onClick={() => setSelectedDetail({ title: structure.authority.authority_holder.display_name, kind: 'AUTHORITY', payload: structure.authority.authority_holder })}>
          <div style={{ color: '#c4b5fd', fontSize: 12, fontWeight: 700 }}>FINAL AUTHORITY</div>
          <div style={{ fontSize: 20, fontWeight: 800, marginTop: 4 }}>{structure.authority.authority_holder.display_name}</div>
          <div style={{ color: '#94a3b8', fontSize: 12, marginTop: 8 }}>{structure.authority.authority_holder.responsibilities.join(' · ')}</div>
        </button>
      </Card>

      <Card title="Layer 2 · Formal Personas">
        <div className="aaa-card-grid">
          {structure.formal_personas.map((persona) => <button key={persona.persona_id} type="button" style={nodeButtonStyle('#1d4ed8')} onClick={() => setSelectedDetail({ title: persona.formal_name, kind: 'PERSONA', payload: persona })}>
            <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8, alignItems: 'center' }}>
              <span style={{ color: '#93c5fd', fontSize: 11, fontWeight: 800 }}>PERSONA</span>
              <strong style={{ color: statusColor(persona.active_channel_binding_state), fontSize: 11 }}>{persona.active_channel_binding_state}</strong>
            </div>
            <div style={{ fontWeight: 800, marginTop: 7 }}>{persona.korean_name}{persona.alias ? ` (${persona.alias})` : ''}</div>
            <div style={{ color: '#cbd5e1', fontSize: 11, marginTop: 4 }}>{persona.formal_name}</div>
            <div style={{ color: '#64748b', fontSize: 11, marginTop: 8 }}>{persona.domain}</div>
            <div style={{ color: '#94a3b8', fontSize: 11, marginTop: 8 }}>{persona.active_channels.length ? persona.active_channels.map((row) => row.display_name).join(', ') : 'NO ACTIVE CHANNEL'}</div>
          </button>)}
        </div>
      </Card>

      <Card title="Layer 3 · Active Channels / Controllers">
        <div className="aaa-card-grid">
          {structure.active_channels.map((channel) => <button key={channel.channel_instance_id} type="button" style={nodeButtonStyle(channel.channel_type === 'ADVISORY' ? '#a16207' : channel.channel_type === 'CONTROLLER' ? '#0f766e' : channel.channel_type === 'VALIDATION' ? '#be123c' : '#475569')} onClick={() => setSelectedDetail({ title: channel.display_name, kind: 'CHANNEL / CONTROLLER', payload: channel })}>
            <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8 }}>
              <span style={{ color: '#bae6fd', fontSize: 11, fontWeight: 800 }}>{channel.channel_type}</span>
              <strong style={{ color: statusColor(channel.status), fontSize: 11 }}>{channel.status}</strong>
            </div>
            <div style={{ fontWeight: 800, marginTop: 7 }}>{channel.display_name}</div>
            <div style={{ color: '#94a3b8', fontSize: 11, marginTop: 6 }}>{channel.persona_binding ? `PERSONA BINDING → ${shortPersona(channel.persona_binding)}` : 'NO FORMAL PERSONA IDENTITY'}</div>
            <div style={{ color: '#64748b', fontSize: 11, marginTop: 5 }}>{channel.role ?? channel.authority_relation ?? 'Role metadata not registered'}</div>
          </button>)}
          {structure.active_channels.length === 0 && <span style={{ color: '#9ca3af' }}>No active Channel evidence. No Channel is inferred from chat activity.</span>}
        </div>
      </Card>

      <Card title="Active workstreams">
        <div className="aaa-card-grid">
          {structure.workstreams.map((workstream) => <button key={workstream.workstream_id} type="button" style={nodeButtonStyle('#475569')} onClick={() => setSelectedDetail({ title: workstream.display_name, kind: 'WORKSTREAM', payload: workstream })}>
            <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8 }}>
              <span style={{ color: '#cbd5e1', fontSize: 11, fontWeight: 800 }}>WORKSTREAM</span>
              <strong style={{ color: statusColor(workstream.status), fontSize: 11 }}>{workstream.status}</strong>
            </div>
            <div style={{ fontWeight: 800, marginTop: 7 }}>{workstream.display_name}</div>
            <div style={{ color: '#94a3b8', fontSize: 11, marginTop: 6 }}>Owner/domain: {workstream.domain_owner}</div>
            <div style={{ color: '#64748b', fontSize: 11, marginTop: 5 }}>{String(workstream.current_activity ?? 'UNKNOWN')}</div>
          </button>)}
        </div>
      </Card>

      <Card title="Approved Post-IV roadmap">
        <div style={{ marginBottom: 10 }}>
          <strong>{structure.roadmap.current_stage}</strong>
          <span style={{ color: '#94a3b8' }}> · {structure.roadmap.current_gate} · </span>
          <strong style={{ color: statusColor(structure.roadmap.current_stage_state) }}>{structure.roadmap.current_stage_state}</strong>
        </div>
        <div className="aaa-stage-flow">
          {structure.roadmap.stages.map((stage) => <button key={stage.id} type="button" onClick={() => setSelectedDetail({ title: `${stage.id} · ${stage.name}`, kind: 'ROADMAP STAGE', payload: stage })} style={{ ...nodeButtonStyle(stage.id === structure.roadmap.current_stage ? '#2563eb' : '#334155'), minWidth: 180, flex: '1 1 180px' }}>
            <div style={{ fontSize: 11, color: '#93c5fd' }}>{stage.id}</div>
            <div style={{ fontWeight: 700, marginTop: 4 }}>{stage.name}</div>
            <div style={{ color: statusColor(stage.display_state), fontSize: 11, marginTop: 7 }}>{stage.display_state}</div>
          </button>)}
        </div>
      </Card>

      <Card title="Operational authority gates">
        <div style={{ display: 'grid', gap: 8 }}>
          {Object.entries(structure.authority.operational_flags).map(([key, value]) => <div key={key} style={{ display: 'flex', justifyContent: 'space-between', gap: 12, borderBottom: '1px solid #1f2937', padding: '8px 0' }}>
            <span style={{ color: '#cbd5e1', fontSize: 12 }}>{key}</span>
            <strong style={{ color: value === true ? '#86efac' : value === false ? '#fca5a5' : '#fcd34d', fontSize: 12 }}>{truthLabel(value)}</strong>
          </div>)}
        </div>
      </Card>

      <Card title="P09 / T18 · historical lifecycle ≠ current disposition">
        <div style={{ display: 'grid', gap: 10 }}>
          {structure.historical_runs.map((run) => <button key={run.run_id} type="button" style={nodeButtonStyle('#475569')} onClick={() => setSelectedDetail({ title: run.run_id, kind: 'HISTORICAL RUN', payload: run })}>
            <div style={{ fontWeight: 700 }}>{run.run_id}</div>
            <div className="aaa-flex-row" style={{ marginTop: 7 }}>
              <span>Historical: <strong style={{ color: statusColor(run.historical_state) }}>{run.historical_state}</strong></span>
              <span>Current disposition: <strong style={{ color: statusColor(run.current_disposition) }}>{run.current_disposition}</strong></span>
            </div>
          </button>)}
        </div>
      </Card>

      <div className="aaa-two-col">
        <Card title="Source provenance">
          <div style={{ display: 'grid', gap: 8 }}>
            {Object.entries(structure.projection.sources).map(([name, source]) => <div key={name} style={{ borderBottom: '1px solid #1f2937', paddingBottom: 8 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', gap: 10 }}><strong style={{ fontSize: 12 }}>{name}</strong><strong style={{ color: statusColor(source.availability), fontSize: 11 }}>{source.availability}</strong></div>
              <div style={{ color: '#64748b', fontSize: 11, marginTop: 3 }}>{source.path ?? 'NOT_REGISTERED'} · as of {source.as_of ?? 'UNKNOWN'}</div>
            </div>)}
          </div>
        </Card>
        <DetailPanel selection={selectedDetail} />
      </div>

      {structure.projection.conflicts.length > 0 && <Card title="CONFLICT"><pre style={{ margin: 0, whiteSpace: 'pre-wrap', color: '#fca5a5', fontSize: 12 }}>{JSON.stringify(structure.projection.conflicts, null, 2)}</pre></Card>}
    </div>
  }, [selectedDetail, structure, structureRefreshState])

  const content = useMemo(() => {
    if (active === 'Structure') return structureView
    if (active === 'Operations') return <div style={{ display: 'grid', gap: 16 }}>
      <Card title="T19 worker execution plane"><div style={{ marginBottom: 10, color: executionProjectionConnected ? '#86efac' : '#fcd34d', fontSize: 12 }}>PostgreSQL execution projection: {executionProjectionConnected ? 'CONNECTED' : 'NOT CONNECTED · no worker liveness inferred'}</div><div style={{ display: 'grid', gap: 8 }}>{workers.map((worker) => <div key={worker.worker_id} style={{ borderBottom: '1px solid #1f2937', padding: '9px 0' }}><div style={{ display: 'flex', justifyContent: 'space-between' }}><strong>{worker.worker_id}</strong><strong style={{ color: worker.enabled ? '#86efac' : '#fca5a5' }}>{worker.enabled ? 'ENABLED' : 'DISABLED'}</strong></div><div style={{ color: '#94a3b8', fontSize: 12, marginTop: 4 }}>{worker.worker_type} · {worker.runtime_version} · last seen {worker.last_seen_at ?? 'never'}</div></div>)}{workers.length === 0 && <span style={{ color: '#9ca3af' }}>No connected worker evidence.</span>}</div></Card>
      <Card title="T19 execution tasks"><div style={{ display: 'grid', gap: 8 }}>{tasks.map((task) => <div key={task.task_id} style={{ border: '1px solid #1f2937', borderRadius: 10, padding: 12 }}><div style={{ display: 'flex', justifyContent: 'space-between', gap: 12 }}><strong>{task.task_id}</strong><strong style={{ color: statusColor(task.effective_task_state) }}>{task.effective_task_state}</strong></div><div style={{ color: '#94a3b8', fontSize: 12, marginTop: 5 }}>{task.run_id} · {shortPersona(task.required_persona)}</div><div style={{ color: '#64748b', fontSize: 11, marginTop: 4 }}>worker {task.claimed_by ?? 'unclaimed'} · lease {task.lease_epoch ?? 'none'} · heartbeat {task.last_heartbeat_at ?? 'none'}</div></div>)}{tasks.length === 0 && <span style={{ color: '#9ca3af' }}>No executable task projection connected.</span>}</div></Card>
      <Card title="Persona operations"><div style={{ display: 'grid', gap: 8 }}>{personas.map((row) => <div key={row.persona} style={{ display: 'flex', justifyContent: 'space-between', padding: '9px 0', borderBottom: '1px solid #1f2937' }}><span>{shortPersona(row.persona)}</span><strong style={{ color: statusColor(row.state) }}>{row.state}</strong></div>)}</div></Card>
      <Card title="Registered execution Runs"><div style={{ display: 'grid', gap: 8 }}>{runs.map((run) => <div key={run.run_id} style={{ border: '1px solid #1f2937', borderRadius: 10, padding: 12 }}><div style={{ display: 'flex', justifyContent: 'space-between' }}><strong>{run.run_id}</strong><strong style={{ color: statusColor(run.effective_state) }}>{run.effective_state}</strong></div><div style={{ color: '#64748b', fontSize: 11, marginTop: 5 }}>{run.process_id} · heartbeat {run.last_heartbeat_at ?? 'none'}</div></div>)}</div></Card>
    </div>
    if (active === 'Validation') return <div style={{ display: 'grid', gap: 16 }}><Card title="Shadow discrepancy"><strong style={{ color: statusColor(discrepancy?.status ?? 'UNKNOWN') }}>{discrepancy?.status ?? 'UNAVAILABLE'}</strong></Card><Card title="Anchor comparisons"><div style={{ display: 'grid', gap: 8 }}>{discrepancy?.comparisons.map((row) => <div key={row.key} style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #1f2937', padding: '8px 0' }}><span>{row.key}</span><strong style={{ color: statusColor(row.status) }}>{row.status}</strong></div>)}</div></Card></div>
    if (active !== 'Home') return <Card title={active}><p style={{ margin: 0, color: '#9ca3af' }}>Deterministic read-only view. Mutation surfaces remain disabled in Owner Console.</p></Card>
    const runningCount = runs.filter((run) => run.effective_state === 'RUNNING_CONFIRMED').length
    const liveWorkerCount = workers.filter((worker) => worker.enabled && worker.last_seen_at).length
    return <div style={{ display: 'grid', gap: 16 }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16 }}>
        <Card title="Current State"><strong>{status?.current_state.version ?? 'UNAVAILABLE'}</strong><div style={{ marginTop: 8, color: '#93c5fd' }}>{status?.aaa_role ?? 'SHADOW_NONAUTHORITATIVE'}</div></Card>
        <Card title="Operating Structure"><strong style={{ color: statusColor(structure?.projection.status ?? 'UNKNOWN') }}>{structure?.projection.status ?? 'UNAVAILABLE'}</strong><div style={{ marginTop: 8, color: '#9ca3af' }}>{structure?.roadmap.current_stage ?? 'UNKNOWN'} · {structure?.roadmap.current_gate ?? 'UNKNOWN'}</div></Card>
        <Card title="Runs"><strong style={{ color: '#86efac' }}>{runningCount} RUNNING</strong><div style={{ marginTop: 8, color: '#9ca3af' }}>{runs.length} registered</div></Card>
        <Card title="T19 Workers"><strong style={{ color: executionProjectionConnected ? '#86efac' : '#fcd34d' }}>{liveWorkerCount} observed</strong><div style={{ marginTop: 8, color: '#9ca3af' }}>{executionProjectionConnected ? 'PostgreSQL projection connected' : 'No liveness inferred'}</div></Card>
        <Card title="Shadow State Match"><strong style={{ color: statusColor(discrepancy?.status ?? 'UNKNOWN') }}>{discrepancy?.status ?? 'UNAVAILABLE'}</strong></Card>
        <Card title="Work Orders"><strong>{workCount ?? '—'}</strong><span style={{ color: '#9ca3af' }}> versioned records</span></Card>
        <Card title="Canonical Write"><strong style={{ color: '#fca5a5' }}>PROHIBITED</strong></Card>
        <Card title="LLM Dependency"><strong style={{ color: '#86efac' }}>{status?.llm_required_for_control_plane === false ? 'NOT REQUIRED' : 'UNKNOWN'}</strong><div style={{ marginTop: 8, color: '#9ca3af' }}>Owner-visible state without requiring an LLM connection.</div></Card>
      </div>
      <Card title="Control status"><div style={{ color: '#d1d5db' }}>{status?.current_state.status ?? 'READ_ONLY_API_NOT_CONNECTED'}</div></Card>
      <Card title="Validation gates"><div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>{gates.length > 0 ? gates.map((gate) => <Pill key={gate}>{gate}</Pill>) : <span style={{ color: '#9ca3af' }}>No gate data loaded.</span>}</div></Card>
    </div>
  }, [active, discrepancy, executionProjectionConnected, gates, personas, runs, status, structure, structureView, tasks, workCount, workers])

  return <div style={{ minHeight: '100vh', background: '#0b1020', color: '#f9fafb', fontFamily: 'Inter, ui-sans-serif, system-ui, sans-serif' }}>
    <style>{`
      .aaa-shell { display:grid; grid-template-columns:220px minmax(0, 1fr); min-height:calc(100vh - 82px); }
      .aaa-nav { border-right:1px solid #1f2937; padding:16px; }
      .aaa-card-grid { display:grid; grid-template-columns:repeat(auto-fit, minmax(230px, 1fr)); gap:12px; }
      .aaa-stage-flow { display:flex; flex-wrap:wrap; gap:10px; }
      .aaa-two-col { display:grid; grid-template-columns:minmax(0, 1fr) minmax(0, 1fr); gap:16px; }
      .aaa-flex-row { display:flex; gap:14px; flex-wrap:wrap; align-items:center; font-size:12px; }
      @media (max-width: 760px) {
        .aaa-shell { grid-template-columns:1fr; }
        .aaa-nav { border-right:none; border-bottom:1px solid #1f2937; display:flex; overflow-x:auto; gap:6px; }
        .aaa-nav button { min-width:max-content; }
        .aaa-two-col { grid-template-columns:1fr; }
      }
    `}</style>
    <header style={{ padding: '20px 28px', borderBottom: '1px solid #1f2937', display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12 }}>
      <div><div style={{ fontWeight: 800, fontSize: 22 }}>Asset Agent ASA</div><div style={{ color: '#64748b', fontSize: 13 }}>AAA Owner Console · deterministic-first</div></div>
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', justifyContent: 'flex-end' }}>
        <span style={{ fontSize: 12, padding: '6px 10px', border: '1px solid #334155', borderRadius: 999, color: apiState === 'ONLINE' ? '#86efac' : '#fca5a5' }}>API {apiState}</span>
        <span style={{ fontSize: 12, padding: '6px 10px', border: '1px solid #334155', borderRadius: 999, color: statusColor(structureRefreshState) }}>STRUCTURE {structureRefreshState}</span>
        <span style={{ fontSize: 12, padding: '6px 10px', border: '1px solid #334155', borderRadius: 999, color: '#cbd5e1' }}>SHADOW / READ-ONLY</span>
      </div>
    </header>
    <div className="aaa-shell">
      <nav className="aaa-nav">{navItems.map((item) => <button key={item} type="button" onClick={() => setActive(item)} style={{ width: '100%', textAlign: 'left', marginBottom: 5, padding: '10px 12px', borderRadius: 8, border: 'none', cursor: 'pointer', color: active === item ? '#fff' : '#94a3b8', background: active === item ? '#1e293b' : 'transparent', fontWeight: active === item ? 700 : 500 }}>{item}</button>)}</nav>
      <main style={{ padding: 28, maxWidth: 1280, width: '100%', boxSizing: 'border-box' }}>
        <div style={{ marginBottom: 20 }}><h1 style={{ margin: 0, fontSize: 26 }}>{active === 'Structure' ? 'Current Operating Structure · 현재 실무 구조' : active}</h1><p style={{ color: '#64748b', marginTop: 6 }}>{active === 'Structure' ? 'Persistent Control Plane projection. Persona, Channel, Authority and Workstream are distinct.' : 'Owner-visible persistent state without inferring execution from chat activity.'}</p></div>
        {content}
      </main>
    </div>
  </div>
}

import { useState, useEffect } from 'react'
import { type Match, type BetSelection, type PlacedBet, type OddsMarket, type OddsOption } from './data'
import {
  cancelBetSlip, createBankroll, depositBankroll, loadBankrolls,
  loadBetSlips, settleBetLeg,
  withdrawBankroll,
} from './api'
import {
  TrendingUp, Star, ChevronRight, ChevronLeft,
  Circle, Activity, BarChart3, Users, BookOpen,
  Trash2, CheckCircle2, XCircle, Clock,
  AlertTriangle, Target, X, Filter, Search
} from 'lucide-react'

type MatchTab = 'live' | 'lineup' | 'stats' | 'analysis' | 'markets' | 'h2h'

function LiveBadge({ minute }: { minute?: number }) {
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '2px 8px', borderRadius: '4px', background: 'rgba(255,59,59,0.15)', color: '#ff3b3b', fontSize: '11px', fontWeight: 700, fontFamily: "'JetBrains Mono', monospace" }}>
      <span className="pulse-live" style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#ff3b3b', display: 'inline-block' }} />
      {minute ? `${minute}'` : 'AO VIVO'}
    </span>
  )
}

function FormBadge({ result }: { result: string }) {
  const c: Record<string, [string, string]> = { V: ['rgba(0,200,83,0.15)', '#00c853'], E: ['rgba(251,191,36,0.15)', '#fbbf24'], D: ['rgba(255,23,68,0.15)', '#ff1744'] }
  const [bg, color] = c[result] || c.E
  return <span style={{ width: '24px', height: '24px', borderRadius: '4px', background: bg, color, display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: '11px', fontWeight: 700 }}>{result}</span>
}

function Card({ children, style }: { children: React.ReactNode; style?: React.CSSProperties }) {
  return <div style={{ background: '#22252a', border: '1px solid #444a52', borderRadius: '12px', ...style }}>{children}</div>
}

function MatchCard({ match, onClick, isFavorite, onToggleFavorite }: {
  match: Match; onClick: () => void; isFavorite: boolean; onToggleFavorite: () => void
}) {
  return (
    <div
      className="match-card-interactive"
      role="button"
      tabIndex={0}
      aria-label={`Abrir ${match.homeTeam.name} contra ${match.awayTeam.name}`}
      onClick={onClick}
      onKeyDown={event => {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault()
          onClick()
        }
      }}
    >
    <Card style={{ cursor: 'pointer', transition: 'border-color 0.15s' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 16px', borderBottom: '1px solid #444a52' }}>
        <span style={{ fontSize: '12px', color: '#5a6480', fontFamily: "'JetBrains Mono', monospace" }}>{match.startTime}</span>
        {match.status === 'live' && <LiveBadge minute={match.minute} />}
        {match.status === 'finished' && <span style={{ fontSize: '11px', padding: '2px 8px', borderRadius: '4px', background: '#444a52', color: '#5a6480' }}>Encerrado</span>}
        {match.status === 'upcoming' && <span style={{ fontSize: '11px', color: '#5a6480' }}>Em breve</span>}
        <button
          aria-label={isFavorite ? 'Remover partida dos favoritos' : 'Adicionar partida aos favoritos'}
          aria-pressed={isFavorite}
          onClick={e => { e.stopPropagation(); onToggleFavorite() }}
          style={{ background: 'none', border: 'none', cursor: 'pointer', color: isFavorite ? '#fbbf24' : '#59616b', padding: '2px' }}
        >
          <Star size={14} fill={isFavorite ? '#fbbf24' : 'none'} />
        </button>
      </div>

      <div style={{ padding: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px' }}>
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{ width: '36px', height: '36px', borderRadius: '8px', background: '#2b2f35', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '20px' }}>{match.homeTeam.logo}</div>
            <span style={{ fontWeight: 600, fontSize: '13px', color: '#eef0f9' }}>{match.homeTeam.name}</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexShrink: 0 }}>
            {match.homeScore !== undefined
              ? <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ fontFamily: "'Russo One', sans-serif", fontSize: '22px', color: '#eef0f9' }}>{match.homeScore}</span>
                <span style={{ fontFamily: "'Russo One', sans-serif", fontSize: '16px', color: '#59616b' }}>:</span>
                <span style={{ fontFamily: "'Russo One', sans-serif", fontSize: '22px', color: '#eef0f9' }}>{match.awayScore}</span>
              </div>
              : <span style={{ fontSize: '12px', color: '#5a6480', fontFamily: "'JetBrains Mono', monospace" }}>vs</span>
            }
          </div>
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: '10px', justifyContent: 'flex-end' }}>
            <span style={{ fontWeight: 600, fontSize: '13px', color: '#eef0f9', textAlign: 'right' }}>{match.awayTeam.name}</span>
            <div style={{ width: '36px', height: '36px', borderRadius: '8px', background: '#2b2f35', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '20px' }}>{match.awayTeam.logo}</div>
          </div>
        </div>

        {match.markets.length > 0 && match.status !== 'finished' && (
          <div style={{ marginTop: '12px', paddingTop: '12px', borderTop: '1px solid #444a52', display: 'flex', gap: '8px' }}>
            {(match.markets.find(m => m.name === 'Resultado da Partida')?.options || []).slice(0, 3).map(o => (
              <button key={o.label}
                onClick={e => { e.stopPropagation(); onClick() }}
                style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '8px', borderRadius: '8px', background: '#2b2f35', border: '1px solid #444a52', cursor: 'pointer', transition: 'all 0.15s' }}
                onMouseEnter={e => { e.currentTarget.style.borderColor = '#00e887'; e.currentTarget.style.background = '#00e887'; Array.from(e.currentTarget.children).forEach((c: any) => c.style.color = '#17191c') }}
                onMouseLeave={e => { e.currentTarget.style.borderColor = '#444a52'; e.currentTarget.style.background = '#2b2f35'; Array.from(e.currentTarget.children).forEach((c: any, i) => c.style.color = i === 0 ? '#7a88b0' : '#eef0f9') }}
              >
                <span style={{ fontSize: '11px', color: '#7a88b0', marginBottom: '2px' }}>{o.label}</span>
                <span style={{ fontFamily: "'JetBrains Mono', monospace", fontWeight: 700, fontSize: '14px', color: '#eef0f9' }}>{o.odds.toFixed(2)}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      <div style={{ padding: '0 16px 12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontSize: '11px', color: '#5a6480' }}>Ver detalhes e mercados</span>
        <ChevronRight size={14} color="#00e887" />
      </div>
    </Card>
    </div>
  )
}

export function HomeView({ matches, onMatchClick, favorites, onToggleFavorite }: {
  matches: Match[]; onMatchClick: (m: Match) => void; favorites: string[]; onToggleFavorite: (id: string) => void
}) {
  const [scope, setScope] = useState<'live' | 'today' | 'next' | 'finished'>('live')
  const [league, setLeague] = useState('all')
  const [search, setSearch] = useState('')
  const [searchOpen, setSearchOpen] = useState(false)
  const live = matches.filter(m =>
    m.status === 'live' && Boolean(m.kickoffAt)
  )
  const todayKey = new Date().toLocaleDateString('en-CA')
  const upcomingToday = matches.filter(m =>
    m.status === 'upcoming' && m.kickoffAt &&
    new Date(m.kickoffAt).toLocaleDateString('en-CA') === todayKey
  )
  const next = matches.filter(m =>
    m.status === 'upcoming' && m.kickoffAt &&
    new Date(m.kickoffAt).toLocaleDateString('en-CA') > todayKey
  )
  const finished = matches
    .filter(m => m.status === 'finished')
    .sort((a, b) => new Date(b.kickoffAt || 0).getTime() - new Date(a.kickoffAt || 0).getTime())
  const scoped = scope === 'live'
    ? live : scope === 'today'
    ? upcomingToday : scope === 'next'
    ? next : finished
  const leagues = Array.from(new Set(matches.map(m => m.league))).sort()
  const normalizedSearch = search.trim().normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase('pt-BR')
  const visible = scoped.filter(match => {
    if (league !== 'all' && match.league !== league) return false
    if (!normalizedSearch) return true

    return [match.homeTeam.name, match.awayTeam.name, match.league]
      .some(value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase('pt-BR').includes(normalizedSearch))
  })

  const byLeague = (list: Match[]) => list.reduce((acc, m) => { if (!acc[m.league]) acc[m.league] = []; acc[m.league].push(m); return acc }, {} as Record<string, Match[]>)

  return (
    <div className="animate-fade-in">
      <div style={{ padding: '24px 0 16px' }}>
        <h1 style={{ fontFamily: "'Russo One', sans-serif", fontSize: '24px', color: '#eef0f9', letterSpacing: '0.05em', margin: 0 }}>CENTRAL DE PARTIDAS</h1>
        <p style={{ fontSize: '13px', color: '#5a6480', marginTop: '4px' }}>{new Date().toLocaleDateString('pt-BR', { weekday: 'long', day: 'numeric', month: 'long' })}</p>
      </div>

      <div className="match-controls" style={{ position: 'relative', display: 'flex', flexWrap: 'nowrap', alignItems: 'center', gap: 8, marginBottom: 16 }}>
        {[
          { id: 'live', label: `Ao vivo (${live.length})` },
          { id: 'today', label: `Em breve (${upcomingToday.length})` },
          { id: 'next', label: `Próximas partidas (${next.length})` },
          { id: 'finished', label: `Encerradas (${finished.length})` },
        ].map(item => (
          <button key={item.id} onClick={() => setScope(item.id as typeof scope)}
            style={{ flexShrink: 0, whiteSpace: 'nowrap', padding: '9px 12px', borderRadius: 8, border: `1px solid ${scope === item.id ? '#00e887' : '#444a52'}`, background: scope === item.id ? 'rgba(0,232,135,.12)' : '#22252a', color: scope === item.id ? '#00e887' : '#7a88b0', cursor: 'pointer', fontWeight: 700 }}>
            {item.label}
          </button>
        ))}
        <button
          className="match-search-button"
          type="button"
          onClick={() => setSearchOpen(current => !current)}
          aria-label="Pesquisar partidas e competições"
          aria-expanded={searchOpen}
          title="Pesquisar partidas e competições"
          style={{ marginLeft: 'auto', flex: '0 0 42px', height: 42, display: 'grid', placeItems: 'center', borderRadius: 8, border: `1px solid ${searchOpen || normalizedSearch ? '#00e887' : '#444a52'}`, background: searchOpen || normalizedSearch ? 'rgba(0,232,135,.12)' : '#22252a', color: searchOpen || normalizedSearch ? '#00e887' : '#7a88b0', cursor: 'pointer' }}
        >
          <Search size={17} />
        </button>
        {searchOpen && (
          <div className="match-search-panel" role="search" style={{ position: 'absolute', zIndex: 10, top: 'calc(100% + 8px)', right: 190, width: 300, display: 'flex', alignItems: 'center', filter: 'drop-shadow(0 10px 20px rgba(0,0,0,.35))' }}>
            <Search size={15} aria-hidden="true" style={{ position: 'absolute', left: 12, color: '#7a88b0', pointerEvents: 'none' }} />
            <input
              autoFocus
              type="search"
              value={search}
              onChange={event => setSearch(event.target.value)}
              onKeyDown={event => { if (event.key === 'Escape') setSearchOpen(false) }}
              placeholder="Buscar time ou competição"
              aria-label="Buscar partidas por time ou competição"
              style={{ width: '100%', boxSizing: 'border-box', background: '#22252a', color: '#eef0f9', border: '1px solid #00e887', borderRadius: 8, padding: '11px 38px', outline: 'none' }}
            />
            {search && (
              <button type="button" onClick={() => setSearch('')} aria-label="Limpar pesquisa" title="Limpar pesquisa"
                style={{ position: 'absolute', right: 8, display: 'grid', placeItems: 'center', padding: 4, color: '#7a88b0', background: 'transparent', border: 0, cursor: 'pointer' }}>
                <X size={14} />
              </button>
            )}
          </div>
        )}
        <label className="match-league-filter" style={{ flex: '0 0 180px', height: 42, display: 'flex', alignItems: 'center', gap: 7, color: '#7a88b0' }}>
          <Filter size={14} style={{ flexShrink: 0 }} />
          <select value={league} onChange={event => setLeague(event.target.value)}
            style={{ width: '100%', height: 42, minWidth: 0, background: '#22252a', color: '#eef0f9', border: '1px solid #444a52', borderRadius: 8, padding: '0 10px' }}>
            <option value="all">Todas as ligas</option>
            {leagues.map(item => <option key={item} value={item}>{item}</option>)}
          </select>
        </label>
      </div>

      {visible.length === 0 && (
        <Card style={{ padding: 24, textAlign: 'center', color: '#7a88b0' }}>
          {normalizedSearch
            ? `Nenhuma partida ou competição encontrada para “${search.trim()}”.`
            : 'Nenhuma partida encontrada nesta categoria.'}
        </Card>
      )}
      {Object.entries(byLeague(visible)).map(([l, ms]) => (
        <LeagueGroup key={l} league={ms[0].league} logo={ms[0].leagueLogo} country={ms[0].country}
          group={ms[0].competitionGroup}>
          {ms.map(m => <MatchCard key={m.id} match={m} onClick={() => onMatchClick(m)} isFavorite={favorites.includes(m.id)} onToggleFavorite={() => onToggleFavorite(m.id)} />)}
        </LeagueGroup>
      ))}
    </div>
  )
}

function LeagueGroup({ league, logo, country, group, children }: { league: string; logo: string; country: string; group?: Match['competitionGroup']; children: React.ReactNode }) {
  return (
    <div style={{ marginBottom: '16px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px', padding: '0 4px' }}>
        <span style={{ fontSize: '16px' }}>{logo}</span>
        <span style={{ fontSize: '12px', fontWeight: 600, color: '#7a88b0' }}>{league}</span>
        <span style={{ fontSize: '11px', color: '#59616b' }}>· {country}</span>
        <span style={{ marginLeft: 'auto', fontSize: '9px', color: group === 'observation' ? '#f59e0b' : '#00e887', border: '1px solid currentColor', borderRadius: 10, padding: '2px 7px' }}>
          {group === 'national_teams' ? 'SELEÇÕES' : group === 'core' ? 'NÚCLEO' : 'OBSERVAÇÃO'}
        </span>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>{children}</div>
    </div>
  )
}

export function MatchView({ match, betSlip, onAddBet, onBack, isFavorite, onToggleFavorite }: {
  match: Match; betSlip: BetSelection[]
  onAddBet: (matchId: string, matchName: string, market: string, option: string, odds: number, marketId?: number) => void
  onBack: () => void; isFavorite: boolean; onToggleFavorite: () => void
}) {
  const [tab, setTab] = useState<MatchTab>(
    new URLSearchParams(window.location.search).get('tab') === 'stats'
      ? 'stats'
      : match.status === 'live' ? 'live' : match.status === 'finished' ? 'stats' : 'lineup'
  )
  const matchName = `${match.homeTeam.name} vs ${match.awayTeam.name}`
  const addBet = (market: string, option: string, odds: number) => {
    const marketId = Number(match.markets.find(item => item.name === market)?.id)
    onAddBet(
      match.id, matchName, market, option, odds,
      Number.isFinite(marketId) ? marketId : undefined,
    )
  }

  const tabs: { id: MatchTab; label: string; icon: React.ReactNode }[] = [
    { id: 'live', label: match.status === 'finished' ? 'Eventos' : 'Ao Vivo', icon: <Activity size={13} /> },
    { id: 'lineup', label: 'Escalação', icon: <Users size={13} /> },
    { id: 'stats', label: 'Estatísticas', icon: <BarChart3 size={13} /> },
    { id: 'markets', label: 'Mercados', icon: <Target size={13} /> },
    { id: 'analysis', label: 'Análise', icon: <TrendingUp size={13} /> },
    { id: 'h2h', label: 'H2H', icon: <BookOpen size={13} /> },
  ]

  return (
    <div className="animate-fade-in">
      <button onClick={onBack} style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '16px 0', fontSize: '13px', color: '#7a88b0', background: 'none', border: 'none', cursor: 'pointer' }}>
        <ChevronLeft size={15} /> Voltar
      </button>

      <Card style={{ marginBottom: '16px', overflow: 'hidden' }}>
        <div style={{ padding: '20px 24px 16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ fontSize: '20px' }}>{match.leagueLogo}</span>
              <div>
                <div style={{ fontSize: '13px', fontWeight: 600, color: '#7a88b0' }}>{match.league}</div>
                <div style={{ fontSize: '11px', color: '#5a6480' }}>{match.country}</div>
              </div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              {match.status === 'live' && <LiveBadge minute={match.minute} />}
              {match.status === 'finished' && <span style={{ fontSize: '11px', padding: '4px 10px', borderRadius: '4px', background: '#444a52', color: '#5a6480' }}>Encerrado</span>}
              {match.status === 'upcoming' && <span style={{ fontFamily: "'JetBrains Mono', monospace", fontWeight: 700, fontSize: '16px', color: '#4f8ef7' }}>{match.startTime}</span>}
              <button onClick={onToggleFavorite} style={{ background: 'none', border: 'none', cursor: 'pointer', color: isFavorite ? '#fbbf24' : '#59616b' }}>
                <Star size={18} fill={isFavorite ? '#fbbf24' : 'none'} />
              </button>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '16px' }}>
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px', textAlign: 'center' }}>
              <div style={{ width: '64px', height: '64px', borderRadius: '16px', background: '#2b2f35', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '32px' }}>{match.homeTeam.logo}</div>
              <span style={{ fontWeight: 600, fontSize: '14px', color: '#eef0f9' }}>{match.homeTeam.name}</span>
              <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '11px', color: '#5a6480' }}>{match.homeLineup.formation}</span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' }}>
              {match.homeScore !== undefined
                ? <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontFamily: "'Russo One', sans-serif", fontSize: '40px', color: '#eef0f9' }}>{match.homeScore}</span>
                  <span style={{ fontFamily: "'Russo One', sans-serif", fontSize: '24px', color: '#59616b' }}>:</span>
                  <span style={{ fontFamily: "'Russo One', sans-serif", fontSize: '40px', color: '#eef0f9' }}>{match.awayScore}</span>
                </div>
                : <span style={{ fontFamily: "'Russo One', sans-serif", fontSize: '24px', color: '#59616b' }}>vs</span>
              }
            </div>
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px', textAlign: 'center' }}>
              <div style={{ width: '64px', height: '64px', borderRadius: '16px', background: '#2b2f35', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '32px' }}>{match.awayTeam.logo}</div>
              <span style={{ fontWeight: 600, fontSize: '14px', color: '#eef0f9' }}>{match.awayTeam.name}</span>
              <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '11px', color: '#5a6480' }}>{match.awayLineup.formation}</span>
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', borderTop: '1px solid #444a52', overflowX: 'auto' }}>
          {tabs.map(t => (
            <button key={t.id} onClick={() => setTab(t.id)}
              style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px', padding: '12px 8px', fontSize: '12px', fontWeight: 600, whiteSpace: 'nowrap', border: 'none', borderBottom: `2px solid ${tab === t.id ? '#00e887' : 'transparent'}`, background: tab === t.id ? 'rgba(0,232,135,0.04)' : 'transparent', color: tab === t.id ? '#00e887' : '#5a6480', cursor: 'pointer', transition: 'all 0.15s' }}
            >
              {t.icon}{t.label}
            </button>
          ))}
        </div>
      </Card>

      {tab === 'live' && <LiveTab match={match} />}
      {tab === 'lineup' && <LineupTab match={match} />}
      {tab === 'stats' && <StatsTab match={match} />}
      {tab === 'markets' && <MarketsTab match={match} betSlip={betSlip} onAddBet={addBet} />}
      {tab === 'analysis' && <AnalysisTab match={match} onAddBet={addBet} />}
      {tab === 'h2h' && <H2HTab match={match} />}
    </div>
  )
}

function LiveTab({ match }: { match: Match }) {
  const eventMeta: Record<string, { icon: string; color: string }> = {
    goal: { icon: '⚽', color: '#00e887' }, yellow: { icon: '🟨', color: '#fbbf24' },
    red: { icon: '🟥', color: '#ff1744' }, substitution: { icon: '🔄', color: '#4f8ef7' },
    var: { icon: '📺', color: '#ff7c3a' }, penalty: { icon: '⚽', color: '#00e887' },
  }

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px' }}>
      <div>
        <SectionLabel>Eventos da Partida</SectionLabel>
        {match.status === 'upcoming' ? (
          <Card style={{ padding: '40px', textAlign: 'center' }}>
            <Clock size={32} color="#59616b" style={{ margin: '0 auto 12px' }} />
            <p style={{ fontSize: '13px', color: '#5a6480', margin: 0 }}>A partida ainda não começou</p>
          </Card>
        ) : match.events.length === 0 ? (
          <Card style={{ padding: '32px', textAlign: 'center' }}>
            <p style={{ fontSize: '13px', color: '#5a6480', margin: 0 }}>
              Nenhum evento disponibilizado pelos provedores até o momento.
            </p>
          </Card>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {[...match.events].reverse().map(ev => {
              const meta = eventMeta[ev.type]
              return (
                <Card key={ev.id} style={{ padding: '12px 16px' }}>
                  <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
                    <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '12px', color: '#5a6480', width: '28px', flexShrink: 0, paddingTop: '2px' }}>{ev.minute}'</span>
                    <span style={{ fontSize: '18px', flexShrink: 0 }}>{meta.icon}</span>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                        <span style={{ fontWeight: 600, fontSize: '13px', color: meta.color }}>{ev.player}</span>
                        <span style={{ fontSize: '10px', padding: '2px 6px', borderRadius: '4px', background: ev.team === 'home' ? 'rgba(79,142,247,0.15)' : 'rgba(255,124,58,0.15)', color: ev.team === 'home' ? '#4f8ef7' : '#ff7c3a' }}>
                          {ev.team === 'home' ? match.homeTeam.shortName : match.awayTeam.shortName}
                        </span>
                      </div>
                      {ev.detail && <p style={{ fontSize: '12px', color: '#5a6480', margin: '2px 0 0' }}>{ev.detail}</p>}
                    </div>
                  </div>
                </Card>
              )
            })}
          </div>
        )}
      </div>

      <div>
        <SectionLabel>Estatísticas ao Vivo</SectionLabel>
        <StatsBars match={match} />
      </div>
    </div>
  )
}

function StatsBars({ match }: { match: Match }) {
  const rows = [
    { keys: ['possession_home', 'possession_away'], label: 'Posse de Bola', h: `${match.stats.possession[0]}%`, a: `${match.stats.possession[1]}%`, hv: match.stats.possession[0], av: match.stats.possession[1] },
    { keys: ['shots_home', 'shots_away'], label: 'Chutes', h: String(match.stats.shots[0]), a: String(match.stats.shots[1]), hv: match.stats.shots[0], av: match.stats.shots[1] },
    { keys: ['shots_on_target_home', 'shots_on_target_away'], label: 'No Alvo', h: String(match.stats.shotsOnTarget[0]), a: String(match.stats.shotsOnTarget[1]), hv: match.stats.shotsOnTarget[0], av: match.stats.shotsOnTarget[1] },
    { keys: ['corners_home', 'corners_away'], label: 'Escanteios', h: String(match.stats.corners[0]), a: String(match.stats.corners[1]), hv: match.stats.corners[0], av: match.stats.corners[1] },
    { keys: ['xg_home', 'xg_away'], label: 'xG', h: String(match.stats.xG[0]), a: String(match.stats.xG[1]), hv: match.stats.xG[0], av: match.stats.xG[1] },
  ].filter(row => row.keys.some(key => match.availableStats?.includes(key)))
  if (!match.statsAvailable || rows.length === 0) {
    return (
      <Card style={{ padding: 32, textAlign: 'center', color: '#7a88b0' }}>
        Dados da partida não disponíveis.
      </Card>
    )
  }
  return (
    <Card style={{ overflow: 'hidden' }}>
      {rows.map((row, i) => {
        const total = row.hv + row.av || 1
        const hPct = (row.hv / total) * 100
        return (
          <div key={row.label} style={{ padding: '12px 16px', borderBottom: i < rows.length - 1 ? '1px solid #444a52' : 'none' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
              <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '13px', fontWeight: 700, color: '#eef0f9' }}>{row.h}</span>
              <span style={{ fontSize: '12px', color: '#5a6480' }}>{row.label}</span>
              <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '13px', fontWeight: 700, color: '#eef0f9' }}>{row.a}</span>
            </div>
            <div style={{ height: '4px', borderRadius: '2px', background: '#444a52', display: 'flex', overflow: 'hidden' }}>
              <div style={{ width: `${hPct}%`, background: '#4f8ef7', borderRadius: '2px' }} />
              <div style={{ flex: 1, background: '#ff7c3a' }} />
            </div>
          </div>
        )
      })}
    </Card>
  )
}

function LineupTab({ match }: { match: Match }) {
  const [side, setSide] = useState<'home' | 'away'>('home')
  const lineup = side === 'home' ? match.homeLineup : match.awayLineup
  const team = side === 'home' ? match.homeTeam : match.awayTeam
  const lineupAvailable = lineup.players.length > 0

  const coordsMap: Record<string, { x: number; y: number }[]> = {
    GK: [{ x: 50, y: 90 }],
    DEF: [{ x: 15, y: 70 }, { x: 37, y: 70 }, { x: 63, y: 70 }, { x: 85, y: 70 }],
    MID: [{ x: 20, y: 50 }, { x: 50, y: 48 }, { x: 80, y: 50 }],
    FWD: [{ x: 20, y: 26 }, { x: 50, y: 18 }, { x: 80, y: 26 }],
  }
  const normalizedPosition: Record<string, keyof typeof coordsMap> = {
    G: 'GK', GK: 'GK',
    D: 'DEF', DEF: 'DEF',
    M: 'MID', MID: 'MID',
    F: 'FWD', FWD: 'FWD',
  }
  const parsedGrid = lineup.players.map(player => {
    const [row, column] = (player.grid || '').split(':').map(Number)
    return {
      player,
      row: Number.isFinite(row) && row > 0 ? row : null,
      column: Number.isFinite(column) && column > 0 ? column : null,
    }
  })
  const maxGridRow = Math.max(1, ...parsedGrid.flatMap(item => item.row === null ? [] : [item.row]))
  const columnsByRow = parsedGrid.reduce<Record<number, number>>((acc, item) => {
    if (item.row !== null && item.column !== null) {
      acc[item.row] = Math.max(acc[item.row] || 0, item.column)
    }
    return acc
  }, {})
  const posCount: Record<string, number> = {}
  const positioned = parsedGrid.map(({ player, row, column }) => {
    if (row !== null && column !== null) {
      const columns = columnsByRow[row] || 1
      return {
        ...player,
        coords: {
          x: columns === 1 ? 50 : 12 + ((column - 1) * 76) / (columns - 1),
          y: maxGridRow === 1 ? 50 : 90 - ((row - 1) * 70) / (maxGridRow - 1),
        },
      }
    }
    const position = normalizedPosition[player.position.toUpperCase()] || 'MID'
    const idx = posCount[position] || 0
    posCount[position] = idx + 1
    const options = coordsMap[position]
    const coords = options[Math.min(idx, options.length - 1)]
    return { ...player, coords }
  })

  return (
    <div>
      <div style={{ display: 'flex', borderRadius: '10px', border: '1px solid #444a52', overflow: 'hidden', marginBottom: '16px' }}>
        {(['home', 'away'] as const).map(s => (
          <button key={s} onClick={() => setSide(s)} style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', padding: '12px', fontSize: '13px', fontWeight: 600, background: side === s ? '#343941' : '#22252a', color: side === s ? '#eef0f9' : '#5a6480', border: 'none', cursor: 'pointer', transition: 'all 0.15s' }}>
            <span>{s === 'home' ? match.homeTeam.logo : match.awayTeam.logo}</span>
            <span>{s === 'home' ? match.homeTeam.name : match.awayTeam.name}</span>
          </button>
        ))}
      </div>

      {!lineupAvailable ? (
        <Card style={{ padding: 32, marginBottom: 16, textAlign: 'center', color: '#7a88b0' }}>
          Escalação ainda não disponibilizada pelos provedores para esta partida.
          O sistema continuará consultando automaticamente.
        </Card>
      ) : <Card style={{ overflow: 'hidden', marginBottom: '16px' }}>
        <div style={{ position: 'relative', paddingBottom: '58%', background: 'linear-gradient(180deg, #25282d 0%, #30343a 50%, #25282d 100%)' }}>
          <div style={{ position: 'absolute', inset: '12px 20px', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '4px' }} />
          <div style={{ position: 'absolute', left: '50%', top: '12px', bottom: '12px', width: '1px', background: 'rgba(255,255,255,0.06)', transform: 'translateX(-50%)' }} />
          <div style={{ position: 'absolute', left: '50%', top: '50%', width: '48px', height: '48px', borderRadius: '50%', border: '1px solid rgba(255,255,255,0.06)', transform: 'translate(-50%,-50%)' }} />
          {positioned.map((p, index) => (
            <div key={`${p.number}-${p.name}-${index}`} style={{ position: 'absolute', left: `${p.coords.x}%`, top: `${p.coords.y}%`, transform: 'translate(-50%,-50%)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '2px' }}>
              <div style={{ width: '32px', height: '32px', borderRadius: '50%', border: `2px solid ${team.color}`, background: '#22252a', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: "'JetBrains Mono', monospace", fontSize: '11px', fontWeight: 700, color: '#eef0f9' }}>{p.number}</div>
              <div style={{ padding: '1px 4px', borderRadius: '3px', background: 'rgba(23,25,28,0.92)', color: '#eef0f9', fontSize: '9px', fontWeight: 600, whiteSpace: 'nowrap', maxWidth: '56px', overflow: 'hidden', textOverflow: 'ellipsis' }}>{p.name.split(' ').pop()}</div>
            </div>
          ))}
        </div>
      </Card>}

      {lineupAvailable && <SectionLabel>Banco de Reservas</SectionLabel>}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))', gap: '8px' }}>
        {lineup.bench.map(p => (
          <Card key={p.number} style={{ padding: '8px 12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '11px', color: '#5a6480', width: '24px', textAlign: 'center', fontWeight: 700 }}>{p.number}</span>
            <span style={{ fontSize: '12px', color: '#7a88b0' }}>{p.name}</span>
          </Card>
        ))}
      </div>
    </div>
  )
}

function StatsTab({ match }: { match: Match }) {
  type StatRow = { keys: string[]; label: string; values: [number, number]; suffix?: string; always?: boolean }
  const row = (keys: string[], label: string, values: [number, number], suffix = '', always = false): StatRow =>
    ({ keys, label, values, suffix, always })
  const groups = [
    { title: 'Forma e controle', rows: [
      row(['possession_home', 'possession_away'], 'Posse de bola', match.stats.possession, '%'),
      row(['pass_accuracy_home', 'pass_accuracy_away'], 'Precisão de passes', match.stats.passAccuracy, '%'),
      row(['passes_home', 'passes_away'], 'Passes', match.stats.passes),
      row(['passes_accurate_home', 'passes_accurate_away'], 'Passes certos', match.stats.passesAccurate),
    ] },
    { title: 'Ataque', rows: [
      row([], 'Gols', [match.homeScore || 0, match.awayScore || 0], '', match.homeScore != null && match.awayScore != null),
      row(['shots_home', 'shots_away'], 'Total de chutes', match.stats.shots),
      row(['shots_on_target_home', 'shots_on_target_away'], 'Chutes no gol', match.stats.shotsOnTarget),
      row(['shots_off_target_home', 'shots_off_target_away'], 'Chutes fora do gol', match.stats.shotsOffTarget),
      row(['blocked_shots_home', 'blocked_shots_away'], 'Chutes bloqueados', match.stats.blockedShots),
      row(['shots_inside_box_home', 'shots_inside_box_away'], 'Chutes dentro da área', match.stats.shotsInsideBox),
      row(['shots_outside_box_home', 'shots_outside_box_away'], 'Chutes fora da área', match.stats.shotsOutsideBox),
      row(['corners_home', 'corners_away'], 'Escanteios', match.stats.corners),
      row(['offsides_home', 'offsides_away'], 'Impedimentos', match.stats.offsides),
      row(['xg_home', 'xg_away'], 'Expected Goals (xG)', match.stats.xG),
    ] },
    { title: 'Defesa e disciplina', rows: [
      row(['fouls_home', 'fouls_away'], 'Faltas', match.stats.fouls),
      row(['goalkeeper_saves_home', 'goalkeeper_saves_away'], 'Defesas do goleiro', match.stats.goalkeeperSaves),
      row(['yellow_cards_home', 'yellow_cards_away'], 'Cartões amarelos', match.stats.yellowCards),
      row(['red_cards_home', 'red_cards_away'], 'Cartões vermelhos', match.stats.redCards),
    ] },
  ].map(group => ({ ...group, rows: group.rows.filter(item =>
    item.always || item.keys.some(key => match.availableStats?.includes(key))
  ) })).filter(group => group.rows.length > 0)

  if (!match.statsAvailable || groups.length === 0) {
    return (
      <Card style={{ padding: 40, textAlign: 'center' }}>
        <BarChart3 size={30} color="#59616b" style={{ margin: '0 auto 12px' }} />
        <div style={{ color: '#eef0f9', fontWeight: 700, marginBottom: 5 }}>Dados da partida não disponíveis</div>
        <div style={{ color: '#5a6480', fontSize: 12 }}>
          O sistema continuará consultando os provedores e atualizará o modelo quando as estatísticas forem recebidas.
        </div>
      </Card>
    )
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
      <Card style={{ overflow: 'hidden' }}>
        <div style={{ display: 'flex', padding: '12px 16px', alignItems: 'center' }}>
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: 18 }}>{match.homeTeam.logo}</span>
            <span style={{ fontWeight: 600, fontSize: 13, color: '#eef0f9' }}>{match.homeTeam.name}</span>
          </div>
          <span style={{ fontSize: 11, fontWeight: 700, color: '#5a6480', letterSpacing: '0.1em' }}>COMPARATIVO</span>
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: 8, justifyContent: 'flex-end' }}>
            <span style={{ fontWeight: 600, fontSize: 13, color: '#eef0f9', textAlign: 'right' }}>{match.awayTeam.name}</span>
            <span style={{ fontSize: 18 }}>{match.awayTeam.logo}</span>
          </div>
        </div>
      </Card>
      {groups.map(group => <Card key={group.title} style={{ padding: '18px 16px 8px' }}>
        <h3 style={{ margin: '0 0 18px', textAlign: 'center', color: '#eef0f9', fontSize: 18 }}>{group.title}</h3>
        {group.rows.map(item => {
          const [home, away] = item.values
          const maximum = Math.max(home, away, 1)
          const homeWidth = home === 0 && away === 0 ? 0 : home / maximum * 100
          const awayWidth = home === 0 && away === 0 ? 0 : away / maximum * 100
          return <div key={item.label} style={{ marginBottom: 15 }}>
            <div style={{ display: 'grid', gridTemplateColumns: '64px 1fr 64px', alignItems: 'end', gap: 10, marginBottom: 7 }}>
              <strong style={{ fontFamily: "'JetBrains Mono', monospace", color: '#eef0f9', fontSize: 14 }}>{home}{item.suffix}</strong>
              <span style={{ textAlign: 'center', color: '#a8b0c8', fontSize: 12 }}>{item.label}</span>
              <strong style={{ fontFamily: "'JetBrains Mono', monospace", color: '#eef0f9', fontSize: 14, textAlign: 'right' }}>{away}{item.suffix}</strong>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <div style={{ height: 6, borderRadius: 4, background: '#444a52', overflow: 'hidden', display: 'flex', justifyContent: 'flex-end' }}>
                <div style={{ width: `${homeWidth}%`, background: '#4f8ef7', borderRadius: 4 }} />
              </div>
              <div style={{ height: 6, borderRadius: 4, background: '#444a52', overflow: 'hidden' }}>
                <div style={{ width: `${awayWidth}%`, background: '#ff7c3a', borderRadius: 4 }} />
              </div>
            </div>
          </div>
        })}
      </Card>)}
      <div style={{ color: '#5a6480', fontSize: 11, lineHeight: 1.5, padding: '0 4px' }}>
        Estatísticas conciliadas entre os provedores disponíveis. Apenas campos efetivamente recebidos são exibidos; dados ao vivo podem sofrer atraso.
      </div>
    </div>
  )
}

function MarketsTab({ match, betSlip, onAddBet }: {
  match: Match; betSlip: BetSelection[]
  onAddBet: (market: string, option: string, odds: number) => void
}) {
  const isSel = (market: OddsMarket, opt: OddsOption) => betSlip.some(b => b.market === market.name && b.option === opt.label)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      {match.markets.map(market => (
        <Card key={market.id} style={{ overflow: 'hidden' }}>
          <div style={{ padding: '10px 16px', borderBottom: '1px solid #444a52' }}>
            <span style={{ fontSize: '12px', fontWeight: 600, color: '#7a88b0' }}>{market.name}</span>
          </div>
          <div style={{ padding: '12px', display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {market.options.map(opt => {
              const sel = isSel(market, opt)
              return (
                <button key={opt.id} onClick={() => onAddBet(market.name, opt.label, opt.odds)}
                  style={{ flex: '1', minWidth: '80px', display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '12px 8px', borderRadius: '8px', background: sel ? '#00e887' : '#2b2f35', border: `1px solid ${sel ? '#00e887' : '#444a52'}`, cursor: 'pointer', transition: 'all 0.15s' }}
                  onMouseEnter={e => { if (!sel) { e.currentTarget.style.borderColor = '#00e887'; e.currentTarget.style.background = 'rgba(0,232,135,0.08)' } }}
                  onMouseLeave={e => { if (!sel) { e.currentTarget.style.borderColor = '#444a52'; e.currentTarget.style.background = '#2b2f35' } }}
                >
                  <span style={{ fontSize: '11px', color: sel ? '#17191c' : '#7a88b0', marginBottom: '4px', fontWeight: 500 }}>{opt.label}</span>
                  <span style={{ fontFamily: "'JetBrains Mono', monospace", fontWeight: 700, fontSize: '16px', color: sel ? '#17191c' : '#eef0f9' }}>{opt.odds.toFixed(2)}</span>
                </button>
              )
            })}
          </div>
        </Card>
      ))}
    </div>
  )
}

function AnalysisTab({ match, onAddBet }: { match: Match; onAddBet: (market: string, option: string, odds: number) => void }) {
  const [expandedForm, setExpandedForm] = useState<'home' | 'away' | null>(null)
  const confStyle: Record<string, [string, string]> = {
    Alta: ['rgba(0,200,83,0.15)', '#00c853'],
    Média: ['rgba(251,191,36,0.15)', '#fbbf24'],
    Baixa: ['rgba(255,23,68,0.15)', '#ff1744'],
  }
  const categoryLabels: Record<string, string> = {
    result: 'Resultados',
    goals: 'Gols',
    team_goals: 'Gols por equipe',
    score: 'Placares',
    corners: 'Escanteios',
    team_corners: 'Escanteios por equipe',
    cards: 'Cartões',
    team_cards: 'Cartões por equipe',
    manual: 'Mercados manuais',
    other: 'Outros',
  }
  const grouped = match.analysis.recommendations.reduce(
    (result, recommendation) => {
      const category = recommendation.category || 'other'
      result[category] = [...(result[category] || []), recommendation]
      return result
    },
    {} as Record<string, typeof match.analysis.recommendations>,
  )
  const categories = Object.keys(grouped)
  const primaryRecommendations = match.analysis.recommendations.filter(
    item => item.primary && !item.noBet
  )
  const recommended = primaryRecommendations.length
    ? primaryRecommendations
    : match.analysis.recommendations.filter(item => !item.noBet).slice(0, 1)
  const best = recommended[0]
  const [selectedCategory, setSelectedCategory] = useState(
    best?.category || categories[0] || 'other'
  )
  const visible = grouped[selectedCategory] || grouped[categories[0]] || []

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <Card style={{ padding: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
          <BookOpen size={15} color="#4f8ef7" />
          <span style={{ fontWeight: 600, fontSize: '14px', color: '#eef0f9' }}>Resumo da Partida</span>
        </div>
        <p style={{ fontSize: '13px', lineHeight: 1.6, color: '#7a88b0', margin: 0 }}>{match.analysis.summary}</p>
      </Card>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
        {(['home', 'away'] as const).map(side => {
          const team = side === 'home' ? match.homeTeam : match.awayTeam
          const form = side === 'home' ? match.analysis.homeForm : match.analysis.awayForm
          const recent = (side === 'home' ? match.analysis.homeRecent : match.analysis.awayRecent) || []
          const expanded = expandedForm === side
          return (
            <Card key={side} style={{ padding: 0, overflow: 'hidden' }}>
              <button
                type="button"
                onClick={() => setExpandedForm(expanded ? null : side)}
                aria-expanded={expanded}
                style={{ width: '100%', padding: '14px', border: 0, background: 'transparent', cursor: recent.length ? 'pointer' : 'default', textAlign: 'left' }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
                  <span>{team.logo}</span>
                  <span style={{ fontSize: '12px', fontWeight: 600, color: '#7a88b0' }}>{team.shortName} — Forma recente</span>
                  {recent.length > 0 && <span style={{ marginLeft: 'auto', color: '#5a6480', fontSize: 11 }}>{expanded ? 'Ocultar' : 'Ver jogos'}</span>}
                </div>
                <div style={{ display: 'flex', gap: '4px' }}>
                  {form.length ? form.map((r, i) => <FormBadge key={i} result={r} />) : <span style={{ color: '#5a6480', fontSize: 12 }}>Histórico insuficiente</span>}
                </div>
              </button>
              {expanded && recent.length > 0 && (
                <div style={{ borderTop: '1px solid #444a52' }}>
                  {recent.map(game => (
                    <a key={game.id} href={`/matches/${game.id}?tab=stats`}
                      style={{ display: 'block', padding: '10px 14px', borderBottom: '1px solid #2b2f35', color: 'inherit', textDecoration: 'none' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 12 }}>
                        <FormBadge result={game.result || 'E'} />
                        <span style={{ flex: 1, color: '#7a88b0' }}>{game.homeTeam} <strong style={{ color: '#eef0f9' }}>{game.homeScore}–{game.awayScore}</strong> {game.awayTeam}</span>
                        <span style={{ color: game.statisticsAvailable ? '#4f8ef7' : '#5a6480', fontSize: 10 }}>{game.statisticsAvailable ? 'Ver estatísticas' : 'Ver partida'}</span>
                      </div>
                      <div style={{ marginTop: 4, paddingLeft: 28, fontSize: 10, color: '#5a6480' }}>{game.date} · {game.competition}</div>
                    </a>
                  ))}
                </div>
              )}
            </Card>
          )
        })}
      </div>

      <Card style={{ padding: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
          <AlertTriangle size={15} color="#ff7c3a" />
          <span style={{ fontWeight: 600, fontSize: '14px', color: '#eef0f9' }}>Fatores-Chave</span>
        </div>
        {match.analysis.keyFactors.length === 0 && (
          <div style={{ fontSize: 13, color: '#5a6480' }}>Ainda não há amostra estatística suficiente para destacar fatores-chave.</div>
        )}
        {match.analysis.keyFactors.map((f, i) => (
          <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', marginBottom: '8px', fontSize: '13px', color: '#7a88b0' }}>
            <span style={{ width: '5px', height: '5px', borderRadius: '50%', background: '#4f8ef7', flexShrink: 0, marginTop: '6px' }} />
            {f}
          </div>
        ))}
      </Card>

      {match.analysis.recommendations.length > 0 && (
        <div>
          <SectionLabel>Análise dos Mercados</SectionLabel>
          {recommended.map((item, index) => (
            <Card key={`${item.market}:${item.tip}`} style={{ padding: '16px', marginBottom: 12, borderColor: '#00e887', background: 'rgba(0,232,135,.04)' }}>
              <div style={{ fontSize: 10, color: '#00e887', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '.12em', marginBottom: 7 }}>
                {index === 0
                  ? 'Melhor aposta indicada pelo modelo'
                  : `Recomendação adicional do modelo ${index + 1}`}
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'center' }}>
                <div>
                      <div style={{ color: '#eef0f9', fontWeight: 700 }}>{item.tip}</div>
                      <div style={{ color: '#7a88b0', fontSize: 12 }}>{item.market} · {categoryLabels[item.category || 'other'] || item.category}</div>
                      <div style={{ color: '#4f8ef7', fontSize: 11, marginTop: 4 }}>
                        Probabilidade calibrada: {((item.calibratedProbability ?? item.probability ?? 0) * 100).toFixed(1)}%
                      </div>
                      <div style={{ color: '#7a88b0', fontSize: 10, marginTop: 3 }}>
                        {item.recommendationTier === 'high_confidence' ? 'Alta confiança' : item.recommendationTier === 'statistical_value' ? 'Valor estatístico' : 'Experimental'}
                        {item.probabilityInterval ? ` · intervalo ${(item.probabilityInterval.low * 100).toFixed(0)}%–${(item.probabilityInterval.high * 100).toFixed(0)}%` : ''}
                        {item.fractionalKelly != null ? ` · exposição ${(item.fractionalKelly * 100).toFixed(2)}%` : ''}
                      </div>
                      <div style={{ color: '#7a88b0', fontSize: 11, marginTop: 4 }}>{item.reasoning}</div>
                </div>
                <button onClick={() => onAddBet(item.market, item.tip, item.odds)}
                  aria-label={`Adicionar ${item.market}: ${item.tip} ao bilhete`}
                  style={{ flexShrink: 0, padding: '9px 12px', borderRadius: 8, border: '1px solid #00e887', background: 'rgba(0,232,135,.1)', color: '#00e887', fontWeight: 700, cursor: 'pointer' }}>
                  {item.odds.toFixed(2)}
                </button>
              </div>
            </Card>
          ))}
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 7, marginBottom: 12 }}>
            {categories.map(category => (
              <button key={category} onClick={() => setSelectedCategory(category)}
                style={{ padding: '8px 11px', borderRadius: 8, border: `1px solid ${selectedCategory === category ? '#00e887' : '#444a52'}`, background: selectedCategory === category ? 'rgba(0,232,135,.1)' : '#22252a', color: selectedCategory === category ? '#00e887' : '#7a88b0', cursor: 'pointer', fontSize: 12, fontWeight: 600 }}>
                {categoryLabels[category] || category} ({grouped[category].length})
              </button>
            ))}
          </div>
          {visible.map((rec, i) => {
            const [bg, color] = confStyle[rec.confidence]
            return (
              <Card key={i} style={{ padding: '16px', marginBottom: '10px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', gap: '12px', marginBottom: '8px' }}>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: '14px', color: '#eef0f9' }}>{rec.tip}</div>
                    <div style={{ fontSize: '12px', color: '#5a6480' }}>{rec.market}</div>
                    {rec.noBet && (
                      <div style={{ fontSize: '11px', color: '#fbbf24', marginTop: 4 }}>
                        Aposta não recomendada pelo modelo
                      </div>
                    )}
                    <div style={{ fontSize: '11px', color: '#4f8ef7', marginTop: 4 }}>
                      Probabilidade calibrada: {((rec.calibratedProbability ?? rec.probability ?? 0) * 100).toFixed(1)}%
                    </div>
                    <div style={{ fontSize: '10px', color: '#7a88b0', marginTop: 3 }}>
                      {rec.recommendationTier === 'high_confidence' ? 'Alta confiança' : rec.recommendationTier === 'statistical_value' ? 'Valor estatístico' : 'Experimental'}
                      {rec.probabilityInterval ? ` · intervalo ${(rec.probabilityInterval.low * 100).toFixed(0)}%–${(rec.probabilityInterval.high * 100).toFixed(0)}%` : ''}
                    </div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexShrink: 0 }}>
                    <span style={{ fontSize: '11px', padding: '2px 8px', borderRadius: '4px', background: bg, color, fontWeight: 600 }}>{rec.confidence}</span>
                    <div style={{ textAlign: 'right' }}>
                      <span style={{ display: 'block', fontFamily: "'JetBrains Mono', monospace", fontWeight: 700, fontSize: '18px', color: '#00e887' }}>{rec.odds.toFixed(2)}</span>
                      <span style={{ display: 'block', fontSize: 9, color: rec.marketOddsAvailable ? '#7a88b0' : '#fbbf24', textTransform: 'uppercase' }}>
                        {rec.marketOddsAvailable ? 'Odd de mercado' : 'Odd justa do modelo'}
                      </span>
                    </div>
                  </div>
                </div>
                <p style={{ fontSize: '12px', color: '#7a88b0', marginBottom: '12px' }}>{rec.reasoning}</p>
                <button onClick={() => onAddBet(rec.market, rec.tip, rec.odds)}
                  style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(0,232,135,0.08)', border: '1px solid #00e887', color: '#00e887', fontSize: '12px', fontWeight: 600, cursor: 'pointer', transition: 'all 0.15s' }}
                  onMouseEnter={e => { e.currentTarget.style.background = 'rgba(0,232,135,0.16)' }}
                  onMouseLeave={e => { e.currentTarget.style.background = 'rgba(0,232,135,0.08)' }}
                >
                  + Adicionar ao Bilhete ({rec.marketOddsAvailable ? '' : 'odd justa '}{rec.odds.toFixed(2)})
                </button>
              </Card>
            )
          })}
        </div>
      )}
    </div>
  )
}

function H2HTab({ match }: { match: Match }) {
  const wins = match.h2h.filter(h => (h.homeTeam === match.homeTeam.name && h.homeScore > h.awayScore) || (h.awayTeam === match.homeTeam.name && h.awayScore > h.homeScore)).length
  const draws = match.h2h.filter(h => h.homeScore === h.awayScore).length
  const losses = match.h2h.length - wins - draws

  return (
    <div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '10px', marginBottom: '16px' }}>
        {[{ label: match.homeTeam.shortName, value: wins, color: '#4f8ef7' }, { label: 'Empates', value: draws, color: '#fbbf24' }, { label: match.awayTeam.shortName, value: losses, color: '#ff7c3a' }].map(s => (
          <Card key={s.label} style={{ padding: '16px', textAlign: 'center' }}>
            <div style={{ fontFamily: "'Russo One', sans-serif", fontSize: '32px', color: s.color, marginBottom: '4px' }}>{s.value}</div>
            <div style={{ fontSize: '11px', color: '#5a6480' }}>{s.label}</div>
          </Card>
        ))}
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {match.h2h.map((h, i) => {
          const homeDiff = h.homeScore - h.awayScore
          return (
            <Card key={i} style={{ padding: '12px 16px' }}>
              <a href={h.id ? `/matches/${h.id}?tab=stats` : undefined}
                style={{ color: 'inherit', textDecoration: 'none', display: 'block', cursor: h.id ? 'pointer' : 'default' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{ flex: 1, textAlign: 'right' }}>
                  <span style={{ fontWeight: 600, fontSize: '13px', color: homeDiff > 0 ? '#00c853' : '#eef0f9' }}>{h.homeTeam}</span>
                </div>
                <div style={{ fontFamily: "'JetBrains Mono', monospace", fontWeight: 700, fontSize: '14px', padding: '4px 12px', borderRadius: '6px', background: '#444a52', color: '#eef0f9', flexShrink: 0 }}>
                  {h.homeScore} — {h.awayScore}
                </div>
                <div style={{ flex: 1 }}>
                  <span style={{ fontWeight: 600, fontSize: '13px', color: homeDiff < 0 ? '#00c853' : '#eef0f9' }}>{h.awayTeam}</span>
                </div>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '6px' }}>
                <span style={{ fontSize: '11px', color: '#5a6480' }}>{h.date}</span>
                <span style={{ fontSize: '11px', color: '#5a6480' }}>{h.competition}{h.id ? ' · Ver estatísticas' : ''}</span>
              </div>
              </a>
            </Card>
          )
        })}
      </div>
    </div>
  )
}

export function BetSlipDrawer({ selections, onRemove, onOddsChange, onClose, totalOdds, onPlace }: {
  selections: BetSelection[]; onRemove: (id: string) => void
  onOddsChange: (id: string, odds: number) => void
  onClose: () => void; totalOdds: number; onPlace: (stake: number) => void
}) {
  const [stake, setStake] = useState('50')
  const [oddDrafts, setOddDrafts] = useState<Record<string, string>>({})
  useEffect(() => {
    setOddDrafts(current => Object.fromEntries(
      selections.map(item => [
        item.id,
        current[item.id] ?? item.odds.toFixed(2),
      ])
    ))
  }, [selections])
  const commitOdd = (selection: BetSelection) => {
    const parsed = Number(oddDrafts[selection.id])
    if (Number.isFinite(parsed) && parsed > 1 && parsed <= 1000) {
      onOddsChange(selection.id, parsed)
      setOddDrafts(current => ({
        ...current,
        [selection.id]: parsed.toFixed(2),
      }))
      return
    }
    setOddDrafts(current => ({
      ...current,
      [selection.id]: selection.odds.toFixed(2),
    }))
  }
  const stakeNum = parseFloat(stake) || 0
  const potential = (stakeNum * totalOdds).toFixed(2)
  const profit = (parseFloat(potential) - stakeNum).toFixed(2)
  const risk = totalOdds > 15 ? 'Alto' : totalOdds > 5 ? 'Médio' : 'Baixo'
  const riskColor = risk === 'Alto' ? '#ff1744' : risk === 'Médio' ? '#fbbf24' : '#00c853'
  const riskPct = risk === 'Alto' ? 90 : risk === 'Médio' ? 55 : 25

  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 50, display: 'flex', justifyContent: 'flex-end' }}>
      <div onClick={onClose} style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.65)' }} />
      <div className="animate-slide-right" style={{ position: 'relative', width: '100%', maxWidth: '380px', background: '#22252a', borderLeft: '1px solid #444a52', display: 'flex', flexDirection: 'column', maxHeight: '100vh' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '16px 20px', borderBottom: '1px solid #444a52' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Target size={18} color="#00e887" />
            <span style={{ fontWeight: 600, fontSize: '15px', color: '#eef0f9' }}>Bilhete de Apostas</span>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: '#5a6480', cursor: 'pointer' }}>
            <X size={20} />
          </button>
        </div>

        <div style={{ flex: 1, overflowY: 'auto', padding: '16px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {selections.length === 0 ? (
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '48px 0', color: '#5a6480', textAlign: 'center' }}>
              <Target size={40} color="#59616b" style={{ marginBottom: '12px' }} />
              <p style={{ fontSize: '13px', margin: 0 }}>Nenhuma seleção</p>
              <p style={{ fontSize: '12px', marginTop: '4px', color: '#59616b' }}>Clique em uma odd para adicionar</p>
            </div>
          ) : selections.map(sel => (
            <div key={sel.id} style={{ background: '#2b2f35', border: '1px solid #444a52', borderRadius: '10px', padding: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: '11px', color: '#5a6480', marginBottom: '2px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{sel.matchName}</div>
                  <div style={{ fontSize: '12px', color: '#7a88b0' }}>{sel.market}</div>
                  <div style={{ fontWeight: 600, fontSize: '14px', color: '#eef0f9', marginTop: '2px' }}>{sel.option}</div>
                  {!sel.marketId && (
                    <div style={{ fontSize: '10px', color: '#fbbf24', marginTop: '5px' }}>
                      Mercado sem vínculo local: {sel.market}. Será registrado manualmente.
                    </div>
                  )}
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '6px' }}>
                  <label style={{ fontSize: '10px', color: '#5a6480' }}>Odd do bilhete</label>
                  <input
                    aria-label={`Odd manual para ${sel.option}`}
                    type="number" min="1.01" max="1000" step="0.01"
                    value={oddDrafts[sel.id] ?? sel.odds.toFixed(2)}
                    onChange={event => setOddDrafts(current => ({
                      ...current,
                      [sel.id]: event.target.value,
                    }))}
                    onBlur={() => commitOdd(sel)}
                    onKeyDown={event => {
                      if (event.key === 'Enter') event.currentTarget.blur()
                    }}
                    style={{ width: '82px', background: '#22252a', border: '1px solid #59616b', borderRadius: '6px', padding: '6px 8px', textAlign: 'right', fontFamily: "'JetBrains Mono', monospace", fontWeight: 700, fontSize: '16px', color: '#00e887', outline: 'none' }}
                    onFocus={event => event.currentTarget.select()}
                  />
                  <span style={{ fontSize: '10px', color: '#5a6480' }}>
                    Referência: {(sel.sourceOdds ?? sel.odds).toFixed(2)}
                  </span>
                  <button onClick={() => onRemove(sel.id)} style={{ background: 'none', border: 'none', color: '#5a6480', cursor: 'pointer' }}>
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {selections.length > 0 && (
          <div style={{ borderTop: '1px solid #444a52', padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '13px', color: '#7a88b0' }}>Odds combinadas</span>
              <span style={{ fontFamily: "'JetBrains Mono', monospace", fontWeight: 700, fontSize: '22px', color: '#00e887' }}>{totalOdds.toFixed(2)}x</span>
            </div>

            <div>
              <label style={{ fontSize: '12px', color: '#5a6480', display: 'block', marginBottom: '8px' }}>Valor da aposta (R$)</label>
              <input type="number" value={stake} onChange={e => setStake(e.target.value)}
                style={{ width: '100%', background: '#2b2f35', border: '1px solid #444a52', borderRadius: '8px', padding: '10px 12px', fontSize: '14px', fontFamily: "'JetBrains Mono', monospace", fontWeight: 700, color: '#eef0f9', outline: 'none', boxSizing: 'border-box' }}
                onFocus={e => e.target.style.borderColor = '#00e887'} onBlur={e => e.target.style.borderColor = '#444a52'}
              />
              <div style={{ display: 'flex', gap: '6px', marginTop: '8px' }}>
                {[10, 25, 50, 100].map(q => (
                  <button key={q} onClick={() => setStake(String(q))}
                    style={{ flex: 1, padding: '6px', borderRadius: '6px', background: '#2b2f35', border: '1px solid #444a52', color: '#7a88b0', fontSize: '12px', cursor: 'pointer' }}
                    onMouseEnter={e => e.currentTarget.style.borderColor = '#00e887'}
                    onMouseLeave={e => e.currentTarget.style.borderColor = '#444a52'}
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>

            <div style={{ background: '#2b2f35', borderRadius: '8px', padding: '12px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                <span style={{ fontSize: '12px', color: '#5a6480' }}>Retorno potencial</span>
                <span style={{ fontFamily: "'JetBrains Mono', monospace", fontWeight: 700, fontSize: '16px', color: '#00e887' }}>R$ {potential}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '12px', color: '#5a6480' }}>Lucro estimado</span>
                <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '13px', color: '#7a88b0' }}>R$ {profit}</span>
              </div>
            </div>

            <div style={{ background: '#2b2f35', border: '1px solid #444a52', borderRadius: '8px', padding: '12px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span style={{ fontSize: '12px', color: '#5a6480' }}>Análise de Risco</span>
                <span style={{ fontSize: '12px', fontWeight: 600, color: riskColor }}>{risk}</span>
              </div>
              <div style={{ height: '4px', borderRadius: '2px', background: '#444a52', marginBottom: '8px' }}>
                <div style={{ width: `${riskPct}%`, height: '100%', background: riskColor, borderRadius: '2px', transition: 'all 0.3s' }} />
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: '#5a6480' }}>
                <span>Prob. implícita: {((1 / totalOdds) * 100).toFixed(1)}%</span>
                <span>{selections.length} sel.</span>
              </div>
            </div>

            <button onClick={() => { if (stakeNum > 0) onPlace(stakeNum) }}
              disabled={stakeNum <= 0}
              style={{ width: '100%', padding: '14px', borderRadius: '10px', background: '#00e887', color: '#17191c', fontWeight: 700, fontSize: '14px', border: 'none', cursor: stakeNum > 0 ? 'pointer' : 'not-allowed', opacity: stakeNum > 0 ? 1 : 0.5, transition: 'all 0.15s' }}
              onMouseEnter={e => { if (stakeNum > 0) e.currentTarget.style.transform = 'scale(1.02)' }}
              onMouseLeave={e => e.currentTarget.style.transform = 'scale(1)'}
            >
              Confirmar Aposta — R$ {stakeNum.toFixed(2)}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export function BankrollView({ bets, setBets, bankroll, bankrollId, onBankrollCreated, onError, onBalanceChanged, pending }: {
  bets: PlacedBet[]; setBets: (b: PlacedBet[]) => void; bankroll: number
  bankrollId: number | null; onBankrollCreated: (item: any) => void; onError: (message: string) => void
  onBalanceChanged: (balance: number) => void
  wonTotal: number; lostTotal: number; pending: number
}) {
  const [creating, setCreating] = useState(false)
  const [name, setName] = useState('Banca Principal')
  const [initialBalance, setInitialBalance] = useState('1000')
  const [unitPercentage, setUnitPercentage] = useState('1')
  const [movement, setMovement] = useState<'deposit' | 'withdraw' | null>(null)
  const [movementAmount, setMovementAmount] = useState('')
  const [period, setPeriod] = useState<'week' | 'month' | 'year' | 'all'>('month')
  const periodStart = (() => {
    const date = new Date()
    if (period === 'week') date.setDate(date.getDate() - 7)
    if (period === 'month') date.setMonth(date.getMonth() - 1)
    if (period === 'year') date.setFullYear(date.getFullYear() - 1)
    return period === 'all' ? null : date
  })()
  const periodBets = bets.filter(item => {
    if (!periodStart) return true
    const [day, month, year] = item.date.split('/').map(Number)
    return new Date(year, month - 1, day) >= periodStart
  })
  const periodWon = periodBets.filter(b => b.status === 'won').reduce((a, b) => a + b.potentialReturn - b.stake, 0)
  const periodLost = periodBets.filter(b => b.status === 'lost').reduce((a, b) => a + b.stake, 0)
  const netPL = periodWon - periodLost

  const settle = async (
    slipId: string, legId: string, result: 'won' | 'lost' | 'void'
  ) => {
    try {
      await settleBetLeg(slipId, legId, result)
      setBets(await loadBetSlips())
      const active = (await loadBankrolls()).find(item => item.active)
      if (active) onBalanceChanged(active.balance)
    } catch (error: any) {
      onError(error.message)
    }
  }

  const stCfg: Record<string, { label: string; bg: string; color: string; icon: React.ReactNode }> = {
    pending: { label: 'Pendente', bg: 'rgba(251,191,36,0.15)', color: '#fbbf24', icon: <Clock size={13} /> },
    won: { label: 'Ganhou', bg: 'rgba(0,200,83,0.15)', color: '#00c853', icon: <CheckCircle2 size={13} /> },
    lost: { label: 'Perdeu', bg: 'rgba(255,23,68,0.15)', color: '#ff1744', icon: <XCircle size={13} /> },
    void: { label: 'Anulada', bg: 'rgba(122,136,176,0.15)', color: '#7a88b0', icon: <Circle size={13} /> },
    partial: { label: 'Parcial', bg: 'rgba(79,142,247,0.15)', color: '#4f8ef7', icon: <AlertTriangle size={13} /> },
    canceled: { label: 'Cancelada', bg: 'rgba(122,136,176,0.15)', color: '#7a88b0', icon: <XCircle size={13} /> },
  }
  const unknownStatus = {
    label: 'Status desconhecido',
    bg: 'rgba(122,136,176,0.15)',
    color: '#7a88b0',
    icon: <AlertTriangle size={13} />,
  }

  return (
    <div className="animate-fade-in">
      <div style={{ padding: '24px 0 16px' }}>
        <h1 style={{ fontFamily: "'Russo One', sans-serif", fontSize: '24px', color: '#eef0f9', letterSpacing: '0.05em', margin: 0 }}>GESTÃO DE BANCA</h1>
        <p style={{ fontSize: '13px', color: '#5a6480', marginTop: '4px' }}>Acompanhe suas apostas e performance</p>
      </div>

      {bankrollId && (
        <Card style={{ padding: '14px', marginBottom: '16px', display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}>
          <button onClick={() => setMovement('deposit')} style={{ padding: '10px 16px', borderRadius: 8, background: '#00e887', color: '#17191c', border: 0, fontWeight: 700, cursor: 'pointer' }}>
            + Depósito
          </button>
          <button onClick={() => setMovement('withdraw')} style={{ padding: '10px 16px', borderRadius: 8, background: '#444a52', color: '#eef0f9', border: '1px solid #59616b', fontWeight: 700, cursor: 'pointer' }}>
            − Saque
          </button>
          {movement && <>
            <input autoFocus type="number" min="0.01" step="0.01" placeholder="Valor em R$" value={movementAmount} onChange={event => setMovementAmount(event.target.value)}
              style={{ width: 150, background: '#2b2f35', border: '1px solid #59616b', borderRadius: 7, padding: 10, color: '#eef0f9' }} />
            <button onClick={async () => {
              const amount = Number(movementAmount)
              if (!amount || amount <= 0) return onError('Informe um valor maior que zero.')
              try {
                const transaction = movement === 'deposit'
                  ? await depositBankroll(bankrollId, amount)
                  : await withdrawBankroll(bankrollId, amount)
                onBalanceChanged(transaction.balance_after)
                setMovement(null)
                setMovementAmount('')
              } catch (error: any) {
                onError(error.message)
              }
            }} style={{ padding: '10px 14px', borderRadius: 7, background: '#4f8ef7', color: '#fff', border: 0, fontWeight: 700, cursor: 'pointer' }}>
              Confirmar {movement === 'deposit' ? 'depósito' : 'saque'}
            </button>
            <button onClick={() => { setMovement(null); setMovementAmount('') }} style={{ background: 'none', border: 0, color: '#7a88b0', cursor: 'pointer' }}>Cancelar</button>
          </>}
        </Card>
      )}

      <div style={{ display: 'flex', gap: 6, marginBottom: 12 }}>
        {([
          ['week', 'Semanal'], ['month', 'Mensal'], ['year', 'Anual'], ['all', 'Todo período'],
        ] as const).map(([value, label]) => (
          <button key={value} onClick={() => setPeriod(value)}
            style={{ padding: '7px 12px', borderRadius: 7, border: '1px solid #444a52', background: period === value ? '#444a52' : 'transparent', color: period === value ? '#00e887' : '#7a88b0', cursor: 'pointer', fontSize: 12 }}>
            {label}
          </button>
        ))}
      </div>

      {!bankrollId && (
        <Card style={{ padding: '20px', marginBottom: '20px', borderColor: '#00e887' }}>
          <div style={{ fontSize: '16px', color: '#eef0f9', fontWeight: 700, marginBottom: '6px' }}>
            Crie sua primeira banca
          </div>
          <p style={{ fontSize: '12px', color: '#7a88b0', margin: '0 0 16px' }}>
            A banca é necessária para controlar saldo, exposição, unidades e registrar bilhetes reais.
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '10px' }}>
            <label style={{ fontSize: '11px', color: '#7a88b0' }}>
              Nome
              <input value={name} onChange={event => setName(event.target.value)}
                style={{ width: '100%', boxSizing: 'border-box', marginTop: 6, background: '#2b2f35', border: '1px solid #444a52', borderRadius: 7, padding: 10, color: '#eef0f9' }} />
            </label>
            <label style={{ fontSize: '11px', color: '#7a88b0' }}>
              Saldo inicial (R$)
              <input type="number" min="0.01" step="0.01" value={initialBalance} onChange={event => setInitialBalance(event.target.value)}
                style={{ width: '100%', boxSizing: 'border-box', marginTop: 6, background: '#2b2f35', border: '1px solid #444a52', borderRadius: 7, padding: 10, color: '#eef0f9' }} />
            </label>
            <label style={{ fontSize: '11px', color: '#7a88b0' }}>
              Valor da unidade (%)
              <input type="number" min="0.1" max="100" step="0.1" value={unitPercentage} onChange={event => setUnitPercentage(event.target.value)}
                style={{ width: '100%', boxSizing: 'border-box', marginTop: 6, background: '#2b2f35', border: '1px solid #444a52', borderRadius: 7, padding: 10, color: '#eef0f9' }} />
            </label>
          </div>
          <button disabled={creating} onClick={async () => {
            setCreating(true)
            try {
              const item = await createBankroll({
                name: name.trim(),
                initial_balance: Number(initialBalance),
                currency: 'BRL',
                unit_percentage: Number(unitPercentage),
              })
              onBankrollCreated(item)
            } catch (error: any) {
              onError(error.message)
            } finally {
              setCreating(false)
            }
          }} style={{ marginTop: 14, padding: '11px 18px', borderRadius: 8, background: '#00e887', color: '#17191c', border: 0, fontWeight: 700, cursor: creating ? 'wait' : 'pointer' }}>
            {creating ? 'Criando…' : 'Criar e ativar banca'}
          </button>
        </Card>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '10px', marginBottom: '20px' }}>
        {[
          { label: 'Banca Total', value: `R$ ${bankroll.toFixed(2)}`, color: '#eef0f9' },
          { label: 'Lucro / Prejuízo', value: `${netPL >= 0 ? '+' : ''}R$ ${netPL.toFixed(2)}`, color: netPL >= 0 ? '#00c853' : '#ff1744' },
          { label: 'Ganhos', value: `R$ ${periodWon.toFixed(2)}`, color: '#00c853' },
          { label: 'Perdas', value: `R$ ${periodLost.toFixed(2)}`, color: '#ff1744' },
        ].map((c, i) => (
          <Card key={i} style={{ padding: '16px' }}>
            <div style={{ fontSize: '11px', color: '#5a6480', marginBottom: '8px' }}>{c.label}</div>
            <span style={{ fontFamily: "'JetBrains Mono', monospace", fontWeight: 700, fontSize: '18px', color: c.color }}>{c.value}</span>
          </Card>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px', marginBottom: '24px' }}>
        {[{ label: 'Total de Apostas', value: bets.length }, { label: 'Pendentes', value: pending }, { label: 'Liquidadas', value: bets.filter(b => b.status !== 'pending').length }].map((s, i) => (
          <Card key={i} style={{ padding: '14px', textAlign: 'center' }}>
            <div style={{ fontFamily: "'Russo One', sans-serif", fontSize: '32px', color: '#eef0f9', marginBottom: '4px' }}>{s.value}</div>
            <div style={{ fontSize: '11px', color: '#5a6480' }}>{s.label}</div>
          </Card>
        ))}
      </div>

      <SectionLabel>Histórico de Apostas</SectionLabel>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {bets.map(bet => {
          const cfg = stCfg[bet.status] ?? unknownStatus
          return (
            <Card key={bet.id} style={{ overflow: 'hidden' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 16px', borderBottom: '1px solid #444a52' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ color: cfg.color }}>{cfg.icon}</span>
                  <span style={{ fontSize: '11px', padding: '2px 8px', borderRadius: '4px', background: cfg.bg, color: cfg.color, fontWeight: 600 }}>{cfg.label}</span>
                  <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '12px', color: '#5a6480' }}>{bet.date}</span>
                  <span style={{ fontFamily: "'JetBrains Mono', monospace", fontWeight: 700, fontSize: '13px', color: '#eef0f9' }}>{bet.totalOdds.toFixed(2)}x</span>
                </div>
              </div>
              <div style={{ padding: '12px 16px' }}>
                {bet.selections.map(sel => (
                  <div key={sel.id} style={{ display: 'flex', justifyContent: 'space-between', gap: 12, padding: '8px 0', borderBottom: '1px solid #444a52', fontSize: '12px' }}>
                    <div style={{ color: '#5a6480' }}>
                      <span>{sel.matchName}</span>
                      <span style={{ margin: '0 6px', color: '#59616b' }}>·</span>
                      <span style={{ color: '#7a88b0' }}>{sel.market}</span>
                      <span style={{ margin: '0 6px', color: '#59616b' }}>·</span>
                      <span style={{ color: '#eef0f9', fontWeight: 600 }}>{sel.option}</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexShrink: 0 }}>
                      <span style={{ fontFamily: "'JetBrains Mono', monospace", fontWeight: 700, color: '#00e887' }}>{sel.odds.toFixed(2)}</span>
                      {sel.status === 'pending' && <>
                        <button title="Liquidar como ganha" onClick={() => settle(bet.id, sel.id, 'won')} style={{ fontSize: 10, padding: '4px 7px', borderRadius: 5, background: 'rgba(0,200,83,.15)', color: '#00c853', border: 0, cursor: 'pointer' }}>Ganhou</button>
                        <button title="Liquidar como perdida" onClick={() => settle(bet.id, sel.id, 'lost')} style={{ fontSize: 10, padding: '4px 7px', borderRadius: 5, background: 'rgba(255,23,68,.15)', color: '#ff1744', border: 0, cursor: 'pointer' }}>Perdeu</button>
                        <button title="Anular seleção" onClick={() => settle(bet.id, sel.id, 'void')} style={{ fontSize: 10, padding: '4px 7px', borderRadius: 5, background: 'rgba(122,136,176,.15)', color: '#7a88b0', border: 0, cursor: 'pointer' }}>Anular</button>
                      </>}
                    </div>
                  </div>
                ))}
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '10px', fontSize: '12px' }}>
                  <span style={{ color: '#5a6480' }}>Apostado: <span style={{ fontFamily: "'JetBrains Mono', monospace", fontWeight: 700, color: '#eef0f9' }}>R$ {bet.stake.toFixed(2)}</span></span>
                  <span style={{ color: '#5a6480' }}>Retorno: <span style={{ fontFamily: "'JetBrains Mono', monospace", fontWeight: 700, color: bet.status === 'won' ? '#00c853' : bet.status === 'lost' ? '#ff1744' : '#eef0f9' }}>R$ {bet.potentialReturn.toFixed(2)}</span></span>
                </div>
              </div>
            </Card>
          )
        })}
      </div>
    </div>
  )
}

export function BetsView({ bets, setBets, onError, onSettled }: {
  bets: PlacedBet[]
  setBets: (bets: PlacedBet[]) => void
  onError: (message: string) => void
  onSettled: () => void
}) {
  const [status, setStatus] = useState<'all' | PlacedBet['status']>('all')
  const visible = status === 'all' ? bets : bets.filter(item => item.status === status)
  const settle = async (slipId: string, legId: string, result: 'won' | 'lost' | 'void') => {
    try {
      await settleBetLeg(slipId, legId, result)
      setBets(await loadBetSlips())
      onSettled()
    } catch (error: any) {
      onError(error.message)
    }
  }
  const labels: Record<PlacedBet['status'], { label: string; color: string }> = {
    pending: { label: 'Pendente', color: '#fbbf24' },
    won: { label: 'Ganhou', color: '#00c853' },
    lost: { label: 'Perdeu', color: '#ff1744' },
    void: { label: 'Anulada', color: '#7a88b0' },
    partial: { label: 'Parcial', color: '#4f8ef7' },
    canceled: { label: 'Cancelada', color: '#7a88b0' },
  }
  const cancel = async (slipId: string) => {
    if (!window.confirm('Cancelar esta aposta e devolver o valor apostado à banca?')) return
    try {
      await cancelBetSlip(slipId)
      setBets(await loadBetSlips())
      onSettled()
    } catch (error: any) {
      onError(error.message)
    }
  }
  return (
    <div className="animate-fade-in">
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 7, marginBottom: 16 }}>
        {([
          ['all', 'Todas'], ['pending', 'Pendentes'], ['won', 'Ganhas'],
          ['lost', 'Perdidas'], ['void', 'Anuladas'], ['partial', 'Parciais'],
          ['canceled', 'Canceladas'],
        ] as const).map(([value, label]) => (
          <button key={value} onClick={() => setStatus(value)}
            style={{ padding: '8px 12px', borderRadius: 7, border: `1px solid ${status === value ? '#00e887' : '#444a52'}`, background: status === value ? 'rgba(0,232,135,.1)' : '#22252a', color: status === value ? '#00e887' : '#7a88b0', cursor: 'pointer' }}>
            {label} ({value === 'all' ? bets.length : bets.filter(item => item.status === value).length})
          </button>
        ))}
      </div>
      {visible.length === 0 && (
        <Card style={{ padding: 40, textAlign: 'center', color: '#7a88b0' }}>
          Nenhuma aposta encontrada nesta categoria.
        </Card>
      )}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {visible.map(bet => {
          const cfg = labels[bet.status]
          return (
            <Card key={bet.id} style={{ overflow: 'hidden' }}>
              <div style={{ padding: '11px 16px', borderBottom: '1px solid #444a52', display: 'flex', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 9 }}>
                  <span style={{ color: cfg.color, fontWeight: 700 }}>{cfg.label}</span>
                  <span style={{ color: '#5a6480', fontFamily: "'JetBrains Mono', monospace", fontSize: 12 }}>{bet.date}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <strong style={{ color: '#eef0f9', fontFamily: "'JetBrains Mono', monospace" }}>{bet.totalOdds.toFixed(2)}x</strong>
                  {bet.status === 'pending' && (
                    <button className="cancel-bet-button" onClick={() => cancel(bet.id)}>
                      Cancelar aposta
                    </button>
                  )}
                </div>
              </div>
              <div style={{ padding: '8px 16px 14px' }}>
                {bet.selections.map(selection => (
                  <div key={selection.id} style={{ padding: '10px 0', borderBottom: '1px solid #444a52', display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
                    <div style={{ minWidth: 0 }}>
                      <strong style={{ display: 'block', color: '#eef0f9', fontSize: 13 }}>{selection.matchName}</strong>
                      <span style={{ color: '#7a88b0', fontSize: 12 }}>{selection.market} · {selection.option}</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                      <strong style={{ color: '#00e887', fontFamily: "'JetBrains Mono', monospace" }}>{selection.odds.toFixed(2)}</strong>
                      {selection.status === 'pending' && <>
                        <button onClick={() => settle(bet.id, selection.id, 'won')} className="settle-button won">Ganhou</button>
                        <button onClick={() => settle(bet.id, selection.id, 'lost')} className="settle-button lost">Perdeu</button>
                        <button onClick={() => settle(bet.id, selection.id, 'void')} className="settle-button void">Anular</button>
                      </>}
                    </div>
                  </div>
                ))}
                <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, paddingTop: 11, color: '#7a88b0', fontSize: 12 }}>
                  <span>Apostado: <strong style={{ color: '#eef0f9' }}>R$ {bet.stake.toFixed(2)}</strong></span>
                  <span>Retorno potencial: <strong style={{ color: '#eef0f9' }}>R$ {bet.potentialReturn.toFixed(2)}</strong></span>
                </div>
              </div>
            </Card>
          )
        })}
      </div>
    </div>
  )
}

export function FavoritesView({ matches, favorites, onMatchClick, onToggleFavorite }: {
  matches: Match[]; favorites: string[]; onMatchClick: (m: Match) => void; onToggleFavorite: (id: string) => void
}) {
  const favMatches = matches.filter(m => favorites.includes(m.id))
  return (
    <div className="animate-fade-in">
      <div style={{ padding: '24px 0 16px' }}>
        <h1 style={{ fontFamily: "'Russo One', sans-serif", fontSize: '24px', color: '#eef0f9', letterSpacing: '0.05em', margin: 0 }}>FAVORITOS</h1>
        <p style={{ fontSize: '13px', color: '#5a6480', marginTop: '4px' }}>Partidas e times acompanhados</p>
      </div>
      {favMatches.length === 0 ? (
        <Card style={{ padding: '48px', textAlign: 'center' }}>
          <Star size={40} color="#59616b" style={{ margin: '0 auto 12px' }} />
          <p style={{ fontSize: '13px', color: '#5a6480', margin: 0 }}>Nenhum favorito ainda</p>
          <p style={{ fontSize: '12px', marginTop: '4px', color: '#59616b' }}>Clique na estrela em qualquer partida para favoritar</p>
        </Card>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {favMatches.map(m => (
            <MatchCard key={m.id} match={m} onClick={() => onMatchClick(m)} isFavorite={true} onToggleFavorite={() => onToggleFavorite(m.id)} />
          ))}
        </div>
      )}
    </div>
  )
}

export function SystemView({ maturity }: { maturity: any }) {
  if (!maturity) {
    return <Card style={{ marginTop: 24, padding: 32, color: '#7a88b0' }}>
      Carregando diagnóstico operacional...
    </Card>
  }
  const percent = (value: number) => `${(value * 100).toFixed(1)}%`
  const coverages = [
    ['Estatísticas', maturity.coverage.statistics],
    ['Odds', maturity.coverage.odds],
    ['Previsões', maturity.coverage.predictions],
    ['Escalações', maturity.coverage.lineups],
  ]
  const rawCoverages = maturity.raw_coverage ? [
    ['Estatísticas', maturity.raw_coverage.statistics],
    ['Odds', maturity.raw_coverage.odds],
    ['Previsões', maturity.raw_coverage.predictions],
    ['Escalações', maturity.raw_coverage.lineups],
  ] : []
  return (
    <div className="animate-fade-in">
      <div style={{ padding: '24px 0 16px' }}>
        <h1 style={{ fontFamily: "'Russo One', sans-serif", fontSize: 24, color: '#eef0f9', margin: 0 }}>
          SAÚDE DO SISTEMA
        </h1>
        <p style={{ fontSize: 13, color: '#5a6480' }}>
          Cobertura, atualidade e disponibilidade dos motores
        </p>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(190px, 1fr))', gap: 10 }}>
        <Card style={{ padding: 16 }}>
          <div style={{ color: '#5a6480', fontSize: 11 }}>SLA operacional</div>
          <div style={{ color: maturity.quality_score >= .7 ? '#00e887' : '#fbbf24', fontSize: 28, fontWeight: 700 }}>
            {percent(maturity.quality_score)}
          </div>
        </Card>
        {coverages.map(([label, value]: any) => (
          <Card key={label} style={{ padding: 16 }}>
            <div style={{ color: '#5a6480', fontSize: 11 }}>{label}</div>
            <div style={{ color: value >= .7 ? '#00e887' : '#fbbf24', fontSize: 22, fontWeight: 700 }}>
              {percent(value)}
            </div>
          </Card>
        ))}
      </div>
      {rawCoverages.length > 0 && <>
        <SectionLabel>Cobertura bruta (todos os jogos)</SectionLabel>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(190px, 1fr))', gap: 10, marginBottom: 24 }}>
          {rawCoverages.map(([label, value]: any) => (
            <Card key={`raw-${label}`} style={{ padding: 16 }}>
              <div style={{ color: '#5a6480', fontSize: 11 }}>{label}</div>
              <div style={{ color: '#7a88b0', fontSize: 22, fontWeight: 700 }}>
                {percent(value)}
              </div>
            </Card>
          ))}
        </div>
      </>}
      <SectionLabel>Provedores</SectionLabel>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: 8, marginBottom: 24 }}>
        {Object.entries(maturity.providers).map(([name, item]: [string, any]) => (
          <Card key={name} style={{ padding: 12, display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: '#eef0f9', fontSize: 12 }}>{name}</span>
            <span style={{ color: item.available ? '#00e887' : '#ff1744', fontSize: 11 }}>
              {item.available ? `Ativo · ${item.latency_ms ?? '—'} ms` : 'Indisponível'}
            </span>
          </Card>
        ))}
      </div>
      <SectionLabel>Alertas operacionais</SectionLabel>
      {maturity.alerts.length === 0 ? (
        <Card style={{ padding: 16, color: '#00e887' }}>Nenhum alerta ativo.</Card>
      ) : maturity.alerts.map((alert: any) => (
        <Card key={alert.code} style={{ padding: 14, marginBottom: 8, borderColor: alert.severity === 'critical' ? '#ff1744' : '#fbbf24' }}>
          <strong style={{ color: '#eef0f9', fontSize: 12 }}>{alert.code}</strong>
          <div style={{ color: '#7a88b0', fontSize: 12, marginTop: 4 }}>{alert.message}</div>
        </Card>
      ))}
    </div>
  )
}

function SectionLabel({ children }: { children: React.ReactNode }) {
  return <div style={{ fontSize: '11px', fontWeight: 700, color: '#5a6480', letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: '12px' }}>{children}</div>
}

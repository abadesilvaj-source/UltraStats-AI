import { useState, useCallback, useEffect } from 'react'
import { type Match, type BetSelection, type PlacedBet, type OddsMarket, type OddsOption } from './data'
import {
  analyzeBetSlip, createBankroll, depositBankroll, loadBankrolls, loadMatch,
  loadBetSlips, loadMatches, loadMaturity, placeBet, settleBetLeg,
  withdrawBankroll,
} from './api'
import {
  Home, TrendingUp, Star, Wallet, ChevronRight, ChevronLeft,
  Circle, Zap, Activity, BarChart3, Users, BookOpen,
  Trash2, CheckCircle2, XCircle, Clock,
  AlertTriangle, Target, X, Menu, Filter, Grid3X3
} from 'lucide-react'

type View = 'home' | 'match' | 'bankroll' | 'favorites' | 'system'
type MatchTab = 'live' | 'lineup' | 'stats' | 'analysis' | 'markets' | 'h2h'

export default function App() {
  const [matches, setMatches] = useState<Match[]>([])
  const [loadError, setLoadError] = useState('')
  const [view, setView] = useState<View>('home')
  const [selectedMatch, setSelectedMatch] = useState<Match | null>(null)
  const [betSlip, setBetSlip] = useState<BetSelection[]>([])
  const [betSlipOpen, setBetSlipOpen] = useState(false)
  const [placedBets, setPlacedBets] = useState<PlacedBet[]>([])
  const [favorites, setFavorites] = useState<string[]>(['m1', 'm3'])
  const [bankrollAmount, setBankrollAmount] = useState(0)
  const [bankrollId, setBankrollId] = useState<number | null>(null)
  const [navOpen, setNavOpen] = useState(false)
  const [maturity, setMaturity] = useState<any>(null)

  useEffect(() => {
    loadMatches().then(setMatches).catch(error => setLoadError(error.message))
    loadBankrolls().then(items => {
      const active = items.find(item => item.active)
      if (active) {
        setBankrollId(active.id)
        setBankrollAmount(active.balance)
      }
    }).catch(error => setLoadError(error.message))
    loadBetSlips().then(setPlacedBets).catch(error => setLoadError(error.message))
    loadMaturity().then(setMaturity).catch(error => setLoadError(error.message))
    const timer = window.setInterval(
      () => loadMatches().then(setMatches).catch(() => undefined),
      60_000,
    )
    return () => window.clearInterval(timer)
  }, [])

  const openMatch = useCallback((match: Match) => {
    setSelectedMatch(match)
    setView('match')
    loadMatch(match.id).then(setSelectedMatch).catch(error => setLoadError(error.message))
  }, [])

  const addToBetSlip = useCallback((matchId: string, matchName: string, market: string, option: string, odds: number) => {
    setBetSlip(prev => {
      const id = `${matchId}-${market}-${option}`
      if (prev.find(b => b.id === id)) return prev.filter(b => b.id !== id)
      const source = selectedMatch?.id === matchId
        ? selectedMatch
        : matches.find(item => item.id === matchId)
      const marketId = Number(source?.markets.find(item => item.name === market)?.id)
      return [...prev, {
        id, matchId, matchName, market, marketId, option,
        odds, sourceOdds: odds,
      }]
    })
    setBetSlipOpen(true)
  }, [matches, selectedMatch])

  const removeBet = useCallback((id: string) => setBetSlip(prev => prev.filter(b => b.id !== id)), [])
  const updateBetOdds = useCallback((id: string, odds: number) => {
    setBetSlip(prev => prev.map(item => (
      item.id === id ? { ...item, odds } : item
    )))
  }, [])
  const toggleFavorite = useCallback((id: string) => setFavorites(prev => prev.includes(id) ? prev.filter(f => f !== id) : [...prev, id]), [])

  const totalOdds = betSlip.reduce((acc, b) => acc * b.odds, 1)
  const wonTotal = placedBets.filter(b => b.status === 'won').reduce((a, b) => a + b.potentialReturn - b.stake, 0)
  const lostTotal = placedBets.filter(b => b.status === 'lost').reduce((a, b) => a + b.stake, 0)
  const pendingCount = placedBets.filter(b => b.status === 'pending').length

  return (
    <div style={{ minHeight: '100vh', background: '#07080f', fontFamily: "'DM Sans', sans-serif" }}>
      <Nav
        view={view} setView={setView} betCount={betSlip.length}
        onBetSlipOpen={() => setBetSlipOpen(true)} navOpen={navOpen}
        setNavOpen={setNavOpen} clearMatch={() => setSelectedMatch(null)}
      />

      <main style={{ paddingTop: '56px', paddingBottom: '32px', maxWidth: '1200px', margin: '0 auto', padding: '56px 16px 32px' }}>
        {loadError && <div style={{ marginTop: 16, padding: 12, border: '1px solid #ff1744', borderRadius: 8, color: '#ff1744' }}>{loadError}</div>}
        {view === 'home' && <HomeView matches={matches} onMatchClick={openMatch} favorites={favorites} onToggleFavorite={toggleFavorite} />}
        {view === 'match' && selectedMatch && (
          <MatchView match={selectedMatch} betSlip={betSlip} onAddBet={addToBetSlip}
            onBack={() => setView('home')} isFavorite={favorites.includes(selectedMatch.id)}
            onToggleFavorite={() => toggleFavorite(selectedMatch.id)} />
        )}
        {view === 'bankroll' && (
          <BankrollView bets={placedBets} setBets={setPlacedBets} bankroll={bankrollAmount}
            bankrollId={bankrollId}
            onBankrollCreated={(item) => {
              setBankrollId(item.id)
              setBankrollAmount(item.balance)
              setLoadError('')
            }}
            onError={setLoadError}
            onBalanceChanged={(balance) => {
              setBankrollAmount(balance)
              setLoadError('')
            }}
            wonTotal={wonTotal} lostTotal={lostTotal} pending={pendingCount} />
        )}
        {view === 'favorites' && (
          <FavoritesView matches={matches} favorites={favorites} onMatchClick={openMatch} onToggleFavorite={toggleFavorite} />
        )}
        {view === 'system' && <SystemView maturity={maturity} />}
      </main>

      {betSlipOpen && (
        <BetSlipDrawer selections={betSlip} onRemove={removeBet}
          onOddsChange={updateBetOdds} onClose={() => setBetSlipOpen(false)}
          totalOdds={totalOdds}
          onPlace={async (stake) => {
            if (!bankrollId) {
              setLoadError('Crie e ative uma banca antes de confirmar o bilhete.')
              setBetSlipOpen(false)
              setSelectedMatch(null)
              setView('bankroll')
              return
            }
            try {
              const payload = {
                bankroll_id: bankrollId,
                bookmaker: 'Odd informada pelo usuário',
                stake_amount: stake,
                legs: betSlip.map(item => ({
                  match_id: Number(item.matchId),
                  market_id: item.marketId,
                  market_name: item.market,
                  selection: item.option,
                  odd_value: item.odds,
                })),
              }
              const assessment = await analyzeBetSlip(payload)
              const manualMarkets = assessment.unavailable_markets || []
              if (!assessment.approved && manualMarkets.length === 0) {
                setLoadError(
                  `Bilhete bloqueado pelo risco: ${assessment.warnings.join(', ') || 'valor conservador insuficiente'}.`
                )
                return
              }
            await placeBet(payload)
            } catch (error: any) {
              setLoadError(error.message)
              return
            }
            const newBet: PlacedBet = {
              id: `bet-${Date.now()}`,
              selections: betSlip.map(s => ({ ...s, status: 'pending' })),
              stake, potentialReturn: parseFloat((stake * totalOdds).toFixed(2)),
              totalOdds: parseFloat(totalOdds.toFixed(3)),
              date: new Date().toLocaleDateString('pt-BR'), status: 'pending',
            }
            setPlacedBets(prev => [newBet, ...prev])
            setBankrollAmount(value => Math.max(0, value - stake))
            setBetSlip([])
            setBetSlipOpen(false)
          }}
        />
      )}

      {betSlip.length > 0 && !betSlipOpen && (
        <button onClick={() => setBetSlipOpen(true)}
          style={{ position: 'fixed', bottom: '24px', right: '24px', zIndex: 40, display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 20px', borderRadius: '12px', background: '#00e887', color: '#07080f', fontWeight: 700, fontSize: '14px', border: 'none', cursor: 'pointer', boxShadow: '0 8px 32px rgba(0,232,135,0.3)', transition: 'transform 0.15s' }}
          onMouseEnter={e => (e.currentTarget.style.transform = 'scale(1.05)')}
          onMouseLeave={e => (e.currentTarget.style.transform = 'scale(1)')}
        >
          <Target size={18} />
          <span>Bilhete ({betSlip.length})</span>
          <span style={{ fontFamily: "'JetBrains Mono', monospace", fontWeight: 700 }}>{totalOdds.toFixed(2)}x</span>
        </button>
      )}
    </div>
  )
}

function Nav({ view, setView, betCount, onBetSlipOpen, navOpen, setNavOpen, clearMatch }: {
  view: View; setView: (v: View) => void; betCount: number
  onBetSlipOpen: () => void; navOpen: boolean; setNavOpen: (v: boolean) => void; clearMatch: () => void
}) {
  const navItems = [
    { id: 'home' as View, label: 'Hoje', icon: Home },
    { id: 'favorites' as View, label: 'Favoritos', icon: Star },
    { id: 'bankroll' as View, label: 'Banca', icon: Wallet },
    { id: 'system' as View, label: 'Sistema', icon: Activity },
  ]

  const s: Record<string, React.CSSProperties> = {
    header: { position: 'fixed', top: 0, left: 0, right: 0, zIndex: 50, background: '#0f1119', borderBottom: '1px solid #1e2438', height: '56px' },
    inner: { maxWidth: '1200px', margin: '0 auto', padding: '0 16px', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'space-between' },
    logo: { display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer', background: 'none', border: 'none' },
    logoIcon: { width: '32px', height: '32px', borderRadius: '8px', background: '#00e887', display: 'flex', alignItems: 'center', justifyContent: 'center' },
    logoText: { fontFamily: "'Russo One', sans-serif", fontSize: '18px', color: '#eef0f9', letterSpacing: '0.05em' },
    nav: { display: 'flex', alignItems: 'center', gap: '4px' },
    betBtn: { display: 'flex', alignItems: 'center', gap: '8px', padding: '8px 16px', borderRadius: '8px', background: '#00e887', color: '#07080f', fontWeight: 700, fontSize: '13px', border: 'none', cursor: 'pointer' },
  }

  return (
    <header style={s.header}>
      <div style={s.inner}>
        <button style={s.logo} onClick={() => { setView('home'); clearMatch() }}>
          <div style={s.logoIcon}><Zap size={16} color="#07080f" fill="#07080f" /></div>
          <span style={s.logoText}>ULTRASTATS AI</span>
        </button>

        <nav style={{ ...s.nav, display: 'none', ...{ ['@media (min-width:768px)']: { display: 'flex' } } }} className="hidden md:flex">
          {navItems.map(({ id, label, icon: Icon }) => (
            <button key={id} onClick={() => { setView(id); clearMatch() }}
              style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '8px 16px', borderRadius: '8px', fontSize: '13px', fontWeight: 500, background: view === id ? '#1e2438' : 'transparent', color: view === id ? '#00e887' : '#7a88b0', border: 'none', cursor: 'pointer', transition: 'all 0.15s' }}
            >
              <Icon size={14} />{label}
            </button>
          ))}
        </nav>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button
            onClick={() => { setView('bankroll'); clearMatch() }}
            title="Gestão de banca, risco, apostas, liquidação, operações e modelos"
            style={{ ...s.betBtn, background: '#1e2438', color: '#eef0f9' }}
          >
            <Grid3X3 size={14} />
            <span className="hidden sm:inline">Funcionalidades</span>
          </button>
          {betCount > 0 && (
            <button onClick={onBetSlipOpen} style={s.betBtn}>
              <Target size={14} />
              <span className="hidden sm:inline">Bilhete</span>
              <span style={{ width: '20px', height: '20px', borderRadius: '50%', background: '#07080f', color: '#00e887', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '11px', fontWeight: 700 }}>{betCount}</span>
            </button>
          )}
          <button className="md:hidden" onClick={() => setNavOpen(!navOpen)}
            style={{ background: 'none', border: 'none', color: '#7a88b0', cursor: 'pointer', padding: '8px' }}>
            <Menu size={20} />
          </button>
        </div>
      </div>

      {navOpen && (
        <div className="md:hidden" style={{ background: '#0f1119', borderTop: '1px solid #1e2438', padding: '8px 16px', display: 'flex', gap: '4px' }}>
          {navItems.map(({ id, label, icon: Icon }) => (
            <button key={id} onClick={() => { setView(id); setNavOpen(false); clearMatch() }}
              style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px', padding: '8px', borderRadius: '8px', fontSize: '11px', fontWeight: 500, background: view === id ? '#1e2438' : 'transparent', color: view === id ? '#00e887' : '#7a88b0', border: 'none', cursor: 'pointer' }}>
              <Icon size={18} />{label}
            </button>
          ))}
        </div>
      )}
    </header>
  )
}

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
  return <div style={{ background: '#0f1119', border: '1px solid #1e2438', borderRadius: '12px', ...style }}>{children}</div>
}

function MatchCard({ match, onClick, isFavorite, onToggleFavorite }: {
  match: Match; onClick: () => void; isFavorite: boolean; onToggleFavorite: () => void
}) {
  return (
    <Card style={{ cursor: 'pointer', transition: 'border-color 0.15s' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 16px', borderBottom: '1px solid #1e2438' }}>
        <span style={{ fontSize: '12px', color: '#5a6480', fontFamily: "'JetBrains Mono', monospace" }}>{match.startTime}</span>
        {match.status === 'live' && <LiveBadge minute={match.minute} />}
        {match.status === 'finished' && <span style={{ fontSize: '11px', padding: '2px 8px', borderRadius: '4px', background: '#1e2438', color: '#5a6480' }}>Encerrado</span>}
        {match.status === 'upcoming' && <span style={{ fontSize: '11px', color: '#5a6480' }}>Em breve</span>}
        <button onClick={e => { e.stopPropagation(); onToggleFavorite() }} style={{ background: 'none', border: 'none', cursor: 'pointer', color: isFavorite ? '#fbbf24' : '#2a3150', padding: '2px' }}>
          <Star size={14} fill={isFavorite ? '#fbbf24' : 'none'} />
        </button>
      </div>

      <div onClick={onClick} style={{ padding: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px' }}>
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{ width: '36px', height: '36px', borderRadius: '8px', background: '#161b26', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '20px' }}>{match.homeTeam.logo}</div>
            <span style={{ fontWeight: 600, fontSize: '13px', color: '#eef0f9' }}>{match.homeTeam.name}</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexShrink: 0 }}>
            {match.homeScore !== undefined
              ? <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ fontFamily: "'Russo One', sans-serif", fontSize: '22px', color: '#eef0f9' }}>{match.homeScore}</span>
                <span style={{ fontFamily: "'Russo One', sans-serif", fontSize: '16px', color: '#2a3150' }}>:</span>
                <span style={{ fontFamily: "'Russo One', sans-serif", fontSize: '22px', color: '#eef0f9' }}>{match.awayScore}</span>
              </div>
              : <span style={{ fontSize: '12px', color: '#5a6480', fontFamily: "'JetBrains Mono', monospace" }}>vs</span>
            }
          </div>
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: '10px', justifyContent: 'flex-end' }}>
            <span style={{ fontWeight: 600, fontSize: '13px', color: '#eef0f9', textAlign: 'right' }}>{match.awayTeam.name}</span>
            <div style={{ width: '36px', height: '36px', borderRadius: '8px', background: '#161b26', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '20px' }}>{match.awayTeam.logo}</div>
          </div>
        </div>

        {match.markets.length > 0 && match.status !== 'finished' && (
          <div style={{ marginTop: '12px', paddingTop: '12px', borderTop: '1px solid #1e2438', display: 'flex', gap: '8px' }}>
            {(match.markets.find(m => m.name === 'Resultado da Partida')?.options || []).slice(0, 3).map(o => (
              <button key={o.label}
                onClick={e => { e.stopPropagation(); onClick() }}
                style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '8px', borderRadius: '8px', background: '#161b26', border: '1px solid #1e2438', cursor: 'pointer', transition: 'all 0.15s' }}
                onMouseEnter={e => { e.currentTarget.style.borderColor = '#00e887'; e.currentTarget.style.background = '#00e887'; Array.from(e.currentTarget.children).forEach((c: any) => c.style.color = '#07080f') }}
                onMouseLeave={e => { e.currentTarget.style.borderColor = '#1e2438'; e.currentTarget.style.background = '#161b26'; Array.from(e.currentTarget.children).forEach((c: any, i) => c.style.color = i === 0 ? '#7a88b0' : '#eef0f9') }}
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
  )
}

function HomeView({ matches, onMatchClick, favorites, onToggleFavorite }: {
  matches: Match[]; onMatchClick: (m: Match) => void; favorites: string[]; onToggleFavorite: (id: string) => void
}) {
  const [scope, setScope] = useState<'live' | 'today' | 'next'>('live')
  const [league, setLeague] = useState('all')
  const live = matches.filter(m => m.status === 'live')
  const todayKey = new Date().toLocaleDateString('en-CA')
  const upcomingToday = matches.filter(m =>
    m.status === 'upcoming' && m.kickoffAt &&
    new Date(m.kickoffAt).toLocaleDateString('en-CA') === todayKey
  )
  const next = matches.filter(m =>
    m.status === 'upcoming' && m.kickoffAt &&
    new Date(m.kickoffAt).toLocaleDateString('en-CA') > todayKey
  )
  const scoped = scope === 'live' ? live : scope === 'today' ? upcomingToday : next
  const leagues = Array.from(new Set(matches.map(m => m.league))).sort()
  const visible = league === 'all' ? scoped : scoped.filter(m => m.league === league)

  const byLeague = (list: Match[]) => list.reduce((acc, m) => { if (!acc[m.league]) acc[m.league] = []; acc[m.league].push(m); return acc }, {} as Record<string, Match[]>)

  return (
    <div className="animate-fade-in">
      <div style={{ padding: '24px 0 16px' }}>
        <h1 style={{ fontFamily: "'Russo One', sans-serif", fontSize: '24px', color: '#eef0f9', letterSpacing: '0.05em', margin: 0 }}>CENTRAL DE PARTIDAS</h1>
        <p style={{ fontSize: '13px', color: '#5a6480', marginTop: '4px' }}>{new Date().toLocaleDateString('pt-BR', { weekday: 'long', day: 'numeric', month: 'long' })}</p>
      </div>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 16 }}>
        {[
          { id: 'live', label: `Ao vivo (${live.length})` },
          { id: 'today', label: `Em breve (${upcomingToday.length})` },
          { id: 'next', label: `Próximas partidas (${next.length})` },
        ].map(item => (
          <button key={item.id} onClick={() => setScope(item.id as typeof scope)}
            style={{ padding: '9px 14px', borderRadius: 8, border: `1px solid ${scope === item.id ? '#00e887' : '#1e2438'}`, background: scope === item.id ? 'rgba(0,232,135,.12)' : '#0f1119', color: scope === item.id ? '#00e887' : '#7a88b0', cursor: 'pointer', fontWeight: 700 }}>
            {item.label}
          </button>
        ))}
        <label style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 8, color: '#7a88b0' }}>
          <Filter size={14} />
          <select value={league} onChange={event => setLeague(event.target.value)}
            style={{ background: '#0f1119', color: '#eef0f9', border: '1px solid #1e2438', borderRadius: 8, padding: '9px 12px' }}>
            <option value="all">Todas as ligas</option>
            {leagues.map(item => <option key={item} value={item}>{item}</option>)}
          </select>
        </label>
      </div>

      {visible.length === 0 && (
        <Card style={{ padding: 24, textAlign: 'center', color: '#7a88b0' }}>
          Nenhuma partida encontrada nesta categoria.
        </Card>
      )}
      {Object.entries(byLeague(visible)).map(([l, ms]) => (
        <LeagueGroup key={l} league={ms[0].league} logo={ms[0].leagueLogo} country={ms[0].country}>
          {ms.map(m => <MatchCard key={m.id} match={m} onClick={() => onMatchClick(m)} isFavorite={favorites.includes(m.id)} onToggleFavorite={() => onToggleFavorite(m.id)} />)}
        </LeagueGroup>
      ))}
    </div>
  )
}

function Section({ title, accent, icon, children }: { title: string; accent: string; icon: React.ReactNode; children: React.ReactNode }) {
  return (
    <div style={{ marginBottom: '32px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
        {icon}
        <h2 style={{ fontSize: '11px', fontWeight: 700, color: accent, letterSpacing: '0.1em', textTransform: 'uppercase', margin: 0 }}>{title}</h2>
      </div>
      {children}
    </div>
  )
}

function LeagueGroup({ league, logo, country, children }: { league: string; logo: string; country: string; children: React.ReactNode }) {
  return (
    <div style={{ marginBottom: '16px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px', padding: '0 4px' }}>
        <span style={{ fontSize: '16px' }}>{logo}</span>
        <span style={{ fontSize: '12px', fontWeight: 600, color: '#7a88b0' }}>{league}</span>
        <span style={{ fontSize: '11px', color: '#2a3150' }}>· {country}</span>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>{children}</div>
    </div>
  )
}

function MatchView({ match, betSlip, onAddBet, onBack, isFavorite, onToggleFavorite }: {
  match: Match; betSlip: BetSelection[]
  onAddBet: (matchId: string, matchName: string, market: string, option: string, odds: number) => void
  onBack: () => void; isFavorite: boolean; onToggleFavorite: () => void
}) {
  const [tab, setTab] = useState<MatchTab>(match.status === 'live' ? 'live' : 'lineup')
  const matchName = `${match.homeTeam.name} vs ${match.awayTeam.name}`
  const addBet = (market: string, option: string, odds: number) => onAddBet(match.id, matchName, market, option, odds)

  const tabs: { id: MatchTab; label: string; icon: React.ReactNode }[] = [
    { id: 'live', label: 'Ao Vivo', icon: <Activity size={13} /> },
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
              {match.status === 'finished' && <span style={{ fontSize: '11px', padding: '4px 10px', borderRadius: '4px', background: '#1e2438', color: '#5a6480' }}>Encerrado</span>}
              {match.status === 'upcoming' && <span style={{ fontFamily: "'JetBrains Mono', monospace", fontWeight: 700, fontSize: '16px', color: '#4f8ef7' }}>{match.startTime}</span>}
              <button onClick={onToggleFavorite} style={{ background: 'none', border: 'none', cursor: 'pointer', color: isFavorite ? '#fbbf24' : '#2a3150' }}>
                <Star size={18} fill={isFavorite ? '#fbbf24' : 'none'} />
              </button>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '16px' }}>
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px', textAlign: 'center' }}>
              <div style={{ width: '64px', height: '64px', borderRadius: '16px', background: '#161b26', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '32px' }}>{match.homeTeam.logo}</div>
              <span style={{ fontWeight: 600, fontSize: '14px', color: '#eef0f9' }}>{match.homeTeam.name}</span>
              <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '11px', color: '#5a6480' }}>{match.homeLineup.formation}</span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' }}>
              {match.homeScore !== undefined
                ? <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontFamily: "'Russo One', sans-serif", fontSize: '40px', color: '#eef0f9' }}>{match.homeScore}</span>
                  <span style={{ fontFamily: "'Russo One', sans-serif", fontSize: '24px', color: '#2a3150' }}>:</span>
                  <span style={{ fontFamily: "'Russo One', sans-serif", fontSize: '40px', color: '#eef0f9' }}>{match.awayScore}</span>
                </div>
                : <span style={{ fontFamily: "'Russo One', sans-serif", fontSize: '24px', color: '#2a3150' }}>vs</span>
              }
            </div>
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px', textAlign: 'center' }}>
              <div style={{ width: '64px', height: '64px', borderRadius: '16px', background: '#161b26', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '32px' }}>{match.awayTeam.logo}</div>
              <span style={{ fontWeight: 600, fontSize: '14px', color: '#eef0f9' }}>{match.awayTeam.name}</span>
              <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '11px', color: '#5a6480' }}>{match.awayLineup.formation}</span>
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', borderTop: '1px solid #1e2438', overflowX: 'auto' }}>
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
            <Clock size={32} color="#2a3150" style={{ margin: '0 auto 12px' }} />
            <p style={{ fontSize: '13px', color: '#5a6480', margin: 0 }}>A partida ainda não começou</p>
          </Card>
        ) : match.events.length === 0 ? (
          <Card style={{ padding: '32px', textAlign: 'center' }}>
            <p style={{ fontSize: '13px', color: '#5a6480', margin: 0 }}>Nenhum evento ainda</p>
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
    { label: 'Posse de Bola', h: `${match.stats.possession[0]}%`, a: `${match.stats.possession[1]}%`, hv: match.stats.possession[0], av: match.stats.possession[1] },
    { label: 'Chutes', h: String(match.stats.shots[0]), a: String(match.stats.shots[1]), hv: match.stats.shots[0], av: match.stats.shots[1] },
    { label: 'No Alvo', h: String(match.stats.shotsOnTarget[0]), a: String(match.stats.shotsOnTarget[1]), hv: match.stats.shotsOnTarget[0], av: match.stats.shotsOnTarget[1] },
    { label: 'Escanteios', h: String(match.stats.corners[0]), a: String(match.stats.corners[1]), hv: match.stats.corners[0], av: match.stats.corners[1] },
    { label: 'Faltas', h: String(match.stats.fouls[0]), a: String(match.stats.fouls[1]), hv: match.stats.fouls[1], av: match.stats.fouls[0] },
    { label: 'xG', h: String(match.stats.xG[0]), a: String(match.stats.xG[1]), hv: match.stats.xG[0], av: match.stats.xG[1] },
  ]
  return (
    <Card style={{ overflow: 'hidden' }}>
      {rows.map((row, i) => {
        const total = row.hv + row.av || 1
        const hPct = (row.hv / total) * 100
        return (
          <div key={row.label} style={{ padding: '12px 16px', borderBottom: i < rows.length - 1 ? '1px solid #1e2438' : 'none' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
              <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '13px', fontWeight: 700, color: '#eef0f9' }}>{row.h}</span>
              <span style={{ fontSize: '12px', color: '#5a6480' }}>{row.label}</span>
              <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '13px', fontWeight: 700, color: '#eef0f9' }}>{row.a}</span>
            </div>
            <div style={{ height: '4px', borderRadius: '2px', background: '#1e2438', display: 'flex', overflow: 'hidden' }}>
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

  const coordsMap: Record<string, { x: number; y: number }[]> = {
    GK: [{ x: 50, y: 90 }],
    DEF: [{ x: 15, y: 70 }, { x: 37, y: 70 }, { x: 63, y: 70 }, { x: 85, y: 70 }],
    MID: [{ x: 20, y: 50 }, { x: 50, y: 48 }, { x: 80, y: 50 }],
    FWD: [{ x: 20, y: 26 }, { x: 50, y: 18 }, { x: 80, y: 26 }],
  }
  const posCount: Record<string, number> = {}
  const positioned = lineup.players.map(p => {
    const idx = posCount[p.position] || 0
    posCount[p.position] = idx + 1
    const coords = (coordsMap[p.position] || [{ x: 50, y: 50 }])[idx] || { x: 50, y: 50 }
    return { ...p, coords }
  })

  return (
    <div>
      <div style={{ display: 'flex', borderRadius: '10px', border: '1px solid #1e2438', overflow: 'hidden', marginBottom: '16px' }}>
        {(['home', 'away'] as const).map(s => (
          <button key={s} onClick={() => setSide(s)} style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', padding: '12px', fontSize: '13px', fontWeight: 600, background: side === s ? '#1c2235' : '#0f1119', color: side === s ? '#eef0f9' : '#5a6480', border: 'none', cursor: 'pointer', transition: 'all 0.15s' }}>
            <span>{s === 'home' ? match.homeTeam.logo : match.awayTeam.logo}</span>
            <span>{s === 'home' ? match.homeTeam.name : match.awayTeam.name}</span>
          </button>
        ))}
      </div>

      <Card style={{ overflow: 'hidden', marginBottom: '16px' }}>
        <div style={{ position: 'relative', paddingBottom: '58%', background: 'linear-gradient(180deg, #081408 0%, #0c200c 50%, #081408 100%)' }}>
          <div style={{ position: 'absolute', inset: '12px 20px', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '4px' }} />
          <div style={{ position: 'absolute', left: '50%', top: '12px', bottom: '12px', width: '1px', background: 'rgba(255,255,255,0.06)', transform: 'translateX(-50%)' }} />
          <div style={{ position: 'absolute', left: '50%', top: '50%', width: '48px', height: '48px', borderRadius: '50%', border: '1px solid rgba(255,255,255,0.06)', transform: 'translate(-50%,-50%)' }} />
          {positioned.map(p => (
            <div key={p.number} style={{ position: 'absolute', left: `${p.coords.x}%`, top: `${p.coords.y}%`, transform: 'translate(-50%,-50%)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '2px' }}>
              <div style={{ width: '32px', height: '32px', borderRadius: '50%', border: `2px solid ${team.color}`, background: '#0f1119', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: "'JetBrains Mono', monospace", fontSize: '11px', fontWeight: 700, color: '#eef0f9' }}>{p.number}</div>
              <div style={{ padding: '1px 4px', borderRadius: '3px', background: 'rgba(7,8,15,0.9)', color: '#eef0f9', fontSize: '9px', fontWeight: 600, whiteSpace: 'nowrap', maxWidth: '56px', overflow: 'hidden', textOverflow: 'ellipsis' }}>{p.name.split(' ').pop()}</div>
            </div>
          ))}
        </div>
      </Card>

      <SectionLabel>Banco de Reservas</SectionLabel>
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
  const rows = [
    { label: 'Posse de Bola', h: `${match.stats.possession[0]}%`, a: `${match.stats.possession[1]}%`, hv: match.stats.possession[0], av: match.stats.possession[1] },
    { label: 'Chutes Totais', h: String(match.stats.shots[0]), a: String(match.stats.shots[1]), hv: match.stats.shots[0], av: match.stats.shots[1] },
    { label: 'Chutes no Alvo', h: String(match.stats.shotsOnTarget[0]), a: String(match.stats.shotsOnTarget[1]), hv: match.stats.shotsOnTarget[0], av: match.stats.shotsOnTarget[1] },
    { label: 'Escanteios', h: String(match.stats.corners[0]), a: String(match.stats.corners[1]), hv: match.stats.corners[0], av: match.stats.corners[1] },
    { label: 'Faltas Cometidas', h: String(match.stats.fouls[0]), a: String(match.stats.fouls[1]), hv: match.stats.fouls[1], av: match.stats.fouls[0] },
    { label: 'Cartões Amarelos', h: String(match.stats.yellowCards[0]), a: String(match.stats.yellowCards[1]), hv: match.stats.yellowCards[1], av: match.stats.yellowCards[0] },
    { label: 'Impedimentos', h: String(match.stats.offsides[0]), a: String(match.stats.offsides[1]), hv: match.stats.offsides[1], av: match.stats.offsides[0] },
    { label: 'Passes', h: String(match.stats.passes[0]), a: String(match.stats.passes[1]), hv: match.stats.passes[0], av: match.stats.passes[1] },
    { label: 'Precisão de Passes', h: `${match.stats.passAccuracy[0]}%`, a: `${match.stats.passAccuracy[1]}%`, hv: match.stats.passAccuracy[0], av: match.stats.passAccuracy[1] },
    { label: 'Expected Goals (xG)', h: String(match.stats.xG[0]), a: String(match.stats.xG[1]), hv: match.stats.xG[0], av: match.stats.xG[1] },
  ]

  return (
    <Card style={{ overflow: 'hidden' }}>
      <div style={{ display: 'flex', padding: '12px 16px', borderBottom: '1px solid #1e2438' }}>
        <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '18px' }}>{match.homeTeam.logo}</span>
          <span style={{ fontWeight: 600, fontSize: '13px', color: '#eef0f9' }}>{match.homeTeam.name}</span>
        </div>
        <span style={{ fontSize: '11px', fontWeight: 700, color: '#5a6480', letterSpacing: '0.1em' }}>ESTATÍSTICA</span>
        <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: '8px', justifyContent: 'flex-end' }}>
          <span style={{ fontWeight: 600, fontSize: '13px', color: '#eef0f9', textAlign: 'right' }}>{match.awayTeam.name}</span>
          <span style={{ fontSize: '18px' }}>{match.awayTeam.logo}</span>
        </div>
      </div>
      {rows.map((row, i) => {
        const total = row.hv + row.av || 1
        const hPct = (row.hv / total) * 100
        return (
          <div key={row.label} style={{ padding: '12px 16px', borderBottom: i < rows.length - 1 ? '1px solid #1e2438' : 'none' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span style={{ fontFamily: "'JetBrains Mono', monospace", fontWeight: 700, fontSize: '14px', color: '#eef0f9' }}>{row.h}</span>
              <span style={{ fontSize: '12px', color: '#5a6480' }}>{row.label}</span>
              <span style={{ fontFamily: "'JetBrains Mono', monospace", fontWeight: 700, fontSize: '14px', color: '#eef0f9' }}>{row.a}</span>
            </div>
            <div style={{ height: '5px', borderRadius: '3px', background: '#1e2438', display: 'flex', overflow: 'hidden' }}>
              <div style={{ width: `${hPct}%`, background: '#4f8ef7' }} />
              <div style={{ flex: 1, background: '#ff7c3a' }} />
            </div>
          </div>
        )
      })}
    </Card>
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
          <div style={{ padding: '10px 16px', borderBottom: '1px solid #1e2438' }}>
            <span style={{ fontSize: '12px', fontWeight: 600, color: '#7a88b0' }}>{market.name}</span>
          </div>
          <div style={{ padding: '12px', display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {market.options.map(opt => {
              const sel = isSel(market, opt)
              return (
                <button key={opt.id} onClick={() => onAddBet(market.name, opt.label, opt.odds)}
                  style={{ flex: '1', minWidth: '80px', display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '12px 8px', borderRadius: '8px', background: sel ? '#00e887' : '#161b26', border: `1px solid ${sel ? '#00e887' : '#1e2438'}`, cursor: 'pointer', transition: 'all 0.15s' }}
                  onMouseEnter={e => { if (!sel) { e.currentTarget.style.borderColor = '#00e887'; e.currentTarget.style.background = 'rgba(0,232,135,0.08)' } }}
                  onMouseLeave={e => { if (!sel) { e.currentTarget.style.borderColor = '#1e2438'; e.currentTarget.style.background = '#161b26' } }}
                >
                  <span style={{ fontSize: '11px', color: sel ? '#07080f' : '#7a88b0', marginBottom: '4px', fontWeight: 500 }}>{opt.label}</span>
                  <span style={{ fontFamily: "'JetBrains Mono', monospace", fontWeight: 700, fontSize: '16px', color: sel ? '#07080f' : '#eef0f9' }}>{opt.odds.toFixed(2)}</span>
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
  const best = match.analysis.recommendations.find(
    item => item.primary && !item.noBet
  ) || match.analysis.recommendations.find(item => !item.noBet)
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
          return (
            <Card key={side} style={{ padding: '14px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
                <span>{team.logo}</span>
                <span style={{ fontSize: '12px', fontWeight: 600, color: '#7a88b0' }}>{team.shortName} — Forma</span>
              </div>
              <div style={{ display: 'flex', gap: '4px' }}>{form.map((r, i) => <FormBadge key={i} result={r} />)}</div>
            </Card>
          )
        })}
      </div>

      <Card style={{ padding: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
          <AlertTriangle size={15} color="#ff7c3a" />
          <span style={{ fontWeight: 600, fontSize: '14px', color: '#eef0f9' }}>Fatores-Chave</span>
        </div>
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
          {best && (
            <Card style={{ padding: '16px', marginBottom: 12, borderColor: '#00e887', background: 'rgba(0,232,135,.04)' }}>
              <div style={{ fontSize: 10, color: '#00e887', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '.12em', marginBottom: 7 }}>
                Melhor aposta indicada pelo modelo
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'center' }}>
                <div>
                  <div style={{ color: '#eef0f9', fontWeight: 700 }}>{best.tip}</div>
                  <div style={{ color: '#7a88b0', fontSize: 12 }}>{best.market} · {categoryLabels[best.category || 'other'] || best.category}</div>
                  <div style={{ color: '#7a88b0', fontSize: 11, marginTop: 4 }}>{best.reasoning}</div>
                </div>
                <button onClick={() => onAddBet(best.market, best.tip, best.odds)}
                  style={{ flexShrink: 0, padding: '9px 12px', borderRadius: 8, border: '1px solid #00e887', background: 'rgba(0,232,135,.1)', color: '#00e887', fontWeight: 700, cursor: 'pointer' }}>
                  {best.odds.toFixed(2)}
                </button>
              </div>
            </Card>
          )}
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 7, marginBottom: 12 }}>
            {categories.map(category => (
              <button key={category} onClick={() => setSelectedCategory(category)}
                style={{ padding: '8px 11px', borderRadius: 8, border: `1px solid ${selectedCategory === category ? '#00e887' : '#1e2438'}`, background: selectedCategory === category ? 'rgba(0,232,135,.1)' : '#0f1119', color: selectedCategory === category ? '#00e887' : '#7a88b0', cursor: 'pointer', fontSize: 12, fontWeight: 600 }}>
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
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexShrink: 0 }}>
                    <span style={{ fontSize: '11px', padding: '2px 8px', borderRadius: '4px', background: bg, color, fontWeight: 600 }}>{rec.confidence}</span>
                    <span style={{ fontFamily: "'JetBrains Mono', monospace", fontWeight: 700, fontSize: '18px', color: '#00e887' }}>{rec.odds.toFixed(2)}</span>
                  </div>
                </div>
                <p style={{ fontSize: '12px', color: '#7a88b0', marginBottom: '12px' }}>{rec.reasoning}</p>
                <button onClick={() => onAddBet(rec.market, rec.tip, rec.odds)}
                  style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(0,232,135,0.08)', border: '1px solid #00e887', color: '#00e887', fontSize: '12px', fontWeight: 600, cursor: 'pointer', transition: 'all 0.15s' }}
                  onMouseEnter={e => { e.currentTarget.style.background = 'rgba(0,232,135,0.16)' }}
                  onMouseLeave={e => { e.currentTarget.style.background = 'rgba(0,232,135,0.08)' }}
                >
                  + Adicionar ao Bilhete ({rec.odds.toFixed(2)})
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
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{ flex: 1, textAlign: 'right' }}>
                  <span style={{ fontWeight: 600, fontSize: '13px', color: homeDiff > 0 ? '#00c853' : '#eef0f9' }}>{h.homeTeam}</span>
                </div>
                <div style={{ fontFamily: "'JetBrains Mono', monospace", fontWeight: 700, fontSize: '14px', padding: '4px 12px', borderRadius: '6px', background: '#1e2438', color: '#eef0f9', flexShrink: 0 }}>
                  {h.homeScore} — {h.awayScore}
                </div>
                <div style={{ flex: 1 }}>
                  <span style={{ fontWeight: 600, fontSize: '13px', color: homeDiff < 0 ? '#00c853' : '#eef0f9' }}>{h.awayTeam}</span>
                </div>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '6px' }}>
                <span style={{ fontSize: '11px', color: '#5a6480' }}>{h.date}</span>
                <span style={{ fontSize: '11px', color: '#5a6480' }}>{h.competition}</span>
              </div>
            </Card>
          )
        })}
      </div>
    </div>
  )
}

function BetSlipDrawer({ selections, onRemove, onOddsChange, onClose, totalOdds, onPlace }: {
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
      <div className="animate-slide-right" style={{ position: 'relative', width: '100%', maxWidth: '380px', background: '#0f1119', borderLeft: '1px solid #1e2438', display: 'flex', flexDirection: 'column', maxHeight: '100vh' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '16px 20px', borderBottom: '1px solid #1e2438' }}>
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
              <Target size={40} color="#2a3150" style={{ marginBottom: '12px' }} />
              <p style={{ fontSize: '13px', margin: 0 }}>Nenhuma seleção</p>
              <p style={{ fontSize: '12px', marginTop: '4px', color: '#2a3150' }}>Clique em uma odd para adicionar</p>
            </div>
          ) : selections.map(sel => (
            <div key={sel.id} style={{ background: '#161b26', border: '1px solid #1e2438', borderRadius: '10px', padding: '12px' }}>
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
                    style={{ width: '82px', background: '#0f1119', border: '1px solid #2a3150', borderRadius: '6px', padding: '6px 8px', textAlign: 'right', fontFamily: "'JetBrains Mono', monospace", fontWeight: 700, fontSize: '16px', color: '#00e887', outline: 'none' }}
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
          <div style={{ borderTop: '1px solid #1e2438', padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '13px', color: '#7a88b0' }}>Odds combinadas</span>
              <span style={{ fontFamily: "'JetBrains Mono', monospace", fontWeight: 700, fontSize: '22px', color: '#00e887' }}>{totalOdds.toFixed(2)}x</span>
            </div>

            <div>
              <label style={{ fontSize: '12px', color: '#5a6480', display: 'block', marginBottom: '8px' }}>Valor da aposta (R$)</label>
              <input type="number" value={stake} onChange={e => setStake(e.target.value)}
                style={{ width: '100%', background: '#161b26', border: '1px solid #1e2438', borderRadius: '8px', padding: '10px 12px', fontSize: '14px', fontFamily: "'JetBrains Mono', monospace", fontWeight: 700, color: '#eef0f9', outline: 'none', boxSizing: 'border-box' }}
                onFocus={e => e.target.style.borderColor = '#00e887'} onBlur={e => e.target.style.borderColor = '#1e2438'}
              />
              <div style={{ display: 'flex', gap: '6px', marginTop: '8px' }}>
                {[10, 25, 50, 100].map(q => (
                  <button key={q} onClick={() => setStake(String(q))}
                    style={{ flex: 1, padding: '6px', borderRadius: '6px', background: '#161b26', border: '1px solid #1e2438', color: '#7a88b0', fontSize: '12px', cursor: 'pointer' }}
                    onMouseEnter={e => e.currentTarget.style.borderColor = '#00e887'}
                    onMouseLeave={e => e.currentTarget.style.borderColor = '#1e2438'}
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>

            <div style={{ background: '#161b26', borderRadius: '8px', padding: '12px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                <span style={{ fontSize: '12px', color: '#5a6480' }}>Retorno potencial</span>
                <span style={{ fontFamily: "'JetBrains Mono', monospace", fontWeight: 700, fontSize: '16px', color: '#00e887' }}>R$ {potential}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '12px', color: '#5a6480' }}>Lucro estimado</span>
                <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '13px', color: '#7a88b0' }}>R$ {profit}</span>
              </div>
            </div>

            <div style={{ background: '#161b26', border: '1px solid #1e2438', borderRadius: '8px', padding: '12px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span style={{ fontSize: '12px', color: '#5a6480' }}>Análise de Risco</span>
                <span style={{ fontSize: '12px', fontWeight: 600, color: riskColor }}>{risk}</span>
              </div>
              <div style={{ height: '4px', borderRadius: '2px', background: '#1e2438', marginBottom: '8px' }}>
                <div style={{ width: `${riskPct}%`, height: '100%', background: riskColor, borderRadius: '2px', transition: 'all 0.3s' }} />
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: '#5a6480' }}>
                <span>Prob. implícita: {((1 / totalOdds) * 100).toFixed(1)}%</span>
                <span>{selections.length} sel.</span>
              </div>
            </div>

            <button onClick={() => { if (stakeNum > 0) onPlace(stakeNum) }}
              disabled={stakeNum <= 0}
              style={{ width: '100%', padding: '14px', borderRadius: '10px', background: '#00e887', color: '#07080f', fontWeight: 700, fontSize: '14px', border: 'none', cursor: stakeNum > 0 ? 'pointer' : 'not-allowed', opacity: stakeNum > 0 ? 1 : 0.5, transition: 'all 0.15s' }}
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

function BankrollView({ bets, setBets, bankroll, bankrollId, onBankrollCreated, onError, onBalanceChanged, pending }: {
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
  }

  return (
    <div className="animate-fade-in">
      <div style={{ padding: '24px 0 16px' }}>
        <h1 style={{ fontFamily: "'Russo One', sans-serif", fontSize: '24px', color: '#eef0f9', letterSpacing: '0.05em', margin: 0 }}>GESTÃO DE BANCA</h1>
        <p style={{ fontSize: '13px', color: '#5a6480', marginTop: '4px' }}>Acompanhe suas apostas e performance</p>
      </div>

      {bankrollId && (
        <Card style={{ padding: '14px', marginBottom: '16px', display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}>
          <button onClick={() => setMovement('deposit')} style={{ padding: '10px 16px', borderRadius: 8, background: '#00e887', color: '#07080f', border: 0, fontWeight: 700, cursor: 'pointer' }}>
            + Depósito
          </button>
          <button onClick={() => setMovement('withdraw')} style={{ padding: '10px 16px', borderRadius: 8, background: '#1e2438', color: '#eef0f9', border: '1px solid #2a3150', fontWeight: 700, cursor: 'pointer' }}>
            − Saque
          </button>
          {movement && <>
            <input autoFocus type="number" min="0.01" step="0.01" placeholder="Valor em R$" value={movementAmount} onChange={event => setMovementAmount(event.target.value)}
              style={{ width: 150, background: '#161b26', border: '1px solid #2a3150', borderRadius: 7, padding: 10, color: '#eef0f9' }} />
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
            style={{ padding: '7px 12px', borderRadius: 7, border: '1px solid #1e2438', background: period === value ? '#1e2438' : 'transparent', color: period === value ? '#00e887' : '#7a88b0', cursor: 'pointer', fontSize: 12 }}>
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
                style={{ width: '100%', boxSizing: 'border-box', marginTop: 6, background: '#161b26', border: '1px solid #1e2438', borderRadius: 7, padding: 10, color: '#eef0f9' }} />
            </label>
            <label style={{ fontSize: '11px', color: '#7a88b0' }}>
              Saldo inicial (R$)
              <input type="number" min="0.01" step="0.01" value={initialBalance} onChange={event => setInitialBalance(event.target.value)}
                style={{ width: '100%', boxSizing: 'border-box', marginTop: 6, background: '#161b26', border: '1px solid #1e2438', borderRadius: 7, padding: 10, color: '#eef0f9' }} />
            </label>
            <label style={{ fontSize: '11px', color: '#7a88b0' }}>
              Valor da unidade (%)
              <input type="number" min="0.1" max="100" step="0.1" value={unitPercentage} onChange={event => setUnitPercentage(event.target.value)}
                style={{ width: '100%', boxSizing: 'border-box', marginTop: 6, background: '#161b26', border: '1px solid #1e2438', borderRadius: 7, padding: 10, color: '#eef0f9' }} />
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
          }} style={{ marginTop: 14, padding: '11px 18px', borderRadius: 8, background: '#00e887', color: '#07080f', border: 0, fontWeight: 700, cursor: creating ? 'wait' : 'pointer' }}>
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
          const cfg = stCfg[bet.status]
          return (
            <Card key={bet.id} style={{ overflow: 'hidden' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 16px', borderBottom: '1px solid #1e2438' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ color: cfg.color }}>{cfg.icon}</span>
                  <span style={{ fontSize: '11px', padding: '2px 8px', borderRadius: '4px', background: cfg.bg, color: cfg.color, fontWeight: 600 }}>{cfg.label}</span>
                  <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '12px', color: '#5a6480' }}>{bet.date}</span>
                  <span style={{ fontFamily: "'JetBrains Mono', monospace", fontWeight: 700, fontSize: '13px', color: '#eef0f9' }}>{bet.totalOdds.toFixed(2)}x</span>
                </div>
              </div>
              <div style={{ padding: '12px 16px' }}>
                {bet.selections.map(sel => (
                  <div key={sel.id} style={{ display: 'flex', justifyContent: 'space-between', gap: 12, padding: '8px 0', borderBottom: '1px solid #1e2438', fontSize: '12px' }}>
                    <div style={{ color: '#5a6480' }}>
                      <span>{sel.matchName}</span>
                      <span style={{ margin: '0 6px', color: '#2a3150' }}>·</span>
                      <span style={{ color: '#7a88b0' }}>{sel.market}</span>
                      <span style={{ margin: '0 6px', color: '#2a3150' }}>·</span>
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

function FavoritesView({ matches, favorites, onMatchClick, onToggleFavorite }: {
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
          <Star size={40} color="#2a3150" style={{ margin: '0 auto 12px' }} />
          <p style={{ fontSize: '13px', color: '#5a6480', margin: 0 }}>Nenhum favorito ainda</p>
          <p style={{ fontSize: '12px', marginTop: '4px', color: '#2a3150' }}>Clique na estrela em qualquer partida para favoritar</p>
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

function SystemView({ maturity }: { maturity: any }) {
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

import { useCallback, useEffect, useState } from 'react'
import {
  BrowserRouter, NavLink, Navigate, Route, Routes,
  useLocation, useNavigate, useParams,
} from 'react-router-dom'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import {
  Activity, BarChart3, BrainCircuit, Database, FlaskConical,
  Grid3X3, Home, Menu, Receipt, RefreshCw, ShieldCheck, Star,
  Target, Wallet, X, Zap,
} from 'lucide-react'
import {
  BankrollView, BetSlipDrawer, FavoritesView, HomeView, MatchView,
  SystemView,
} from '../App'
import type { BetSelection, Match, PlacedBet } from '../data'
import {
  analyzeBetSlip, loadBankrolls, loadBetSlips, loadMatch, loadMatches,
  loadMaturity, placeBet,
} from '../api'

type Bankroll = {
  id: number
  balance: number
  active: boolean
}

const navigation = [
  { to: '/', label: 'Central de partidas', icon: Home },
  { to: '/favorites', label: 'Favoritos', icon: Star },
  { to: '/bankroll', label: 'Gestão de banca', icon: Wallet },
  { to: '/bets', label: 'Minhas apostas', icon: Receipt },
  { to: '/analysis', label: 'Análises', icon: BarChart3 },
  { to: '/risk', label: 'Gestão de risco', icon: ShieldCheck },
  { to: '/statistics', label: 'Motor estatístico', icon: Activity },
  { to: '/models', label: 'Modelos e aprendizado', icon: BrainCircuit },
  { to: '/recommendations', label: 'Recomendações', icon: Target },
  { to: '/providers', label: 'Provedores e qualidade', icon: Database },
]

const queryKeys = {
  matches: ['matches'] as const,
  bankrolls: ['bankrolls'] as const,
  bets: ['bets'] as const,
  maturity: ['maturity'] as const,
}

function useStoredFavorites() {
  const [favorites, setFavorites] = useState<string[]>(() => {
    try {
      return JSON.parse(localStorage.getItem('ultrastats:favorites') || '[]')
    } catch {
      return []
    }
  })
  useEffect(() => {
    localStorage.setItem('ultrastats:favorites', JSON.stringify(favorites))
  }, [favorites])
  const toggle = useCallback((id: string) => {
    setFavorites(current => current.includes(id)
      ? current.filter(item => item !== id)
      : [...current, id])
  }, [])
  return { favorites, toggle }
}

export default function AppRouter() {
  return (
    <BrowserRouter>
      <UltraStatsApp />
    </BrowserRouter>
  )
}

function UltraStatsApp() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { favorites, toggle } = useStoredFavorites()
  const [betSlip, setBetSlip] = useState<BetSelection[]>([])
  const [betSlipOpen, setBetSlipOpen] = useState(false)
  const [message, setMessage] = useState('')
  const [placedBets, setPlacedBets] = useState<PlacedBet[]>([])

  const matchesQuery = useQuery({
    queryKey: queryKeys.matches,
    queryFn: loadMatches,
    refetchInterval: 60_000,
    staleTime: 20_000,
    retry: 2,
  })
  const bankrollQuery = useQuery({
    queryKey: queryKeys.bankrolls,
    queryFn: loadBankrolls,
    staleTime: 30_000,
  })
  const betsQuery = useQuery({
    queryKey: queryKeys.bets,
    queryFn: loadBetSlips,
    staleTime: 20_000,
  })
  const maturityQuery = useQuery({
    queryKey: queryKeys.maturity,
    queryFn: loadMaturity,
    refetchInterval: 120_000,
    staleTime: 60_000,
  })

  useEffect(() => {
    if (betsQuery.data) setPlacedBets(betsQuery.data)
  }, [betsQuery.data])

  const matches = matchesQuery.data || []
  const bankroll = (bankrollQuery.data || []).find(
    (item: Bankroll) => item.active,
  ) as Bankroll | undefined
  const totalOdds = betSlip.reduce((value, item) => value * item.odds, 1)

  const addToBetSlip = useCallback((
    matchId: string,
    matchName: string,
    market: string,
    option: string,
    odds: number,
  ) => {
    const source = matches.find(item => item.id === matchId)
    const marketId = Number(source?.markets.find(item => item.name === market)?.id)
    setBetSlip(current => {
      const id = `${matchId}-${market}-${option}`
      if (current.some(item => item.id === id)) {
        return current.filter(item => item.id !== id)
      }
      return [...current, {
        id, matchId, matchName, market, marketId, option,
        odds, sourceOdds: odds,
      }]
    })
    setBetSlipOpen(true)
  }, [matches])

  const placeCurrentBet = async (stake: number) => {
    if (!bankroll) {
      setMessage('Crie e ative uma banca antes de confirmar o bilhete.')
      setBetSlipOpen(false)
      navigate('/bankroll')
      return
    }
    const payload = {
      bankroll_id: bankroll.id,
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
    try {
      const assessment = await analyzeBetSlip(payload)
      if (!assessment.approved && !(assessment.unavailable_markets || []).length) {
        setMessage(
          `Bilhete bloqueado pelo risco: ${
            assessment.warnings?.join(', ') || 'valor conservador insuficiente'
          }.`,
        )
        return
      }
      await placeBet(payload)
      setBetSlip([])
      setBetSlipOpen(false)
      setMessage('Bilhete registrado com sucesso.')
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.bets }),
        queryClient.invalidateQueries({ queryKey: queryKeys.bankrolls }),
      ])
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Falha ao registrar bilhete.')
    }
  }

  const isLoading = (
    matchesQuery.isPending || bankrollQuery.isPending
    || betsQuery.isPending || maturityQuery.isPending
  )
  const queryError = [
    matchesQuery.error, bankrollQuery.error, betsQuery.error, maturityQuery.error,
  ].find(Boolean)

  return (
    <AppShell
      betCount={betSlip.length}
      onBetSlipOpen={() => setBetSlipOpen(true)}
      refreshing={matchesQuery.isFetching}
      onRefresh={() => queryClient.invalidateQueries()}
    >
      {message && (
        <StatusBanner message={message} onClose={() => setMessage('')} />
      )}
      {queryError && (
        <StatusBanner
          message={queryError instanceof Error ? queryError.message : 'Falha de comunicação.'}
          onClose={() => queryClient.invalidateQueries()}
          retry
        />
      )}
      {isLoading && !matchesQuery.data ? <LoadingScreen /> : (
        <Routes>
          <Route path="/" element={
            <HomeView
              matches={matches}
              favorites={favorites}
              onToggleFavorite={toggle}
              onMatchClick={match => navigate(`/matches/${match.id}`)}
            />
          } />
          <Route path="/matches/:matchId" element={
            <MatchRoute
              fallbackMatches={matches}
              favorites={favorites}
              toggleFavorite={toggle}
              betSlip={betSlip}
              onAddBet={addToBetSlip}
            />
          } />
          <Route path="/favorites" element={
            <FavoritesView
              matches={matches}
              favorites={favorites}
              onToggleFavorite={toggle}
              onMatchClick={match => navigate(`/matches/${match.id}`)}
            />
          } />
          <Route path="/bankroll" element={
            <BankrollView
              bets={placedBets}
              setBets={setPlacedBets}
              bankroll={bankroll?.balance || 0}
              bankrollId={bankroll?.id || null}
              onBankrollCreated={() => {
                setMessage('')
                queryClient.invalidateQueries({ queryKey: queryKeys.bankrolls })
              }}
              onError={setMessage}
              onBalanceChanged={() => {
                setMessage('')
                queryClient.invalidateQueries({ queryKey: queryKeys.bankrolls })
              }}
              wonTotal={placedBets.filter(item => item.status === 'won')
                .reduce((sum, item) => sum + item.potentialReturn - item.stake, 0)}
              lostTotal={placedBets.filter(item => item.status === 'lost')
                .reduce((sum, item) => sum + item.stake, 0)}
              pending={placedBets.filter(item => item.status === 'pending').length}
            />
          } />
          <Route path="/bets" element={
            <FeaturePage title="MINHAS APOSTAS" subtitle="Histórico, pendências e liquidação manual">
              <BankrollView
                bets={placedBets}
                setBets={setPlacedBets}
                bankroll={bankroll?.balance || 0}
                bankrollId={bankroll?.id || null}
                onBankrollCreated={() => queryClient.invalidateQueries({ queryKey: queryKeys.bankrolls })}
                onError={setMessage}
                onBalanceChanged={() => queryClient.invalidateQueries({ queryKey: queryKeys.bankrolls })}
                wonTotal={0} lostTotal={0}
                pending={placedBets.filter(item => item.status === 'pending').length}
              />
            </FeaturePage>
          } />
          <Route path="/system" element={<SystemView maturity={maturityQuery.data} />} />
          <Route path="/analysis" element={<EnginePage kind="analysis" maturity={maturityQuery.data} />} />
          <Route path="/risk" element={<EnginePage kind="risk" maturity={maturityQuery.data} />} />
          <Route path="/statistics" element={<EnginePage kind="statistics" maturity={maturityQuery.data} />} />
          <Route path="/models" element={<EnginePage kind="models" maturity={maturityQuery.data} />} />
          <Route path="/recommendations" element={<EnginePage kind="recommendations" maturity={maturityQuery.data} />} />
          <Route path="/providers" element={<SystemView maturity={maturityQuery.data} />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      )}
      {betSlipOpen && (
        <BetSlipDrawer
          selections={betSlip}
          onRemove={id => setBetSlip(current => current.filter(item => item.id !== id))}
          onOddsChange={(id, odds) => setBetSlip(current => current.map(
            item => item.id === id ? { ...item, odds } : item,
          ))}
          onClose={() => setBetSlipOpen(false)}
          totalOdds={totalOdds}
          onPlace={placeCurrentBet}
        />
      )}
      {betSlip.length > 0 && !betSlipOpen && (
        <button className="floating-bet" onClick={() => setBetSlipOpen(true)}
          aria-label={`Abrir bilhete com ${betSlip.length} seleções`}>
          <Target size={18} />
          Bilhete ({betSlip.length})
          <strong>{totalOdds.toFixed(2)}x</strong>
        </button>
      )}
    </AppShell>
  )
}

function MatchRoute({
  fallbackMatches, favorites, toggleFavorite, betSlip, onAddBet,
}: {
  fallbackMatches: Match[]
  favorites: string[]
  toggleFavorite: (id: string) => void
  betSlip: BetSelection[]
  onAddBet: (
    matchId: string, matchName: string, market: string,
    option: string, odds: number,
  ) => void
}) {
  const { matchId = '' } = useParams()
  const navigate = useNavigate()
  const fallback = fallbackMatches.find(item => item.id === matchId)
  const query = useQuery({
    queryKey: ['match', matchId],
    queryFn: () => loadMatch(matchId),
    enabled: Boolean(matchId),
    placeholderData: fallback,
    staleTime: 15_000,
  })
  if (query.isPending || !query.data) return <LoadingScreen compact />
  if (query.error) {
    return <EmptyState title="Partida indisponível" action={() => navigate('/')} />
  }
  return (
    <MatchView
      match={query.data}
      betSlip={betSlip}
      onAddBet={onAddBet}
      onBack={() => navigate('/')}
      isFavorite={favorites.includes(matchId)}
      onToggleFavorite={() => toggleFavorite(matchId)}
    />
  )
}

function AppShell({
  children, betCount, onBetSlipOpen, refreshing, onRefresh,
}: {
  children: React.ReactNode
  betCount: number
  onBetSlipOpen: () => void
  refreshing: boolean
  onRefresh: () => void
}) {
  const [menuOpen, setMenuOpen] = useState(false)
  const location = useLocation()
  useEffect(() => setMenuOpen(false), [location.pathname])
  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="topbar-inner">
          <NavLink to="/" className="brand" aria-label="UltraStats AI — início">
            <span className="brand-icon"><Zap size={16} fill="currentColor" /></span>
            <span>ULTRASTATS AI</span>
          </NavLink>
          <div className="topbar-actions">
            <button className="icon-button" onClick={onRefresh}
              aria-label="Atualizar dados">
              <RefreshCw size={16} className={refreshing ? 'spin' : ''} />
            </button>
            {betCount > 0 && (
              <button className="bet-button" onClick={onBetSlipOpen}>
                <Target size={15} /> Bilhete <span>{betCount}</span>
              </button>
            )}
            <button className="feature-button" onClick={() => setMenuOpen(value => !value)}
              aria-expanded={menuOpen} aria-controls="feature-menu">
              {menuOpen ? <X size={16} /> : <Grid3X3 size={16} />}
              Funcionalidades
            </button>
            <button className="mobile-menu-button" onClick={() => setMenuOpen(value => !value)}
              aria-label={menuOpen ? 'Fechar menu' : 'Abrir menu'}>
              {menuOpen ? <X /> : <Menu />}
            </button>
          </div>
        </div>
      </header>
      <div className="workspace">
        <aside id="feature-menu" className={`sidebar ${menuOpen ? 'open' : ''}`}>
          <div className="sidebar-title">FUNCIONALIDADES</div>
          <nav aria-label="Funcionalidades principais">
            {navigation.map(({ to, label, icon: Icon }) => (
              <NavLink key={to} to={to} end={to === '/'}
                className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                <Icon size={16} /><span>{label}</span>
              </NavLink>
            ))}
          </nav>
          <NavLink to="/system" className="system-link">
            <FlaskConical size={16} /> Visão técnica
          </NavLink>
        </aside>
        {menuOpen && <button className="menu-backdrop" onClick={() => setMenuOpen(false)}
          aria-label="Fechar menu" />}
        <main className="content">{children}</main>
      </div>
    </div>
  )
}

function StatusBanner({
  message, onClose, retry = false,
}: {
  message: string
  onClose: () => void
  retry?: boolean
}) {
  return (
    <div className={`status-banner ${retry ? 'error' : ''}`} role={retry ? 'alert' : 'status'}>
      <span>{message}</span>
      <button onClick={onClose}>{retry ? 'Tentar novamente' : 'Fechar'}</button>
    </div>
  )
}

function LoadingScreen({ compact = false }: { compact?: boolean }) {
  return (
    <section className={`loading-screen ${compact ? 'compact' : ''}`} aria-live="polite">
      <div className="skeleton heading" />
      <div className="skeleton tabs" />
      {[1, 2, 3].map(item => <div className="skeleton card" key={item} />)}
      <span>Atualizando dados dos provedores…</span>
    </section>
  )
}

function EmptyState({ title, action }: { title: string; action: () => void }) {
  return (
    <section className="empty-state">
      <Activity size={28} />
      <h1>{title}</h1>
      <button onClick={action}>Voltar à central</button>
    </section>
  )
}

function FeaturePage({
  title, subtitle, children,
}: {
  title: string
  subtitle: string
  children: React.ReactNode
}) {
  return (
    <section>
      <div className="page-heading">
        <h1>{title}</h1>
        <p>{subtitle}</p>
      </div>
      {children}
    </section>
  )
}

const engineCopy = {
  analysis: ['ANÁLISES', 'Projeções organizadas por partida, mercado e confiança.'],
  risk: ['GESTÃO DE RISCO', 'Exposição, limites e qualidade antes da confirmação.'],
  statistics: ['MOTOR ESTATÍSTICO', 'Cobertura, evidência e atualização pós-partida.'],
  models: ['MODELOS E APRENDIZADO', 'Calibração, validação e evolução do machine learning.'],
  recommendations: ['RECOMENDAÇÕES', 'Oportunidades avaliadas com gates de segurança.'],
} as const

function EnginePage({
  kind, maturity,
}: {
  kind: keyof typeof engineCopy
  maturity: any
}) {
  const [title, subtitle] = engineCopy[kind]
  const quality = maturity?.quality_score
  const coverage = maturity?.coverage || {}
  return (
    <FeaturePage title={title} subtitle={subtitle}>
      <div className="engine-grid">
        <MetricCard label="Qualidade operacional"
          value={quality == null ? '—' : `${Math.round(quality * 100)}%`} />
        <MetricCard label="Estatísticas"
          value={coverage.statistics == null ? '—' : `${Math.round(coverage.statistics * 100)}%`} />
        <MetricCard label="Previsões"
          value={coverage.predictions == null ? '—' : `${Math.round(coverage.predictions * 100)}%`} />
        <MetricCard label="Odds"
          value={coverage.odds == null ? '—' : `${Math.round(coverage.odds * 100)}%`} />
      </div>
      <SystemView maturity={maturity} />
    </FeaturePage>
  )
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="metric-card">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  )
}

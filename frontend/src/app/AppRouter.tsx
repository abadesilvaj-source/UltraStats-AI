import { useCallback, useEffect, useState } from 'react'
import {
  BrowserRouter, NavLink, Navigate, Route, Routes,
  useLocation, useNavigate, useParams,
} from 'react-router-dom'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import {
  Activity, AlertTriangle, BarChart3, BrainCircuit, CheckCircle2, Database, FlaskConical,
  Grid3X3, Home, Menu, Receipt, RefreshCw, ShieldCheck, Star,
  Target, TrendingUp, Wallet, X, Zap,
} from 'lucide-react'
import {
  BankrollView, BetSlipDrawer, FavoritesView, HomeView, MatchView,
  SystemView,
} from '../App'
import type { BetSelection, Match, PlacedBet } from '../data'
import {
  analyzeBetSlip, loadBankrolls, loadBetSlips, loadMatch, loadMatches,
  loadIntelligence, loadMaturity, loadPredictions, loadRecommendations, placeBet,
} from '../api'
import type { PredictionDto, RecommendationDto } from '../api'

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
  predictions: ['predictions'] as const,
  recommendations: ['recommendations'] as const,
  intelligence: ['intelligence'] as const,
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
  const predictionsQuery = useQuery({
    queryKey: queryKeys.predictions,
    queryFn: loadPredictions,
    staleTime: 60_000,
    refetchInterval: 120_000,
  })
  const recommendationsQuery = useQuery({
    queryKey: queryKeys.recommendations,
    queryFn: loadRecommendations,
    staleTime: 60_000,
    refetchInterval: 120_000,
  })
  const intelligenceQuery = useQuery({
    queryKey: queryKeys.intelligence,
    queryFn: loadIntelligence,
    staleTime: 60_000,
    refetchInterval: 120_000,
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
    predictionsQuery.error, recommendationsQuery.error, intelligenceQuery.error,
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
          <Route path="/analysis" element={
            <AnalysisPage predictions={predictionsQuery.data || []} onOpenMatch={id => navigate(`/matches/${id}`)} />
          } />
          <Route path="/risk" element={
            <RiskPage recommendations={recommendationsQuery.data || []} onOpenMatch={id => navigate(`/matches/${id}`)} />
          } />
          <Route path="/statistics" element={
            <StatisticsPage maturity={maturityQuery.data} intelligence={intelligenceQuery.data} />
          } />
          <Route path="/models" element={
            <ModelsPage maturity={maturityQuery.data} intelligence={intelligenceQuery.data} />
          } />
          <Route path="/recommendations" element={
            <RecommendationsPage recommendations={recommendationsQuery.data || []} onOpenMatch={id => navigate(`/matches/${id}`)} />
          } />
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

function AnalysisPage({ predictions, onOpenMatch }: {
  predictions: PredictionDto[]; onOpenMatch: (id: number) => void
}) {
  const [evidence, setEvidence] = useState('all')
  const [search, setSearch] = useState('')
  const visible = predictions
    .filter(item => evidence === 'all' || item.evidence === evidence)
    .filter(item => `${item.match} ${item.market} ${item.competition}`.toLocaleLowerCase()
      .includes(search.toLocaleLowerCase()))
  return (
    <FeaturePage title="ANÁLISES" subtitle="Probabilidades produzidas pelo motor, organizadas por partida e mercado.">
      <div className="engine-grid">
        <MetricCard label="Previsões ativas" value={String(predictions.length)} />
        <MetricCard label="Partidas analisadas" value={String(new Set(predictions.map(item => item.match_id)).size)} />
        <MetricCard label="Evidência média/alta" value={String(predictions.filter(item => item.evidence !== 'low').length)} />
        <MetricCard label="Modelos ativos" value={String(new Set(predictions.map(item => item.model)).size)} />
      </div>
      <div className="data-toolbar">
        <input aria-label="Pesquisar análises" placeholder="Pesquisar partida, liga ou mercado…" value={search}
          onChange={event => setSearch(event.target.value)} />
        <select aria-label="Filtrar análises" value={evidence} onChange={event => setEvidence(event.target.value)}>
          <option value="all">Todas as evidências</option><option value="high">Evidência alta</option>
          <option value="medium">Evidência média</option><option value="low">Evidência baixa</option>
        </select>
      </div>
      <DataList empty="Nenhuma previsão encontrada com estes filtros.">
        {visible.slice(0, 120).map(item => (
          <button className="data-row" key={item.id} onClick={() => onOpenMatch(item.match_id)}>
            <div><strong>{item.match}</strong><span>{item.competition} · {item.market}</span></div>
            <div><strong>{item.selection}</strong><span>{Math.round(item.probability * 100)}% · {evidenceLabel(item.evidence)}</span></div>
          </button>
        ))}
      </DataList>
    </FeaturePage>
  )
}

function RiskPage({ recommendations, onOpenMatch }: {
  recommendations: RecommendationDto[]; onOpenMatch: (id: number) => void
}) {
  const primary = recommendations.filter(item => item.is_primary_recommendation)
  return (
    <FeaturePage title="GESTÃO DE RISCO" subtitle="Exposição, evidência e bloqueios avaliados antes da aposta.">
      <div className="engine-grid">
        <MetricCard label="Sugestões principais" value={String(primary.length)} />
        <MetricCard label="Valor confirmado" value={String(recommendations.filter(item => item.actionable).length)} />
        <MetricCard label="Não recomendados" value={String(recommendations.filter(item => item.no_bet).length)} />
        <MetricCard label="Risco alto" value={String(recommendations.filter(item => item.risk === 'high').length)} />
      </div>
      <section className="insight-panel">
        <div><ShieldCheck size={20} /><strong>Política de risco aplicada</strong></div>
        <p>Mercados de evidência baixa continuam disponíveis com aviso. Somente oportunidades aprovadas nos gates de valor, confiança e correlação são classificadas como acionáveis.</p>
      </section>
      <DataList empty="Nenhuma avaliação de risco disponível.">
        {primary.slice(0, 80).map(item => (
          <button className="data-row" key={`${item.match_id}-${item.market_id}`} onClick={() => onOpenMatch(item.match_id)}>
            <div><strong>{item.match}</strong><span>{item.market} · {item.selection}</span></div>
            <RiskBadge item={item} />
          </button>
        ))}
      </DataList>
    </FeaturePage>
  )
}

function StatisticsPage({ maturity, intelligence }: { maturity: any; intelligence: any }) {
  const statistics = intelligence?.statistics || {}
  const coverage = maturity?.coverage || {}
  const raw = maturity?.raw_coverage || {}
  return (
    <FeaturePage title="MOTOR ESTATÍSTICO" subtitle="Cobertura pós-jogo e atualização das estatísticas coletadas.">
      <div className="engine-grid">
        <MetricCard label="Partidas com estatísticas" value={String(statistics.matches_with_statistics ?? '—')} />
        <MetricCard label="Cobertura elegível" value={percent(coverage.statistics)} />
        <MetricCard label="Cobertura bruta" value={percent(raw.statistics)} />
        <MetricCard label="Tentativas em 24h" value={String(statistics.recent_attempts ?? '—')} />
      </div>
      <section className="insight-panel">
        <div><Activity size={20} /><strong>Última atualização estatística</strong></div>
        <p>{statistics.last_update ? formatDateTime(statistics.last_update) : 'Nenhuma atualização registrada.'}</p>
      </section>
      <CoverageBars items={[
        ['Estatísticas pós-jogo', coverage.statistics], ['Odds', coverage.odds],
        ['Previsões', coverage.predictions], ['Escalações', raw.lineups],
      ]} />
    </FeaturePage>
  )
}

function ModelsPage({ maturity, intelligence }: { maturity: any; intelligence: any }) {
  const learning = intelligence?.learning || {}
  const validation = learning.latest_validation
  const metrics = validation?.metrics || {}
  return (
    <FeaturePage title="MODELOS E APRENDIZADO" subtitle="Auditoria, validação e evolução do modelo preditivo.">
      <div className="engine-grid">
        <MetricCard label="Previsões auditadas" value={String(learning.audited_predictions ?? '—')} />
        <MetricCard label="Modelos registrados" value={String(learning.registered_models ?? '—')} />
        <MetricCard label="Datasets de treino" value={String(learning.training_datasets ?? '—')} />
        <MetricCard label="Cobertura preditiva" value={percent(maturity?.coverage?.predictions)} />
      </div>
      <section className={`insight-panel ${validation?.approved ? 'success' : 'warning'}`}>
        <div>{validation?.approved ? <CheckCircle2 size={20} /> : <AlertTriangle size={20} />}
          <strong>{validation ? (validation.approved ? 'Modelo aprovado no último gate' : 'Modelo ainda não aprovado') : 'Validação ainda não disponível'}</strong>
        </div>
        <p>{validation?.evaluated_at ? `Avaliado em ${formatDateTime(validation.evaluated_at)}` : 'O pipeline precisa acumular evidência auditada para uma validação conclusiva.'}</p>
      </section>
      <div className="model-metrics">
        {Object.entries(metrics).slice(0, 12).map(([key, value]) => (
          <div key={key}><span>{humanize(key)}</span><strong>{formatMetric(value)}</strong></div>
        ))}
        {!Object.keys(metrics).length && <p>Nenhuma métrica de validação consolidada disponível.</p>}
      </div>
    </FeaturePage>
  )
}

function RecommendationsPage({ recommendations, onOpenMatch }: {
  recommendations: RecommendationDto[]; onOpenMatch: (id: number) => void
}) {
  const [filter, setFilter] = useState('primary')
  const primary = recommendations.filter(item => item.is_primary_recommendation)
  const visible = filter === 'all' ? recommendations
    : filter === 'value' ? recommendations.filter(item => item.actionable) : primary
  return (
    <FeaturePage title="RECOMENDAÇÕES" subtitle="Melhor sugestão por partida, com indicação explícita de segurança.">
      <div className="engine-grid">
        <MetricCard label="Partidas cobertas" value={String(new Set(recommendations.map(item => item.match_id)).size)} />
        <MetricCard label="Sugestões principais" value={String(primary.length)} />
        <MetricCard label="Apostas de valor" value={String(recommendations.filter(item => item.actionable).length)} />
        <MetricCard label="Mercados avaliados" value={String(recommendations.length)} />
      </div>
      <div className="segmented-control">
        {[['primary', 'Melhores por partida'], ['value', 'Valor confirmado'], ['all', 'Todos os mercados']].map(([id, label]) => (
          <button key={id} className={filter === id ? 'active' : ''} onClick={() => setFilter(id)}>{label}</button>
        ))}
      </div>
      <DataList empty="Nenhuma recomendação disponível nesta categoria.">
        {visible.slice(0, 120).map(item => (
          <button className="recommendation-row" key={`${item.match_id}-${item.market_id}`} onClick={() => onOpenMatch(item.match_id)}>
            <div className="recommendation-icon"><TrendingUp size={17} /></div>
            <div><strong>{item.match}</strong><span>{item.market} · {item.selection}</span></div>
            <div className="recommendation-score"><strong>{Math.round(item.probability * 100)}%</strong><RiskBadge item={item} /></div>
          </button>
        ))}
      </DataList>
    </FeaturePage>
  )
}

function DataList({ children, empty }: { children: React.ReactNode; empty: string }) {
  const isEmpty = Array.isArray(children) && children.length === 0
  return <div className="data-list">{isEmpty ? <div className="data-empty">{empty}</div> : children}</div>
}

function RiskBadge({ item }: { item: RecommendationDto }) {
  const label = item.actionable ? 'Valor confirmado'
    : item.recommendation_type === 'model_pick' ? 'Melhor projeção' : 'Não recomendada'
  return <span className={`risk-badge ${item.actionable ? 'safe' : item.no_bet ? 'blocked' : 'projection'}`}>{label}</span>
}

function CoverageBars({ items }: { items: [string, number | undefined][] }) {
  return <div className="coverage-list">{items.map(([label, value]) => (
    <div key={label}><div><span>{label}</span><strong>{percent(value)}</strong></div>
      <progress max="1" value={value || 0} aria-label={`${label}: ${percent(value)}`} /></div>
  ))}</div>
}

const percent = (value?: number) => value == null ? '—' : `${Math.round(value * 100)}%`
const evidenceLabel = (value: string) => ({ high: 'Alta', medium: 'Média', low: 'Baixa' }[value] || value)
const formatDateTime = (value: string) => new Date(value).toLocaleString('pt-BR')
const humanize = (value: string) => value.replace(/_/g, ' ').replace(/^\w/, (letter: string) => letter.toUpperCase())
const formatMetric = (value: unknown) => typeof value === 'number'
  ? (value >= 0 && value <= 1 ? `${(value * 100).toFixed(1)}%` : value.toFixed(2))
  : String(value)

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="metric-card">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  )
}

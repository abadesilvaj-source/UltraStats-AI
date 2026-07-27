import type { Match, MatchAnalysis, MatchStats, Lineup, OddsMarket, PlacedBet } from './data'

const API = import.meta.env.VITE_API_URL || '/api/v1'

const emptyLineup = (): Lineup => ({ formation: '—', players: [], bench: [] })
const emptyStats = (): MatchStats => ({
  possession: [0, 0], shots: [0, 0], shotsOnTarget: [0, 0],
  corners: [0, 0], fouls: [0, 0], yellowCards: [0, 0],
  redCards: [0, 0], offsides: [0, 0], passes: [0, 0],
  passAccuracy: [0, 0], xG: [0, 0],
})
const emptyAnalysis = (): MatchAnalysis => ({
  summary: 'Análise processada pelo motor estatístico multifuente.',
  homeForm: [], awayForm: [], keyFactors: [], recommendations: [],
})

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!response.ok) {
    const body = await response.json().catch(() => ({ error: response.statusText }))
    throw new Error(body.error || 'Falha na API')
  }
  return response.json()
}

function team(item: any, home: boolean) {
  return {
    id: String(item.id),
    name: item.name,
    shortName: item.name.slice(0, 3).toUpperCase(),
    logo: item.name.slice(0, 2).toUpperCase(),
    color: home ? '#4f8ef7' : '#ff7c3a',
  }
}

function lineup(rows: any[], teamName: string): Lineup {
  const row = rows.find(entry =>
    entry.team?.name?.localeCompare(teamName, undefined, { sensitivity: 'base' }) === 0
  )
  if (!row) return emptyLineup()
  const players = (items: any[]) => items.map(player => ({
    number: Number(player.number || 0),
    name: player.name || 'Jogador não informado',
    position: player.pos || '—',
  }))
  return {
    formation: row.formation || '—',
    players: players(row.start_xi || []),
    bench: players(row.substitutes || []),
  }
}

function adapt(item: any): Match {
  const stats = item.statistics
  const availableStats = stats
    ? Object.entries(stats)
        .filter(([, value]) => value !== null && value !== undefined)
        .map(([key]) => key)
    : []
  const analysis = emptyAnalysis()
  const bestByMarket = new Map<string, any>()
  for (const row of item.recommendations || item.analysis || []) {
    const current = bestByMarket.get(row.market)
    if (!current || row.probability > current.probability) {
      bestByMarket.set(row.market, row)
    }
  }
  analysis.recommendations = Array.from(bestByMarket.values()).map(row => ({
    category: row.market_category || 'other',
    market: row.market,
    tip: row.display_selection || row.selection,
    projection: row.selection,
    noBet: Boolean(row.no_bet),
    primary: Boolean(row.is_primary_recommendation),
    recommendationType: row.recommendation_type,
    confidence: row.confidence >= .75 ? 'Alta' : row.confidence >= .55 ? 'Média' : 'Baixa',
    odds: row.implied_probability
      ? 1 / row.implied_probability
      : 1 / Math.max(row.probability, .01),
    reasoning: row.no_bet
      ? `Aposta não recomendada · margem entre cenários ${((row.probability_margin || 0) * 100).toFixed(1)}%`
      : row.recommendation_type === 'model_pick'
      ? `Melhor projeção disponível para a partida · ainda sem valor estatístico confirmado`
      : row.conservative_expected_value != null
      ? `EV conservador ${(row.conservative_expected_value * 100).toFixed(1)}% · ${row.actionable ? 'acionável' : 'bloqueada'}`
      : row.expected_value != null
      ? `EV ${(row.expected_value * 100).toFixed(1)}% · evidência ${row.evidence || 'limitada'}`
      : `Probabilidade ${(row.probability * 100).toFixed(1)}% · odd justa do modelo`,
  }))
  if (item.data_fusion?.provenance) {
    analysis.keyFactors = Object.entries(item.data_fusion.provenance).map(
      ([field, detail]: [string, any]) =>
        `${field}: ${detail.provider} · ${detail.contributors?.length || 1} fonte(s)`
    )
    analysis.summary = item.data_fusion.conflicts?.length
      ? `Dados conciliados com ${item.data_fusion.conflicts.length} divergência(s) resolvida(s) por qualidade, atualidade e consenso.`
      : 'Dados conciliados entre os provedores disponíveis, sem divergências relevantes.'
  }
  const lineups = item.lineups || []
  return {
    id: String(item.id),
    league: item.competition.name,
    leagueLogo: '⚽',
    country: item.competition.country || '',
    status: item.status === 'in_progress' ? 'live' : item.status === 'finished' ? 'finished' : 'upcoming',
    startTime: new Date(item.kickoff_at).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }),
    kickoffAt: item.kickoff_at,
    homeTeam: team(item.home_team, true),
    awayTeam: team(item.away_team, false),
    homeScore: item.score?.home ?? undefined,
    awayScore: item.score?.away ?? undefined,
    homeLineup: lineup(lineups, item.home_team.name),
    awayLineup: lineup(lineups, item.away_team.name),
    events: [],
    statsAvailable: availableStats.length > 0,
    availableStats,
    stats: stats ? {
      ...emptyStats(),
      possession: [stats.possession_home || 0, stats.possession_away || 0],
      shots: [stats.shots_home || 0, stats.shots_away || 0],
      shotsOnTarget: [stats.shots_on_target_home || 0, stats.shots_on_target_away || 0],
      corners: [stats.corners_home || 0, stats.corners_away || 0],
      yellowCards: [stats.yellow_cards_home || 0, stats.yellow_cards_away || 0],
      redCards: [stats.red_cards_home || 0, stats.red_cards_away || 0],
      offsides: [stats.offsides_home || 0, stats.offsides_away || 0],
      xG: [stats.xg_home || 0, stats.xg_away || 0],
    } : emptyStats(),
    markets: (item.markets || []).map((market: any): OddsMarket => ({
      id: String(market.id),
      name: market.name,
      options: market.options.map((option: any) => ({
        id: `${market.id}:${option.selection}`,
        label: option.selection,
        odds: option.odd,
      })),
    })),
    h2h: [],
    analysis,
  }
}

export async function loadMatches(): Promise<Match[]> {
  const rows = await request<any[]>(
    '/matches?status=scheduled,in_progress,finished&limit=500'
  )
  return rows.map(adapt)
}

export async function loadMatch(id: string): Promise<Match> {
  return adapt(await request(`/matches/${id}`))
}

export async function placeBet(payload: unknown) {
  return request('/bet-slips', { method: 'POST', body: JSON.stringify(payload) })
}

export async function settleBetLeg(
  slipId: string, legId: string, result: 'won' | 'lost' | 'void'
) {
  return request(`/bet-slips/${slipId}/legs/${legId}/settle`, {
    method: 'PATCH',
    body: JSON.stringify({ result }),
  })
}

export async function loadBetSlips(): Promise<PlacedBet[]> {
  const rows = await request<any[]>('/bet-slips')
  return rows.map(item => {
    const results = item.legs.map((leg: any) => leg.result || leg.status)
    const status: PlacedBet['status'] = item.status === 'pending'
      ? 'pending'
      : results.every((value: string) => value === 'won') ? 'won'
      : results.some((value: string) => value === 'lost') ? 'lost'
      : results.every((value: string) => value === 'void') ? 'void'
      : 'partial'
    return {
      id: String(item.id),
      selections: item.legs.map((leg: any) => ({
        id: String(leg.id),
        matchId: String(leg.match_id),
        matchName: leg.match,
        market: leg.market,
        marketId: leg.market_id,
        option: leg.selection,
        odds: leg.odd,
        status: leg.result || leg.status,
      })),
      stake: item.stake_amount,
      potentialReturn: item.payout_amount ?? item.potential_return,
      totalOdds: item.total_odds,
      date: new Date(item.placed_at).toLocaleDateString('pt-BR'),
      status,
    }
  })
}

export async function analyzeBetSlip(payload: unknown): Promise<any> {
  return request('/bet-slips/analyze', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function loadBankrolls(): Promise<any[]> {
  return request('/bankrolls')
}

export async function createBankroll(payload: {
  name: string
  initial_balance: number
  currency: string
  unit_percentage: number
}): Promise<any> {
  return request('/bankrolls', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function depositBankroll(bankrollId: number, amount: number) {
  return request(`/bankrolls/${bankrollId}/deposit`, {
    method: 'POST',
    body: JSON.stringify({ amount, description: 'Depósito pelo aplicativo' }),
  })
}

export async function withdrawBankroll(bankrollId: number, amount: number) {
  return request(`/bankrolls/${bankrollId}/withdraw`, {
    method: 'POST',
    body: JSON.stringify({ amount, description: 'Saque pelo aplicativo' }),
  })
}

export async function loadMaturity(): Promise<any> {
  return request('/maturity/status')
}

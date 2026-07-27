import type { Match, MatchAnalysis, MatchStats, Lineup, OddsMarket } from './data'

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
  const analysis = emptyAnalysis()
  const bestByMarket = new Map<string, any>()
  for (const row of item.analysis || []) {
    const current = bestByMarket.get(row.market)
    if (!current || row.probability > current.probability) {
      bestByMarket.set(row.market, row)
    }
  }
  analysis.recommendations = Array.from(bestByMarket.values()).map(row => ({
    market: row.market,
    tip: row.selection,
    confidence: row.confidence >= .75 ? 'Alta' : row.confidence >= .55 ? 'Média' : 'Baixa',
    odds: row.implied_probability
      ? 1 / row.implied_probability
      : 1 / Math.max(row.probability, .01),
    reasoning: row.expected_value != null
      ? `EV ${(row.expected_value * 100).toFixed(1)}% · evidência ${row.evidence || 'limitada'}`
      : `Probabilidade ${(row.probability * 100).toFixed(1)}% · odd justa do modelo`,
  }))
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
  const rows = await request<any[]>('/matches?status=scheduled,in_progress&limit=500')
  return rows.map(adapt)
}

export async function loadMatch(id: string): Promise<Match> {
  return adapt(await request(`/matches/${id}`))
}

export async function placeBet(payload: unknown) {
  return request('/bet-slips', { method: 'POST', body: JSON.stringify(payload) })
}

export async function loadBankrolls(): Promise<any[]> {
  return request('/bankrolls')
}

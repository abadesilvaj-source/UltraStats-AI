export type MatchStatus = 'live' | 'upcoming' | 'finished'

export interface Team {
  id: string
  name: string
  shortName: string
  logo: string
  color: string
}

export interface Player {
  number: number
  name: string
  position: string
}

export interface Lineup {
  formation: string
  players: Player[]
  bench: Player[]
}

export interface LiveEvent {
  id: string
  minute: number
  type: 'goal' | 'yellow' | 'red' | 'substitution' | 'var' | 'penalty'
  team: 'home' | 'away'
  player: string
  detail?: string
}

export interface MatchStats {
  possession: [number, number]
  shots: [number, number]
  shotsOnTarget: [number, number]
  corners: [number, number]
  fouls: [number, number]
  yellowCards: [number, number]
  redCards: [number, number]
  offsides: [number, number]
  passes: [number, number]
  passAccuracy: [number, number]
  xG: [number, number]
}

export interface OddsMarket {
  id: string
  name: string
  options: OddsOption[]
}

export interface OddsOption {
  id: string
  label: string
  odds: number
}

export interface Match {
  id: string
  league: string
  leagueLogo: string
  country: string
  status: MatchStatus
  minute?: number
  startTime: string
  kickoffAt?: string
  homeTeam: Team
  awayTeam: Team
  homeScore?: number
  awayScore?: number
  homeLineup: Lineup
  awayLineup: Lineup
  events: LiveEvent[]
  stats: MatchStats
  markets: OddsMarket[]
  h2h: H2HMatch[]
  analysis: MatchAnalysis
}

export interface H2HMatch {
  date: string
  homeTeam: string
  awayTeam: string
  homeScore: number
  awayScore: number
  competition: string
}

export interface MatchAnalysis {
  summary: string
  homeForm: string[]
  awayForm: string[]
  keyFactors: string[]
  recommendations: Recommendation[]
}

export interface Recommendation {
  market: string
  tip: string
  projection?: string
  noBet?: boolean
  primary?: boolean
  recommendationType?: string
  confidence: 'Alta' | 'Média' | 'Baixa'
  odds: number
  reasoning: string
}

export interface BetSelection {
  id: string
  matchId: string
  matchName: string
  market: string
  marketId?: number
  option: string
  odds: number
  status?: 'pending' | 'won' | 'lost' | 'cashout'
}

export interface PlacedBet {
  id: string
  selections: BetSelection[]
  stake: number
  potentialReturn: number
  totalOdds: number
  date: string
  status: 'pending' | 'won' | 'lost' | 'partial'
}

const arsenal: Team = {
  id: 'ars',
  name: 'Arsenal',
  shortName: 'ARS',
  logo: '🔴',
  color: '#EF0107',
}
const mancity: Team = {
  id: 'mci',
  name: 'Manchester City',
  shortName: 'MCI',
  logo: '🔵',
  color: '#6CABDD',
}
const liverpool: Team = {
  id: 'liv',
  name: 'Liverpool',
  shortName: 'LIV',
  logo: '🔴',
  color: '#C8102E',
}
const chelsea: Team = {
  id: 'che',
  name: 'Chelsea',
  shortName: 'CHE',
  logo: '🔵',
  color: '#034694',
}
const barcelona: Team = {
  id: 'bar',
  name: 'Barcelona',
  shortName: 'BAR',
  logo: '🔵',
  color: '#004D98',
}
const realmadrid: Team = {
  id: 'rma',
  name: 'Real Madrid',
  shortName: 'RMA',
  logo: '⚪',
  color: '#FEBE10',
}
const psg: Team = {
  id: 'psg',
  name: 'PSG',
  shortName: 'PSG',
  logo: '🔵',
  color: '#003399',
}
const dortmund: Team = {
  id: 'bvb',
  name: 'Borussia Dortmund',
  shortName: 'BVB',
  logo: '🟡',
  color: '#FDE100',
}
const atletico: Team = {
  id: 'atm',
  name: 'Atlético Madrid',
  shortName: 'ATM',
  logo: '🔴',
  color: '#CE3524',
}
const inter: Team = {
  id: 'int',
  name: 'Inter de Milão',
  shortName: 'INT',
  logo: '⚫',
  color: '#010E80',
}
const napoli: Team = {
  id: 'nap',
  name: 'Napoli',
  shortName: 'NAP',
  logo: '🔵',
  color: '#12A0C3',
}
const juventus: Team = {
  id: 'juv',
  name: 'Juventus',
  shortName: 'JUV',
  logo: '⚫',
  color: '#000000',
}

function makeLineup(names: string[], formation: string): Lineup {
  const positions = ['GK', 'DEF', 'DEF', 'DEF', 'DEF', 'MID', 'MID', 'MID', 'FWD', 'FWD', 'FWD']
  return {
    formation,
    players: names.slice(0, 11).map((name, i) => ({
      number: i + 1,
      name,
      position: positions[i],
    })),
    bench: names.slice(11).map((name, i) => ({
      number: i + 12,
      name,
      position: 'SUB',
    })),
  }
}

function makeMarkets(homeTeam: string, awayTeam: string): OddsMarket[] {
  return [
    {
      id: 'result',
      name: 'Resultado Final (1X2)',
      options: [
        { id: '1', label: `${homeTeam}`, odds: 2.1 },
        { id: 'X', label: 'Empate', odds: 3.4 },
        { id: '2', label: `${awayTeam}`, odds: 3.6 },
      ],
    },
    {
      id: 'dc',
      name: 'Dupla Chance',
      options: [
        { id: '1X', label: `${homeTeam} ou Empate`, odds: 1.32 },
        { id: '12', label: `${homeTeam} ou ${awayTeam}`, odds: 1.48 },
        { id: 'X2', label: `Empate ou ${awayTeam}`, odds: 2.05 },
      ],
    },
    {
      id: 'btts',
      name: 'Ambas Marcam',
      options: [
        { id: 'yes', label: 'Sim', odds: 1.75 },
        { id: 'no', label: 'Não', odds: 2.1 },
      ],
    },
    {
      id: 'ou25',
      name: 'Total de Gols — Over/Under 2.5',
      options: [
        { id: 'o25', label: 'Over 2.5', odds: 1.88 },
        { id: 'u25', label: 'Under 2.5', odds: 1.96 },
      ],
    },
    {
      id: 'ou15',
      name: 'Total de Gols — Over/Under 1.5',
      options: [
        { id: 'o15', label: 'Over 1.5', odds: 1.3 },
        { id: 'u15', label: 'Under 1.5', odds: 3.5 },
      ],
    },
    {
      id: 'ou35',
      name: 'Total de Gols — Over/Under 3.5',
      options: [
        { id: 'o35', label: 'Over 3.5', odds: 3.1 },
        { id: 'u35', label: 'Under 3.5', odds: 1.35 },
      ],
    },
    {
      id: 'ah',
      name: 'Handicap Asiático',
      options: [
        { id: 'ah-1', label: `${homeTeam} -1`, odds: 2.8 },
        { id: 'ah0', label: 'Linha Zero', odds: 1.95 },
        { id: 'ah+1', label: `${awayTeam} +1`, odds: 1.55 },
      ],
    },
    {
      id: 'corners',
      name: 'Total de Escanteios',
      options: [
        { id: 'co9', label: 'Over 9.5', odds: 1.78 },
        { id: 'cu9', label: 'Under 9.5', odds: 2.02 },
      ],
    },
    {
      id: 'firstgoal',
      name: 'Primeiro Gol',
      options: [
        { id: 'fg1', label: `${homeTeam} Marca Primeiro`, odds: 1.9 },
        { id: 'ng', label: 'Sem Gols', odds: 8.0 },
        { id: 'fg2', label: `${awayTeam} Marca Primeiro`, odds: 2.6 },
      ],
    },
    {
      id: 'ht',
      name: 'Resultado no Intervalo',
      options: [
        { id: 'ht1', label: `${homeTeam} Vence`, odds: 2.9 },
        { id: 'htx', label: 'Empate', odds: 2.2 },
        { id: 'ht2', label: `${awayTeam} Vence`, odds: 4.5 },
      ],
    },
  ]
}

export const matches: Match[] = [
  {
    id: 'm1',
    league: 'Premier League',
    leagueLogo: '🏴󠁧󠁢󠁥󠁮󠁧󠁿',
    country: 'Inglaterra',
    status: 'live',
    minute: 67,
    startTime: '17:00',
    homeTeam: arsenal,
    awayTeam: mancity,
    homeScore: 1,
    awayScore: 1,
    homeLineup: makeLineup(
      ['Raya', 'White', 'Saliba', 'Gabriel', 'Zinchenko', 'Partey', 'Rice', 'Ødegaard', 'Saka', 'Havertz', 'Martinelli', 'Tomiyasu', 'Kiwior', 'Jorginho', 'Smith Rowe'],
      '4-3-3',
    ),
    awayLineup: makeLineup(
      ['Ederson', 'Walker', 'Rúben Dias', 'Akanji', 'Gvardiol', 'Rodri', 'Bernardo', 'De Bruyne', 'Doku', 'Haaland', 'Foden', 'Stones', 'Kovacic', 'Grealish', 'Bobb'],
      '4-3-3',
    ),
    events: [
      { id: 'e1', minute: 23, type: 'goal', team: 'home', player: 'Havertz', detail: 'Cabeça após escanteio de Saka' },
      { id: 'e2', minute: 38, type: 'yellow', team: 'away', player: 'Rodri', detail: 'Falta dura em Rice' },
      { id: 'e3', minute: 51, type: 'goal', team: 'away', player: 'Haaland', detail: 'Finalização de dentro da área após passe de De Bruyne' },
      { id: 'e4', minute: 58, type: 'substitution', team: 'home', player: 'Martinelli → Smith Rowe', detail: '' },
      { id: 'e5', minute: 63, type: 'yellow', team: 'home', player: 'Partey', detail: 'Falta em Bernardo Silva' },
      { id: 'e6', minute: 66, type: 'var', team: 'home', player: 'Verificação VAR', detail: 'Possível pênalti em Saka — revisado, jogo continua' },
    ],
    stats: {
      possession: [54, 46],
      shots: [12, 9],
      shotsOnTarget: [5, 4],
      corners: [6, 3],
      fouls: [11, 13],
      yellowCards: [1, 1],
      redCards: [0, 0],
      offsides: [2, 3],
      passes: [487, 413],
      passAccuracy: [88, 85],
      xG: [1.62, 1.38],
    },
    markets: makeMarkets('Arsenal', 'Man City'),
    h2h: [
      { date: '03/03/2024', homeTeam: 'Arsenal', awayTeam: 'Man City', homeScore: 0, awayScore: 0, competition: 'Premier League' },
      { date: '08/10/2023', homeTeam: 'Man City', awayTeam: 'Arsenal', homeScore: 0, awayScore: 1, competition: 'Premier League' },
      { date: '22/04/2023', homeTeam: 'Man City', awayTeam: 'Arsenal', homeScore: 4, awayScore: 1, competition: 'Premier League' },
      { date: '01/01/2023', homeTeam: 'Arsenal', awayTeam: 'Man City', homeScore: 1, awayScore: 3, competition: 'Premier League' },
      { date: '10/04/2022', homeTeam: 'Man City', awayTeam: 'Arsenal', homeScore: 2, awayScore: 2, competition: 'Premier League' },
    ],
    analysis: {
      summary: 'Clássico eletrizante do futebol inglês. Arsenal busca manter a vantagem na tabela enquanto o City tenta confirmar favoritismo fora de casa. Partida equilibrada com ambos buscando o gol da vitória.',
      homeForm: ['V', 'V', 'E', 'V', 'D'],
      awayForm: ['V', 'V', 'V', 'E', 'V'],
      keyFactors: [
        'Arsenal com 87% de aproveitamento em casa nas últimas 8 rodadas',
        'Haaland marcou em 5 dos últimos 6 confrontos diretos',
        'Rice ausente nas últimas 2 partidas — retorna neste confronto',
        'City venceu 3 dos últimos 5 jogos como visitante contra top-6',
        'Árbitro apita em média 2.8 cartões amarelos por partida desta temporada',
      ],
      recommendations: [
        {
          market: 'Ambas Marcam — Sim',
          tip: 'Sim',
          confidence: 'Alta',
          odds: 1.75,
          reasoning: 'Arsenal e City marcaram em 9 dos últimos 10 H2H. Ambas as defesas sofrem pressão intensa e os ataques são letais.',
        },
        {
          market: 'Total de Gols — Over 2.5',
          tip: 'Over 2.5',
          confidence: 'Alta',
          odds: 1.88,
          reasoning: 'Média combinada de 3.4 gols nos últimos 5 H2H. Momento ofensivo de ambas as equipes é excelente.',
        },
        {
          market: 'Total de Escanteios — Over 9.5',
          tip: 'Over 9.5',
          confidence: 'Média',
          odds: 1.78,
          reasoning: 'City gera 6.2 escanteios por jogo, Arsenal 5.1. Média combinada historicamente acima de 10 neste confronto.',
        },
      ],
    },
  },
  {
    id: 'm2',
    league: 'La Liga',
    leagueLogo: '🇪🇸',
    country: 'Espanha',
    status: 'live',
    minute: 34,
    startTime: '17:30',
    homeTeam: barcelona,
    awayTeam: atletico,
    homeScore: 2,
    awayScore: 0,
    homeLineup: makeLineup(
      ['Ter Stegen', 'Koundé', 'Araujo', 'Christensen', 'Balde', 'Pedri', 'Gavi', 'De Jong', 'Yamal', 'Lewandowski', 'Raphinha', 'Íñigo Martínez', 'Fermín', 'Torres', 'Vitor Roque'],
      '4-3-3',
    ),
    awayLineup: makeLineup(
      ['Oblak', 'Molina', 'Savic', 'Witsel', 'Reinildo', 'Koke', 'Barrios', 'Lino', 'De Paul', 'Morata', 'Correa', 'Hermoso', 'Marcos Llorente', 'Riquelme', 'Griezmann'],
      '4-4-2',
    ),
    events: [
      { id: 'e1', minute: 12, type: 'goal', team: 'home', player: 'Lewandowski', detail: 'Pênalti convertido com maestria' },
      { id: 'e2', minute: 28, type: 'yellow', team: 'away', player: 'Savic', detail: 'Falta violenta em Yamal' },
      { id: 'e3', minute: 31, type: 'goal', team: 'home', player: 'Raphinha', detail: 'Chute de fora da área no ângulo direito' },
    ],
    stats: {
      possession: [62, 38],
      shots: [9, 3],
      shotsOnTarget: [5, 1],
      corners: [5, 1],
      fouls: [7, 12],
      yellowCards: [0, 1],
      redCards: [0, 0],
      offsides: [1, 2],
      passes: [389, 218],
      passAccuracy: [91, 78],
      xG: [2.1, 0.42],
    },
    markets: makeMarkets('Barcelona', 'Atlético Madrid'),
    h2h: [
      { date: '25/02/2024', homeTeam: 'Atlético Madrid', awayTeam: 'Barcelona', homeScore: 1, awayScore: 1, competition: 'La Liga' },
      { date: '04/10/2023', homeTeam: 'Barcelona', awayTeam: 'Atlético Madrid', homeScore: 1, awayScore: 0, competition: 'La Liga' },
      { date: '06/03/2023', homeTeam: 'Barcelona', awayTeam: 'Atlético Madrid', homeScore: 1, awayScore: 0, competition: 'La Liga' },
      { date: '06/11/2022', homeTeam: 'Atlético Madrid', awayTeam: 'Barcelona', homeScore: 1, awayScore: 0, competition: 'La Liga' },
      { date: '06/02/2022', homeTeam: 'Atlético Madrid', awayTeam: 'Barcelona', homeScore: 0, awayScore: 4, competition: 'La Liga' },
    ],
    analysis: {
      summary: 'Barcelona domina o confronto no Camp Nou com posse avassaladora. Atlético tenta se reorganizar defensivamente após dois gols sofridos de forma rápida. Lewandowski em excelente forma.',
      homeForm: ['V', 'V', 'V', 'D', 'V'],
      awayForm: ['E', 'V', 'D', 'V', 'V'],
      keyFactors: [
        'Barcelona não perde em casa há 14 partidas consecutivas',
        'Atlético Madrid não marcou fora de casa nas últimas 3 partidas',
        'Yamal é o jogador mais dribláveis da La Liga com 5.2 por jogo',
        'Oblak com 78% de defesas difíceis — pode limitar o placar',
      ],
      recommendations: [
        {
          market: 'Resultado Final',
          tip: 'Barcelona',
          confidence: 'Alta',
          odds: 1.55,
          reasoning: 'Barcelona invicto em casa há 14 partidas. Atlético sem gols fora. Domínio total na partida até agora.',
        },
        {
          market: 'Total de Gols — Over 2.5',
          tip: 'Over 2.5',
          confidence: 'Alta',
          odds: 1.88,
          reasoning: '2 gols já marcados aos 34 minutos. Barcelona com 2.1 xG e pressão constante.',
        },
      ],
    },
  },
  {
    id: 'm3',
    league: 'Champions League',
    leagueLogo: '⭐',
    country: 'Europa',
    status: 'upcoming',
    startTime: '21:00',
    homeTeam: realmadrid,
    awayTeam: psg,
    homeLineup: makeLineup(
      ['Lunin', 'Carvajal', 'Militão', 'Rüdiger', 'Mendy', 'Valverde', 'Tchouaméni', 'Camavinga', 'Bellingham', 'Vini Jr', 'Rodrygo', 'Nacho', 'Kroos', 'Modric', 'Joselu'],
      '4-3-3',
    ),
    awayLineup: makeLineup(
      ['Donnarumma', 'Hakimi', 'Marquinhos', 'Skriniar', 'Hernández', 'Zaire-Emery', 'Vitinha', 'Ruiz', 'Dembélé', 'Mbappé', 'Barcola', 'Beraldo', 'Ugarte', 'Kolo Muani', 'Gonçalo Ramos'],
      '4-3-3',
    ),
    events: [],
    stats: {
      possession: [50, 50],
      shots: [0, 0],
      shotsOnTarget: [0, 0],
      corners: [0, 0],
      fouls: [0, 0],
      yellowCards: [0, 0],
      redCards: [0, 0],
      offsides: [0, 0],
      passes: [0, 0],
      passAccuracy: [0, 0],
      xG: [0, 0],
    },
    markets: makeMarkets('Real Madrid', 'PSG'),
    h2h: [
      { date: '09/03/2022', homeTeam: 'Real Madrid', awayTeam: 'PSG', homeScore: 3, awayScore: 1, competition: 'Champions League' },
      { date: '15/02/2022', homeTeam: 'PSG', awayTeam: 'Real Madrid', homeScore: 1, awayScore: 0, competition: 'Champions League' },
      { date: '03/04/2018', homeTeam: 'Real Madrid', awayTeam: 'PSG', homeScore: 2, awayScore: 1, competition: 'Champions League' },
      { date: '14/02/2018', homeTeam: 'PSG', awayTeam: 'Real Madrid', homeScore: 1, awayScore: 3, competition: 'Champions League' },
      { date: '25/10/2017', homeTeam: 'PSG', awayTeam: 'Real Madrid', homeScore: 1, awayScore: 1, competition: 'Champions League' },
    ],
    analysis: {
      summary: 'Mata-mata dos sonhos na Champions League. Real Madrid favorito em casa pelo histórico europeu invejável, mas PSG traz Mbappé em estado de graça com 8 gols nos últimos 5 jogos europeus.',
      homeForm: ['V', 'V', 'E', 'V', 'V'],
      awayForm: ['V', 'V', 'V', 'V', 'D'],
      keyFactors: [
        'Real Madrid venceu 7 dos últimos 8 jogos em casa na Champions',
        'Mbappé marcou em 4 partidas consecutivas de Champions',
        'Bellingham é o maior criador de chances do Real com 4.1 por jogo',
        'PSG sem vencer no Bernabéu em 4 tentativas',
        'Vinícius Júnior com 5 gols e 3 assistências na Champions esta temporada',
      ],
      recommendations: [
        {
          market: 'Resultado Final',
          tip: 'Real Madrid',
          confidence: 'Média',
          odds: 2.1,
          reasoning: 'Real Madrid favorito em casa. Histórico de 3 vitórias nos últimos 4 H2H. "Magic" europeu do clube joga a favor.',
        },
        {
          market: 'Ambas Marcam — Sim',
          tip: 'Sim',
          confidence: 'Alta',
          odds: 1.75,
          reasoning: 'Ambas equipes com ataques letais. PSG e Real marcaram em todos os H2H recentes. Partida aberta está prevista.',
        },
        {
          market: 'Total de Gols — Over 2.5',
          tip: 'Over 2.5',
          confidence: 'Alta',
          odds: 1.88,
          reasoning: 'Média de 3.8 gols nos últimos 5 H2H. Dois dos maiores ataques do mundo em campo.',
        },
      ],
    },
  },
  {
    id: 'm4',
    league: 'Premier League',
    leagueLogo: '🏴󠁧󠁢󠁥󠁮󠁧󠁿',
    country: 'Inglaterra',
    status: 'upcoming',
    startTime: '19:30',
    homeTeam: liverpool,
    awayTeam: chelsea,
    homeLineup: makeLineup(
      ['Alisson', 'Alexander-Arnold', 'Konate', 'Van Dijk', 'Robertson', 'Szoboszlai', 'Mac Allister', 'Gravenberch', 'Salah', 'Núñez', 'Díaz', 'Tsimikas', 'Endo', 'Elliott', 'Jota'],
      '4-3-3',
    ),
    awayLineup: makeLineup(
      ['Sánchez', 'Gusto', 'Chalobah', 'Thiago Silva', 'Colwill', 'Caicedo', 'Enzo', 'Gallagher', 'Mudryk', 'Jackson', 'Sterling', 'Disasi', 'Kovacic', 'Nkunku', 'Palmer'],
      '4-3-3',
    ),
    events: [],
    stats: {
      possession: [50, 50],
      shots: [0, 0],
      shotsOnTarget: [0, 0],
      corners: [0, 0],
      fouls: [0, 0],
      yellowCards: [0, 0],
      redCards: [0, 0],
      offsides: [0, 0],
      passes: [0, 0],
      passAccuracy: [0, 0],
      xG: [0, 0],
    },
    markets: makeMarkets('Liverpool', 'Chelsea'),
    h2h: [
      { date: '13/01/2024', homeTeam: 'Liverpool', awayTeam: 'Chelsea', homeScore: 4, awayScore: 1, competition: 'Premier League' },
      { date: '02/04/2023', homeTeam: 'Liverpool', awayTeam: 'Chelsea', homeScore: 2, awayScore: 2, competition: 'Premier League' },
      { date: '21/01/2023', homeTeam: 'Chelsea', awayTeam: 'Liverpool', homeScore: 0, awayScore: 0, competition: 'Premier League' },
      { date: '18/09/2022', homeTeam: 'Liverpool', awayTeam: 'Chelsea', homeScore: 1, awayScore: 1, competition: 'Premier League' },
      { date: '22/01/2022', homeTeam: 'Chelsea', awayTeam: 'Liverpool', homeScore: 2, awayScore: 2, competition: 'Premier League' },
    ],
    analysis: {
      summary: 'Duelo de prestígio em Anfield. Liverpool chega em boa fase após sequência de 4 vitórias seguidas. Chelsea busca recuperar desempenho após resultados inconsistentes.',
      homeForm: ['V', 'V', 'V', 'V', 'E'],
      awayForm: ['D', 'V', 'E', 'D', 'V'],
      keyFactors: [
        'Salah marcou em 5 dos últimos 6 jogos em casa',
        'Chelsea sem vencer no Anfield nas últimas 5 visitas',
        'Van Dijk com 91% de duelos vencidos nesta temporada',
        'Palmer é o maior criador de ameaças do Chelsea com 2.8 chances criadas por jogo',
      ],
      recommendations: [
        {
          market: 'Resultado Final',
          tip: 'Liverpool',
          confidence: 'Alta',
          odds: 1.78,
          reasoning: 'Liverpool favorito em casa com sequência de 4 vitórias. Chelsea sem vencer no Anfield nas últimas 5 visitas.',
        },
        {
          market: 'Ambas Marcam — Sim',
          tip: 'Sim',
          confidence: 'Média',
          odds: 1.75,
          reasoning: 'Chelsea tem ataque perigoso com Palmer. Ambas marcaram em 4 dos últimos 5 H2H.',
        },
      ],
    },
  },
  {
    id: 'm5',
    league: 'Serie A',
    leagueLogo: '🇮🇹',
    country: 'Itália',
    status: 'upcoming',
    startTime: '20:45',
    homeTeam: inter,
    awayTeam: napoli,
    homeLineup: makeLineup(
      ['Sommer', 'Pavard', 'De Vrij', 'Bastoni', 'Dumfries', 'Barella', 'Çalhanoğlu', 'Mkhitaryan', 'Dimarco', 'Thuram', 'Lautaro', 'Darmian', 'Frattesi', 'Arnautovic', 'Asllani'],
      '3-5-2',
    ),
    awayLineup: makeLineup(
      ['Meret', 'Di Lorenzo', 'Rrahmani', 'Juan Jesus', 'Mario Rui', 'Lobotka', 'Anguissa', 'Zielinski', 'Politano', 'Osimhen', 'Kvaratskhelia', 'Natan', 'Elmas', 'Raspadori', 'Simeone'],
      '4-3-3',
    ),
    events: [],
    stats: {
      possession: [50, 50],
      shots: [0, 0],
      shotsOnTarget: [0, 0],
      corners: [0, 0],
      fouls: [0, 0],
      yellowCards: [0, 0],
      redCards: [0, 0],
      offsides: [0, 0],
      passes: [0, 0],
      passAccuracy: [0, 0],
      xG: [0, 0],
    },
    markets: makeMarkets('Inter de Milão', 'Napoli'),
    h2h: [
      { date: '17/12/2023', homeTeam: 'Inter', awayTeam: 'Napoli', homeScore: 0, awayScore: 0, competition: 'Serie A' },
      { date: '21/05/2023', homeTeam: 'Napoli', awayTeam: 'Inter', homeScore: 3, awayScore: 1, competition: 'Serie A' },
      { date: '04/01/2023', homeTeam: 'Inter', awayTeam: 'Napoli', homeScore: 1, awayScore: 0, competition: 'Serie A' },
      { date: '13/11/2022', homeTeam: 'Napoli', awayTeam: 'Inter', homeScore: 3, awayScore: 2, competition: 'Serie A' },
      { date: '12/02/2022', homeTeam: 'Inter', awayTeam: 'Napoli', homeScore: 2, awayScore: 0, competition: 'Serie A' },
    ],
    analysis: {
      summary: 'Confronto de gigantes italianos no Giuseppe Meazza. Inter busca consolidar liderança enquanto Napoli tenta surpreender longe de Nápoles com Osimhen e Kvaratskhelia.',
      homeForm: ['V', 'E', 'V', 'V', 'V'],
      awayForm: ['V', 'V', 'D', 'V', 'E'],
      keyFactors: [
        'Inter com 5 vitórias nos últimos 7 jogos em casa',
        'Osimhen marcou em 3 dos últimos 4 jogos fora',
        'Lautaro Martínez artilheiro da Serie A com 21 gols',
        'Kvaratskhelia é o jogador com mais dribles bem-sucedidos da Liga',
      ],
      recommendations: [
        {
          market: 'Resultado Final',
          tip: 'Inter de Milão',
          confidence: 'Média',
          odds: 2.2,
          reasoning: 'Inter forte em casa e com superioridade técnica no meio-campo. Lautaro em excelente forma.',
        },
        {
          market: 'Ambas Marcam — Sim',
          tip: 'Sim',
          confidence: 'Alta',
          odds: 1.75,
          reasoning: 'Napoli com Osimhen é ameaça constante. Inter com Lautaro letal. 4 dos últimos 5 H2H tiveram gols dos dois lados.',
        },
      ],
    },
  },
  {
    id: 'm6',
    league: 'Champions League',
    leagueLogo: '⭐',
    country: 'Europa',
    status: 'finished',
    startTime: '21:00',
    homeTeam: dortmund,
    awayTeam: juventus,
    homeScore: 2,
    awayScore: 1,
    homeLineup: makeLineup(
      ['Kobel', 'Ryerson', 'Hummels', 'Schlotterbeck', 'Maatsen', 'Can', 'Kramer', 'Brandt', 'Sancho', 'Fullkrug', 'Adeyemi', 'Wolf', 'Nmecha', 'Moukoko', 'Bensebaini'],
      '4-2-3-1',
    ),
    awayLineup: makeLineup(
      ['Szczesny', 'Danilo', 'Bremer', 'Gatti', 'Cambiaso', 'Locatelli', 'Rabiot', 'McKennie', 'Kostic', 'Vlahovic', 'Chiesa', 'Alex Sandro', 'Rugani', 'Yildiz', 'Milik'],
      '4-2-3-1',
    ),
    events: [
      { id: 'e1', minute: 15, type: 'goal', team: 'home', player: 'Fullkrug', detail: 'Cabeça em cruzamento de Maatsen' },
      { id: 'e2', minute: 40, type: 'goal', team: 'away', player: 'Vlahovic', detail: 'Pênalti após mão na bola de Schlotterbeck' },
      { id: 'e3', minute: 55, type: 'yellow', team: 'away', player: 'Rabiot', detail: 'Falta em Brandt' },
      { id: 'e4', minute: 71, type: 'goal', team: 'home', player: 'Adeyemi', detail: 'Velocidade em profundidade e finalização precisa' },
      { id: 'e5', minute: 88, type: 'red', team: 'away', player: 'Locatelli', detail: 'Segundo cartão amarelo' },
    ],
    stats: {
      possession: [48, 52],
      shots: [14, 10],
      shotsOnTarget: [6, 4],
      corners: [7, 4],
      fouls: [13, 17],
      yellowCards: [2, 3],
      redCards: [0, 1],
      offsides: [3, 2],
      passes: [421, 468],
      passAccuracy: [83, 87],
      xG: [1.82, 1.24],
    },
    markets: makeMarkets('Dortmund', 'Juventus'),
    h2h: [
      { date: '13/04/2022', homeTeam: 'Juventus', awayTeam: 'Dortmund', homeScore: 3, awayScore: 0, competition: 'Champions League' },
      { date: '07/11/2019', homeTeam: 'Dortmund', awayTeam: 'Juventus', homeScore: 0, awayScore: 1, competition: 'Champions League' },
      { date: '18/10/2019', homeTeam: 'Juventus', awayTeam: 'Dortmund', homeScore: 2, awayScore: 1, competition: 'Champions League' },
      { date: '13/03/2013', homeTeam: 'Juventus', awayTeam: 'Dortmund', homeScore: 0, awayScore: 2, competition: 'Champions League' },
      { date: '13/02/2013', homeTeam: 'Dortmund', awayTeam: 'Juventus', homeScore: 3, awayScore: 0, competition: 'Champions League' },
    ],
    analysis: {
      summary: 'Dortmund venceu a Juventus no Signal Iduna Park em jogo emocionante. Fullkrug e Adeyemi foram os heróis do jogo. Juve perde Locatelli para o jogo de volta.',
      homeForm: ['V', 'V', 'D', 'V', 'E'],
      awayForm: ['E', 'V', 'V', 'D', 'V'],
      keyFactors: [
        'Dortmund venceu os últimos 3 jogos em casa na Champions',
        'Vlahovic marcou em 4 Champions seguidas',
        'Locatelli expulso — desfalque para a volta',
      ],
      recommendations: [],
    },
  },
]

export const initialBankroll: PlacedBet[] = [
  {
    id: 'b1',
    selections: [
      { id: 's1', matchId: 'm3', matchName: 'Real Madrid vs PSG', market: 'Ambas Marcam', option: 'Sim', odds: 1.75, status: 'won' },
      { id: 's2', matchId: 'm4', matchName: 'Liverpool vs Chelsea', market: 'Resultado Final', option: 'Liverpool', odds: 1.78, status: 'won' },
    ],
    stake: 50,
    potentialReturn: 155.75,
    totalOdds: 3.115,
    date: '26/07/2025',
    status: 'won',
  },
  {
    id: 'b2',
    selections: [
      { id: 's3', matchId: 'm1', matchName: 'Arsenal vs Man City', market: 'Total de Gols', option: 'Over 2.5', odds: 1.88, status: 'pending' },
    ],
    stake: 30,
    potentialReturn: 56.4,
    totalOdds: 1.88,
    date: '27/07/2025',
    status: 'pending',
  },
  {
    id: 'b3',
    selections: [
      { id: 's4', matchId: 'm6', matchName: 'Dortmund vs Juventus', market: 'Resultado Final', option: 'Dortmund', odds: 2.4, status: 'won' },
      { id: 's5', matchId: 'm2', matchName: 'Barcelona vs Atlético', market: 'Ambas Marcam', option: 'Não', odds: 2.1, status: 'lost' },
    ],
    stake: 25,
    potentialReturn: 126.0,
    totalOdds: 5.04,
    date: '25/07/2025',
    status: 'lost',
  },
  {
    id: 'b4',
    selections: [
      { id: 's6', matchId: 'm5', matchName: 'Inter vs Napoli', market: 'Total de Gols', option: 'Over 2.5', odds: 1.95, status: 'pending' },
      { id: 's7', matchId: 'm3', matchName: 'Real Madrid vs PSG', market: 'Resultado Final', option: 'Real Madrid', odds: 2.1, status: 'pending' },
    ],
    stake: 40,
    potentialReturn: 163.8,
    totalOdds: 4.095,
    date: '27/07/2025',
    status: 'pending',
  },
]

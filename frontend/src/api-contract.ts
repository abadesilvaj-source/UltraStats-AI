/**
 * Contratos públicos do backend. Mantidos junto do OpenAPI e verificados
 * pelo build TypeScript para impedir mudanças silenciosas de integração.
 */
export interface IntelligencePlatformStatus {
  feature_store: {
    snapshots: number
    latest_as_of: string | null
    leakage_guard: 'strictly_before_kickoff'
  }
  quality: {
    open_incidents: number
    critical: number
    by_kind: Record<string, number>
  }
  models: {
    deployments: number
    champions: number
    shadow_challengers: number
    families: string[]
  }
  backtesting: {
    runs: number
    passed_families: string[]
    method: 'expanding_window_walk_forward'
  }
  decision_control: {
    active_policies: number
    calibrated_segments: number
    drifted_segments: number
    selective_prediction: 'target_accuracy_with_abstention'
    target_accuracy: number
    dimensions: string[]
  }
  explainability: { predictions_explained: number }
  task_queue: { pending: number; failed: number; completed: number }
}

export interface IntelligenceStatus {
  statistics: {
    matches_with_statistics: number
    last_update: string | null
    recent_attempts: number
  }
  learning: {
    audited_predictions: number
    registered_models: number
    training_datasets: number
    latest_validation: {
      approved: boolean
      metrics: Record<string, unknown>
      gate_failures: string[]
      evaluated_at: string
    } | null
  }
  recommendations: { persisted: number; safe: number }
  platform: IntelligencePlatformStatus
}

export interface RecommendationModelTrace {
  model_name: string
  model_version: string
  data_cutoff_at: string
  favorable_factors: string[]
  adverse_factors: string[]
  decision: Record<string, unknown>
}

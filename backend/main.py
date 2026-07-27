import os
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database.session import SessionLocal
from app.models import Market, Match, Team
from app.services import BankrollService, BetSlipService
from backend.queries import ApiQueries
from ultrastats_ai.domain.experience import Favorite
from ultrastats_ai.infrastructure.experience import ExperienceStore
from ultrastats_ai.infrastructure.live import LiveStore


app = FastAPI(
    title="UltraStats AI API",
    version="1.0.0",
    description="API operacional para partidas, análises, recomendações e apostas.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        value.strip()
        for value in os.getenv(
            "FRONTEND_ORIGINS", "http://localhost:5173,http://localhost:8516"
        ).split(",")
        if value.strip()
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


@app.middleware("http")
async def database_session(request: Request, call_next):
    request.state.session = SessionLocal()
    try:
        return await call_next(request)
    finally:
        request.state.session.close()


@app.exception_handler(ValueError)
async def value_error_handler(_request: Request, error: ValueError):
    return JSONResponse({"error": str(error)}, status_code=422)


def queries(request: Request) -> ApiQueries:
    timezone_name = request.query_params.get(
        "timezone", os.getenv("DEFAULT_USER_TIMEZONE", "America/Sao_Paulo")
    )
    return ApiQueries(request.state.session, timezone_name)


@app.get("/api/v1/health")
def health(request: Request):
    return queries(request).system_status()


@app.get("/api/v1/providers/contributions")
def provider_contributions(request: Request):
    return queries(request).fusion_contributions()


@app.get("/api/v1/intelligence/status")
def intelligence_status(request: Request):
    return queries(request).intelligence_status()


@app.get("/api/v1/maturity/status")
def maturity_status(request: Request):
    return queries(request).maturity_status()


@app.get("/api/v1/matches")
def matches(
    request: Request,
    status: str = "scheduled,in_progress",
    limit: int = 200,
    offset: int = 0,
):
    bounded_limit = max(1, min(limit, 500))
    return queries(request).matches(
        statuses=tuple(status.split(",")),
        limit=bounded_limit,
        offset=max(0, offset),
    )


@app.get("/api/v1/matches/{match_id}")
def match_detail(match_id: int, request: Request):
    return queries(request).match_detail(match_id)


@app.get("/api/v1/markets")
def markets(request: Request):
    return queries(request).markets()


@app.get("/api/v1/predictions")
def predictions(request: Request):
    return queries(request).predictions()


@app.get("/api/v1/recommendations")
def recommendations(request: Request):
    return queries(request).recommendations()


@app.get("/api/v1/bankrolls")
def bankrolls(request: Request):
    return queries(request).bankrolls()


def serialize_bankroll(item) -> dict:
    return {
        "id": item.id,
        "name": item.name,
        "currency": item.currency,
        "balance": float(item.current_balance),
        "initial_balance": float(item.initial_balance),
        "unit_percentage": item.unit_percentage,
        "active": item.active,
    }


@app.post("/api/v1/bankrolls", status_code=201)
async def create_bankroll(request: Request):
    payload = await request.json()
    return serialize_bankroll(
        BankrollService(request.state.session).create_bankroll(
            name=str(payload.get("name", "")).strip(),
            initial_balance=float(payload.get("initial_balance", 0)),
            currency=str(payload.get("currency", "BRL")).strip() or "BRL",
            unit_percentage=float(payload.get("unit_percentage", 1)),
        )
    )


def serialize_bankroll_transaction(item) -> dict:
    return {
        "id": item.id,
        "bankroll_id": item.bankroll_id,
        "type": item.transaction_type,
        "amount": float(item.amount),
        "balance_before": float(item.balance_before),
        "balance_after": float(item.balance_after),
        "description": item.description,
        "created_at": item.created_at.isoformat(),
    }


@app.post("/api/v1/bankrolls/{bankroll_id}/deposit", status_code=201)
async def deposit_bankroll(bankroll_id: int, request: Request):
    payload = await request.json()
    return serialize_bankroll_transaction(
        BankrollService(request.state.session).deposit(
            bankroll_id,
            float(payload.get("amount", 0)),
            str(payload.get("description", "")).strip() or None,
        )
    )


@app.post("/api/v1/bankrolls/{bankroll_id}/withdraw", status_code=201)
async def withdraw_bankroll(bankroll_id: int, request: Request):
    payload = await request.json()
    return serialize_bankroll_transaction(
        BankrollService(request.state.session).withdraw(
            bankroll_id,
            float(payload.get("amount", 0)),
            str(payload.get("description", "")).strip() or None,
        )
    )


def serialize_slip(slip, session) -> dict:
    return {
        "id": slip.id,
        "bankroll_id": slip.bankroll_id,
        "bookmaker": slip.bookmaker,
        "kind": slip.kind,
        "stake_amount": float(slip.stake_amount),
        "total_odds": float(slip.total_odds),
        "potential_return": float(slip.potential_return),
        "payout_amount": (
            float(slip.payout_amount) if slip.payout_amount is not None else None
        ),
        "status": slip.status,
        "placed_at": slip.placed_at.isoformat(),
        "legs": [
            {
                "id": leg.id,
                "match_id": leg.match_id,
                "market_id": leg.market_id,
                "match": (
                    f"{session.get(Team, match.home_team_id).name} x "
                    f"{session.get(Team, match.away_team_id).name}"
                    if (match := session.get(Match, leg.match_id)) else
                    f"Partida #{leg.match_id}"
                ),
                "market": (
                    market.name
                    if (market := session.get(Market, leg.market_id))
                    else f"Mercado #{leg.market_id}"
                ),
                "selection": leg.selection,
                "odd": float(leg.odd_value),
                "status": leg.status,
                "result": leg.result,
            }
            for leg in slip.legs
        ],
    }


@app.get("/api/v1/bet-slips")
def list_bet_slips(request: Request):
    return [
        serialize_slip(item, request.state.session)
        for item in BetSlipService(request.state.session).list_all()
    ]


@app.post("/api/v1/bet-slips", status_code=201)
async def create_bet_slip(request: Request):
    payload = await request.json()
    return serialize_slip(
        BetSlipService(request.state.session).create(payload),
        request.state.session,
    )


@app.post("/api/v1/bet-slips/analyze")
async def analyze_bet_slip(request: Request):
    payload = await request.json()
    return BetSlipService(request.state.session).analyze(payload)


@app.get("/api/v1/favorites")
def favorites(request: Request, user_id: str = "default"):
    return [
        {
            "entity_type": item.entity_type,
            "entity_id": item.entity_id,
            "label": item.label,
        }
        for item in ExperienceStore(request.state.session).favorites(user_id)
    ]


@app.post("/api/v1/favorites", status_code=201)
async def add_favorite(request: Request):
    payload = await request.json()
    record = ExperienceStore(request.state.session).add_favorite(
        Favorite(
            str(payload.get("user_id") or "default"),
            str(payload["entity_type"]),
            str(payload["entity_id"]),
            str(payload["label"]),
        ),
        datetime.now(timezone.utc),
    )
    request.state.session.commit()
    return {
        "entity_type": record.entity_type,
        "entity_id": record.entity_id,
        "label": record.label,
    }


@app.get("/api/v1/live")
def live(request: Request):
    return [
        {
            "match_id": item.match_id,
            "revision": item.revision,
            "phase": item.phase,
            "health": item.health,
            "minute": item.minute,
            "score": {"home": item.home_score, "away": item.away_score},
            "statistics": item.statistics,
            "odds": item.odds,
            "probabilities": item.probabilities,
            "recommendations": item.recommendations,
            "captured_at": item.captured_at.isoformat(),
        }
        for item in LiveStore(request.state.session).recent()
    ]

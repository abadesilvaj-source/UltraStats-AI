import os
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database.session import SessionLocal
from app.models import Bankroll, BetSlip, Market, Match, Team, User
from app.services import BankrollService, BetSlipService
from app.services.auth_service import (
    AuthService, COOKIE_NAME, SESSION_TTL, create_session_token, session_user_id,
)
from api.queries import ApiQueries
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
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
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


def current_user(request: Request) -> User:
    user_id = session_user_id(request.cookies.get(COOKIE_NAME))
    user = request.state.session.get(User, user_id) if user_id else None
    if user is None or not user.active:
        raise HTTPException(status_code=401, detail="Autenticação necessária.")
    return user


def public_user(user: User) -> dict:
    return {"id": user.id, "email": user.email, "display_name": user.display_name}


def set_session(response: Response, user: User) -> None:
    response.set_cookie(
        COOKIE_NAME, create_session_token(user.id), max_age=SESSION_TTL,
        httponly=True, samesite="lax", secure=os.getenv("COOKIE_SECURE") == "true",
        path="/",
    )


@app.post("/api/v1/auth/register", status_code=201)
async def register(request: Request, response: Response):
    payload = await request.json()
    user = AuthService(request.state.session).register(
        str(payload.get("email", "")), str(payload.get("password", "")),
        str(payload.get("display_name", "")),
    )
    set_session(response, user)
    return public_user(user)


@app.post("/api/v1/auth/login")
async def login(request: Request, response: Response):
    payload = await request.json()
    user = AuthService(request.state.session).authenticate(
        str(payload.get("email", "")), str(payload.get("password", "")),
    )
    if user is None:
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos.")
    set_session(response, user)
    return public_user(user)


@app.get("/api/v1/auth/me")
def me(request: Request):
    return public_user(current_user(request))


@app.post("/api/v1/auth/logout", status_code=204)
def logout(response: Response):
    response.delete_cookie(COOKIE_NAME, path="/")


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
def predictions(request: Request, limit: int = 500):
    return queries(request).predictions(limit=max(1, min(limit, 1000)))


@app.get("/api/v1/recommendations")
def recommendations(
    request: Request,
    primary_only: bool = False,
    limit: int = 500,
):
    return queries(request).recommendations(
        primary_only=primary_only,
        limit=max(1, min(limit, 1000)),
    )


@app.get("/api/v1/bankrolls")
def bankrolls(request: Request):
    user = current_user(request)
    return [serialize_bankroll(item) for item in BankrollService(
        request.state.session
    ).list_bankrolls(user.id)]


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
    user = current_user(request)
    payload = await request.json()
    return serialize_bankroll(
        BankrollService(request.state.session).create_bankroll(
            user_id=user.id,
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
    user = current_user(request)
    BankrollService(request.state.session).get_bankroll(bankroll_id, user.id)
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
    user = current_user(request)
    BankrollService(request.state.session).get_bankroll(bankroll_id, user.id)
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
    user = current_user(request)
    return [
        serialize_slip(item, request.state.session)
        for item in BetSlipService(request.state.session).list_all()
        if request.state.session.get(Bankroll, item.bankroll_id).user_id == user.id
    ]


@app.post("/api/v1/bet-slips", status_code=201)
async def create_bet_slip(request: Request):
    user = current_user(request)
    payload = await request.json()
    BankrollService(request.state.session).get_bankroll(
        int(payload.get("bankroll_id", 0)), user.id
    )
    return serialize_slip(
        BetSlipService(request.state.session).create(payload),
        request.state.session,
    )


@app.post("/api/v1/bet-slips/analyze")
async def analyze_bet_slip(request: Request):
    user = current_user(request)
    payload = await request.json()
    BankrollService(request.state.session).get_bankroll(
        int(payload.get("bankroll_id", 0)), user.id
    )
    return BetSlipService(request.state.session).analyze(payload)


@app.patch("/api/v1/bet-slips/{slip_id}/legs/{leg_id}/settle")
async def settle_bet_slip_leg(
    slip_id: int, leg_id: int, request: Request
):
    user = current_user(request)
    payload = await request.json()
    slip = request.state.session.get(BetSlip, slip_id)
    if slip is None:
        raise ValueError("Bilhete não encontrado.")
    BankrollService(request.state.session).get_bankroll(slip.bankroll_id, user.id)
    slip = BetSlipService(
        request.state.session
    ).settle_leg_manually(
        slip_id, leg_id, str(payload.get("result", ""))
    )
    return serialize_slip(slip, request.state.session)


@app.post("/api/v1/bet-slips/{slip_id}/cancel")
def cancel_bet_slip(slip_id: int, request: Request):
    user = current_user(request)
    owned_slip = request.state.session.get(BetSlip, slip_id)
    if owned_slip is None:
        raise ValueError("Bilhete não encontrado.")
    BankrollService(request.state.session).get_bankroll(owned_slip.bankroll_id, user.id)
    slip = BetSlipService(request.state.session).cancel(slip_id)
    return serialize_slip(slip, request.state.session)


@app.get("/api/v1/favorites")
def favorites(request: Request):
    user_id = current_user(request).id
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
    user_id = current_user(request).id
    payload = await request.json()
    record = ExperienceStore(request.state.session).add_favorite(
        Favorite(
            user_id,
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

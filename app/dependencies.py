from __future__ import annotations

from fastapi import Request

from app.repositories.audit_repository import AuditRepository
from app.repositories.config_repository import ConfigRepository
from app.repositories.subscription_repository import SubscriptionRepository
from app.repositories.trading_account_repository import TradingAccountRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.user_service import UserService


def get_user_repo() -> UserRepository:
    return UserRepository()


def get_trading_account_repo() -> TradingAccountRepository:
    return TradingAccountRepository()


def get_config_repo() -> ConfigRepository:
    return ConfigRepository()


def get_subscription_repo() -> SubscriptionRepository:
    return SubscriptionRepository()


def get_audit_repo() -> AuditRepository:
    return AuditRepository()


def get_auth_service(request: Request) -> AuthService:
    return AuthService(
        user_repo=get_user_repo(),
        subscription_repo=get_subscription_repo(),
        config_repo=get_config_repo(),
        trading_account_repo=get_trading_account_repo(),
    )


def get_user_service(request: Request) -> UserService:
    return UserService(
        user_repo=get_user_repo(),
        trading_account_repo=get_trading_account_repo(),
        config_repo=get_config_repo(),
        subscription_repo=get_subscription_repo(),
    )

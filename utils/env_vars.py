import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import find_dotenv, load_dotenv


load_dotenv(find_dotenv())


def _clean(value: str | None) -> str | None:
    if value is None:
        return None

    value = value.strip()
    return value or None


def _get(name: str) -> str | None:
    return _clean(os.getenv(name))


def _parse_stop_loss(value: str | None) -> float:
    if value is None:
        return 0.9

    try:
        ratio = float(value)
    except ValueError as exc:
        raise RuntimeError("STOP_LOSS must be a number between 0 and 1.") from exc

    if not 0 < ratio < 1:
        raise RuntimeError("STOP_LOSS must be greater than 0 and less than 1.")

    return ratio


@dataclass(frozen=True)
class Settings:
    refresh_token: str | None
    encryption_key: bytes | None
    stop_loss_ratio: float
    token_path: str | None
    cred_path: str | None
    bot_email: str | None
    email_password: str | None
    email_provider: str | None
    user_email: str | None
    ntfy_channel: str | None
    discord_webhook_url: str | None

    @property
    def email_to_notify(self) -> str | None:
        return self.user_email or self.bot_email

    def require_encryption_key(self) -> bytes:
        if not self.encryption_key:
            raise RuntimeError("encryption_key must be configured in .env.")
        return self.encryption_key

    def require_refresh_token(self) -> str:
        if not self.refresh_token:
            raise RuntimeError("refresh_token must be configured when no token exists in the database.")
        return self.refresh_token

    def require_email_settings(self) -> None:
        missing = []
        if not self.email_provider:
            missing.append("PROVIDER")
        if not self.bot_email:
            missing.append("BOT_EMAIL")
        if not self.email_password:
            missing.append("EMAIL_PASSWORD")
        if not self.email_to_notify:
            missing.append("USER_EMAIL or BOT_EMAIL")

        if missing:
            raise RuntimeError(f"Email alerts are not configured. Missing: {', '.join(missing)}.")

    def validate_startup(self) -> None:
        self.require_encryption_key()
        _parse_stop_loss(str(self.stop_loss_ratio))


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    encryption_key = _get("encryption_key")
    return Settings(
        refresh_token=_get("refresh_token"),
        encryption_key=encryption_key.encode() if encryption_key else None,
        stop_loss_ratio=_parse_stop_loss(_get("STOP_LOSS")),
        token_path=_get("TOKEN_PATH"),
        cred_path=_get("CRED_PATH"),
        bot_email=_get("BOT_EMAIL"),
        email_password=_get("EMAIL_PASSWORD"),
        email_provider=_get("PROVIDER"),
        user_email=_get("USER_EMAIL"),
        ntfy_channel=_get("NTFY_CHANNEL"),
        discord_webhook_url=_get("WEB_HOOK_URL"),
    )


def reload_settings() -> Settings:
    get_settings.cache_clear()
    load_dotenv(find_dotenv(), override=True)
    return get_settings()


# Backwards-compatible names for modules that have not been moved to Settings yet.
REFRESH_TOKEN = _get("refresh_token")
ENCRYPTION_KEY_STR = _get("encryption_key")
ENCRYPTION_KEY = ENCRYPTION_KEY_STR.encode() if ENCRYPTION_KEY_STR else None
PATH_TO_TOKEN = _get("TOKEN_PATH")
PATH_TO_CRED = _get("CRED_PATH")
BOT_EMAIL = _get("BOT_EMAIL")
EMAIL_PASS = _get("EMAIL_PASSWORD")
STOPLOSS_RATIO = _get("STOP_LOSS") or "0.9"
PROVIDER = _get("PROVIDER")
EMAIL_TO_NOTIFY = _get("USER_EMAIL") or BOT_EMAIL
SUBSCRIBED_CHANNEL = _get("NTFY_CHANNEL")
WEB_HOOK_URL = _get("WEB_HOOK_URL")

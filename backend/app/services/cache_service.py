import json
import logging
from typing import Any, cast

from redis.exceptions import RedisError

from app.core.config import settings
from app.core.redis import redis_client


logger = logging.getLogger(__name__)

DASHBOARD_SUMMARY_CACHE_KEY = "dashboard:summary"


def get_dashboard_cache() -> dict[str, Any] | None:
    try:
        cached = cast(str | None, redis_client.get(DASHBOARD_SUMMARY_CACHE_KEY))
    except RedisError:
        logger.warning("Redis dashboard cache read failed", exc_info=True)
        return None

    if cached is None:
        return None

    try:
        return json.loads(cached)
    except json.JSONDecodeError:
        clear_dashboard_cache()
        return None


def set_dashboard_cache(value: dict[str, Any]) -> None:
    try:
        redis_client.setex(
            DASHBOARD_SUMMARY_CACHE_KEY,
            settings.CACHE_TTL_SECONDS,
            json.dumps(value),
        )
    except RedisError:
        logger.warning("Redis dashboard cache write failed", exc_info=True)


def clear_dashboard_cache() -> None:
    try:
        redis_client.delete(DASHBOARD_SUMMARY_CACHE_KEY)
    except RedisError:
        logger.warning("Redis dashboard cache delete failed", exc_info=True)

#!/usr/bin/env python3
import time
import random
import logging

logger = logging.getLogger(__name__)

# Profile definitions: (base_delay_range, jitter, randomize_order, timeout, silent)
STEALTH_PROFILES = {
    1: {"delay": (1, 2),   "jitter": 0,   "randomize": False, "timeout": 30,  "silent": False},
    2: {"delay": (3, 6),   "jitter": 1,   "randomize": False, "timeout": 30,  "silent": False},
    3: {"delay": (8, 15),  "jitter": 3,   "randomize": True,  "timeout": 60,  "silent": False},
    4: {"delay": (20, 45), "jitter": 5,   "randomize": True,  "timeout": 120, "silent": True},
}


def get_profile(level: int) -> dict:
    return STEALTH_PROFILES.get(level, {})


def apply_delay(profile: dict) -> None:
    """Sleep for base delay + random jitter."""
    if not profile:
        return
    low, high = profile["delay"]
    base = random.uniform(low, high)
    jitter = random.uniform(0, profile["jitter"])
    total = base + jitter
    if not profile.get("silent"):
        logger.info(f"[~] Stealth delay: {total:.1f}s")
    time.sleep(total)


def prepare_users(users: list, profile: dict) -> list:
    """Shuffle users if randomize is enabled."""
    if profile.get("randomize"):
        shuffled = users.copy()
        random.shuffle(shuffled)
        if not profile.get("silent"):
            logger.info("[~] Stealth: user order randomized")
        return shuffled
    return users


def configure_logging(profile: dict) -> None:
    """Reduce log verbosity in silent mode (level 4)."""
    if profile.get("silent"):
        logging.getLogger().setLevel(logging.WARNING)
        logger.warning("[~] Stealth level 4: switching to minimal logging")

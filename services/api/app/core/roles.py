"""
Role to access_tags mapping.

SECURITY: This module is the single source of truth for authorization.
The model never sees this mapping. Authorization is enforced HERE before
any chunk reaches the retrieval step.

The mapping is loaded from roles.yaml at startup.
Defaults are provided so the service starts safely even without the file.
"""

import os
from typing import Dict, List
from pathlib import Path

import yaml
import structlog

logger = structlog.get_logger(__name__)

# Default mapping — used if roles.yaml is not found
DEFAULT_ROLE_TAG_MAP: Dict[str, List[str]] = {
    "admin": ["admin", "management", "operations", "hr", "shared_user"],
    "management": ["management", "shared_user"],
    "operations": ["operations", "shared_user"],
    "hr": ["hr", "shared_user"],
    "shared_user": ["shared_user"],
}

_role_tag_map: Dict[str, List[str]] = {}


def load_roles_config(config_path: str = "/app/config/roles.yaml") -> None:
    """Load role→tags mapping from roles.yaml. Falls back to defaults."""
    global _role_tag_map

    path = Path(config_path)
    if path.exists():
        try:
            with open(path) as f:
                data = yaml.safe_load(f)
            _role_tag_map = data.get("role_tag_map", DEFAULT_ROLE_TAG_MAP)
            logger.info("roles_config_loaded", path=config_path, roles=list(_role_tag_map.keys()))
        except Exception as e:
            logger.warning("roles_config_load_failed", error=str(e), using="defaults")
            _role_tag_map = DEFAULT_ROLE_TAG_MAP
    else:
        logger.info("roles_config_not_found", path=config_path, using="defaults")
        _role_tag_map = DEFAULT_ROLE_TAG_MAP


def get_allowed_tags(roles: List[str]) -> List[str]:
    """
    Given a list of user roles, return the union of all allowed access_tags.

    This is the primary authorization function. It must be called before
    any Qdrant retrieval. The returned tags are used as a Qdrant filter.

    Args:
        roles: List of role names assigned to the user

    Returns:
        Deduplicated list of access_tags the user is allowed to see
    """
    if not _role_tag_map:
        load_roles_config()

    allowed = set()
    for role in roles:
        tags = _role_tag_map.get(role, [])
        allowed.update(tags)

    return list(allowed)


def get_role_tag_map() -> Dict[str, List[str]]:
    """Return the full role→tags mapping (for admin inspection)."""
    if not _role_tag_map:
        load_roles_config()
    return _role_tag_map


# Load on import so it's ready before first request
load_roles_config()

"""
Standalone unit tests for role→tag mapping.
Tests the DEFAULT_ROLE_TAG_MAP logic directly without importing the full app.
"""


# ---- replicated minimal logic from app/core/roles.py ----
DEFAULT_ROLE_TAG_MAP = {
    "admin": ["admin", "management", "operations", "hr", "shared_user"],
    "management": ["management", "shared_user"],
    "operations": ["operations", "shared_user"],
    "hr": ["hr", "shared_user"],
    "shared_user": ["shared_user"],
}


def get_allowed_tags(roles):
    """Replicated from app.core.roles — derive allowed tags from roles."""
    allowed = set()
    for role in roles:
        tags = DEFAULT_ROLE_TAG_MAP.get(role, [])
        allowed.update(tags)
    return list(allowed)


# ---- tests ----
class TestRoleTagMapping:
    def test_admin_gets_all_tags(self):
        tags = get_allowed_tags(["admin"])
        assert "admin" in tags
        assert "management" in tags
        assert "operations" in tags
        assert "hr" in tags
        assert "shared_user" in tags

    def test_operations_role(self):
        tags = get_allowed_tags(["operations"])
        assert "operations" in tags
        assert "shared_user" in tags
        assert "hr" not in tags
        assert "management" not in tags

    def test_hr_role(self):
        tags = get_allowed_tags(["hr"])
        assert "hr" in tags
        assert "shared_user" in tags
        assert "operations" not in tags

    def test_management_role(self):
        tags = get_allowed_tags(["management"])
        assert "management" in tags
        assert "shared_user" in tags
        assert "hr" not in tags

    def test_shared_user_role(self):
        tags = get_allowed_tags(["shared_user"])
        assert tags == ["shared_user"]

    def test_multiple_roles_union(self):
        tags = get_allowed_tags(["operations", "hr"])
        assert "operations" in tags
        assert "hr" in tags
        assert "shared_user" in tags

    def test_empty_roles_returns_empty(self):
        assert get_allowed_tags([]) == []

    def test_unknown_role_ignored(self):
        assert get_allowed_tags(["nonexistent_role"]) == []

    def test_no_duplicates(self):
        tags = get_allowed_tags(["operations", "hr"])
        assert len(tags) == len(set(tags))

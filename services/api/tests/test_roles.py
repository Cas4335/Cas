"""Tests for role to access tag mapping."""

import pytest
from app.core.roles import get_allowed_tags, DEFAULT_ROLE_TAG_MAP


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
        assert "operations" not in tags

    def test_shared_user_role(self):
        tags = get_allowed_tags(["shared_user"])
        assert tags == ["shared_user"]

    def test_multiple_roles_union(self):
        # User with both operations and hr roles gets union of both
        tags = get_allowed_tags(["operations", "hr"])
        assert "operations" in tags
        assert "hr" in tags
        assert "shared_user" in tags

    def test_empty_roles_returns_empty(self):
        tags = get_allowed_tags([])
        assert tags == []

    def test_unknown_role_ignored(self):
        tags = get_allowed_tags(["nonexistent_role"])
        assert tags == []

    def test_no_duplicates(self):
        # Both roles include shared_user — result should not have duplicates
        tags = get_allowed_tags(["operations", "hr"])
        assert len(tags) == len(set(tags))

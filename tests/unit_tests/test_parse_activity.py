"""Tests for parsing PR and issue activity fetched from GitHub."""

import json

from gh_profiler.utils import profile_utils
from gh_profiler.utils.profile_data import profile_data as pdata


def _pr_node(owner, state="OPEN", merged_at=None):
    """Return a PR node like those in GraphQL search results."""
    return {
        "number": 1,
        "state": state,
        "createdAt": "2026-06-15T00:00:00Z",
        "closedAt": None,
        "mergedAt": merged_at,
        "url": f"https://github.com/{owner}/repo/pull/1",
        "repository": {
            "nameWithOwner": f"{owner}/repo",
            "isInOrganization": False,
            "owner": {"__typename": "User", "login": owner},
        },
    }


def _issue_node(owner, title="Issue title", state_reason=None):
    """Return an issue node like those in GraphQL search results."""
    return {
        "number": 1,
        "title": title,
        "createdAt": "2026-06-15T00:00:00Z",
        "state": "OPEN",
        "stateReason": state_reason,
        "url": f"https://github.com/{owner}/repo/issues/1",
        "repository": {
            "nameWithOwner": f"{owner}/repo",
            "isInOrganization": False,
            "owner": {"__typename": "User", "login": owner},
        },
    }


def _search_response(nodes):
    """Return a JSON string like the output of a gh graphql search call."""
    search = {"issueCount": len(nodes), "nodes": nodes}
    return json.dumps({"data": {"search": search}})


def test_parse_pr_activity_null_nodes():
    """Null nodes, e.g. PRs in SAML-protected repos, should be ignored.

    GitHub returns null for search result nodes the authenticated user
    can't access, which previously crashed with:
    TypeError: 'NoneType' object is not subscriptable
    """
    pdata.orgs = []
    nodes = [
        _pr_node("ehmatthes"),
        _pr_node("external_user", state="MERGED", merged_at="2026-06-16T00:00:00Z"),
        None,
        None,
    ]

    profile_utils._parse_pr_activity(_search_response(nodes))

    assert pdata.opened_count == 2
    assert pdata.opened_count_owned == 1
    assert pdata.opened_count_orgs == 0
    assert pdata.opened_count_external == 1
    assert pdata.merged_count_external == 1
    assert pdata.closed_count_external == 0


def test_parse_issue_activity_null_nodes():
    """Null nodes, e.g. issues in SAML-protected repos, should be ignored."""
    pdata.orgs = []
    nodes = [
        _issue_node("ehmatthes"),
        _issue_node("external_user"),
        None,
    ]

    profile_utils._parse_issue_activity(_search_response(nodes))

    assert pdata.issues_owned == 1
    assert pdata.issues_orgs == 0
    assert pdata.issues_external == 1
    assert pdata.issues_not_planned == 0

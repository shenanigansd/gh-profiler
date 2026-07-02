"""Tests for parsing PR/issue activity, including missing repository data.

GitHub's search API can return a null `repository` (or a repository with a
null `owner`) for results the authenticated user can no longer fully
resolve, e.g. a repo that was deleted, transferred, or made private after
the PR/issue was opened. These should be handled gracefully rather than
raising a TypeError.
"""

import json

from gh_profiler.utils import profile_utils
from gh_profiler.utils.profile_data import profile_data as pdata


def test_parse_pr_activity_handles_null_repository():
    pdata.username = "shenanigansd"
    pdata.orgs = []

    data = {
        "data": {
            "search": {
                "nodes": [
                    {"repository": None, "state": "CLOSED", "mergedAt": None},
                    {
                        "repository": {"owner": {"login": "shenanigansd"}},
                        "state": "OPEN",
                        "mergedAt": None,
                    },
                ]
            }
        }
    }

    profile_utils._parse_pr_activity(json.dumps(data))

    assert pdata.opened_count == 2
    assert pdata.opened_count_owned == 1
    assert pdata.opened_count_external == 1


def test_parse_issue_activity_handles_null_repository():
    pdata.username = "shenanigansd"
    pdata.orgs = []

    data = {
        "data": {
            "search": {
                "issueCount": 2,
                "nodes": [
                    {
                        "repository": None,
                        "title": "Some issue",
                        "stateReason": None,
                    },
                    {
                        "repository": {"owner": {"login": "shenanigansd"}},
                        "title": "Another issue",
                        "stateReason": None,
                    },
                ],
            }
        }
    }

    profile_utils._parse_issue_activity(json.dumps(data))

    assert pdata.new_issue_count == 2
    assert pdata.issues_owned == 1
    assert pdata.issues_external == 1

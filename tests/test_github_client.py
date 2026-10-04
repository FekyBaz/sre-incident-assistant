import pytest

from app.tools.github_client import GitHubClient, GitHubClientError


def test_parse_repository_variants():
    client = GitHubClient()
    assert client.parse_repository("FekyBaz/sre-incident-assistant") == (
        "FekyBaz",
        "sre-incident-assistant",
    )
    assert client.parse_repository("https://github.com/FekyBaz/sre-incident-assistant.git") == (
        "FekyBaz",
        "sre-incident-assistant",
    )


def test_parse_repository_rejects_non_github():
    with pytest.raises(GitHubClientError):
        GitHubClient.parse_repository("https://example.com/acme/project")



@pytest.mark.parametrize("value", [
    "FekyBaz/sre-incident-assistant",
    "https://github.com/FekyBaz/sre-incident-assistant",
    "https://github.com/FekyBaz/sre-incident-assistant.git",
    "git@github.com:FekyBaz/sre-incident-assistant.git",
])
def test_all_documented_repository_forms(value):
    assert GitHubClient.parse_repository(value) == ("FekyBaz", "sre-incident-assistant")

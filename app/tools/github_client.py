from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

import httpx

from app.core.config import settings


class GitHubClientError(RuntimeError):
    """Raised when GitHub evidence cannot be collected."""


@dataclass(frozen=True)
class GitHubCommit:
    sha: str
    message: str
    author: str | None
    committed_at: str | None
    url: str | None
    files: list[str]


@dataclass(frozen=True)
class GitHubCommitDiff:
    sha: str
    message: str
    files: list[dict[str, object]]
    patch: str


class GitHubClient:
    BASE_URL = "https://api.github.com"

    def __init__(self, token: str | None = None, timeout: float = 15.0) -> None:
        self.timeout = timeout
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    def _request(self, method: str, path: str, **kwargs: object) -> dict | list:
        url = f"{self.BASE_URL}{path}"
        try:
            response = httpx.request(
                method,
                url,
                headers=self.headers,
                timeout=self.timeout,
                **kwargs,
            )
        except httpx.HTTPError as exc:
            raise GitHubClientError("Could not connect to GitHub.") from exc

        if response.status_code >= 400:
            detail = response.text[:500]
            raise GitHubClientError(
                f"GitHub API returned {response.status_code}: {detail}"
            )

        try:
            return response.json()
        except ValueError as exc:
            raise GitHubClientError("GitHub returned invalid JSON.") from exc

    @staticmethod
    def parse_repository(value: str) -> tuple[str, str]:
        raw = value.strip()
        if raw.startswith("git@github.com:"):
            raw = f"https://github.com/{raw.split(':', 1)[1]}"
        elif "://" not in raw:
            raw = f"https://github.com/{raw}"

        parsed = urlparse(raw)
        if parsed.netloc.lower() not in {"github.com", "www.github.com"}:
            raise GitHubClientError("Repository must be hosted on github.com.")

        parts = [part for part in parsed.path.split("/") if part]
        if len(parts) < 2:
            raise GitHubClientError("Repository must use the owner/name format.")

        owner = parts[0]
        name = parts[1].removesuffix(".git")
        return owner, name

    def validate_repository(self, repository: str) -> dict[str, object]:
        owner, name = self.parse_repository(repository)
        data = self._request("GET", f"/repos/{owner}/{name}")
        if not isinstance(data, dict):
            raise GitHubClientError("Unexpected repository response.")
        return {
            "full_name": data.get("full_name", f"{owner}/{name}"),
            "default_branch": data.get("default_branch"),
            "private": data.get("private", False),
            "archived": data.get("archived", False),
            "description": data.get("description"),
        }

    def get_recent_commits(self, repository: str, limit: int = 10) -> list[GitHubCommit]:
        owner, name = self.parse_repository(repository)
        limit = max(1, min(limit, 50))
        data = self._request(
            "GET",
            f"/repos/{owner}/{name}/commits",
            params={"per_page": limit},
        )
        if not isinstance(data, list):
            raise GitHubClientError("Unexpected commits response.")

        commits: list[GitHubCommit] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            commit = item.get("commit", {})
            author = commit.get("author", {}) if isinstance(commit, dict) else {}
            sha = str(item.get("sha", ""))
            file_names: list[str] = []
            if sha:
                try:
                    detail = self._request("GET", f"/repos/{owner}/{name}/commits/{sha}")
                    if isinstance(detail, dict):
                        detail_files = detail.get("files", [])
                        file_names = [
                            str(file.get("filename"))
                            for file in detail_files
                            if isinstance(file, dict) and file.get("filename")
                        ][:100]
                except GitHubClientError:
                    # Commit metadata remains useful even if the detail request fails.
                    file_names = []

            commits.append(
                GitHubCommit(
                    sha=sha,
                    message=str(commit.get("message", "")).splitlines()[0][:500],
                    author=str(author.get("name")) if author.get("name") else None,
                    committed_at=str(author.get("date")) if author.get("date") else None,
                    url=str(item.get("html_url")) if item.get("html_url") else None,
                    files=file_names,
                )
            )
        return commits

    def get_commit_diff(self, repository: str, commit_sha: str, max_patch_chars: int = 30_000) -> GitHubCommitDiff:
        owner, name = self.parse_repository(repository)
        data = self._request("GET", f"/repos/{owner}/{name}/commits/{commit_sha}")
        if not isinstance(data, dict):
            raise GitHubClientError("Unexpected commit response.")

        commit = data.get("commit", {})
        message = str(commit.get("message", "")).splitlines()[0][:500] if isinstance(commit, dict) else ""
        files = data.get("files", [])
        normalized_files = []
        patches: list[str] = []
        for file in files if isinstance(files, list) else []:
            if not isinstance(file, dict):
                continue
            normalized = {
                "filename": file.get("filename"),
                "status": file.get("status"),
                "additions": file.get("additions", 0),
                "deletions": file.get("deletions", 0),
                "changes": file.get("changes", 0),
            }
            normalized_files.append(normalized)
            patch = file.get("patch")
            if patch:
                patches.append(f"--- {file.get('filename')} ---\\n{patch}")

        patch_text = "\\n".join(patches)
        return GitHubCommitDiff(
            sha=commit_sha,
            message=message,
            files=normalized_files,
            patch=patch_text[:max_patch_chars],
        )


def get_github_client() -> GitHubClient:
    return GitHubClient(token=settings.github_token or None)

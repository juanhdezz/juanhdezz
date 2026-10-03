"""Reescribe la sección de actividad del README con los últimos repos públicos con push.

Solo usa la librería estándar. Lee GITHUB_TOKEN si existe (evita el rate limit anónimo).
"""
import json
import os
import re
import urllib.request
from pathlib import Path

USER = "juanhdezz"
LIMIT = 5
README = Path(__file__).resolve().parents[2] / "README.md"
START, END = "<!-- activity:start -->", "<!-- activity:end -->"


def fetch_repos():
    req = urllib.request.Request(
        f"https://api.github.com/users/{USER}/repos?type=owner&sort=pushed&per_page=30",
        headers={"Accept": "application/vnd.github+json", "User-Agent": USER},
    )
    if token := os.environ.get("GITHUB_TOKEN"):
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def render(repos):
    return "\n".join(
        f"- [{r['name']}]({r['html_url']}) <sub>{r['language'] or 'Sin lenguaje'}, último push {r['pushed_at'][:10]}</sub>"
        for r in repos
    )


def main():
    repos = [r for r in fetch_repos() if not (r["fork"] or r["archived"] or r["name"] == USER)][:LIMIT]
    text = README.read_text(encoding="utf-8")
    block = f"{START}\n{render(repos)}\n{END}"
    new, count = re.subn(re.escape(START) + r".*?" + re.escape(END), lambda _: block, text, flags=re.S)
    if count != 1:
        raise SystemExit("No se encontraron los marcadores de actividad en README.md")
    README.write_text(new, encoding="utf-8")


if __name__ == "__main__":
    main()

"""Baixa o calendário público de contribuições do GitHub (sem token) e grava
data/contributions.json com os dias e estatísticas derivadas.

Uso: python scripts/fetch_contributions.py [usuario]
"""

import json
import re
import sys
import urllib.request
from datetime import date, timedelta
from html.parser import HTMLParser
from pathlib import Path

USERNAME = sys.argv[1] if len(sys.argv) > 1 else "pedroluizmm"
OUT = Path(__file__).resolve().parent.parent / "data" / "contributions.json"


class CalendarParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells = {}  # id do <td> -> {"date", "level"}
        self.counts = {}  # id do <td> -> contagem (vinda do tool-tip)
        self._tip_for = None
        self._tip_text = ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "td" and "ContributionCalendar-day" in (a.get("class") or ""):
            if a.get("data-date") and a.get("id"):
                self.cells[a["id"]] = {
                    "date": a["data-date"],
                    "level": int(a.get("data-level") or 0),
                }
        elif tag == "tool-tip" and a.get("for"):
            self._tip_for = a["for"]
            self._tip_text = ""

    def handle_data(self, data):
        if self._tip_for:
            self._tip_text += data

    def handle_endtag(self, tag):
        if tag == "tool-tip" and self._tip_for:
            m = re.match(r"\s*([\d,]+)\s+contribution", self._tip_text)
            self.counts[self._tip_for] = int(m.group(1).replace(",", "")) if m else 0
            self._tip_for = None


def fetch(username):
    req = urllib.request.Request(
        f"https://github.com/users/{username}/contributions",
        headers={"User-Agent": "profile-readme-heatmap"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def longest_run(days):
    best = run = 0
    for d in days:
        run = run + 1 if d["count"] > 0 else 0
        best = max(best, run)
    return best


def current_run(days):
    # Um dia de hoje ainda vazio não quebra a sequência.
    tail = days[:-1] if days and days[-1]["count"] == 0 else days
    run = 0
    for d in reversed(tail):
        if d["count"] == 0:
            break
        run += 1
    return run


def main():
    parser = CalendarParser()
    parser.feed(fetch(USERNAME))

    today = date.today() + timedelta(days=1)  # tolerância de fuso horário
    days = sorted(
        (
            {"date": c["date"], "level": c["level"], "count": parser.counts.get(cid, 0)}
            for cid, c in parser.cells.items()
            if date.fromisoformat(c["date"]) <= today
        ),
        key=lambda d: d["date"],
    )
    if not days:
        sys.exit("Nenhum dia encontrado: o HTML do GitHub pode ter mudado.")

    best = max(days, key=lambda d: d["count"])
    data = {
        "username": USERNAME,
        "total": sum(d["count"] for d in days),
        "current_streak": current_run(days),
        "longest_streak": longest_run(days),
        "best_day": {"date": best["date"], "count": best["count"]},
        "days": days,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    print(f"{len(days)} dias, {data['total']} contribuições -> {OUT}")


if __name__ == "__main__":
    main()

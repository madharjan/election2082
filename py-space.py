
"""
Nepal Election 2082 — Sainte-Laguë PR Seat Allocation + FPTP Results
PR  data: https://result.election.gov.np/PRVoteChartResult2082.aspx
FPTP data: https://result.election.gov.np/FPTPWLChartResult2082.aspx
"""

import anvil.server
import sys
import heapq
import json
import os
import requests
from datetime import datetime, timezone, timedelta
from deep_translator import GoogleTranslator

# sys.stdout.reconfigure(encoding='utf-8')

# ─── Configuration ────────────────────────────────────────────────────────────
BASE_URL       = "https://result.election.gov.np"
PR_PAGE        = "/PRVoteChartResult2082.aspx"
FPTP_PAGE      = "/FPTPWLChartResult2082.aspx"
PR_DATA_FILE   = "PRHoRPartyTop5.txt"   # contains ALL parties despite the name
FPTP_DATA_FILE = "HoRPartyTop5.txt"
HANDLER        = "/Handlers/SecureJson.ashx?file=JSONFiles/Election2082/Common/"

TOTAL_SEATS      = 110   # Federal PR seats
FPTP_TOTAL_SEATS = 165   # Total FPTP constituencies
THRESHOLD        = 0.03  # 3% minimum vote share (set 0 to disable)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

# ─── Translation ──────────────────────────────────────────────────────────────

_translator = GoogleTranslator(source='ne', target='en')

def translate_names(parties: list[dict]) -> None:
  """Translate all party names in-place, adding a 'name_en' key."""
  for p in parties:
    try:
      p["name_en"] = _translator.translate(p["name"]).strip()
    except Exception:
      p["name_en"] = p["name"]  # fallback to original


# ─── Fetch data ───────────────────────────────────────────────────────────────

def _new_session() -> tuple[requests.Session, str]:
  """Create a session and return (session, csrf_token)."""
  session = requests.Session()
  session.headers.update(HEADERS)
  session.get(BASE_URL + PR_PAGE, timeout=30)
  csrf = session.cookies.get("CsrfToken", "")
  session.headers.update({
    "Referer":          BASE_URL + PR_PAGE,
    "X-Csrf-Token":     csrf,
    "X-Requested-With": "XMLHttpRequest",
  })
  return session, csrf


def fetch_pr_votes() -> tuple[int, list[dict], requests.Session]:
  """Returns (total_votes, parties, session) — session is reused for FPTP."""
  session, _ = _new_session()
  resp = session.get(BASE_URL + HANDLER + PR_DATA_FILE, timeout=30)
  resp.raise_for_status()

  parties = []
  for item in resp.json():
    name  = (item.get("PoliticalPartyName") or "").strip()
    votes = int(item.get("TotalVoteReceived") or 0)
    if name and votes > 0:
      parties.append({"name": name, "votes": votes})

  total = sum(p["votes"] for p in parties)
  translate_names(parties)
  return total, parties, session


def fetch_fptp_seats(session: requests.Session) -> dict[str, dict]:
  """
    Reuses the existing session to fetch FPTP win/lead data.
    Returns {nepali_party_name: {"won": int, "lead": int, "total": int}}
    """
  session.headers.update({"Referer": BASE_URL + FPTP_PAGE})
  resp = session.get(BASE_URL + HANDLER + FPTP_DATA_FILE, timeout=30)
  resp.raise_for_status()

  fptp = {}
  for item in resp.json():
    name = (item.get("PoliticalPartyName") or "").strip()
    if name:
      fptp[name] = {
        "won":   int(item.get("TotWin", 0)),
        "lead":  int(item.get("TotLead", 0)),
        "total": int(item.get("TotWinLead", 0)),
      }
  return fptp


# ─── Sainte-Laguë ─────────────────────────────────────────────────────────────

def sainte_lague(parties: list[dict], total_seats: int,
                 threshold: float = 0.0) -> list[dict]:
  """
    Allocate seats using the Sainte-Laguë method (divisors 1, 3, 5, 7 …).

    Returns a list of dicts sorted by seats desc, then votes desc:
    {"name", "votes", "vote_share", "seats", "excluded"}
    """
  total_votes = sum(p["votes"] for p in parties)

  eligible, results = [], []
  for p in parties:
    share = p["votes"] / total_votes if total_votes else 0
    entry = {"name": p["name"], "name_en": p.get("name_en", ""),
             "votes": p["votes"], "vote_share": share, "seats": 0}
    if share >= threshold:
      eligible.append(entry)
    else:
      entry["excluded"] = True
      results.append(entry)

  if not eligible:
    raise ValueError("No parties passed the electoral threshold.")

  # Max-heap via negated quotients
  heap = []
  for i, p in enumerate(eligible):
    heapq.heappush(heap, (-p["votes"] / 1.0, p["name"], i, 1))

  seat_count = [0] * len(eligible)
  for _ in range(total_seats):
    neg_q, name, idx, step = heapq.heappop(heap)
    seat_count[idx] += 1
    next_div = 2 * (step + 1) - 1          # 1→3→5→7→…
    heapq.heappush(heap, (-eligible[idx]["votes"] / next_div,
                          eligible[idx]["name"], idx, step + 1))

  for i, p in enumerate(eligible):
    p["seats"]    = seat_count[i]
    p["excluded"] = False
    results.append(p)

  results.sort(key=lambda x: (-x["seats"], -x["votes"]))
  return results


# ─── Display ──────────────────────────────────────────────────────────────────

def _build_rows(results: list[dict], total_votes: int,
                fptp: dict[str, dict],
                all_parties: list[dict] | None = None) -> list[dict]:
  """Merge PR-qualified parties + FPTP-only parties into one row list."""
  qualified     = [r for r in results if not r.get("excluded")]
  pr_names      = {r["name"] for r in qualified}
  fptp_only_nps = [n for n in fptp if n not in pr_names]

  # Translate FPTP-only party names
  rows = []
  for r in qualified:
    fi = fptp.get(r["name"], {"won": 0, "lead": 0, "total": 0})
    rows.append({
      "name_en":    r.get("name_en") or r["name"],
      "name_np":    r["name"],
      "votes":      r["votes"],
      "vote_share": r["vote_share"],
      "pr_seats":   r["seats"],
      "fptp_won":   fi["won"],
      "fptp_total": fi["total"],
    })

  pr_lookup = {p["name"]: p for p in (all_parties or [])}
  for np_name in fptp_only_nps:
    try:
      en = _translator.translate(np_name).strip()
      if en.lower() == "independent":
        en = "Independent Candidate"
    except Exception:
      en = np_name
    fi   = fptp[np_name]
    pr   = pr_lookup.get(np_name)
    votes = pr["votes"] if pr else 0
    share = votes / total_votes if pr and total_votes else 0.0
    rows.append({
      "name_en":    en,
      "name_np":    np_name,
      "votes":      votes,
      "vote_share": share,
      "pr_seats":   0,
      "fptp_won":   fi["won"],
      "fptp_total": fi["total"],
    })

  rows.sort(key=lambda x: (-x["fptp_won"], -x["votes"]))
  return rows

# ─── Shared data fetch ────────────────────────────────────────────────────────

_CACHE_FILE = os.path.join(os.sep, "tmp", "election2082_cache.json")
_CACHE_TTL  = timedelta(minutes=5)


def _load_cache() -> dict | None:
  try:
    with open(_CACHE_FILE, "r", encoding="utf-8") as f:
      c = json.load(f)
    ts = datetime.fromisoformat(c["_cached_at"])
    if (datetime.now(timezone.utc) - ts) < _CACHE_TTL:
      return c
  except Exception:
    pass
  return None


def _save_cache(data: dict) -> None:
  try:
    payload = {**data, "_cached_at": datetime.now(timezone.utc).isoformat()}
    with open(_CACHE_FILE, "w", encoding="utf-8") as f:
      json.dump(payload, f, ensure_ascii=False)
  except Exception:
    pass


def _get_data() -> dict:
  """Return cached data if fetched within the last 5 minutes, else fetch live."""
  cached = _load_cache()
  if cached is not None:
    cached.pop("_cached_at", None)
    return {**cached, "from_cache": True}

  total_votes, parties, session = fetch_pr_votes()
  fptp    = fetch_fptp_seats(session)
  results = sainte_lague(parties, TOTAL_SEATS, THRESHOLD)
  rows    = _build_rows(results, total_votes, fptp, parties)

  allocated      = sum(r["pr_seats"] for r in rows)
  pr_parties     = len([r for r in results if not r.get("excluded")])
  fptp_parties   = len(fptp)
  tf = {
    "won":   sum(v["won"]   for v in fptp.values()),
    "total": sum(v["total"] for v in fptp.values()),
  }
  fptp_undeclared  = FPTP_TOTAL_SEATS - tf["won"]
  total_undeclared = (TOTAL_SEATS + tf["total"]) - (allocated + tf["won"])

  _NST    = timezone(timedelta(hours=5, minutes=45))
  now_nst = datetime.now(_NST).strftime("%Y-%m-%d %H:%M NST")

  _cache = {
    "fetched_at":        now_nst,
    "total_votes":       total_votes,
    "pr_seats":          TOTAL_SEATS,
    "threshold_pct":     THRESHOLD * 100,
    "pr_parties_qualified": pr_parties,
    "fptp_parties":      fptp_parties,
    "fptp_declared":     tf["won"],
    "fptp_total_seats":  FPTP_TOTAL_SEATS,
    "election_seats":    tf["total"],
    "allocated_pr":      allocated,
    "declared_total":    TOTAL_SEATS + tf["won"],
    "fptp_undeclared":   fptp_undeclared,
    "total_undeclared":  total_undeclared,
    "parties": [
      {
        "name":       r["name_en"],
        "name_np":    r["name_np"],
        "votes":      r["votes"],
        "vote_share": round(r["vote_share"] * 100, 4),
        "pr_seats":   r["pr_seats"],
        "fptp_won":   r["fptp_won"],
        "fptp_total": r["fptp_total"],
      }
      for r in rows
    ],
  }
  _save_cache(_cache)
  return {**_cache, "from_cache": False}


# ─── Endpoints ────────────────────────────────────────────────────────────────

@anvil.server.route('/json')
def json_results(**p):
  data = _get_data()
  body = json.dumps(data, ensure_ascii=False, indent=2)
  resp = anvil.server.HttpResponse(200, body)
  resp.headers["Content-Type"] = "application/json; charset=utf-8"
  return resp


@anvil.server.route('/html')
def html_results(**p):
  d   = _get_data()
  rows = d["parties"]

  def pct(val, denom):
    return f"{val / denom * 100:.2f}%" if val and denom else ""

  party_rows = ""
  for r in rows:
    share = f"{r['vote_share']:.2f}%" if r["vote_share"] else "—"
    votes = f"{r['votes']:,}"          if r["votes"]      else "—"
    seats = str(r["pr_seats"])         if r["pr_seats"]   else ("—" if not r["votes"] else "")
    total_seats = r["pr_seats"] + r["fptp_won"]
    sp    = pct(total_seats, d["declared_total"])
    party_rows += (
      f"<tr>"
      f"<td>{r['name']}</td>"
      f"<td class='r'>{votes}</td>"
      f"<td class='r'>{share}</td>"
      f"<td class='r'>{seats}</td>"
      f"<td class='r'>{r['fptp_won']}</td>"
      f"<td class='r'>{total_seats}</td>"
      f"<td class='r'>{sp}</td>"
      f"</tr>\n"
    )

  total_votes_fmt = f"{d['total_votes']:,}"
  total_share     = sum(r["vote_share"] for r in rows if r["votes"])
  declared_pct    = pct(d["declared_total"], TOTAL_SEATS + FPTP_TOTAL_SEATS)

  html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Nepal Election 2082 Results</title>
  <style>
    body {{ font-family: monospace; padding: 1rem; background:#f9f9f9; color:#111; }}
    h1   {{ font-size:1.1rem; margin-bottom:.25rem; }}
    .meta{{ font-size:.85rem; color:#555; margin-bottom:.5rem; }}
    table{{ border-collapse:collapse; width:100%; font-size:.85rem; }}
    th,td{{ border:1px solid #ccc; padding:.3rem .6rem; white-space:nowrap; }}
    th   {{ background:#222; color:#fff; text-align:center; }}
    tr:nth-child(even){{ background:#f0f0f0; }}
    .r   {{ text-align:right; }}
    tfoot td{{ font-weight:bold; background:#e8e8e8; }}
    .info{{ width:auto; margin-bottom:1rem; }}
    .info th{{ text-align:left; }}
    .info td{{ text-align:right; }}
    .subhdr td{{ background:#444; color:#fff; font-weight:bold; }}
  </style>
</head>
<body>
  <h1>Nepal Election 2082 — FPTP &amp; PR (Sainte-Laguë) Results</h1>
  <p class="meta">
    Fetched: {d['fetched_at']} &nbsp;·&nbsp; {'cached' if d['from_cache'] else 'live'} <br/>
    PR data : <a href="https://result.election.gov.np/PRVoteChartResult2082.aspx">https://result.election.gov.np/PRVoteChartResult2082.aspx</a> <br/>
    FPTP data: <a href="https://result.election.gov.np/FPTPWLChartResult2082.aspx">https://result.election.gov.np/FPTPWLChartResult2082.aspx</a> 
  </p>
  <table class="info">
    <thead>
      <tr><th>Total PR Votes</th><th>PR Seats</th><th>PR Threshold</th><th>PR Parties (qualified)</th></tr>
    </thead>
    <tbody>
      <tr>
        <td>{total_votes_fmt}</td>
        <td>{d['pr_seats']}</td>
        <td>{d['threshold_pct']:.0f}%</td>
        <td>{d['pr_parties_qualified']}</td>
      </tr>
      <tr class="subhdr"><td>FPTP Parties (declared)</td><td>FPTP Seats (declared)</td><td>FPTP Election Seats</td><td>FPTP Total Seats</td></tr>
      <tr>
        <td>{d['fptp_parties']}</td>
        <td>{d['fptp_declared']}</td>
        <td>{d['election_seats']}</td>
        <td>{d['fptp_total_seats']}</td>
      </tr>
    </tbody>
  </table>
  <table>
    <thead>
      <tr>
        <th>Party</th>
        <th>PR Votes</th>
        <th>Share</th>
        <th>PR Seats</th>
        <th>FPTP Seats</th>
        <th>Total Seats</th>
        <th>Seats %</th>
      </tr>
    </thead>
    <tbody>
{party_rows}    </tbody>
    <tfoot>
      <tr>
        <td>Declared</td>
        <td class='r'>{total_votes_fmt}</td>
        <td class='r'>{total_share*100:.2f}%</td>
        <td class='r'>{d['allocated_pr']}</td>
        <td class='r'>{d['fptp_declared']}</td>
        <td class='r'>{d['declared_total']}</td>
        <td class='r'>{declared_pct}</td>
      </tr>
      <tr>
        <td>Un-declared</td>
        <td></td><td></td><td></td>
        <td class='r'>{d['fptp_undeclared']}</td>
        <td class='r'>{d['total_undeclared']}</td>
        <td></td>
      </tr>
    </tfoot>
  </table>
</body>
</html>"""

  resp = anvil.server.HttpResponse(200, html)
  resp.headers["Content-Type"] = "text/html; charset=utf-8"
  return resp


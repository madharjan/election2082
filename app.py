"""
Nepal Election 2082 — Sainte-Laguë PR Seat Allocation + FPTP Results
PR  data: https://result.election.gov.np/PRVoteChartResult2082.aspx
FPTP data: https://result.election.gov.np/FPTPWLChartResult2082.aspx
"""

import sys
import heapq
import requests
from deep_translator import GoogleTranslator

sys.stdout.reconfigure(encoding='utf-8')

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
    session.get(BASE_URL + PR_PAGE, timeout=20)
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
    resp = session.get(BASE_URL + HANDLER + PR_DATA_FILE, timeout=20)
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
    resp = session.get(BASE_URL + HANDLER + FPTP_DATA_FILE, timeout=20)
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


def print_results(total_votes: int, results: list[dict], total_seats: int,
                  threshold: float, fptp: dict[str, dict],
                  all_parties: list[dict] | None = None) -> None:
    rows      = _build_rows(results, total_votes, fptp, all_parties)
    allocated = sum(r["pr_seats"] for r in rows)

    COL = 42
    def seat_pct(val: int, denom: int) -> str:
        if not val or not denom:
            return ""
        return f"{val / denom * 100:.2f}%"

    SEP = f"├{'─'*(COL+2)}┼{'─'*12}┼{'─'*10}┼{'─'*10}┼{'─'*7}┼{'─'*8}┼{'─'*9}┤"
    TOP = f"┌{'─'*(COL+2)}┬{'─'*12}┬{'─'*10}┬{'─'*10}┬{'─'*7}┬{'─'*8}┬{'─'*9}┐"
    BOT = f"└{'─'*(COL+2)}┴{'─'*12}┴{'─'*10}┴{'─'*10}┴{'─'*7}┴{'─'*8}┴{'─'*9}┘"
    HDR = (f"│ {'Party':<{COL}} │ {'PR Votes':>10} │ {'Share':>8} │"
           f" {'PR Seats':>8} │ {'FPTP':>5} │ {'Total':>6} │ {'Seats %':>7} │")

    fptp_parties = len(fptp)
    pr_parties   = len([r for r in results if not r.get("excluded")])
    tf = {"won": sum(v["won"] for v in fptp.values()),
          "total": sum(v["total"] for v in fptp.values())}
    print()
    print(f"  Nepal Election 2082 — FPTP Results & PR (Sainte-Laguë)")
    print(f"  {'─'*54}")
    print(f"  PR  :: Total votes : {total_votes:,}   Seats : {total_seats}   Threshold : {threshold*100:.0f}%   Parties (qualified) : {pr_parties}")
    print(f"  FPTP:: Parties (declared) : {fptp_parties}   Seats (declared): {tf['won']}   Election seats: {tf['total']}  Total seats: {FPTP_TOTAL_SEATS}")
    print()
    print(TOP)
    print(HDR)
    print(SEP)
    for r in rows:
        name  = r["name_en"][:COL]
        votes = f"{r['votes']:,}" if r["votes"] else "—"
        share = f"{r['vote_share']*100:.2f}%" if r["vote_share"] else "—"
        seats = str(r["pr_seats"]) if r["pr_seats"] else ("—" if not r["votes"] else "")
        pct   = seat_pct(r["fptp_total"], tf["total"])
        print(f"│ {name:<{COL}} │ {votes:>10} │ {share:>8} │"
              f" {seats:>8} │ {r['fptp_won']:>5} │ {r['fptp_total']:>6} │ {pct:>7} │")
    print(SEP)
    total_pr_votes = sum(r["votes"] for r in rows)
    total_share    = sum(r["vote_share"] for r in rows if r["votes"]) * 100
    fptp_undeclared  = FPTP_TOTAL_SEATS - tf["won"]
    total_undeclared = (TOTAL_SEATS + tf["total"]) - (allocated + tf["won"])
    declared_pct = seat_pct(tf["total"], tf["total"])
    print(f"│ {'Declared':<{COL}} │ {total_pr_votes:>10,} │ {total_share:>7.2f}% │"
          f" {allocated:>8} │ {tf['won']:>5} │ {tf['total']:>6} │ {declared_pct:>7} │")
    print(f"│ {'Un-declared':<{COL}} │ {'':>10} │ {'':>8} │"
          f" {'':>8} │ {fptp_undeclared:>5} │ {total_undeclared:>6} │ {'':>7} │")
    print(BOT)
    print()



# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    total_votes, parties, session = fetch_pr_votes()
    fptp = fetch_fptp_seats(session)
    results = sainte_lague(parties, TOTAL_SEATS, THRESHOLD)
    print_results(total_votes, results, TOTAL_SEATS, THRESHOLD, fptp, parties)


if __name__ == "__main__":
    main()

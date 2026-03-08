
# Nepal Election 2082

Nepal Election 2082 — FPTP Results & PR (Sainte-Laguë) Seat Allocation

* PR data:   <https://result.election.gov.np/PRVoteChartResult2082.aspx>
* FPTP data: <https://result.election.gov.np/FPTPWLChartResult2082.aspx>

## Public URLs

* https://tiny.cc/election2082
* https://steel-kind-treeshrew.anvil.app/html

## Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

### Python script

```bash
python app.py
```

## Configuration

Edit the constants at the top of `app.py` (or the Configuration cell in the notebook) to adjust:

| Constant           | Default | Description                                    |
| ------------------ | ------- | ---------------------------------------------- |
| `TOTAL_SEATS`      | `110`   | Federal PR seats                               |
| `FPTP_TOTAL_SEATS` | `165`   | Total FPTP constituencies                      |
| `THRESHOLD`        | `0.03`  | Minimum PR vote share (3%); set `0` to disable |

## Sample output

```txt

  Nepal Election 2082 — FPTP Results & PR (Sainte-Laguë)   [2026-03-07 23:01 NST]
  ──────────────────────────────────────────────────────
  PR  :: Total votes : 1,189,048   Seats : 110   Threshold : 3%   Parties (qualified) : 5
  FPTP:: Parties (declared) : 7   Seats (declared): 93   Election seats: 164  Total seats: 165

┌────────────────────────────────────────────┬────────────┬──────────┬──────────┬───────┬────────┬─────────┐
│ Party                                      │   PR Votes │    Share │ PR Seats │  FPTP │  Total │ Seats % │
├────────────────────────────────────────────┼────────────┼──────────┼──────────┼───────┼────────┼─────────┤
│ National Independent Party                 │    609,789 │   51.28% │       61 │    74 │    122 │  74.39% │
│ Nepali Congress                            │    204,383 │   17.19% │       21 │    10 │     18 │  10.98% │
│ Nepal Communist Party (Unified Marxist-Len │    162,734 │   13.69% │       16 │     5 │     12 │   7.32% │
│ Nepali Communist Party                     │     79,499 │    6.69% │        8 │     2 │      7 │   4.27% │
│ National Democratic Party                  │     43,720 │    3.68% │        4 │     1 │      1 │   0.61% │
│ Independent Candidate                      │          — │        — │        — │     1 │      1 │   0.61% │
│ Labor Culture Party                        │     21,466 │    1.81% │          │     0 │      3 │   1.83% │
├────────────────────────────────────────────┼────────────┼──────────┼──────────┼───────┼────────┼─────────┤
│ Declared                                   │  1,121,591 │   94.33% │      110 │    93 │    164 │ 100.00% │
│ Un-declared                                │            │          │          │    72 │     71 │         │
└────────────────────────────────────────────┴────────────┴──────────┴──────────┴───────┴────────┴─────────┘

```

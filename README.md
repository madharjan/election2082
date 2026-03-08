
# Nepal Election 2082

Nepal Election 2082 — FPTP Results & PR (Sainte-Laguë) Seat Allocation

* PR data:   <https://result.election.gov.np/PRVoteChartResult2082.aspx>
* FPTP data: <https://result.election.gov.np/FPTPWLChartResult2082.aspx>

## Public URLs

* https://tiny.cc/election2082

* https://steel-kind-treeshrew.anvil.app/html - webpage

* https://steel-kind-treeshrew.anvil.app/json - API

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
  Nepal Election 2082 — FPTP Results & PR (Sainte-Laguë)   [2026-03-08 19:26 NST]
  * PR data:   https://result.election.gov.np/PRVoteChartResult2082.aspx
  * FPTP data: https://result.election.gov.np/FPTPWLChartResult2082.aspx
  ┌─────────────────────────┬───────────────────────┬─────────────────────┬────────────────────────┐
  │ Total PR Votes          │ PR Seats              │ PR Threshold        │ PR Parties (qualified) │
  ├─────────────────────────┼───────────────────────┼─────────────────────┼────────────────────────┤
  │               5,340,898 │                   110 │                  3% │                      5 │
  ├─────────────────────────┼───────────────────────┼─────────────────────┼────────────────────────┤
  │ FPTP Parties (declared) │ FPTP Seats (declared) │ FPTP Election Seats │ FPTP Total Seats       │
  ├─────────────────────────┼───────────────────────┼─────────────────────┼────────────────────────┤
  │                       7 │                   157 │                 164 │                    165 │
  └─────────────────────────┴───────────────────────┴─────────────────────┴────────────────────────┘

┌────────────────────────────────────────────┬────────────┬──────────┬──────────┬───────┬────────┬─────────┐
│ Party                                      │   PR Votes │    Share │ PR Seats │  FPTP │  Total │ Seats % │
├────────────────────────────────────────────┼────────────┼──────────┼──────────┼───────┼────────┼─────────┤
│ National Independent Party                 │  2,625,861 │   49.17% │       60 │   121 │    181 │  67.79% │
│ Nepali Congress                            │    885,802 │   16.59% │       20 │    17 │     37 │  13.86% │
│ Nepal Communist Party (Unified Marxist-Len │    760,765 │   14.24% │       18 │     7 │     25 │   9.36% │
│ Nepali Communist Party                     │    364,094 │    6.82% │        8 │     7 │     15 │   5.62% │
│ Labor Culture Party                        │    137,674 │    2.58% │          │     3 │      3 │   1.12% │
│ National Democratic Party                  │    189,396 │    3.55% │        4 │     1 │      5 │   1.87% │
│ Independent Candidate                      │          — │        — │        — │     1 │      1 │   0.37% │
├────────────────────────────────────────────┼────────────┼──────────┼──────────┼───────┼────────┼─────────┤
│ Declared                                   │  4,963,592 │   92.94% │      110 │   157 │    267 │  97.09% │
│ Un-declared                                │            │          │          │     8 │      7 │         │
└────────────────────────────────────────────┴────────────┴──────────┴──────────┴───────┴────────┴─────────┘
```

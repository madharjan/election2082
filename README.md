
# Nepal Election 2082

Nepal Election 2082 — FPTP Results & PR (Sainte-Laguë) Seat Allocation

* PR data:   <https://result.election.gov.np/PRVoteChartResult2082.aspx>
* FPTP data: <https://result.election.gov.np/FPTPWLChartResult2082.aspx>

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

  Nepal Election 2082 — FPTP Results & PR (Sainte-Laguë)
  ──────────────────────────────────────────────────────
  PR  :: Total votes : 1,115,518   Seats : 110   Threshold : 3%   Parties (qualified) : 5
  FPTP:: Parties (declared) : 7   Seats (declared): 92   Election seats: 164  Total seats: 165

┌────────────────────────────────────────────┬────────────┬──────────┬──────────┬───────┬────────┬─────────┐
│ Party                                      │   PR Votes │    Share │ PR Seats │  FPTP │  Total │ Seats % │
├────────────────────────────────────────────┼────────────┼──────────┼──────────┼───────┼────────┼─────────┤
│ National Independent Party                 │    572,637 │   51.33% │       61 │    74 │    122 │  74.39% │
│ Nepali Congress                            │    191,823 │   17.20% │       21 │    10 │     18 │  10.98% │
│ Nepal Communist Party (Unified Marxist-Len │    151,447 │   13.58% │       16 │     4 │     12 │   7.32% │
│ Nepali Communist Party                     │     75,777 │    6.79% │        8 │     2 │      7 │   4.27% │
│ National Democratic Party                  │     41,226 │    3.70% │        4 │     1 │      1 │   0.61% │
│ Independent Candidate                      │          — │        — │        — │     1 │      1 │   0.61% │
│ Labor Culture Party                        │     19,995 │    1.79% │          │     0 │      3 │   1.83% │
├────────────────────────────────────────────┼────────────┼──────────┼──────────┼───────┼────────┼─────────┤
│ Declared                                   │  1,052,905 │   94.39% │      110 │    92 │    164 │ 100.00% │
│ Un-declared                                │            │          │          │    73 │     72 │         │
└────────────────────────────────────────────┴────────────┴──────────┴──────────┴───────┴────────┴─────────┘

```

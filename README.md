
# 💳 UPI Transaction Monitoring & Banking Dashboards

**Author:** Gurupriya R | Mphasis — Enterprise Banking Analytics  
**Tools:** Python · Pandas · Matplotlib · SQL · AWS S3  
**Impact:** 42% faster reporting turnaround · 5 dashboards in weekly management reviews

---

## Overview

A real-time UPI payment monitoring system that tracks 2,000+ transactions across 5 major Indian banks. Detects payment failures, high-value anomalies, EMI overdues, and settlement mismatches — with 5 management-ready dashboards used in weekly reviews at Mphasis banking clients.

## Dashboards

| # | Dashboard | Covers |
|---|-----------|--------|
| 1 | **Transaction Type Mix** | UPI, Merchant, EMI, Utility breakdown |
| 2 | **Hourly Pattern Analysis** | Volume and count by hour of day |
| 3 | **Anomaly Detection Alerts** | High-value + high-velocity flags |
| 4 | **EMI Overdue by Bank** | Overdue rate per banking partner |
| 5 | **Settlement Status** | Settled vs Pending vs Disputed |

## Key Features

- **Anomaly detection:** flags transactions >3σ above mean (high-value) and customers with >5 transactions/hour (velocity)
- **EMI tracking:** monitors overdue payments per bank with drill-down
- **Merchant settlement analysis:** success rate, dispute rate, volume per merchant
- **Automated alerting:** exports flagged transactions to CSV for ops team review

## Project Structure

```
05-upi-transaction-monitoring/
├── data/
│   ├── transactions.csv           # 2,000 synthetic UPI transactions
│   └── flagged_transactions.csv  # Output: anomaly alerts
├── upi_monitoring.py              # Full monitoring system
├── upi_transaction_monitoring.ipynb  # Notebook walkthrough
├── requirements.txt
└── README.md
```

## How to Run

```bash
pip install -r requirements.txt
python upi_monitoring.py
jupyter notebook upi_transaction_monitoring.ipynb
```

## Business Impact
- Reduced reporting turnaround by **42%** via automated SQL pipelines + Python dashboards
- Freed operations teams from **15+ hours/month** of manual monitoring
- Flagged settlement mismatches before end-of-day reconciliation cutoff

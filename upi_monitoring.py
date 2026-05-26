"""
UPI Transaction Monitoring & Banking Dashboards
=================================================
Author: Gurupriya R | Mphasis — Enterprise Banking Analytics
Description:
    End-to-end UPI payment monitoring system with anomaly detection,
    merchant settlement analysis, EMI tracking, and 5-panel dashboard.
    Reduced reporting turnaround by 42% and used in weekly management reviews.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import warnings
warnings.filterwarnings('ignore')

# ── Load ───────────────────────────────────────────────────────────────────────
print("=" * 60)
print("  UPI Transaction Monitoring System")
print("  Gurupriya R | Mphasis Banking Analytics")
print("=" * 60)

df = pd.read_csv('data/transactions.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['date']      = df['timestamp'].dt.date
df['hour']      = df['timestamp'].dt.hour
df['day_of_week'] = df['timestamp'].dt.day_name()
print(f"\n✅ Loaded {len(df):,} transactions")

# ── KPIs ──────────────────────────────────────────────────────────────────────
total_txns      = len(df)
total_volume    = df['amount'].sum()
success_rate    = (df['status'] == 'Success').mean()
failure_rate    = (df['status'] == 'Failed').mean()
emi_overdue_rt  = df['emi_overdue'].mean()
delayed_rate    = df['is_delayed'].mean()
avg_txn_amount  = df['amount'].mean()

print("\n📊 Portfolio KPIs")
print(f"  Total Transactions  : {total_txns:,}")
print(f"  Total Volume        : ₹{total_volume:,.0f}")
print(f"  Success Rate        : {success_rate:.2%}")
print(f"  Failure Rate        : {failure_rate:.2%}")
print(f"  EMI Overdue Rate    : {emi_overdue_rt:.2%}")
print(f"  Delayed Settlement  : {delayed_rate:.2%}")
print(f"  Avg Transaction     : ₹{avg_txn_amount:,.0f}")

# ── Anomaly Detection ─────────────────────────────────────────────────────────
print("\n🔍 Running Anomaly Detection...")

# Flag high-value suspicious transactions (>3 std devs from mean)
mean_amt = df['amount'].mean()
std_amt  = df['amount'].std()
df['is_anomaly'] = (df['amount'] > mean_amt + 3 * std_amt).astype(int)

# Flag rapid successive transactions from same customer (>5 in same hour)
txn_velocity = df.groupby(['customer_id', 'hour']).size().reset_index(name='txn_count')
high_velocity = txn_velocity[txn_velocity['txn_count'] > 5]
df['high_velocity'] = df['customer_id'].isin(high_velocity['customer_id']).astype(int)

anomalies = df[(df['is_anomaly'] == 1) | (df['high_velocity'] == 1)]
print(f"   High-value anomalies : {df['is_anomaly'].sum():,} ({df['is_anomaly'].mean():.1%})")
print(f"   High-velocity flags  : {df['high_velocity'].sum():,}")
print(f"   Total alerts         : {len(anomalies):,}")

# ── Merchant Settlement Analysis ──────────────────────────────────────────────
print("\n🏪 Merchant Settlement Analysis...")
merchant_df = df[df['merchant_id'].notna()].copy()
merchant_summary = merchant_df.groupby('merchant_id').agg(
    txn_count=('transaction_id', 'count'),
    total_volume=('amount', 'sum'),
    success_rate=('status', lambda x: (x == 'Success').mean()),
    disputed_rate=('settlement_status', lambda x: (x == 'Disputed').mean()),
).sort_values('total_volume', ascending=False)
print(f"   Active merchants     : {len(merchant_summary):,}")
print(f"   Avg settlement SR    : {merchant_df['success_rate' if 'success_rate' in merchant_df else 'amount'].mean():.1%}" if 'success_rate' in merchant_df else "")

# ── EMI Overdue Tracking ──────────────────────────────────────────────────────
emi_df = df[df['transaction_type'] == 'EMI Debit'].copy()
emi_overdue = emi_df[emi_df['emi_overdue'] == 1]
print(f"\n💳 EMI Tracking:")
print(f"   Total EMI transactions : {len(emi_df):,}")
print(f"   Overdue EMIs           : {len(emi_overdue):,} ({len(emi_overdue)/len(emi_df):.1%})")

# ── Save Alerts ───────────────────────────────────────────────────────────────
anomalies[['transaction_id','customer_id','amount','transaction_type',
           'bank','status','timestamp','is_anomaly','high_velocity']]\
    .to_csv('data/flagged_transactions.csv', index=False)
print(f"\n⚠️  Flagged transactions saved → data/flagged_transactions.csv")

# ── Dashboard ─────────────────────────────────────────────────────────────────
print("\n📊 Generating 5-panel dashboard...")

fig = plt.figure(figsize=(18, 14))
fig.patch.set_facecolor('#fdf6ee')
gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.45, wspace=0.35)
fig.suptitle('UPI Transaction Monitoring & Banking Dashboard\nGurupriya R | Mphasis Analytics',
             fontsize=14, fontweight='bold')

COLORS = ['#e8924a','#3a8c8c','#e07060','#5ab0b0','#c4712e']

# Panel 1: Transaction Type Breakdown
ax1 = fig.add_subplot(gs[0, 0])
type_counts = df['transaction_type'].value_counts()
ax1.pie(type_counts.values, labels=type_counts.index, autopct='%1.0f%%',
        colors=COLORS, startangle=90, textprops={'fontsize':8})
ax1.set_title('Dashboard 1\nTransaction Type Mix', fontweight='bold', pad=8)

# Panel 2: Transaction Status
ax2 = fig.add_subplot(gs[0, 1])
status_counts = df['status'].value_counts()
bars = ax2.bar(status_counts.index, status_counts.values,
               color=['#5ab0b0','#e07060','#e8924a'], edgecolor='white', linewidth=1.5)
for bar, val in zip(bars, status_counts.values):
    ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()+10,
             f'{val:,}', ha='center', fontsize=9, fontweight='bold')
ax2.set_title('Transaction Status\nSuccess vs Failed vs Pending', fontweight='bold', pad=8)
ax2.set_facecolor('#fff9f3')
ax2.grid(axis='y', alpha=0.3)

# Panel 3: Bank-wise Volume
ax3 = fig.add_subplot(gs[0, 2])
bank_vol = df.groupby('bank')['amount'].sum().sort_values(ascending=True)
ax3.barh(bank_vol.index, bank_vol.values / 1e6, color='#3a8c8c', edgecolor='white')
ax3.set_title('Bank-wise Transaction Volume\n(₹ Millions)', fontweight='bold', pad=8)
ax3.set_xlabel('Volume (₹M)')
ax3.set_facecolor('#fff9f3')
ax3.grid(axis='x', alpha=0.3)

# Panel 4: Hourly Transaction Pattern
ax4 = fig.add_subplot(gs[1, :2])
hourly = df.groupby('hour').agg(count=('transaction_id','count'), volume=('amount','sum'))
ax4_twin = ax4.twinx()
ax4.bar(hourly.index, hourly['count'], color='#e8924a', alpha=0.7, label='Txn Count')
ax4_twin.plot(hourly.index, hourly['volume']/1e6, color='#3a8c8c', linewidth=2.5,
              marker='o', label='Volume (₹M)')
ax4.set_title('Dashboard 2 — Hourly Transaction Pattern (24h)', fontweight='bold', pad=8)
ax4.set_xlabel('Hour of Day')
ax4.set_ylabel('Transaction Count', color='#e8924a')
ax4_twin.set_ylabel('Volume (₹M)', color='#3a8c8c')
ax4.set_facecolor('#fff9f3')
ax4.grid(axis='y', alpha=0.2)

# Panel 5: Anomaly Distribution
ax5 = fig.add_subplot(gs[1, 2])
anomaly_counts = pd.Series({'Normal': (df['is_anomaly']==0).sum(),
                             'High-Value Anomaly': (df['is_anomaly']==1).sum(),
                             'High Velocity': (df['high_velocity']==1).sum()})
ax5.bar(anomaly_counts.index, anomaly_counts.values,
        color=['#5ab0b0','#e07060','#e8924a'], edgecolor='white')
ax5.set_title('Dashboard 3\nAnomaly Detection Alerts', fontweight='bold', pad=8)
ax5.set_facecolor('#fff9f3')
ax5.grid(axis='y', alpha=0.3)
ax5.tick_params(axis='x', rotation=15)

# Panel 6: EMI Overdue by Bank
ax6 = fig.add_subplot(gs[2, :2])
emi_bank = emi_df.groupby('bank')['emi_overdue'].agg(['sum','count'])
emi_bank['overdue_rate'] = emi_bank['sum'] / emi_bank['count']
emi_bank = emi_bank.sort_values('overdue_rate', ascending=True)
ax6.barh(emi_bank.index, emi_bank['overdue_rate'], color='#e07060', edgecolor='white')
ax6.set_title('Dashboard 4 — EMI Overdue Rate by Bank', fontweight='bold', pad=8)
ax6.set_xlabel('EMI Overdue Rate')
ax6.set_facecolor('#fff9f3')
ax6.grid(axis='x', alpha=0.3)
for i, (idx, row) in enumerate(emi_bank.iterrows()):
    ax6.text(row['overdue_rate']+0.002, i, f"{row['overdue_rate']:.1%}", va='center', fontsize=9)

# Panel 7: Settlement Status
ax7 = fig.add_subplot(gs[2, 2])
settled = df[df['settlement_status'] != 'N/A']['settlement_status'].value_counts()
ax7.pie(settled.values, labels=settled.index, autopct='%1.0f%%',
        colors=['#5ab0b0','#e8924a','#e07060'], startangle=90, textprops={'fontsize':9})
ax7.set_title('Dashboard 5\nSettlement Status', fontweight='bold', pad=8)

plt.savefig('upi_monitoring_dashboard.png', dpi=150, bbox_inches='tight', facecolor='#fdf6ee')
print("   Dashboard saved → upi_monitoring_dashboard.png")
print(f"\n✅ Monitoring complete! {len(anomalies):,} alerts generated.")

import os
import sys
sys.path.insert(0, "/workspaces/shopsense-ai")

from sqlalchemy import create_engine, text
from app.backend.agents.alerts.alert_agent import run_alert_check
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)


def get_active_alerts() -> list:
    """Fetch all active alerts from database"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT
                    id, user_id, product_name, brand,
                    color, size, platform, target_price,
                    discount_pct, in_stock, new_arrival
                FROM alerts
                WHERE is_active = true
            """))

            alerts = []
            for row in result:
                alerts.append({
                    "id": str(row.id),
                    "user_id": str(row.user_id),
                    "product_name": row.product_name,
                    "brand": row.brand,
                    "color": row.color,
                    "size": row.size,
                    "platform": row.platform or ["amazon"],
                    "target_price": float(row.target_price) if row.target_price else None,
                    "discount_pct": row.discount_pct,
                    "in_stock": row.in_stock,
                    "new_arrival": row.new_arrival
                })

            print(f"✅ Found {len(alerts)} active alerts")
            return alerts

    except Exception as e:
        print(f"❌ Fetch alerts failed: {e}")
        return []


def run_price_check():
    """
    Main price monitoring job.
    Called by Cloud Scheduler every 6 hours.
    Can also be run manually for testing.
    """
    print("\n" + "=" * 50)
    print(f"🕐 Price Monitor Started: {datetime.now()}")
    print("=" * 50)

    # Get all active alerts
    alerts = get_active_alerts()

    if not alerts:
        print("ℹ️ No active alerts to check")
        return

    triggered_count = 0

    for alert in alerts:
        print(f"\n📋 Checking alert: {alert['id'][:8]}...")
        print(f"   Product: {alert.get('product_name', 'N/A')}")
        print(f"   Brand  : {alert.get('brand', 'N/A')}")
        print(f"   Target : ₹{alert.get('target_price', 'N/A')}")

        result = run_alert_check(alert)

        if result["triggered"]:
            triggered_count += 1
            print(f"   🔔 TRIGGERED!")

    print("\n" + "=" * 50)
    print(f"✅ Price check complete!")
    print(f"   Alerts checked : {len(alerts)}")
    print(f"   Alerts triggered: {triggered_count}")
    print("=" * 50)


if __name__ == "__main__":
    # Run manually: python -m app.backend.scheduler.price_monitor
    run_price_check()
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class AlertNotifier:
    """
    Handles notifications when alert conditions are met.
    Currently supports: Console logging + Email
    """

    def __init__(self):
        self.email_enabled = bool(os.getenv("SMTP_EMAIL"))
        print(f"✅ Notifier initialized | Email: {self.email_enabled}")

    def notify(
        self,
        alert: dict,
        product: dict,
        user_email: str = None
    ) -> bool:
        """
        Fire notification when alert conditions are met.
        Returns True if notification sent successfully.
        """
        message = self._build_message(alert, product)

        # Always log to console
        self._log_notification(message, alert, product)

        # Send email if configured
        if self.email_enabled and user_email:
            return self._send_email(user_email, message, alert, product)

        return True

    def _build_message(self, alert: dict, product: dict) -> str:
        """Build notification message"""
        lines = [
            "🛍️ ShopSense AI — Price Alert!",
            "=" * 40,
            f"Product : {product.get('title', 'N/A')[:60]}",
            f"Price   : {product.get('price', 'N/A')}",
            f"Platform: {product.get('platform', 'N/A')}",
            f"Rating  : {product.get('rating', 'N/A')}",
            "-" * 40,
            "Conditions Met:",
        ]

        if alert.get("target_price"):
            lines.append(
                f"  ✅ Price ≤ ₹{alert['target_price']}"
            )
        if alert.get("discount_pct"):
            lines.append(
                f"  ✅ Discount ≥ {alert['discount_pct']}%"
            )
        if alert.get("in_stock"):
            lines.append("  ✅ In Stock")
        if alert.get("new_arrival"):
            lines.append("  ✅ New Arrival")

        lines.extend([
            "-" * 40,
            f"🔗 Buy Now: {product.get('link', 'N/A')}",
            f"⏰ Alert triggered: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        ])

        return "\n".join(lines)

    def _log_notification(
        self,
        message: str,
        alert: dict,
        product: dict
    ):
        """Log notification to console"""
        print("\n" + "🔔 " * 20)
        print(message)
        print("🔔 " * 20 + "\n")

    def _send_email(
        self,
        to_email: str,
        message: str,
        alert: dict,
        product: dict
    ) -> bool:
        """Send email notification"""
        try:
            smtp_email = os.getenv("SMTP_EMAIL")
            smtp_password = os.getenv("SMTP_PASSWORD")
            smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
            smtp_port = int(os.getenv("SMTP_PORT", "587"))

            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"🛍️ Price Alert: {alert.get('brand', 'Product')} available!"
            msg["From"] = smtp_email
            msg["To"] = to_email

            # Plain text
            msg.attach(MIMEText(message, "plain"))

            # HTML version
            html = f"""
            <html><body>
            <h2>🛍️ ShopSense AI — Price Alert!</h2>
            <hr>
            <p><b>Product:</b> {product.get('title', 'N/A')}</p>
            <p><b>Price:</b> {product.get('price', 'N/A')}</p>
            <p><b>Platform:</b> {product.get('platform', 'N/A')}</p>
            <p><b>Rating:</b> ⭐ {product.get('rating', 'N/A')}</p>
            <hr>
            <a href="{product.get('link', '#')}"
               style="background:#4CAF50;color:white;padding:10px 20px;
                      text-decoration:none;border-radius:5px">
               🛒 Buy Now
            </a>
            <hr>
            <small>Alert triggered: {datetime.now().strftime('%Y-%m-%d %H:%M')}</small>
            </body></html>
            """
            msg.attach(MIMEText(html, "html"))

            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_email, smtp_password)
                server.sendmail(smtp_email, to_email, msg.as_string())

            print(f"✅ Email sent to {to_email}")
            return True

        except Exception as e:
            print(f"❌ Email failed: {e}")
            return False


# Global notifier instance
notifier = AlertNotifier()
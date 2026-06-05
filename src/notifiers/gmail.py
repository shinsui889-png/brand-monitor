"""Gmail通知モジュール"""
import smtplib
import logging
from datetime import datetime, timezone, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .base import BaseNotifier

logger = logging.getLogger(__name__)

JST = timezone(timedelta(hours=9))
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


class GmailNotifier(BaseNotifier):
    """smtplib + Gmailアプリパスワードで通知するクラス"""

    def __init__(self, user: str, app_password: str, to: str):
        self.user = user
        self.app_password = app_password
        self.to = to

    def notify(self, items: list[dict]) -> None:
        """
        新着商品をまとめて1通のメールで送信する。

        Args:
            items: 通知する商品リスト
        """
        if not items:
            logger.info("通知対象なし → スキップ")
            return

        now_jst = datetime.now(JST).strftime("%Y/%m/%d %H:%M JST")
        count = len(items)

        # ブランド一覧（件名に表示）
        brands = list(dict.fromkeys(i["brand"] for i in items))
        brand_str = ", ".join(brands[:3])
        if len(brands) > 3:
            brand_str += f" 他{len(brands) - 3}ブランド"

        subject = f"[仕入れ監視] 新着 {count}件 - {brand_str} ({now_jst})"

        # プレーンテキスト本文
        plain = self._build_plain(items, now_jst)

        # HTML本文
        html = self._build_html(items, now_jst)

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.user
        msg["To"] = self.to
        msg.attach(MIMEText(plain, "plain", "utf-8"))
        msg.attach(MIMEText(html, "html", "utf-8"))

        try:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.ehlo()
                server.starttls()
                server.login(self.user, self.app_password)
                server.sendmail(self.user, self.to, msg.as_string())
            logger.info(f"Gmail送信完了: {count}件 → {self.to}")
        except smtplib.SMTPException as e:
            logger.error(f"Gmail送信エラー: {e}")
            raise

    def _build_plain(self, items: list[dict], now_jst: str) -> str:
        lines = [
            f"■ 新着商品通知（{len(items)}件）",
            f"  {now_jst}",
            "",
        ]
        for i, item in enumerate(items, 1):
            lines += [
                f"[{i}] {item['brand']}",
                f"    商品名: {item['name']}",
                f"    価格:   ¥{item['price']:,}",
                f"    URL:    {item['url']}",
                "",
            ]
        lines += [
            "─" * 40,
            "※ このメールはGitHub Actionsによる自動送信です",
        ]
        return "\n".join(lines)

    def _build_html(self, items: list[dict], now_jst: str) -> str:
        rows = ""
        for i, item in enumerate(items, 1):
            rows += f"""
            <tr style="background:{'#f9f9f9' if i % 2 == 0 else '#fff'};">
              <td style="padding:8px 12px; font-weight:bold; color:#c2185b; width:28px;">{i}</td>
              <td style="padding:8px 12px;">
                <strong>{item['brand']}</strong><br>
                <span style="font-size:14px;">{item['name']}</span><br>
                <span style="color:#e53935; font-weight:bold;">¥{item['price']:,}</span><br>
                <a href="{item['url']}" style="color:#1565c0; font-size:12px; word-break:break-all;">{item['url']}</a>
              </td>
            </tr>"""

        return f"""<!DOCTYPE html>
<html lang="ja"><body style="font-family:sans-serif; max-width:680px; margin:0 auto;">
  <h2 style="color:#ad1457; border-bottom:2px solid #ad1457; padding-bottom:6px;">
    🛍️ 仕入れ監視 新着 {len(items)}件
  </h2>
  <p style="color:#555; font-size:13px;">{now_jst}</p>
  <table style="width:100%; border-collapse:collapse; font-size:14px;">
    <thead>
      <tr style="background:#ad1457; color:#fff;">
        <th style="padding:8px 12px;">#</th>
        <th style="padding:8px 12px; text-align:left;">商品情報</th>
      </tr>
    </thead>
    <tbody>{rows}</tbody>
  </table>
  <p style="color:#999; font-size:11px; margin-top:16px;">
    ※ このメールはGitHub Actionsによる自動送信です
  </p>
</body></html>"""

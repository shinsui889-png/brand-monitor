"""エントリーポイント: 1時間ごとに実行されるメイン処理"""
import logging
import sys

import yaml
from pathlib import Path

from config import (
    load_brands_config,
    RAKUTEN_APP_ID,
    GMAIL_USER,
    GMAIL_APP_PASSWORD,
    NOTIFY_TO,
)
from fetchers.rakuten import fetch_all_new_items
from notifiers.gmail import GmailNotifier
from storage import filter_new_items, mark_as_notified

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


def main() -> int:
    """
    メイン処理。

    Returns:
        終了コード（0: 正常, 1: エラー）
    """
    logger.info("=== brand-monitor 起動 ===")

    # --- 設定読み込み ---
    try:
        config = load_brands_config()
    except Exception as e:
        logger.error(f"設定ファイル読み込みエラー: {e}")
        return 1

    sites = config.get("sites", [])
    storage_config = config.get("storage", {})
    max_days = storage_config.get("max_days", 30)
    max_count = storage_config.get("max_count", 5000)

    # --- シークレット読み込み ---
    try:
        app_id = RAKUTEN_APP_ID()
        notifier = GmailNotifier(
            user=GMAIL_USER(),
            app_password=GMAIL_APP_PASSWORD(),
            to=NOTIFY_TO(),
        )
    except EnvironmentError as e:
        logger.error(str(e))
        return 1

    # --- 商品取得 ---
    all_items: list[dict] = []
    for site in sites:
        if site.get("api") != "rakuten":
            logger.warning(f"未対応のAPI: {site.get('api')} → スキップ")
            continue
        items = fetch_all_new_items(app_id, site)
        all_items.extend(items)

    if not all_items:
        logger.info("取得商品なし → 終了")
        return 0

    # --- 新着フィルタリング ---
    new_items = filter_new_items(all_items, max_days, max_count)

    # --- 通知 ---
    if new_items:
        try:
            notifier.notify(new_items)
            mark_as_notified(new_items, max_days, max_count)
        except Exception as e:
            logger.error(f"通知エラー: {e}")
            return 1
    else:
        logger.info("新着なし → 通知スキップ")

    logger.info("=== 処理完了 ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())

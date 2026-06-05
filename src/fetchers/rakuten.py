"""楽天市場 商品検索API 取得モジュール"""
import time
import logging
import requests
from typing import Generator

logger = logging.getLogger(__name__)

RAKUTEN_API_URL = (
    "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20220601"
)
# APIリクエスト間隔（秒）- サイトへの負荷対策
REQUEST_INTERVAL = 1.0


def fetch_new_items(
    app_id: str,
    shop_code: str,
    brand: str,
    max_items: int = 30,
) -> list[dict]:
    """
    楽天APIで指定ブランドの新着商品を取得する。

    Args:
        app_id: 楽天アプリID
        shop_code: 楽天ショップID（例: bazzstore）
        brand: 監視ブランド名（例: MOUSSY）
        max_items: 最大取得件数

    Returns:
        商品情報リスト [{"id", "brand", "name", "price", "url", "site"}]
    """
    params = {
        "applicationId": app_id,
        "shopCode": shop_code,
        "keyword": brand,
        "hits": min(max_items, 30),  # APIの上限は30件/リクエスト
        "sort": "-updateTimestamp",  # 新着順
        "formatVersion": 2,
    }

    try:
        logger.info(f"楽天API取得: shop={shop_code}, brand={brand}")
        resp = requests.get(RAKUTEN_API_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        logger.error(f"楽天API取得エラー: {e}")
        return []
    finally:
        time.sleep(REQUEST_INTERVAL)  # 負荷対策

    items = []
    for item in data.get("Items", []):
        item_info = {
            "id": item.get("itemCode", ""),       # 楽天商品コード（一意ID）
            "brand": brand,
            "name": item.get("itemName", ""),
            "price": item.get("itemPrice", 0),
            "url": item.get("itemUrl", ""),
            "site": shop_code,
        }
        # IDが空の場合はURLをIDとして使用
        if not item_info["id"]:
            item_info["id"] = item_info["url"]

        if item_info["id"] and item_info["name"]:
            items.append(item_info)

    logger.info(f"  → {len(items)}件取得")
    return items


def fetch_all_new_items(
    app_id: str,
    site_config: dict,
) -> list[dict]:
    """
    サイト設定に基づき、全ブランドの新着商品を取得する。

    Args:
        app_id: 楽天アプリID
        site_config: brands.yml のサイト設定1件

    Returns:
        全ブランドの商品リスト（重複なし）
    """
    shop_code = site_config["shop_code"]
    brands = site_config.get("brands", [])
    all_items = []

    for brand in brands:
        items = fetch_new_items(app_id, shop_code, brand)
        all_items.extend(items)

    return all_items

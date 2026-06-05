"""通知済み商品データの管理モジュール"""
import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

DATA_FILE = Path(__file__).parent.parent / "data" / "notified.json"


def _load() -> dict:
    """notified.json を読み込む"""
    if not DATA_FILE.exists():
        return {"schema_version": 1, "last_cleanup": None, "items": []}
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


def _save(data: dict) -> None:
    """notified.json に書き込む"""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def filter_new_items(
    items: list[dict],
    max_days: int = 30,
    max_count: int = 5000,
) -> list[dict]:
    """
    通知済みIDと照合し、未通知の新着商品のみを返す。
    同時に古いエントリのクリーンアップも実施。

    Args:
        items: 今回取得した商品リスト
        max_days: 保存期間（日）
        max_count: 最大保存件数

    Returns:
        未通知の新着商品リスト
    """
    data = _load()
    notified_ids = {entry["id"] for entry in data["items"]}

    # 未通知の商品を抽出
    new_items = [item for item in items if item["id"] not in notified_ids]
    logger.info(f"取得 {len(items)}件 → 新着 {len(new_items)}件（既通知 {len(notified_ids)}件）")

    return new_items


def mark_as_notified(
    items: list[dict],
    max_days: int = 30,
    max_count: int = 5000,
) -> None:
    """
    通知済みとしてIDを保存し、古いエントリをクリーンアップする。

    Args:
        items: 通知した商品リスト
        max_days: 保存期間（日）
        max_count: 最大保存件数
    """
    if not items:
        return

    data = _load()
    now_utc = datetime.now(timezone.utc).isoformat()

    # 新規エントリを追加
    for item in items:
        data["items"].append({
            "id": item["id"],
            "brand": item.get("brand", ""),
            "site": item.get("site", ""),
            "notified_at": now_utc,
        })

    # クリーンアップ（保存期間・件数上限）
    data["items"] = _cleanup(data["items"], max_days, max_count)
    data["last_cleanup"] = now_utc

    _save(data)
    logger.info(f"通知済みとして保存: {len(items)}件 → 合計 {len(data['items'])}件")


def _cleanup(
    items: list[dict],
    max_days: int,
    max_count: int,
) -> list[dict]:
    """古いエントリを削除する"""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=max_days)).isoformat()

    # 1. 保存期間を超えたものを削除
    before = len(items)
    items = [x for x in items if x.get("notified_at", "") >= cutoff]
    removed_by_date = before - len(items)

    # 2. 件数上限を超えたら古い順に削除
    removed_by_count = 0
    if len(items) > max_count:
        items = sorted(items, key=lambda x: x.get("notified_at", ""))
        items = items[-max_count:]
        removed_by_count = len(items) - max_count

    if removed_by_date or removed_by_count:
        logger.info(
            f"クリーンアップ: 期間超過 {removed_by_date}件, "
            f"件数超過 {removed_by_count}件 削除 → 残 {len(items)}件"
        )
    return items

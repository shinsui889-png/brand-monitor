"""設定・シークレット読み込み"""
import os
import yaml
from pathlib import Path


def load_brands_config() -> dict:
    """brands.yml を読み込む"""
    config_path = Path(__file__).parent.parent / "config" / "brands.yml"
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_env(key: str, required: bool = True) -> str:
    """環境変数を取得。required=True の場合は未設定でエラー"""
    value = os.environ.get(key, "")
    if required and not value:
        raise EnvironmentError(
            f"環境変数 {key} が設定されていません。"
            "GitHub Secrets または .env ファイルを確認してください。"
        )
    return value


# 楽天API
RAKUTEN_APP_ID = lambda: get_env("RAKUTEN_APP_ID")

# Gmail
GMAIL_USER = lambda: get_env("GMAIL_USER")
GMAIL_APP_PASSWORD = lambda: get_env("GMAIL_APP_PASSWORD")
NOTIFY_TO = lambda: get_env("NOTIFY_TO")

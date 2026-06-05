# brand-monitor

中古アパレルせどり仕入れ支援ツール。  
指定ブランドの新着商品を1時間ごとに監視し、Gmailで通知します。

## 対応サイト

| サイト | API | 状態 |
|---|---|---|
| BAZZSTORE | 楽天市場API | ✅ フェーズ1 |
| ベクトルパーク | 楽天市場API | 🔜 フェーズ3 |
| トレジャーファクトリー | Yahoo!ショッピングAPI | 🔜 フェーズ3 |

## セットアップ

### 1. 楽天アプリIDを取得

1. https://webservice.rakuten.co.jp/ にアクセス
2. 新規アプリ登録 → アプリIDを取得

### 2. Gmailアプリパスワードを取得

1. Googleアカウント → セキュリティ → 2段階認証を有効化
2. アプリパスワードを生成（「メール」用）

### 3. GitHub Secretsに登録

リポジトリの Settings → Secrets and variables → Actions → New repository secret で以下を登録：

| Secret名 | 説明 |
|---|---|
| `RAKUTEN_APP_ID` | 楽天アプリID |
| `GMAIL_USER` | 送信元Gmailアドレス |
| `GMAIL_APP_PASSWORD` | Gmailアプリパスワード |
| `NOTIFY_TO` | 通知先メールアドレス |

### 4. 監視ブランドの設定

`config/brands.yml` を編集してブランドを追加します：

```yaml
sites:
  - name: bazzstore
    api: rakuten
    shop_code: bazzstore
    brands:
      - MOUSSY
      - "Y's"   # 記号含む場合はクォートで囲む
```

## ローカルテスト

```bash
# 仮想環境の作成
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 依存パッケージのインストール
pip install -r requirements.txt

# 環境変数を設定してテスト実行
export RAKUTEN_APP_ID=your_app_id
export GMAIL_USER=your@gmail.com
export GMAIL_APP_PASSWORD=your_app_password
export NOTIFY_TO=shinsui889@gmail.com

cd src && python main.py
```

## 実行スケジュール

GitHub Actions により **毎時0分（UTC）** に自動実行されます。  
日本時間では 毎時9時〜翌0時（UTC 0〜15時）に実行されます。

## 通知形式

件名: `[仕入れ監視] 新着 3件 - MOUSSY (2026/6/5 15:00 JST)`

本文: 各商品の**ブランド・商品名・価格・URL**をまとめて1通で送信

## データ保存

- `data/notified.json` に通知済み商品IDを保存
- 30日以上経過したデータは自動削除
- 最大5,000件まで保存（超過分は古い順に削除）

## LINE通知への切り替え（将来対応）

`src/notifiers/line.py` を追加し、`config/brands.yml` の `notification.method` を `line` に変更するだけで切り替え可能な設計になっています。

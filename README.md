# mimamori-backend

見守りぬいぐるみ開発版のバックエンドAPI

## 概要

このプロジェクトは「見守りぬいぐるみ」システムのバックエンドAPIです。FastAPIを使用して構築されており、WebSocket通信をサポートしています。

## 技術スタック

- **フレームワーク**: FastAPI
- **サーバー**: Uvicorn
- **コンテナ**: Docker & Docker Compose
- **言語**: Python 3.x

## 機能

- REST API エンドポイント
- WebSocket通信サポート
- CORS設定（フロントエンド連携用）

## セットアップ

### 前提条件

- Docker Desktop がインストールされていること
- Git がインストールされていること

### インストール手順

1. リポジトリをクローン
```bash
git clone [リポジトリURL]
cd mimamori-backend
```

2. Dockerコンテナを起動
```bash
docker-compose up -d
```

3. APIが起動していることを確認
```bash
curl http://localhost:8000
# レスポンス: {"message":"Hello, World!"}
```

### ローカル開発（Dockerを使わない場合）

1. Python仮想環境を作成
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. 依存関係をインストール
```bash
pip install -r requirements.txt
```

3. サーバーを起動
```bash
python app/main.py
```

## API仕様

### エンドポイント

#### GET /
- **説明**: ヘルスチェック用エンドポイント
- **レスポンス**: `{"message": "Hello, World!"}`

#### WebSocket /ws
- **説明**: WebSocket接続用エンドポイント
- **用途**: リアルタイム通信（実装予定）

### CORS設定

現在、以下のオリジンからのアクセスを許可しています：
- `http://localhost:3001`

## 開発方法

### コードの変更

`app/main.py`を編集すると、Uvicornのホットリロード機能により自動的に反映されます。

### 新しい依存関係の追加

1. ローカル環境の場合
```bash
pip install [パッケージ名]
pip freeze > requirements.txt
```

2. Dockerコンテナの再ビルド
```bash
docker-compose down
docker-compose up -d --build
```

## トラブルシューティング

### ポート8000が使用中の場合

```bash
# 使用中のプロセスを確認
lsof -i :8000

# Dockerコンテナを確認
docker ps

# 必要に応じてコンテナを停止
docker-compose down
```

### Dockerコンテナのログを確認

```bash
docker-compose logs -f app
```


## コントリビューション

1. featureブランチを作成
```bash
git checkout -b feature/your-feature-name
```

2. 変更をコミット
```bash
git add .
git commit -m "feat: 機能の説明"
```

3. プルリクエストを作成

# 見守りシステム バックエンド

高齢者見守りシステムのバックエンドAPI。音声処理、会話管理、日次サマリー生成などの機能を提供します。

## システム構成

### アーキテクチャ

3層アーキテクチャを採用し、責務の分離とメンテナンス性を重視した設計。

- **UI層 (routers)**: HTTPリクエスト/レスポンス処理
- **Service層 (services)**: ビジネスロジック
- **Repository層 (repositories)**: データアクセス、外部API連携

### 技術スタック

- **言語**: Python 3.11+
- **フレームワーク**: FastAPI 0.104.1
- **サーバー**: Uvicorn
- **パッケージ管理**: uv
- **データベース**: Supabase
- **AI**: OpenAI API
- **音声合成**: VoiceVox

## 機能概要

### 音声処理
- 音声ファイルのテキスト変換（Whisper）
- AI応答生成（GPT-4o-mini）
- テキスト音声合成（VoiceVox）

### データ管理
- 高齢者情報管理
- 会話履歴記録・検索
- 日次サマリー自動生成
- 感情分析データ保存

### API機能
- RESTful API設計
- 適切なHTTPステータスコード
- 構造化エラーレスポンス
- OpenAPI仕様書自動生成

## セットアップ

### 前提条件

- Python 3.11以上
- uv パッケージマネージャー
- Supabaseアカウント
- OpenAI APIキー
- VoiceVoxサーバー（ローカル起動）

### 環境変数設定

`.env` ファイルを作成し、以下を設定：

```env
# OpenAI API設定
OPENAI_API_KEY=your_openai_api_key_here

# Supabase設定
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here

# サーバー設定
HOST=0.0.0.0
PORT=8000

# VoiceVox設定（オプション）
VOICEVOX_URL=http://localhost:50021
SPEAKER_ID=3
```

### インストール・起動

```bash
# 依存関係インストール
uv sync

# 開発サーバー起動
uv run python app/main.py
```

## API仕様

### エンドポイント一覧

| メソッド | パス | 説明 |
|---------|------|------|
| GET | `/health` | ヘルスチェック |
| POST | `/api/v1/conversations/process-audio` | 音声処理 |
| GET | `/api/v1/elderly/{person_id}` | 高齢者情報取得 |
| GET | `/api/v1/elderly/{person_id}/conversations` | 会話履歴取得 |
| GET | `/api/v1/elderly/{person_id}/summaries` | 日次サマリー取得 |
| POST | `/api/v1/elderly/{person_id}/summaries` | 日次サマリー生成 |
| GET | `/api/v1/elderly/{person_id}/dashboard` | ダッシュボードデータ取得 |

### 認証

現在は認証なしで動作。将来的にJWTベース認証を予定。

## 開発

### ディレクトリ構造

```
app/
├── main.py                 # エントリーポイント
├── routers/               # UI層（HTTPハンドラ）
│   ├── conversation_router.py
│   ├── elderly_router.py
│   └── health_router.py
├── services/              # Service層（ビジネスロジック）
│   ├── conversation_service.py
│   ├── elderly_service.py
│   └── summary_service.py
├── repositories/          # Repository層（データアクセス）
│   ├── database_repository.py
│   ├── openai_repository.py
│   └── voice_repository.py
├── interfaces/            # インターフェース定義
│   ├── repositories.py
│   └── services.py
├── schemas/               # データモデル
│   ├── models.py
│   ├── requests.py
│   └── responses.py
├── core/                  # 共通機能
│   ├── container.py       # DIコンテナ
│   ├── dependencies.py   # 依存性注入
│   └── exceptions.py     # カスタム例外
└── config/               # 設定
    └── settings.py
```

### 依存性注入

DIコンテナパターンを採用し、シングルトンでサービスインスタンスを管理。

```python
from app.core.dependencies import get_conversation_service

# ルーター内で使用
async def process_audio(
    audio: UploadFile,
    service: ConversationServiceInterface = Depends(get_conversation_service)
):
    return await service.process_voice_conversation(audio)
```

### テスト

```bash
# 単体テスト（予定）
uv run pytest tests/

# 型チェック
uv run mypy app/
```

## デプロイ

### Docker

```bash
# イメージビルド
docker build -t mimamori-backend .

# コンテナ起動
docker run -p 8000:8000 --env-file .env mimamori-backend
```

### 本番環境

- 環境変数の適切な設定
- CORS設定の本番対応
- ログレベルの調整
- セキュリティヘッダーの追加

## トラブルシューティング

### よくある問題

**ポート8000使用エラー**
```bash
lsof -i :8000
docker ps | grep 8000
```

**依存関係エラー**
```bash
uv sync --frozen
```

**環境変数未設定**
- `.env`ファイルの存在確認
- 必須環境変数の設定確認

### ログ確認

```bash
# 開発時
uv run python app/main.py

# Docker使用時
docker logs [container-id]
```





## ファイル構造

```
app/
├── main_new.py              # 新アーキテクチャのエントリポイント
├── routers/                 # UI層
│   ├── conversation_router.py
│   ├── elderly_router.py
│   └── health_router.py
├── services_new/            # Service層
│   ├── conversation_service.py
│   ├── elderly_service.py
│   └── summary_service.py
├── repositories/            # Repository層
│   ├── database_repository.py
│   ├── openai_repository.py
│   └── voice_repository.py
├── interfaces/              # インターフェース定義
│   ├── repositories.py
│   └── services.py
├── schemas/                 # データモデル
│   ├── models.py
│   ├── requests.py
│   └── responses.py
├── core/                    # 共通機能
│   ├── container.py         # DIコンテナ
│   ├── dependencies.py     # 依存性注入ヘルパー
│   └── exceptions.py        # カスタム例外
└── config/                  # 設定
    └── settings.py
```

## 依存関係の流れ

```
UI Layer (Router)
    ↓ depends on
Service Layer
    ↓ depends on
Repository Layer
    ↓ depends on
External Systems (DB, APIs)
```



## API エンドポイント構造

### 新API（v2）
- `POST /api/v2/conversations/process-audio` - 音声処理
- `GET /api/v2/elderly/{person_id}` - 高齢者情報取得
- `GET /api/v2/elderly/{person_id}/conversations` - 会話履歴取得
- `GET /api/v2/elderly/{person_id}/summaries` - サマリー取得
- `POST /api/v2/elderly/{person_id}/summaries` - サマリー生成
- `GET /api/v2/elderly/{person_id}/dashboard` - ダッシュボードデータ
- `GET /health` - ヘルスチェック







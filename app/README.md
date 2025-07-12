# Voice Assistant Server

音声チャットシステムのサーバーサイド実装です。

## アーキテクチャ

### レイヤー構成
```
app/
├── api/           # API層 - エンドポイント定義
├── services/      # サービス層 - ビジネスロジック
├── models/        # モデル層 - データスキーマ
├── config/        # 設定層 - 環境変数管理
└── main.py        # エントリーポイント
```

### 責務分離
- **API層**: リクエスト/レスポンス処理、バリデーション
- **サービス層**: OpenAI API呼び出し、VOICEVOX連携
- **モデル層**: データ型定義、シリアライゼーション
- **設定層**: 環境変数、設定値管理

## セットアップ

### 1. 依存関係のインストール
```bash
uv add -r requirements.txt
```

### 2. 環境変数の設定
プロジェクトルートの`.env`ファイルに以下を設定:
```
OPENAI_API_KEY=your_openai_api_key_here
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
```

### 3. VOICEVOXの起動
```bash
# VOICEVOXアプリケーションを起動するか、以下のコマンドでサーバーを起動
voicevox_engine --host 0.0.0.0 --port 50021
```

### 4. サーバーの起動
```bash
# プロジェクトルートから実行
python run_server.py
```

## API エンドポイント

### POST /process_audio
音声ファイルを受信してAI応答音声を返します。

**リクエスト**
- Content-Type: multipart/form-data
- Body: audio (WAVファイル)

**レスポンス**
- Content-Type: audio/wav
- Body: 合成音声データ

### GET /health
サーバーのヘルスチェックを行います。

**レスポンス**
```json
{
  "status": "ok",
  "message": "Voice Assistant API is running"
}
```

## 設定項目

| 環境変数 | デフォルト値 | 説明 |
|----------|-------------|------|
| `OPENAI_API_KEY` | - | OpenAI APIキー（必須） |
| `SERVER_HOST` | 0.0.0.0 | サーバーのホスト |
| `SERVER_PORT` | 8000 | サーバーのポート |

## 依存関係

- FastAPI: Web APIフレームワーク
- uvicorn: ASGIサーバー
- OpenAI: AI API クライアント
- requests: HTTP クライアント
- pydantic: データバリデーション
# 開発用：シンプル & 高速ビルド
FROM python:3.11-slim

WORKDIR /app

# 開発用：キャッシュ最適化
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリコピー
COPY . .

# 開発用：ホットリロード対応
EXPOSE 8000

# 開発コマンド：--reload付き
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
# デプロイ手順書

## 概要

このアプリケーションは以下の無料サービスを使用してデプロイします：

- **バックエンド**: Render (無料プラン)
- **フロントエンド**: Vercel (無料プラン)
- **データベース**: Supabase (既に設定済み)

---

## 1. バックエンドのデプロイ (Render)

### 手順

1. **Renderアカウントを作成**
   - https://render.com にアクセス
   - GitHubアカウントでサインアップ

2. **新しいWeb Serviceを作成**
   - Dashboard > "New" > "Web Service"
   - GitHubリポジトリ `Ryuya-hub/medcareercoach_app` を選択
   - 以下の設定を入力:
     - **Name**: `medcareercoach-backend`
     - **Region**: `Oregon (US West)`
     - **Branch**: `master`
     - **Root Directory**: `backend`
     - **Runtime**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **環境変数を設定**
   - "Environment" タブで以下を追加:
   ```
   DATABASE_URL=postgresql://postgres:rh1129217@db.whxiswwmiijpropxqgjq.supabase.co:5432/postgres
   SECRET_KEY=your-secret-key-please-change-this-in-production-with-a-strong-random-key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=1440
   CORS_ORIGINS=https://your-frontend-url.vercel.app
   COACH_INVITATION_CODE=COACH2025SECURE
   SUPABASE_URL=https://whxiswwmiijpropxqgjq.supabase.co
   SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndoeGlzd3dtaWlqcHJvcHhxZ2pxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI4NzIxODIsImV4cCI6MjA3ODQ0ODE4Mn0.0My76JUB8OEzgoHNKcJrRqbWVqDr2kvsqZqpJr1j46M
   ```

4. **デプロイ実行**
   - "Create Web Service" をクリック
   - デプロイが完了するまで待機（5-10分）
   - デプロイ完了後、URLをコピー（例: `https://medcareercoach-backend.onrender.com`）

---

## 2. フロントエンドのデプロイ (Vercel)

### 手順

1. **Vercelアカウントを作成**
   - https://vercel.com にアクセス
   - GitHubアカウントでサインアップ

2. **新しいプロジェクトを作成**
   - Dashboard > "Add New" > "Project"
   - GitHubリポジトリ `Ryuya-hub/medcareercoach_app` をインポート

3. **ビルド設定**
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

4. **環境変数を設定**
   - "Environment Variables" で以下を追加:
   ```
   VITE_API_URL=https://medcareercoach-backend.onrender.com
   ```
   （※ 上記のURLはRenderで取得したバックエンドのURLに置き換えてください）

5. **デプロイ実行**
   - "Deploy" をクリック
   - デプロイが完了するまで待機（3-5分）
   - デプロイ完了後、URLをコピー（例: `https://medcareercoach-app.vercel.app`）

6. **RenderのCORS設定を更新**
   - Renderに戻り、環境変数 `CORS_ORIGINS` をVercelのURLに更新
   - 例: `CORS_ORIGINS=https://medcareercoach-app.vercel.app`
   - サービスを再デプロイ

---

## 3. 動作確認

1. VercelのURLにアクセス
2. ログインページが表示されることを確認
3. アカウント登録とログインをテスト
4. 各機能（職務経歴書作成、添削など）をテスト

---

## トラブルシューティング

### バックエンドが起動しない場合

- Renderのログを確認: Dashboard > Logs
- 環境変数が正しく設定されているか確認
- データベース接続URLが正しいか確認

### フロントエンドがバックエンドに接続できない場合

- `VITE_API_URL` が正しく設定されているか確認
- RenderのCORS設定にVercelのURLが含まれているか確認
- ブラウザのコンソールでエラーを確認

### データベース接続エラー

- Supabaseのデータベース認証情報が正しいか確認
- Supabaseのプロジェクトが稼働しているか確認

---

## 注意事項

- **Renderの無料プラン**: 15分間アクティビティがないとスリープ状態になります。最初のアクセスは遅くなる可能性があります。
- **Vercelの無料プラン**: 月間100GBの帯域幅制限があります。
- **環境変数**: 本番環境では必ず強力な `SECRET_KEY` を設定してください。

---

## メンテナンス

### コードを更新する場合

1. ローカルで変更を加える
2. `git add .`
3. `git commit -m "変更内容"`
4. `git push origin master`
5. RenderとVercelが自動的に再デプロイします

### データベースのマイグレーション

新しいマイグレーションを実行する場合:
1. Renderのダッシュボードで "Shell" を開く
2. `python migrate_resumes.py` を実行

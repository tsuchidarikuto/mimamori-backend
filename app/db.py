from supabase import create_client, Client
from config import settings

# Supabaseクライアントを初期化
try:
    # 'create_client'は同期的ですが、その後の操作は非同期にできます
    supabase_client: Client = create_client(settings.supabase_url, settings.supabase_key)
    print("Successfully connected to Supabase.")
except Exception as e:
    print(f"Error connecting to Supabase: {e}")
    supabase_client = None

# 'async def' に変更
async def add_log(log_content: str) -> bool:
    """
    会話ログをSupabaseのlogsテーブルに非同期で挿入する関数
    """
    if not supabase_client:
        print("Supabase client not initialized. Cannot add log.")
        return False
        
    try:
        data = {"log": log_content}
        # 'await' をつけて非同期実行
        response = await supabase_client.table("logs").insert(data).execute()
        
        if len(response.data) > 0:
            print(f"Successfully logged (async): {log_content[:50]}...")
            return True
        else:
            print(f"Failed to log conversation. Response: {response}")
            return False

    except Exception as e:
        print(f"An error occurred while logging to Supabase: {e}")
        return False
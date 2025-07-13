import os
from supabase import create_client, Client
from typing import Optional

class SupabaseConfig:
    def __init__(self):
        self.url: str = os.getenv("SUPABASE_URL", "")
        self.key: str = os.getenv("SUPABASE_ANON_KEY", "")
        self.service_role_key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
        
    def validate(self) -> bool:
        """設定値の検証"""
        return bool(self.url and self.key)

class SupabaseClient:
    _instance: Optional['SupabaseClient'] = None
    _client: Optional[Client] = None
    
    def __new__(cls) -> 'SupabaseClient':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self.config = SupabaseConfig()
            if not self.config.validate():
                raise ValueError("Supabase URL and ANON_KEY must be set in environment variables")
            
            self._client = create_client(self.config.url, self.config.key)
    
    @property
    def client(self) -> Client:
        """Supabaseクライアントを取得"""
        if self._client is None:
            raise RuntimeError("Supabase client not initialized")
        return self._client
    
    def get_service_client(self) -> Client:
        """サービスロールキーを使用したクライアントを取得（管理操作用）"""
        if not self.config.service_role_key:
            raise ValueError("SUPABASE_SERVICE_ROLE_KEY must be set for service operations")
        return create_client(self.config.url, self.config.service_role_key)

# シングルトンインスタンス
supabase_client = SupabaseClient()

def get_supabase() -> Client:
    """依存性注入用のSupabaseクライアント取得関数"""
    return supabase_client.client
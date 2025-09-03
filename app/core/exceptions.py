"""カスタム例外クラス定義"""


class AppException(Exception):
    """アプリケーション共通例外クラス"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class DatabaseException(AppException):
    """データベース関連の例外"""
    def __init__(self, message: str):
        super().__init__(message, status_code=500)


class ValidationException(AppException):
    """バリデーション関連の例外"""
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class AuthenticationException(AppException):
    """認証関連の例外"""
    def __init__(self, message: str):
        super().__init__(message, status_code=401)


class NotFoundException(AppException):
    """リソースが見つからない例外"""
    def __init__(self, message: str):
        super().__init__(message, status_code=404)
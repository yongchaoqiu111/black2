"""Black2 SDK Exceptions"""

class Black2APIError(Exception):
    """Base exception for Black2 API errors"""
    
    def __init__(self, code: int, message: str, detail: any = None):
        self.code = code
        self.message = message
        self.detail = detail
        super().__init__(f"[{code}] {message}")

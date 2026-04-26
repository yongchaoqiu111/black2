"""
API Response Standardization Module

Provides unified response structure for AI Agent compatibility.
Format: {code, message, data}
"""

from typing import Optional, Any, Dict
from fastapi.responses import JSONResponse


class APIResponse:
    """Standardized API response wrapper"""
    
    @staticmethod
    def success(data: Any = None, message: str = "Success", code: int = 200) -> Dict[str, Any]:
        """
        Success response
        
        Args:
            data: Response data
            message: Success message
            code: HTTP status code
            
        Returns:
            Standardized success response
        """
        return {
            "code": code,
            "message": message,
            "data": data
        }
    
    @staticmethod
    def error(code: int, message: str, data: Any = None) -> Dict[str, Any]:
        """
        Error response
        
        Args:
            code: Error code (4001-4999 for client errors, 5001-5999 for server errors)
            message: Error description
            data: Optional error details
            
        Returns:
            Standardized error response
        """
        return {
            "code": code,
            "message": message,
            "data": data
        }


# Global error codes for AI Agent parsing
ERROR_CODES = {
    # Client Errors (4001-4999)
    "PARAM_INVALID": 4001,
    "SIGNATURE_INVALID": 4002,
    "TRANSACTION_NOT_FOUND": 4003,
    "STATUS_CONFLICT": 4004,
    "INSUFFICIENT_BALANCE": 4005,
    "RATE_LIMIT_EXCEEDED": 4006,
    
    # Server Errors (5001-5999)
    "FUND_RELEASE_FAILED": 5001,
    "DATABASE_ERROR": 5002,
    "X402_INTEGRATION_ERROR": 5003,
    "ARBITRATION_FAILED": 5004,
}

"""Custom exception classes for Tevkil Platform."""


class TevkilException(Exception):
    """Base exception for all Tevkil-specific errors."""
    
    def __init__(self, message: str, status_code: int = 500, payload=None):
        """
        Initialize Tevkil exception.
        
        Args:
            message: Human-readable error message
            status_code: HTTP status code
            payload: Additional error context (dict)
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}
    
    def to_dict(self):
        """Convert exception to dictionary for JSON response."""
        rv = dict(self.payload)
        rv['error'] = self.message
        rv['status_code'] = self.status_code
        return rv


class ValidationError(TevkilException):
    """Input validation failed (400 Bad Request)."""
    
    def __init__(self, message: str, field: str = None):
        """
        Initialize validation error.
        
        Args:
            message: Validation error message
            field: Field name that failed validation
        """
        payload = {'field': field} if field else {}
        super().__init__(message, status_code=400, payload=payload)


class AuthenticationError(TevkilException):
    """Authentication failed (401 Unauthorized)."""
    
    def __init__(self, message: str = "Kimlik doğrulama başarısız"):
        super().__init__(message, status_code=401)


class AuthorizationError(TevkilException):
    """User not authorized for this action (403 Forbidden)."""
    
    def __init__(self, message: str = "Bu işlem için yetkiniz yok"):
        super().__init__(message, status_code=403)


class ResourceNotFoundError(TevkilException):
    """Resource not found (404 Not Found)."""
    
    def __init__(self, resource: str, identifier: int | str = None):
        """
        Initialize resource not found error.
        
        Args:
            resource: Resource type (e.g., "İlan", "Kullanıcı")
            identifier: Resource ID or other identifier
        """
        if identifier:
            message = f"{resource} bulunamadı (ID: {identifier})"
        else:
            message = f"{resource} bulunamadı"
        super().__init__(message, status_code=404)


class ConflictError(TevkilException):
    """Resource conflict (409 Conflict)."""
    
    def __init__(self, message: str):
        """
        Initialize conflict error.
        
        Example: "Bu e-posta adresi zaten kayıtlı"
        """
        super().__init__(message, status_code=409)


class RateLimitExceeded(TevkilException):
    """Rate limit exceeded (429 Too Many Requests)."""
    
    def __init__(self, retry_after: int = 60):
        """
        Initialize rate limit error.
        
        Args:
            retry_after: Seconds until user can retry
        """
        message = f"Çok fazla istek. {retry_after} saniye sonra tekrar deneyin."
        super().__init__(message, status_code=429, payload={'retry_after': retry_after})
        self.retry_after = retry_after


class DatabaseError(TevkilException):
    """Database operation failed (500 Internal Server Error)."""
    
    def __init__(self, message: str = "Veritabanı hatası"):
        super().__init__(message, status_code=500)


class ExternalServiceError(TevkilException):
    """External service (WhatsApp, Email, etc.) error (503 Service Unavailable)."""
    
    def __init__(self, service: str, message: str = None):
        """
        Initialize external service error.
        
        Args:
            service: Service name (e.g., "WhatsApp", "Email")
            message: Optional error message
        """
        if message:
            full_message = f"{service} servisi hatası: {message}"
        else:
            full_message = f"{service} servisi şu anda kullanılamıyor"
        super().__init__(full_message, status_code=503)


class SpamDetectedError(TevkilException):
    """Spam content detected (400 Bad Request)."""
    
    def __init__(self, message: str = "Spam içerik tespit edildi"):
        super().__init__(message, status_code=400)


class AccountLockedException(TevkilException):
    """Account is locked due to security reasons (403 Forbidden)."""
    
    def __init__(self, locked_until=None):
        """
        Initialize account locked error.
        
        Args:
            locked_until: datetime when account will be unlocked
        """
        if locked_until:
            from datetime import datetime, timezone
            remaining = int((locked_until - datetime.now(timezone.utc)).total_seconds() / 60)
            message = f"Hesabınız kilitli. {remaining} dakika sonra tekrar deneyin."
        else:
            message = "Hesabınız kilitlendi. Lütfen destek ekibiyle iletişime geçin."
        super().__init__(message, status_code=403)

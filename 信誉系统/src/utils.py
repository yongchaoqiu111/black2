import hashlib
import hmac

def hash_data(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()

def sign_data(data: str, secret: str) -> str:
    return hmac.new(secret.encode(), data.encode(), hashlib.sha256).hexdigest()

def verify_signature(data: str, signature: str, secret: str) -> bool:
    expected = sign_data(data, secret)
    return hmac.compare_digest(expected, signature)
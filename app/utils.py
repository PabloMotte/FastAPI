from passlib.context import CryptContext
# Prepare for password hashing
pwd_context = CryptContext(schemes="bcrypt", deprecated="auto")

def hash(pwd):
    return pwd_context.hash(pwd)

def verify(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)
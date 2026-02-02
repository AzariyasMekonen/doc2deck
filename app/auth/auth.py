from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from .models import User, database
import os
import hashlib
from bson import ObjectId

class AuthService:
    def __init__(self):
        self.secret_key = os.getenv("SECRET_KEY", "your-secret-key-change-this")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30

    def verify_password(self, plain_password, hashed_password):
        return self.get_password_hash(plain_password) == hashed_password

    def get_password_hash(self, password):
        salt = "doc2deck_salt"
        return hashlib.sha256((password + salt).encode()).hexdigest()

    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    async def verify_token(self, token: str):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            username: str = payload.get("sub")
            if username is None:
                return None
            user_doc = await database.users.find_one({"username": username})
            if user_doc:
                user_doc["_id"] = str(user_doc["_id"])
                return User(**user_doc)
            return None
        except JWTError:
            return None

    async def create_user(self, username: str, email: str, password: str):
        # Check if user exists
        if await database.users.find_one({"username": username}):
            raise ValueError("Username already exists")
        if await database.users.find_one({"email": email}):
            raise ValueError("Email already exists")
        
        hashed_password = self.get_password_hash(password)
        user = User(username=username, email=email, hashed_password=hashed_password)
        result = await database.users.insert_one(user.dict(by_alias=True, exclude={"id"}))
        user.id = result.inserted_id
        return user

    async def authenticate_user(self, username: str, password: str):
        user_doc = await database.users.find_one({"username": username})
        if not user_doc or not self.verify_password(password, user_doc["hashed_password"]):
            return None
        
        access_token = self.create_access_token(data={"sub": username})
        return access_token
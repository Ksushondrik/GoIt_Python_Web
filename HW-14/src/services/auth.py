import pickle
from datetime import datetime, timedelta
from typing import Optional

import redis
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.config import config
from src.database.db import get_db
from src.repository import users as repository_users


class Auth:

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = config.SECRET_KEY_JWT
    ALGORITHM = config.ALGORITHM
    cache = redis.Redis(
        host=config.REDIS_DOMAIN,
        port=config.REDIS_PORT,
        db=0,
        password=config.REDIS_PASSWORD,
    )

    def verify_password(self, plain_password, hashed_password):
        """
        Verifies if the given plain password matches the hashed password.

        :param plain_password: The plain text password to be verified.
        :type plain_password: str
        :param hashed_password: The hashed password to compare against.
        :type hashed_password: str
        :return: True if the plain password matches the hashed password, otherwise False.
        :rtype: bool
        :doc-author: Trelent
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Generates a hashed version of the given password.

        :param password: The plain text password to be hashed.
        :type password: str
        :return: The hashed version of the password.
        :rtype: str
        :doc-author: Trelent
        """
        return self.pwd_context.hash(password)

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

    # define a function to generate a new access token
    async def create_access_token(
        self, data: dict, expires_delta: Optional[float] = None
    ):
        """
        Creates a JSON Web Token (JWT) for access with optional expiration time.

        :param data: The payload data to be included in the token.
        :type data: dict
        :param expires_delta: Optional expiration time in seconds. If not provided, the token will expire in 15 minutes.
        :type expires_delta: Optional[float]
        :return: The encoded JWT access token.
        :rtype: str
        :doc-author: Trelent
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update(
            {"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"}
        )
        encoded_access_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return encoded_access_token

    # define a function to generate a new refresh token
    async def create_refresh_token(
        self, data: dict, expires_delta: Optional[float] = None
    ):
        """
        Creates a JSON Web Token (JWT) for refresh with optional expiration time.

        :param data: The payload data to be included in the token.
        :type data: dict
        :param expires_delta: Optional expiration time in seconds. If not provided, the token will expire in 7 days.
        :type expires_delta: Optional[float]
        :return: The encoded JWT refresh token.
        :rtype: str
        :doc-author: Trelent
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update(
            {"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"}
        )
        encoded_refresh_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return encoded_refresh_token

    async def decode_refresh_token(
        self, refresh_token: str
    ):  # get_email_form_refresh_token
        """
        Decodes a refresh token to extract the email address if the token is valid.

        :param refresh_token: The JWT refresh token to be decoded.
        :type refresh_token: str
        :return: The email address extracted from the token if the token is valid.
        :rtype: str
        :raises HTTPException: If the token is invalid or has an incorrect scope.
        :doc-author: Trelent
        """
        try:
            payload = jwt.decode(
                refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM]
            )
            if payload["scope"] == "refresh_token":
                email = payload["sub"]
                return email
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid scope for token",
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

    async def get_current_user(
        self, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
    ):
        """
        Retrieves the current user based on the provided JWT token.

        This method decodes the JWT token to extract the email address and validates
        the token's scope. It then checks the cache for the user. If the user is not
        found in the cache, it retrieves the user from the database and updates the cache.

        :param token: The JWT access token used to authenticate the user.
        :type token: str
        :param db: The database session for querying user information.
        :type db: AsyncSession
        :return: The User object corresponding to the email address extracted from the token.
        :rtype: User
        :raises HTTPException: If the token is invalid, has an incorrect scope, or the user is not found.
        :doc-author: Trelent
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload["scope"] == "access_token":
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user_hash = str(email)

        user = self.cache.get(user_hash)

        if user is None:
            print("User from database")
            user = await repository_users.get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            self.cache.set(user_hash, pickle.dumps(user))
            self.cache.expire(user_hash, 300)
        else:
            print("User from cache")
            user = pickle.loads(user)
        return user

    def create_email_token(self, data: dict):
        """
        Creates a JWT token for email verification or other purposes with a 7-day expiration.

        This method encodes the provided data into a JWT token with an expiration time set to 7 days
        from the current UTC time.

        :param data: A dictionary containing the data to be encoded in the JWT token.
        :type data: dict
        :return: The encoded JWT token as a string.
        :rtype: str
        :doc-author: Trelent
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def get_email_from_token(self, token: str):
        """
        Extracts the email address from the provided JWT token.

        This method decodes the JWT token to retrieve the email address contained within the token's payload.
        If the token is invalid or cannot be decoded, an HTTP 422 exception is raised.

        :param token: The JWT token from which to extract the email address.
        :type token: str
        :return: The email address extracted from the token.
        :rtype: str
        :raises HTTPException: If the token is invalid or cannot be decoded.
        :doc-author: Trelent
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid token for email verification",
            )


auth_service = Auth()

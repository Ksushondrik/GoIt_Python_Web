from fastapi import Depends
from libgravatar import Gravatar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User
from src.schemas.user import UserSchema


async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    """
    Retrieves a user by their email address.

    :param email: The email address of the user to retrieve
    :type email: str
    :param db: The asynchronous database session used to execute the query (optional, default is provided by dependency injection)
    :type db: AsyncSession
    :return: The user with the specified email if found, otherwise None
    :rtype: User or None
    :doc-author: Trelent
    """
    stmt = select(User).filter_by(email=email)
    user = await db.execute(stmt)
    user = user.scalar_one_or_none()
    return user


async def create_user(body: UserSchema, db: AsyncSession = Depends(get_db)):
    """
    Creates a new user with the provided data and generates an avatar from the user's email.

    :param body: The data for the new user
    :type body: UserSchema
    :param db: The asynchronous database session used to execute the query (optional, default is provided by dependency injection)
    :type db: AsyncSession
    :return: The newly created user
    :rtype: User
    :doc-author: Trelent
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as err:
        print(err)
    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: AsyncSession):
    """
    Updates the refresh token for the specified user.

    :param user: The user whose refresh token is being updated
    :type user: User
    :param token: The new refresh token value, or None to clear the token
    :type token: str | None
    :param db: The asynchronous database session used to execute the update
    :type db: AsyncSession
    :return: None
    :doc-author: Trelent
    """
    user.refresh_token = token
    await db.commit()


async def confirmed_email(email: str, db: AsyncSession) -> None:
    """
    Marks the user with the specified email as confirmed.

    :param email: The email address of the user to mark as confirmed
    :type email: str
    :param db: The asynchronous database session used to execute the update
    :type db: AsyncSession
    :return: None
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()


async def update_avatar_url(email: str, url: str | None, db: AsyncSession) -> User:
    """
    Updates the avatar URL for the user with the specified email.

    :param email: The email address of the user whose avatar URL is being updated
    :type email: str
    :param url: The new avatar URL, or None to clear the avatar
    :type url: str | None
    :param db: The asynchronous database session used to execute the update
    :type db: AsyncSession
    :return: The updated user with the new avatar URL
    :rtype: User
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    await db.commit()
    await db.refresh(user)
    return user

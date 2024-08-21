import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, Depends, UploadFile, File
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User
from src.schemas.user import UserResponse
from src.services.auth import auth_service
from src.conf.config import config
from src.repository import users as repositories_users

router = APIRouter(prefix="/users", tags=["users"])
cloudinary.config(
    cloud_name=config.CLD_NAME,
    api_key=config.CLD_API_KEY,
    api_secret=config.CLD_API_SECRET,
    secure=True,
)


@router.get(
    "/me",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def get_current_user(user: User = Depends(auth_service.get_current_user)):
    """
    Retrieves the currently authenticated user.

    :param user: The currently authenticated user, provided by dependency injection.
    :type user: User
    :return: The currently authenticated user.
    :rtype: User
    :doc-author: Trelent
    """
    return user


@router.patch(
    "/avatar",
)
async def get_current_user(
    file: UploadFile = File(),
    user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Updates the avatar URL of the currently authenticated user with an uploaded image file.

    :param file: The image file to be uploaded as the user's new avatar.
    :type file: UploadFile
    :param user: The currently authenticated user, provided by dependency injection.
    :type user: User
    :param db: The asynchronous database session used to execute database operations (optional, default is provided by dependency injection).
    :type db: AsyncSession
    :return: The updated user with the new avatar URL.
    :rtype: User
    :raises HTTPException: If an error occurs during the upload or update process.
    :doc-author: Trelent
    """
    public_id = f"python_web/{user.email}"
    res = cloudinary.uploader.upload(file.file, public_id=public_id, oweite=True)
    print(res)
    res_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=250, height=250, crop="fill", version=res.get("version")
    )
    user = await repositories_users.update_avatar_url(user.email, res_url, db)
    return user

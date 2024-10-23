from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks, Request, Response
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User
from src.repository import users as repositories_users
from src.schemas.user import UserSchema, TokenSchema, UserResponse, RequestEmail
from src.services.auth import auth_service
from src.services.email import send_email

router = APIRouter(prefix='/auth', tags=['auth'])
get_refresh_token = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserSchema, bt: BackgroundTasks, request: Request, db: AsyncSession = Depends(get_db)):
    """
    Handles user signup by creating a new user if the email does not already exist.

    :param body: The data for the new user including email and password
    :type body: UserSchema
    :param bt: The background tasks manager for scheduling asynchronous tasks
    :type bt: BackgroundTasks
    :param request: The HTTP request object, used to get the base URL for email
    :type request: Request
    :param db: The asynchronous database session used to execute database operations (optional, default is provided by dependency injection)
    :type db: AsyncSession
    :return: The newly created user
    :rtype: User
    :raises HTTPException: If a user with the given email already exists
    :doc-author: Trelent
    """
    exist_user = await repositories_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repositories_users.create_user(body, db)
    bt.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    return new_user


@router.post("/login", response_model=TokenSchema)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    Authenticates a user and generates access and refresh tokens.

    :param body: The form data containing username (email) and password
    :type body: OAuth2PasswordRequestForm
    :param db: The asynchronous database session used to execute database operations (optional, default is provided by dependency injection)
    :type db: AsyncSession
    :return: A dictionary containing the access token, refresh token, and token type
    :rtype: dict
    :raises HTTPException: If the user does not exist, email is not confirmed, or the password is incorrect
    :doc-author: Trelent
    """
    print(body.username, body.password)
    user = await repositories_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    # "credention invalid" if user is not - для співробітників
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_this_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repositories_users.update_token(user, refresh_this_token, db)
    return {"access_token": access_token, "refresh_token": refresh_this_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=TokenSchema)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(get_refresh_token),
                        db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):  # Security(get_refresh_token) == Depends(get_refresh_token)
    """
    Refreshes the access token using a valid refresh token.

    :param credentials: The credentials containing the refresh token
    :type credentials: HTTPAuthorizationCredentials
    :param db: The asynchronous database session used to execute database operations (optional, default is provided by dependency injection)
    :type db: AsyncSession
    :return: A dictionary containing the new access token, refresh token, and token type
    :rtype: dict
    :raises HTTPException: If the refresh token is invalid or does not match the user's stored token
    :doc-author: Trelent
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repositories_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_its_token = await auth_service.create_refresh_token(data={"sub": email})
    user.refresh_token = refresh_its_token
    await repositories_users.update_token(user, refresh_its_token, db)
    return {"access_token": access_token, "refresh_token": refresh_its_token, "token_type": "bearer"}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    Confirms the user's email based on the provided verification token.

    :param token: The verification token used to confirm the user's email
    :type token: str
    :param db: The asynchronous database session used to execute database operations (optional, default is provided by dependency injection)
    :type db: AsyncSession
    :return: A dictionary with a message indicating the result of the email confirmation
    :rtype: dict
    :raises HTTPException: If the user does not exist or there is an error in the verification process
    :doc-author: Trelent
    """
    email = await auth_service.get_email_from_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repositories_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: AsyncSession = Depends(get_db)):
    """
    Requests an email confirmation for a user and sends a confirmation email if the user's email is not already confirmed.

    :param body: The request body containing the user's email address
    :type body: RequestEmail
    :param background_tasks: The background tasks manager for scheduling asynchronous tasks
    :type background_tasks: BackgroundTasks
    :param request: The HTTP request object, used to get the base URL for email
    :type request: Request
    :param db: The asynchronous database session used to execute database operations (optional, default is provided by dependency injection)
    :type db: AsyncSession
    :return: A dictionary with a message indicating the status of the email confirmation request
    :rtype: dict
    :doc-author: Trelent
    """
    user = await repositories_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, str(request.base_url))
    return {"message": "Check your email for confirmation."}


@router.get('/{username}')
async def request_email(username: str, response: Response, db: AsyncSession = Depends(get_db)):
    """
    Handles the request for tracking email opens by returning an image.

    :param username: The username of the user who opened the email
    :type username: str
    :param response: The HTTP response object used to return the image
    :type response: Response
    :param db: The asynchronous database session used to execute database operations (optional, default is provided by dependency injection)
    :type db: AsyncSession
    :return: A FileResponse containing an image to indicate that the email was opened
    :rtype: FileResponse
    """
    print('----------------------------------------------------------------')
    print(f'{username} зберігаємо, що він відкрив email в БД')
    print('----------------------------------------------------------------')
    return FileResponse("src/static/open_check.png", media_type="image/png", content_disposition_type="inline")

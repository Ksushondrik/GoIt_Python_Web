import os

import redis.asyncio as redis
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_limiter import FastAPILimiter
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.config import config
from src.database.db import get_db
from src.routes import contacts, users, auth

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_directory = os.path.join(os.path.dirname(__file__), "src/static")
app.mount("/static", StaticFiles(directory=static_directory), name="static")
# app.mount("/static", StaticFiles(directory="src/static"), name="static")

app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")


@app.on_event("startup")
async def startup():
    """
    Initializes the Redis connection and sets up FastAPI rate limiting.

    This function connects to the Redis server using the specified host, port, and password from the configuration.
    It then initializes the FastAPI rate limiter with the Redis connection to handle request rate limiting.

    :raises RedisError: If the connection to the Redis server fails.
    :doc-author: Trelent
    """
    r = await redis.Redis(
        host=config.REDIS_DOMAIN,
        port=config.REDIS_PORT,
        db=0,
        password=config.REDIS_PASSWORD,
    )
    await FastAPILimiter.init(r)


@app.get("/")
def index():
    """
    Returns a simple welcome message for the Contact Application.

    This function acts as the root endpoint of the application, providing a basic response
    with a welcome message indicating that the Contact Application is running.

    :return: A dictionary containing a welcome message.
    :rtype: dict
    :doc-author: Trelent
    """
    return {"message": "Contact Application"}


@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """
    Checks the health of the database connection.

    This function attempts to execute a simple SQL query (`SELECT 1`) to verify
    that the database is properly configured and accessible. If the query fails
    or returns no results, an HTTP 500 error is raised. If the database is reachable
    and the query succeeds, a welcome message is returned.

    :param db: The database session used for executing the query.
    :type db: AsyncSession
    :return: A dictionary containing a welcome message if the database is healthy.
    :rtype: dict
    :raises HTTPException: If the database is not properly configured or
                           there is an error connecting to the database.
    :doc-author: Trelent
    """
    try:
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(
                status_code=500, detail="Database is not configured correctly"
            )
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")

from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User, Role
from src.repository import contacts as repositories_contacts
from src.schemas.contact import ContactSchema, ContactUpdateSchema, ContactResponse
from src.services.auth import auth_service
from src.services.roles import RoleAccess

router = APIRouter(prefix='/contacts', tags=['contacts'])

access_to_route_all = RoleAccess([Role.admin, Role.moderator])


@router.get('/', response_model=list[ContactResponse])
async def get_contacts(limit: int = Query(default=10, ge=10, le=500), offset: int = Query(default=0, ge=0),
                       db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    contacts = await repositories_contacts.get_contacts(limit, offset, db, user)
    return contacts


@router.get('/all', response_model=list[ContactResponse], dependencies=[Depends(access_to_route_all)])
async def get_contacts(limit: int = Query(default=10, ge=10, le=500), offset: int = Query(default=0, ge=0),
                       db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    contacts = await repositories_contacts.get_all_contacts(limit, offset, db)
    return contacts


@router.get('/{contact_id}', response_model=ContactResponse)
async def get_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                      user: User = Depends(auth_service.get_current_user)):
    contact = await repositories_contacts.get_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND!")
    return contact


@router.post('/', response_model=ContactResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(RateLimiter(times=2, seconds=60))])
async def create_contact(body: ContactSchema, db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    contact = await repositories_contacts.create_contact(body, db, user)
    return contact


@router.put('/{contact_id}')
async def update_contact(body: ContactUpdateSchema, contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    contact = await repositories_contacts.update_contact(contact_id, body, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND!")
    return contact


@router.delete('/{contact_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    contact = await repositories_contacts.delete_contact(contact_id, db, user)
    return contact


@router.get('/search/', response_model=list[ContactResponse])
async def search_contacts(first_name: Optional[str] = Query(None), last_name: Optional[str] = Query(None),
                          email: Optional[str] = Query(None), db: AsyncSession = Depends(get_db),
                          user: User = Depends(auth_service.get_current_user)):
    contacts = await repositories_contacts.search_contacts(first_name, last_name, email, db, user)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND!")
    return contacts


@router.get('/upcoming_birthdays/', response_model=list[ContactResponse])
async def get_birthdays_upcoming(db: AsyncSession = Depends(get_db),
                                 user: User = Depends(auth_service.get_current_user)):
    contacts = await repositories_contacts.get_birthdays_upcoming(db, user)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND!")
    return contacts

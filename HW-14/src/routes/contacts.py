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
    """
    Retrieves a paginated list of contacts for the authenticated user.

    :param limit: The maximum number of contacts to return, must be between 10 and 500 (inclusive)
    :type limit: int
    :param offset: The starting point for the list of contacts, must be 0 or greater
    :type offset: int
    :param db: The asynchronous database session used to execute database operations (optional, default is provided by dependency injection)
    :type db: AsyncSession
    :param user: The currently authenticated user for whom to retrieve contacts (optional, default is provided by dependency injection)
    :type user: User
    :return: A list of contacts for the authenticated user
    :rtype: list
    """
    contacts = await repositories_contacts.get_contacts(limit, offset, db, user)
    return contacts


@router.get('/all', response_model=list[ContactResponse], dependencies=[Depends(access_to_route_all)])
async def get_contacts(limit: int = Query(default=10, ge=10, le=500), offset: int = Query(default=0, ge=0),
                       db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    Retrieves a paginated list of all contacts for the authenticated user.

    :param limit: The maximum number of contacts to return, must be between 10 and 500 (inclusive).
    :type limit: int
    :param offset: The starting point for the list of contacts, must be 0 or greater.
    :type offset: int
    :param db: The asynchronous database session used to execute database operations (optional, default is provided by dependency injection).
    :type db: AsyncSession
    :param user: The currently authenticated user for whom to retrieve contacts (optional, default is provided by dependency injection).
    :type user: User
    :return: A list of contacts for the authenticated user.
    :rtype: list
    """
    contacts = await repositories_contacts.get_all_contacts(limit, offset, db)
    return contacts


@router.get('/{contact_id}', response_model=ContactResponse)
async def get_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                      user: User = Depends(auth_service.get_current_user)):
    """
    Retrieves a specific contact for the authenticated user by its ID.

    :param contact_id: The ID of the contact to retrieve, must be greater than or equal to 1.
    :type contact_id: int
    :param db: The asynchronous database session used to execute database operations (optional, default is provided by dependency injection).
    :type db: AsyncSession
    :param user: The currently authenticated user for whom to retrieve the contact (optional, default is provided by dependency injection).
    :type user: User
    :return: The contact with the specified ID if it exists.
    :rtype: Contact
    :raises HTTPException: If the contact with the specified ID does not exist or does not belong to the authenticated user.
    :doc-author: Trelent
    """
    contact = await repositories_contacts.get_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND!")
    return contact


@router.post('/', response_model=ContactResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(RateLimiter(times=2, seconds=60))])
async def create_contact(body: ContactSchema, db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
    Creates a new contact for the authenticated user based on the provided contact data.

    :param body: The contact data to create a new contact.
    :type body: ContactSchema
    :param db: The asynchronous database session used to execute database operations (optional, default is provided by dependency injection).
    :type db: AsyncSession
    :param user: The currently authenticated user for whom the contact is being created (optional, default is provided by dependency injection).
    :type user: User
    :return: The newly created contact.
    :rtype: Contact
    :doc-author: Trelent
    """
    contact = await repositories_contacts.create_contact(body, db, user)
    return contact


@router.put('/{contact_id}')
async def update_contact(body: ContactUpdateSchema, contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
    Updates an existing contact for the authenticated user based on the provided contact data and contact ID.

    :param body: The updated contact data.
    :type body: ContactUpdateSchema
    :param contact_id: The ID of the contact to update, must be greater than or equal to 1.
    :type contact_id: int
    :param db: The asynchronous database session used to execute database operations (optional, default is provided by dependency injection).
    :type db: AsyncSession
    :param user: The currently authenticated user for whom the contact is being updated (optional, default is provided by dependency injection).
    :type user: User
    :return: The updated contact if it exists and belongs to the authenticated user.
    :rtype: Contact
    :raises HTTPException: If the contact with the specified ID does not exist or does not belong to the authenticated user.
    :doc-author: Trelent
    """
    contact = await repositories_contacts.update_contact(contact_id, body, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND!")
    return contact


@router.delete('/{contact_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
    Deletes a contact for the authenticated user based on the provided contact ID.

    :param contact_id: The ID of the contact to delete, must be greater than or equal to 1.
    :type contact_id: int
    :param db: The asynchronous database session used to execute database operations (optional, default is provided by dependency injection).
    :type db: AsyncSession
    :param user: The currently authenticated user for whom the contact is being deleted (optional, default is provided by dependency injection).
    :type user: User
    :return: The deleted contact if it exists and was successfully removed.
    :rtype: Contact
    :raises HTTPException: If the contact with the specified ID does not exist or does not belong to the authenticated user.
    :doc-author: Trelent
    """
    contact = await repositories_contacts.delete_contact(contact_id, db, user)
    return contact


@router.get('/search/', response_model=list[ContactResponse])
async def search_contacts(first_name: Optional[str] = Query(None), last_name: Optional[str] = Query(None),
                          email: Optional[str] = Query(None), db: AsyncSession = Depends(get_db),
                          user: User = Depends(auth_service.get_current_user)):
    """
    Searches for contacts of the authenticated user based on optional filters for first name, last name, and email.

    :param first_name: Optional filter to search contacts by first name. If not provided, no filter is applied.
    :type first_name: Optional[str]
    :param last_name: Optional filter to search contacts by last name. If not provided, no filter is applied.
    :type last_name: Optional[str]
    :param email: Optional filter to search contacts by email. If not provided, no filter is applied.
    :type email: Optional[str]
    :param db: The asynchronous database session used to execute database operations (optional, default is provided by dependency injection).
    :type db: AsyncSession
    :param user: The currently authenticated user for whom to search contacts (optional, default is provided by dependency injection).
    :type user: User
    :return: A list of contacts matching the search criteria for the authenticated user.
    :rtype: list
    :raises HTTPException: If no contacts match the search criteria or if an error occurs during the search.
    :doc-author: Trelent
    """
    contacts = await repositories_contacts.search_contacts(first_name, last_name, email, db, user)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND!")
    return contacts


@router.get('/upcoming_birthdays/', response_model=list[ContactResponse])
async def get_birthdays_upcoming(db: AsyncSession = Depends(get_db),
                                 user: User = Depends(auth_service.get_current_user)):
    """
    Retrieves contacts with upcoming birthdays within the next week for the authenticated user.

    :param db: The asynchronous database session used to execute database operations (optional, default is provided by dependency injection).
    :type db: AsyncSession
    :param user: The currently authenticated user for whom to retrieve contacts with upcoming birthdays (optional, default is provided by dependency injection).
    :type user: User
    :return: A list of contacts with birthdays occurring in the upcoming week.
    :rtype: list
    :raises HTTPException: If no contacts with upcoming birthdays are found for the authenticated user.
    :doc-author: Trelent
    """
    contacts = await repositories_contacts.get_birthdays_upcoming(db, user)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND!")
    return contacts

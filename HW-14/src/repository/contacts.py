from datetime import date, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Contact, User
from src.schemas.contact import ContactSchema, ContactUpdateSchema


async def get_contacts(limit: int, offset: int, db: AsyncSession, user: User):
    """
    Retrieves a list of contacts for the specified user with pagination.

    :param limit: The maximum number of contacts to return
    :type limit: int
    :param offset: The number of contacts to skip before starting to collect the results
    :type offset: int
    :param db: The asynchronous database session used to execute the query
    :type db: AsyncSession
    :param user: The user whose contacts are being retrieved
    :type user: User
    :return: A list of contacts associated with the specified user
    :rtype: list[Contact]
    :doc-author: Trelent
    """
    smtm = select(Contact).filter_by(user_id=user.id).offset(offset).limit(limit)
    contacts = await db.execute(smtm)
    return contacts.scalars().all()


async def get_all_contacts(limit: int, offset: int, db: AsyncSession):
    """
    Retrieves a list of all contacts with pagination.

    :param limit: The maximum number of contacts to return
    :type limit: int
    :param offset: The number of contacts to skip before starting to collect the results
    :type offset: int
    :param db: The asynchronous database session used to execute the query
    :type db: AsyncSession
    :return: A list of all contacts
    :rtype: list[Contact]
    :doc-author: Trelent
    """
    smtm = select(Contact).offset(offset).limit(limit)
    contacts = await db.execute(smtm)
    return contacts.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession, user: User):
    """
    Retrieves a specific contact by its ID for the specified user.

    :param contact_id: The ID of the contact to retrieve
    :type contact_id: int
    :param db: The asynchronous database session used to execute the query
    :type db: AsyncSession
    :param user: The user to whom the contact belongs
    :type user: User
    :return: The contact if found, otherwise None
    :rtype: Contact or None
    :doc-author: Trelent
    """
    smtm = select(Contact).filter_by(id=contact_id, user_id=user.id)
    contact = await db.execute(smtm)
    return contact.scalar_one_or_none()


async def create_contact(body: ContactSchema, db: AsyncSession, user: User):
    """
    Creates a new contact for the specified user.

    :param body: The data for the new contact
    :type body: ContactSchema
    :param db: The asynchronous database session used to execute the query
    :type db: AsyncSession
    :param user: The user who owns the new contact
    :type user: User
    :return: The newly created contact
    :rtype: Contact
    :doc-author: Trelent
    """
    contact = Contact(**body.model_dump(exclude_unset=True), user_id=user.id)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactUpdateSchema, db: AsyncSession, user: User):
    """
    Updates an existing contact for the specified user.

    :param contact_id: The ID of the contact to update
    :type contact_id: int
    :param body: The updated data for the contact
    :type body: ContactUpdateSchema
    :param db: The asynchronous database session used to execute the query
    :type db: AsyncSession
    :param user: The user who owns the contact
    :type user: User
    :return: The updated contact if found, otherwise None
    :rtype: Contact or None
    :doc-author: Trelent
    """
    smtm = select(Contact).filter_by(id=contact_id, user_id=user.id)
    result = await db.execute(smtm)
    contact = result.scalar_one_or_none()
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone = body.phone
        contact.birthday = body.birthday
        contact.additional_data = body.additional_data
        await db.commit()
        await db.refresh(contact)
        return contact


async def delete_contact(contact_id: int, db: AsyncSession, user: User):
    """
    Deletes a specific contact for the specified user.

    :param contact_id: The ID of the contact to delete
    :type contact_id: int
    :param db: The asynchronous database session used to execute the query
    :type db: AsyncSession
    :param user: The user who owns the contact
    :type user: User
    :return: The deleted contact if found, otherwise None
    :rtype: Contact or None
    :doc-author: Trelent
    """
    smtm = select(Contact).filter_by(id=contact_id, user_id=user.id)
    contact = await db.execute(smtm)
    contact = contact.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


async def search_contacts(first_name: Optional[str], last_name: Optional[str], email: Optional[str], db: AsyncSession,
                          user: User):
    """
    Searches for contacts based on the specified criteria for the given user.

    :param first_name: The first name to search for (optional)
    :type first_name: Optional[str]
    :param last_name: The last name to search for (optional)
    :type last_name: Optional[str]
    :param email: The email to search for (optional)
    :type email: Optional[str]
    :param db: The asynchronous database session used to execute the query
    :type db: AsyncSession
    :param user: The user whose contacts are being searched
    :type user: User
    :return: A list of contacts that match the search criteria
    :rtype: list[Contact]
    :doc-author: Trelent
    """
    query = select(Contact).filter_by(user_id=user.id)

    if first_name:
        query = query.filter(Contact.first_name.ilike(f'%{first_name}%'))
    if last_name:
        query = query.filter(Contact.last_name.ilike(f'%{last_name}%'))
    if email:
        query = query.filter(Contact.email.ilike(f'%{email}%'))

    result = await db.execute(query)
    return result.scalars().all()


async def get_birthdays_upcoming(db: AsyncSession, user: User):
    """
    Retrieves a list of contacts with upcoming birthdays within the next week for the specified user.

    :param db: The asynchronous database session used to execute the query
    :type db: AsyncSession
    :param user: The user whose contacts are being checked for upcoming birthdays
    :type user: User
    :return: A list of contacts whose birthdays fall within the next week
    :rtype: list[Contact]
    :doc-author: Trelent
    """
    today = date.today()
    next_week = today + timedelta(days=7)

    query = select(Contact).filter_by(user_id=user.id)
    result = await db.execute(query)
    contacts = result.scalars().all()

    birthdays_list = []

    for contact in contacts:
        birthday = contact.birthday
        if birthday is None:
            continue
        birthday_this_year = date(today.year, birthday.month, birthday.day)

        if today <= birthday_this_year <= next_week:
            birthdays_list.append(contact)
    return birthdays_list

from datetime import date, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Contact, User
from src.schemas.contact import ContactSchema, ContactUpdateSchema


async def get_contacts(limit: int, offset: int, db: AsyncSession, user: User):
    smtm = select(Contact).filter_by(user_id=user.id).offset(offset).limit(limit)
    contacts = await db.execute(smtm)
    return contacts.scalars().all()


async def get_all_contacts(limit: int, offset: int, db: AsyncSession):
    smtm = select(Contact).offset(offset).limit(limit)
    contacts = await db.execute(smtm)
    return contacts.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession, user: User):
    smtm = select(Contact).filter_by(id=contact_id, user_id=user.id)
    contact = await db.execute(smtm)
    return contact.scalar_one_or_none()


async def create_contact(body: ContactSchema, db: AsyncSession, user: User):
    contact = Contact(**body.model_dump(exclude_unset=True), user_id=user.id)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactUpdateSchema, db: AsyncSession, user: User):
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
    smtm = select(Contact).filter_by(id=contact_id, user_id=user.id)
    contact = await db.execute(smtm)
    contact = contact.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


async def search_contacts(first_name: Optional[str], last_name: Optional[str], email: Optional[str], db: AsyncSession,
                          user: User):
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

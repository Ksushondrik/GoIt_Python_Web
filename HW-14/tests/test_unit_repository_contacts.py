import unittest
from datetime import date
from unittest.mock import MagicMock, AsyncMock

from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Contact, User
from src.schemas.contact import ContactSchema, ContactUpdateSchema
from src.repository.contacts import (get_contacts, get_all_contacts, get_contact, create_contact, update_contact, delete_contact,search_contacts, get_birthdays_upcoming)


class TestAsyncContact(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.user = User(id=1, username='test_user', password='qwerty', confirmed=True)
        self.session = AsyncMock(spec=AsyncSession)

    async def test_get_contacts(self):
        limit = 10
        offset = 0

        contacts = [
            Contact(id=1, first_name='John', last_name='Doe', email='john.doe@example.com', phone='1234567890', birthday='2024-08-20', user=self.user),
            Contact(id=2, first_name='Jane', last_name='Doe', email='jane.doe@example.com', phone='9876543210', birthday='2023-06-15', user=self.user),
            Contact(id=3, first_name='Alice', last_name='Smith', email='alice.smith@example.com', phone='0987654321', birthday='2025-12-31', user=self.user)
        ]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_contacts(limit, offset, self.session, self.user)
        self.assertEqual(result, contacts)

    async def test_get_all_contacts(self):
        limit = 10
        offset = 0
        contacts = [
            Contact(id=1, first_name='John', last_name='Doe', email='john.doe@example.com', phone='1234567890', birthday='2024-08-20', user=self.user),
            Contact(id=2, first_name='Jane', last_name='Doe', email='jane.doe@example.com', phone='9876543210', birthday='2023-06-15', user=self.user),
            Contact(id=3, first_name='Alice', last_name='Smith', email='alice.smith@example.com', phone='0987654321', birthday='2025-12-31', user=self.user)
        ]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_all_contacts(limit, offset, self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact(self):
        contact_id = 1

        contact = Contact(id=contact_id, first_name='John', last_name='Doe', email='john.doe@example.com',
                          phone='1234567890', birthday='2024-08-20', user_id=self.user.id)

        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = contact
        self.session.execute.return_value = mocked_contact

        result = await get_contact(contact_id, self.session, self.user)
        self.assertEqual(result, contact)

    async def test_get_contact_not_found(self):
        contact_id = 2

        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = None
        self.session.execute.return_value = mocked_contact

        result = await get_contact(contact_id, self.session, self.user)
        self.assertIsNone(result)

    async def test_create_contact(self):
        contact_data = ContactSchema(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="1234567890",
            birthday=date(1990, 1, 1),
            additional_data="Some additional data"
        )

        expected_contact = Contact(
            id=1,
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="1234567890",
            birthday=date(1990, 1, 1),
            additional_data="Some additional data",
            user_id=self.user.id
        )

        self.session.add = AsyncMock()
        self.session.commit = AsyncMock()
        self.session.refresh = AsyncMock(return_value=expected_contact)

        result = await create_contact(contact_data, self.session, self.user)

        self.assertEqual(result.first_name, expected_contact.first_name)
        self.assertEqual(result.last_name, expected_contact.last_name)
        self.assertEqual(result.email, expected_contact.email)
        self.assertEqual(result.phone, expected_contact.phone)
        self.assertEqual(result.birthday, expected_contact.birthday)
        self.assertEqual(result.additional_data, expected_contact.additional_data)
        self.assertEqual(result.user_id, self.user.id)

    async def test_update_contact(self):
        contact_id = 1
        update_data = ContactUpdateSchema(
            first_name='UpdatedName',
            last_name='UpdatedLastName',
            email='updated.email@example.com',
            phone='1234567890',
            birthday='2024-08-20',
            additional_data='Updated data'
        )

        existing_contact = Contact(id=contact_id, first_name='John', last_name='Doe', email='john.doe@example.com',
                                   phone='1234567890', birthday='2024-08-20', user_id=self.user.id)

        mocked_result = MagicMock()
        mocked_result.scalar_one_or_none.return_value = existing_contact
        self.session.execute.return_value = mocked_result

        self.session.commit = AsyncMock()
        self.session.refresh = AsyncMock()

        result = await update_contact(contact_id, update_data, self.session, self.user)

        self.assertEqual(result.first_name, 'UpdatedName')
        self.assertEqual(result.last_name, 'UpdatedLastName')
        self.assertEqual(result.email, 'updated.email@example.com')

        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once_with(existing_contact)

    async def test_delete_contact(self):
        contact_id = 1

        existing_contact = Contact(id=contact_id, first_name='John', last_name='Doe', email='john.doe@example.com',
                                   phone='1234567890', birthday='2024-08-20', user_id=self.user.id)

        mocked_result = MagicMock()
        mocked_result.scalar_one_or_none.return_value = existing_contact
        self.session.execute.return_value = mocked_result

        self.session.commit = AsyncMock()
        self.session.delete = AsyncMock()

        result = await delete_contact(contact_id, self.session, self.user)

        self.assertEqual(result, existing_contact)
        self.session.delete.assert_called_once_with(existing_contact)
        self.session.commit.assert_called_once()

    async def test_search_contacts(self):
        first_name = 'John'
        last_name = None
        email = None

        contact = Contact(id=1, first_name='John', last_name='Doe', email='john.doe@example.com',
                          phone='1234567890', birthday='2024-08-20', user_id=self.user.id)

        mocked_result = MagicMock()
        mocked_result.scalars.return_value.all.return_value = [contact]
        self.session.execute.return_value = mocked_result

        result = await search_contacts(first_name, last_name, email, self.session, self.user)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].first_name, 'John')

# tests/test_user.py

import unittest
from services.user_service import UserService

class TestUserService(unittest.TestCase):

    def setUp(self):
        # fresh service for each test
        self.service = UserService()

    def test_add_user_success(self):
        result = self.service.add_user("TestUser", "testuser@example.com")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["name"], "TestUser")

    def test_add_user_duplicate_email(self):
        # first insert
        self.service.add_user("UserA", "duplicate@example.com")
        # second insert with same email should fail
        result = self.service.add_user("UserB", "duplicate@example.com")
        self.assertEqual(result["status"], "failed")
        self.assertIn("reason", result)

    def test_get_users(self):
        self.service.add_user("Alpha", "alpha@example.com")
        users = self.service.get_users()
        self.assertTrue(len(users) > 0)

    def test_delete_user(self):
        # add a user first
        self.service.add_user("Beta", "beta@example.com")
        users = self.service.get_users()
        user_id = users[-1][0]  # grab last inserted id
        result = self.service.delete_user(user_id)
        self.assertEqual(result["status"], "success")

if __name__ == "__main__":
    unittest.main()

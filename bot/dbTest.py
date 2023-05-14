# Test Here
import imp
import unittest
from database import Database
import config


class DatabaseTestCase(unittest.TestCase):
    def setUp(self):
        self.testingDb = Database()
        self.test_user = {
            "user_id": 123,
            "chat_id": 456,
            "username": "Vincent",
            "first_name": "Chen",
            "last_name": "Test",
        }

    def tearDown(self):
        # Clean up any resources used by the tests
        self.testingDb.user_collection.delete_one({"_id": self.test_user["user_id"]})
        self.testingDb.dialog_collection.delete_many(
            {"user_id": self.test_user["user_id"]}
        )

    def test_check_if_user_exists(self):
        self.assertFalse(self.testingDb.check_if_user_exists(self.test_user["user_id"]))
        self.testingDb.add_new_user(**self.test_user)
        self.assertTrue(self.testingDb.check_if_user_exists(self.test_user["user_id"]))

    def test_add_new_user(self):
        self.testingDb.add_new_user(**self.test_user)
        user = self.testingDb.user_collection.find_one(
            {"_id": self.test_user["user_id"]}
        )
        self.assertIsNotNone(user)
        self.assertEqual(user["username"], self.test_user["username"])

    def test_start_new_dialog(self):
        self.testingDb.add_new_user(**self.test_user)
        dialog_id = self.testingDb.start_new_dialog(self.test_user["user_id"])
        dialog = self.testingDb.dialog_collection.find_one({"_id": dialog_id})
        self.assertIsNotNone(dialog)

    def test_get_user_attribute(self):
        self.testingDb.add_new_user(**self.test_user)
        username = self.testingDb.get_user_attribute(
            self.test_user["user_id"], "username"
        )
        self.assertEqual(username, self.test_user["username"])

    # TODO - Write time remaining and test time remaining

    def test_update_n_used_tokens(self):
        self.testingDb.add_new_user(**self.test_user)
        model = "gpt-3"
        n_input_tokens = 10
        n_output_tokens = 20
        n_newly_added_tokens = 30

        remaining_tokens = self.testingDb.update_n_used_tokens(
            self.test_user["user_id"],
            model,
            n_input_tokens,
            n_output_tokens,
            n_newly_added_tokens,
        )

        # Check if the remaining tokens are calculated correctly
        self.assertEqual(
            remaining_tokens,
            config.available_token_new_user + n_newly_added_tokens - n_output_tokens,
        )

        # Check if the n_used_tokens attribute is updated correctly
        n_used_tokens_dict = self.testingDb.get_user_attribute(
            self.test_user["user_id"], "n_used_tokens"
        )
        self.assertEqual(n_used_tokens_dict[model]["n_input_tokens"], n_input_tokens)
        self.assertEqual(n_used_tokens_dict[model]["n_output_tokens"], n_output_tokens)
        self.assertEqual(
            n_used_tokens_dict[model]["n_available_output_token"],
            config.available_token_new_user + n_newly_added_tokens,
        )


if __name__ == "__main__":
    unittest.main()

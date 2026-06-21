import os
import unittest
from dotenv import load_dotenv
from adapters.thingsboardAdapter import ThingsboardAdapter as ThingsboardAdapter

load_dotenv()
thingsboard_username = os.getenv("THINGSBOARD_USERNAME")
thingsboard_password = os.getenv("THINGSBOARD_PASSWORD")
tb_url = os.getenv("THINGSBOARD_URL")

class ThingsboardAdapterTest(unittest.TestCase):

    def test_token_is_returned(self):
        adapter = ThingsboardAdapter(tb_url)
        token = adapter.authenticate(thingsboard_username, thingsboard_password)
        self.assertIsNotNone(token)

    #def test_space_is_added(self):
    #    adapter = ThingsboardAdapter(tb_url)
    #    token = adapter.authenticate(thingsboard_username, thingsboard_password)
    #    result = adapter.add_zone(token, "Test Space")
    #    self.assertTrue(result)

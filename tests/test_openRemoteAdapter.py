import os
import unittest
from dotenv import load_dotenv
from adapters.openRemoteAdapter import OpenRemoteAdapter as OpenRemoteAdapter

load_dotenv()
openremote_username = os.getenv("OPENREMOTE_USERNAME")
openremote_password = os.getenv("OPENREMOTE_PASSWORD")
or_url = os.getenv("OPENREMOTE_URL")

class OpenRemoteAdapterTest(unittest.TestCase):

    def test_token_is_returned(self):
        adapter = OpenRemoteAdapter(or_url)
        token = adapter.authenticate(openremote_username, openremote_password)
        self.assertIsNotNone(token)

    #def test_space_is_added(self):
    #    adapter = ThingsboardAdapter(tb_url)
    #    token = adapter.authenticate(thingsboard_username, thingsboard_password)
    #    result = adapter.add_zone(token, "Test Space")
    #    self.assertTrue(result)

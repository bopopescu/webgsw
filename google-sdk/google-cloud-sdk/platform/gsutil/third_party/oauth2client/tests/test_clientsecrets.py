# Copyright 2014 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Unit tests for oauth2client.clientsecrets."""

from io import StringIO
import os
import tempfile
import unittest

from oauth2client._helpers import _from_bytes
from oauth2client import GOOGLE_AUTH_URI
from oauth2client import GOOGLE_REVOKE_URI
from oauth2client import GOOGLE_TOKEN_URI
from oauth2client import clientsecrets


__author__ = 'jcgregorio@google.com (Joe Gregorio)'


DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
VALID_FILE = os.path.join(DATA_DIR, 'client_secrets.json')
INVALID_FILE = os.path.join(DATA_DIR, 'unfilled_client_secrets.json')
NONEXISTENT_FILE = os.path.join(__file__, '..', 'afilethatisntthere.json')


class Test__validate_clientsecrets(unittest.TestCase):

    def test_with_none(self):
        self.assertRaises(clientsecrets.InvalidClientSecretsError,
                          clientsecrets._validate_clientsecrets,
                          None)

    def test_with_other_than_one_key(self):
        self.assertRaises(clientsecrets.InvalidClientSecretsError,
                          clientsecrets._validate_clientsecrets,
                          {})
        self.assertRaises(clientsecrets.InvalidClientSecretsError,
                          clientsecrets._validate_clientsecrets,
                          {'one': 'val', 'two': 'val'})

    def test_with_non_dictionary(self):
        non_dict = [None]
        self.assertRaises(clientsecrets.InvalidClientSecretsError,
                          clientsecrets._validate_clientsecrets,
                          non_dict)

    def test_invalid_client_type(self):
        fake_type = 'fake_type'
        self.assertNotEqual(fake_type, clientsecrets.TYPE_WEB)
        self.assertNotEqual(fake_type, clientsecrets.TYPE_INSTALLED)
        self.assertRaises(clientsecrets.InvalidClientSecretsError,
                          clientsecrets._validate_clientsecrets,
                          {fake_type: None})

    def test_missing_required_type_web(self):
        required = clientsecrets.VALID_CLIENT[
            clientsecrets.TYPE_WEB]['required']
        # We will certainly have less than all 5 keys.
        self.assertEqual(len(required), 5)

        clientsecrets_dict = {
            clientsecrets.TYPE_WEB: {'not_required': None},
        }
        self.assertRaises(clientsecrets.InvalidClientSecretsError,
                          clientsecrets._validate_clientsecrets,
                          clientsecrets_dict)

    def test_string_not_configured_type_web(self):
        string_props = clientsecrets.VALID_CLIENT[
            clientsecrets.TYPE_WEB]['string']

        self.assertTrue('client_id' in string_props)
        clientsecrets_dict = {
            clientsecrets.TYPE_WEB: {
                'client_id': '[[template]]',
                'client_secret': 'seekrit',
                'redirect_uris': None,
                'auth_uri': None,
                'token_uri': None,
            },
        }
        self.assertRaises(clientsecrets.InvalidClientSecretsError,
                          clientsecrets._validate_clientsecrets,
                          clientsecrets_dict)

    def test_missing_required_type_installed(self):
        required = clientsecrets.VALID_CLIENT[
            clientsecrets.TYPE_INSTALLED]['required']
        # We will certainly have less than all 5 keys.
        self.assertEqual(len(required), 5)

        clientsecrets_dict = {
            clientsecrets.TYPE_INSTALLED: {'not_required': None},
        }
        self.assertRaises(clientsecrets.InvalidClientSecretsError,
                          clientsecrets._validate_clientsecrets,
                          clientsecrets_dict)

    def test_string_not_configured_type_installed(self):
        string_props = clientsecrets.VALID_CLIENT[
            clientsecrets.TYPE_INSTALLED]['string']

        self.assertTrue('client_id' in string_props)
        clientsecrets_dict = {
            clientsecrets.TYPE_INSTALLED: {
                'client_id': '[[template]]',
                'client_secret': 'seekrit',
                'redirect_uris': None,
                'auth_uri': None,
                'token_uri': None,
            },
        }
        self.assertRaises(clientsecrets.InvalidClientSecretsError,
                          clientsecrets._validate_clientsecrets,
                          clientsecrets_dict)

    def test_success_type_web(self):
        client_info = {
                'client_id': 'eye-dee',
                'client_secret': 'seekrit',
                'redirect_uris': None,
                'auth_uri': None,
                'token_uri': None,
        }
        clientsecrets_dict = {
            clientsecrets.TYPE_WEB: client_info,
        }
        result = clientsecrets._validate_clientsecrets(clientsecrets_dict)
        self.assertEqual(result, (clientsecrets.TYPE_WEB, client_info))

    def test_success_type_installed(self):
        client_info = {
                'client_id': 'eye-dee',
                'client_secret': 'seekrit',
                'redirect_uris': None,
                'auth_uri': None,
                'token_uri': None,
        }
        clientsecrets_dict = {
            clientsecrets.TYPE_INSTALLED: client_info,
        }
        result = clientsecrets._validate_clientsecrets(clientsecrets_dict)
        self.assertEqual(result, (clientsecrets.TYPE_INSTALLED, client_info))


class Test__loadfile(unittest.TestCase):

    def test_success(self):
        client_type, client_info = clientsecrets._loadfile(VALID_FILE)
        expected_client_info = {
            'client_id': 'foo_client_id',
            'client_secret': 'foo_client_secret',
            'redirect_uris': [],
            'auth_uri': GOOGLE_AUTH_URI,
            'token_uri': GOOGLE_TOKEN_URI,
            'revoke_uri': GOOGLE_REVOKE_URI,
        }
        self.assertEqual(client_type, clientsecrets.TYPE_WEB)
        self.assertEqual(client_info, expected_client_info)

    def test_non_existent(self):
        path = os.path.join(DATA_DIR, 'fake.json')
        self.assertFalse(os.path.exists(path))
        self.assertRaises(clientsecrets.InvalidClientSecretsError,
                          clientsecrets._loadfile, path)

    def test_bad_json(self):
        filename = tempfile.mktemp()
        with open(filename, 'wb') as file_obj:
            file_obj.write(b'[')
        self.assertRaises(ValueError,
                          clientsecrets._loadfile, filename)


class OAuth2CredentialsTests(unittest.TestCase):

    def test_validate_error(self):
        payload = (
            b'{'
            b'  "web": {'
            b'    "client_id": "[[CLIENT ID REQUIRED]]",'
            b'    "client_secret": "[[CLIENT SECRET REQUIRED]]",'
            b'    "redirect_uris": ["http://localhost:8080/oauth2callback"],'
            b'    "auth_uri": "",'
            b'    "token_uri": ""'
            b'  }'
            b'}')
        ERRORS = [
            ('{}', 'Invalid'),
            ('{"foo": {}}', 'Unknown'),
            ('{"web": {}}', 'Missing'),
            ('{"web": {"client_id": "dkkd"}}', 'Missing'),
            (payload, 'Property'),
        ]
        for src, match in ERRORS:
            # Ensure that it is unicode
            src = _from_bytes(src)
            # Test load(s)
            try:
                clientsecrets.loads(src)
                self.fail(src + ' should not be a valid client_secrets file.')
            except clientsecrets.InvalidClientSecretsError as e:
                self.assertTrue(str(e).startswith(match))

            # Test loads(fp)
            try:
                fp = StringIO(src)
                clientsecrets.load(fp)
                self.fail(src + ' should not be a valid client_secrets file.')
            except clientsecrets.InvalidClientSecretsError as e:
                self.assertTrue(str(e).startswith(match))

    def test_load_by_filename(self):
        try:
            clientsecrets._loadfile(NONEXISTENT_FILE)
            self.fail('should fail to load a missing client_secrets file.')
        except clientsecrets.InvalidClientSecretsError as e:
            self.assertTrue(str(e).startswith('File'))


class CachedClientsecretsTests(unittest.TestCase):

    class CacheMock(object):
        def __init__(self):
            self.cache = {}
            self.last_get_ns = None
            self.last_set_ns = None

        def get(self, key, namespace=''):
            # ignoring namespace for easier testing
            self.last_get_ns = namespace
            return self.cache.get(key, None)

        def set(self, key, value, namespace=''):
            # ignoring namespace for easier testing
            self.last_set_ns = namespace
            self.cache[key] = value

    def setUp(self):
        self.cache_mock = self.CacheMock()

    def test_cache_miss(self):
        client_type, client_info = clientsecrets.loadfile(
            VALID_FILE, cache=self.cache_mock)
        self.assertEqual('web', client_type)
        self.assertEqual('foo_client_secret', client_info['client_secret'])

        cached = self.cache_mock.cache[VALID_FILE]
        self.assertEqual({client_type: client_info}, cached)

        # make sure we're using non-empty namespace
        ns = self.cache_mock.last_set_ns
        self.assertTrue(bool(ns))
        # make sure they're equal
        self.assertEqual(ns, self.cache_mock.last_get_ns)

    def test_cache_hit(self):
        self.cache_mock.cache[NONEXISTENT_FILE] = {'web': 'secret info'}

        client_type, client_info = clientsecrets.loadfile(
            NONEXISTENT_FILE, cache=self.cache_mock)
        self.assertEqual('web', client_type)
        self.assertEqual('secret info', client_info)
        # make sure we didn't do any set() RPCs
        self.assertEqual(None, self.cache_mock.last_set_ns)

    def test_validation(self):
        try:
            clientsecrets.loadfile(INVALID_FILE, cache=self.cache_mock)
            self.fail('Expected InvalidClientSecretsError to be raised '
                      'while loading %s' % INVALID_FILE)
        except clientsecrets.InvalidClientSecretsError:
            pass

    def test_without_cache(self):
        # this also ensures loadfile() is backward compatible
        client_type, client_info = clientsecrets.loadfile(VALID_FILE)
        self.assertEqual('web', client_type)
        self.assertEqual('foo_client_secret', client_info['client_secret'])


if __name__ == '__main__':  # pragma: NO COVER
    unittest.main()
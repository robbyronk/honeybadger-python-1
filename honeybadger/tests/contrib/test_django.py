import unittest
import json
from mock import patch
from mock import Mock

from django.conf.urls import url
from django.test import RequestFactory
from django.test import SimpleTestCase
from django.test import override_settings
from django.test import modify_settings
from django.test import Client

from honeybadger import honeybadger
from honeybadger.config import Configuration
from honeybadger.contrib import DjangoHoneybadgerMiddleware
from honeybadger.contrib.django import DjangoPlugin
from honeybadger.contrib.django import clear_request
from honeybadger.contrib.django import set_request
from honeybadger.contrib.django import current_request

from .django.views import plain_view
from .django.views import always_fails
from ..utils import mock_urlopen



class DjangoPluginTestCase(unittest.TestCase):
    def setUp(self):
        self.plugin = DjangoPlugin()
        self.rf = RequestFactory()
        self.config = Configuration()
        self.url = url(r'test', plain_view, name='test_view')

    def tearDown(self):
        clear_request()

    def test_supports_django_request(self):
        request = self.rf.get('test')
        set_request(request)

        self.assertTrue(self.plugin.supports(self.config, {}))

    def test_generate_payload_get(self):
        request = self.rf.get('test', {'a': 1})
        request.resolver_match = self.url.resolve('test')
        set_request(request)

        payload = self.plugin.generate_payload(self.config, {'foo': 'bar'})
        self.assertEqual(payload['url'], 'http://testserver/test?a=1')
        self.assertEqual(payload['action'], 'plain_view')
        self.assertDictEqual(payload['params'], {'a': ['1']})
        self.assertDictEqual(payload['session'], {})
        self.assertDictEqual(payload['context'], {'foo': 'bar'})

    def test_generate_payload_post(self):
        request = self.rf.post('test', data={'a': 1, 'b': 2, 'password': 'notsafe'})
        request.resolver_match = self.url.resolve('test')
        set_request(request)

        payload = self.plugin.generate_payload(self.config, {'foo': 'bar'})
        self.assertEqual(payload['url'], 'http://testserver/test')
        self.assertEqual(payload['action'], 'plain_view')
        self.assertDictEqual(payload['params'], {'a': ['1'], 'b': ['2'], 'password': '[FILTERED]'})
        self.assertDictEqual(payload['session'], {})
        self.assertDictEqual(payload['context'], {'foo': 'bar'})

    def test_generate_payload_with_session(self):
        request = self.rf.get('test')
        request.resolver_match = self.url.resolve('test')
        request.session = {'lang': 'en'}
        set_request(request)

        payload = self.plugin.generate_payload(self.config, {'foo': 'bar'})
        self.assertEqual(payload['url'], 'http://testserver/test')
        self.assertEqual(payload['action'], 'plain_view')
        self.assertDictEqual(payload['session'], {'lang': 'en'})
        self.assertDictEqual(payload['context'], {'foo': 'bar'})

# TODO: add an integration test case that tests the actual integration with Django

class DjangoMiddlewareTestCase(unittest.TestCase):
    def setUp(self):
        self.rf = RequestFactory()
        self.url = url(r'test', plain_view, name='test_view')
        self.middleware = DjangoHoneybadgerMiddleware()

    def tearDown(self):
        clear_request()

    def test_process_request(self):
        request = self.rf.get('/test')
        request.resolver_match = self.url.resolve('test')
        self.middleware.process_request(request)
        self.assertEqual(request, current_request())

    @patch('honeybadger.contrib.django.honeybadger')
    def test_process_exception(self, mock_hb):
        request = self.rf.get('test')
        request.resolver_match = self.url.resolve('test')
        self.middleware.process_request(request)
        exc = ValueError('test exception')
        self.middleware.process_exception(request, exc)

        mock_hb.notify.assert_called_with(exc)
        self.assertIsNone(current_request(), msg='Current request should be cleared after exception handling')

    def test_process_response(self):
        request = self.rf.get('test')
        request.resolver_match = self.url.resolve('test')
        response = Mock()
        honeybadger.set_context(foo='bar')
        self.middleware.process_request(request)

        self.middleware.process_response(request, response)
        self.assertDictEqual({}, honeybadger._get_context(), msg='Context should be cleared after response handling')
        self.assertIsNone(current_request(), msg='Current request should be cleared after response handling')

@override_settings(
    ROOT_URLCONF='honeybadger.tests.contrib.django.urls'
)
@modify_settings(MIDDLEWARE={
    'prepend': ['honeybadger.contrib.django.DjangoHoneybadgerMiddleware']
})
class DjangoMiddlewareIntegrationTestCase(SimpleTestCase):
    def setUp(self):
        self.client = Client()

    def test_context_cleared_after_response(self):
        self.assertIsNone(current_request(), msg='Current request should be empty prior to request')
        response = self.client.get('/plain_view')
        self.assertIsNone(current_request(), msg='Current request should be cleared after request processed')

    @override_settings(
        HONEYBADGER={
            'API_KEY': 'abc123'
        }
    )
    def test_exceptions_handled_by_middleware(self):
        def assert_payload(req):
            error_payload = json.loads(req.data)

            self.assertEqual(req.get_header('X-api-key'), 'abc123')
            self.assertEqual(req.get_full_url(), '{}/v1/notices/'.format(honeybadger.config.endpoint))
            self.assertEqual(error_payload['error']['class'], 'ValueError')
            self.assertEqual(error_payload['error']['message'], 'always fails')


        with mock_urlopen(assert_payload) as request_mock:
            try:
                response = self.client.get('/always_fails/')
            except:
                pass
            self.assertTrue(request_mock.called)
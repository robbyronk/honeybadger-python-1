import unittest

from django.conf.urls import url
from django.http import JsonResponse
from django.test import RequestFactory
from mock import patch, Mock

from honeybadger import honeybadger
from honeybadger.config import Configuration
from honeybadger.contrib import DjangoHoneybadgerMiddleware
from honeybadger.contrib.django import DjangoPlugin, clear_request, set_request, current_request
from honeybadger.tests.test_middleware import view


def view(request):
    # Test view
    return JsonResponse({})


class DjangoPluginTestCase(unittest.TestCase):
    def setUp(self):
        self.plugin = DjangoPlugin()
        self.rf = RequestFactory()
        self.config = Configuration()
        self.url = url(r'test', view, name='test_view')

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
        self.assertEqual(payload['action'], 'view')
        self.assertDictEqual(payload['params'], {'a': ['1']})
        self.assertDictEqual(payload['session'], {})
        self.assertDictEqual(payload['context'], {'foo': 'bar'})

    def test_generate_payload_post(self):
        request = self.rf.post('test', data={'a': 1, 'b': 2, 'password': 'notsafe'})
        request.resolver_match = self.url.resolve('test')
        set_request(request)

        payload = self.plugin.generate_payload(self.config, {'foo': 'bar'})
        self.assertEqual(payload['url'], 'http://testserver/test')
        self.assertEqual(payload['action'], 'view')
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
        self.assertEqual(payload['action'], 'view')
        self.assertDictEqual(payload['session'], {'lang': 'en'})
        self.assertDictEqual(payload['context'], {'foo': 'bar'})


class DjangoMiddlewareTestCase(unittest.TestCase):
    def setUp(self):
        self.rf = RequestFactory()
        self.url = url(r'test', view, name='test_view')
        self.middleware = DjangoHoneybadgerMiddleware()

    def tearDown(self):
        clear_request()

    def test_process_request(self):
        request = self.rf.get('test')
        self.middleware.process_request(request)
        self.assertEqual(request, current_request())

    @patch('honeybadger.middleware.honeybadger')
    def test_process_exception(self, mock_hb):
        request = self.rf.get('test')
        self.middleware.process_request(request)
        exc = ValueError('test exception')
        self.middleware.process_exception(request, exc)

        mock_hb.notify.assert_called_with(exc)
        self.assertIsNone(current_request(), msg='Current request should be cleared after exception handling')

    def test_process_response(self):
        request = self.rf.get('test')
        response = Mock()
        honeybadger.set_context(foo='bar')
        self.middleware.process_request(request)

        self.middleware.process_response(request, response)
        self.assertDictEqual({}, honeybadger._get_context(), msg='Context should be cleared after response handling')
        self.assertIsNone(current_request(), msg='Current request should be cleared after response handling')
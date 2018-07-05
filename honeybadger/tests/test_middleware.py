import warnings

from .contrib.test_django import DjangoMiddlewareTestCase
from honeybadger.middleware import DjangoHoneybadgerMiddleware


class MiddlewareTestCase(DjangoMiddlewareTestCase):
    def test_middleware_import_warning(self):
        with warnings.catch_warnings(record=True) as w:
            middleware = DjangoHoneybadgerMiddleware()
            assert len(w) == 1
            assert issubclass(w[-1].category, FutureWarning)
            assert "moved" in str(w[-1].message)

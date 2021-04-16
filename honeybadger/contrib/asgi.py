from honeybadger import honeybadger, plugins, utils
import urllib

def _looks_like_asgi3(app):
    # TODO: implement this.
    return True


def _get_headers(scope: dict) -> dict:
    headers = {}
    for raw_key, raw_value in scope["headers"]:
        key = raw_key.decode("latin-1")
        value = raw_value.decode("latin-1")
        if key in headers:
            headers[key] = headers["key"] + ", " + value
        else:
            headers[key] = value
    return headers

def _get_query(scope: dict) -> str:
    qs = scope.get("query_string")
    if not qs:
        return None
    return urllib.parse.unquote(qs.decode("latin-1"))

def _get_url(scope: dict, default_scheme: str, host: str = None) -> str:
    scheme = scope.get("scheme", default_scheme)
    server = scope.get("server")
    path = scope.get("root_path", "") + scope.get("path", "")
    if host:
        return "%s://%s%s" % (scheme, host, path)
    
    if server is not None:
        host, port = server
        default_port = {"http": 80, "https": 443, "ws": 80, "wss": 443}[scheme]
        if port != default_port:
            return "%s://%s:%s%s" % (scheme, host, port, path)
        return "%s://%s%s" % (scheme, host, path)
    return path


def _as_context(scope: dict) -> dict:
    ctx = {}
    if scope.get("type") in ("http", "websocket"):
        ctx["method"] = scope.get("method")
        ctx["headers"] = headers = _get_headers(scope)
        ctx["query_string"] = _get_query(scope)
        ctx["url"] = _get_url(
            scope, "http" if scope["type"] == "http" else "ws", headers.get("host")
        )
    ctx["client"] = scope.get("client")  # TODO: do we ALWAYS have to send this, or there are limitations?
    # TODO: should we look at "endpoint"?
    return utils.filter_dict(ctx, honeybadger.config.params_filters)

class ASGIHoneybadger(plugins.Plugin):
    __slots__ = ("__call__", "app")

    def __init__(self, app, **kwargs):
        super().__init__("ASGI")

        if kwargs:
            honeybadger.configure(**kwargs)

        self.app = app

        if _looks_like_asgi3(app):
            self.__call__ = self._run_asgi3
        else:
            self.__call__ = self._run_asgi2

        plugins.default_plugin_manager.register(self)

    def _run_asgi2(self, scope):
        async def inner(receive, send):
            return await self._run_app(scope, lambda: self.app(scope)(receive, send))
        return inner

    async def _run_asgi3(self, scope, receive, send):
        return await self._run_app(scope, lambda: self.app(scope, receive, send))
    
    async def _run_app(self, scope, callback):
        # TODO: Should we check recursive middleware stacks?
        # See: https://github.com/getsentry/sentry-python/blob/master/sentry_sdk/integrations/asgi.py#L112
        try:
            return await callback()
        except Exception as exc:
            honeybadger.notify(exception=exc, context=_as_context(scope))
            raise exc from None
        finally:
            # TODO: do we really need some clean up? See how context is handled.
            honeybadger.reset_context()

    def supports(self, config, context):
        # TODO: implement this.
        return True
    
    def generate_payload(self, default_payload, config, context):
        # TODO: Maybe filter away from context using config?
        return default_payload

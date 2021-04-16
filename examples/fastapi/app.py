from fastapi import FastAPI, HTTPException, APIRouter
from honeybadger import honeybadger, contrib
from honeybadger.contrib import asgi
from honeybadger.contrib import fastapi
import pydantic

honeybadger.configure(api_key='c10787cf')

app = FastAPI()
# contrib.FastAPIHoneybadger(app)
app.add_middleware(asgi.ASGIHoneybadger, params_filters=["user-agent", "host", "url", "query_string", "client"])


@app.get("/raise_some_error")
def raise_some_error(a: str):
    """Raises an error."""
    raise Exception(f"SomeError Occurred (a = {a})")

class DivideRequest(pydantic.BaseModel):
    a: int
    b: int = 0

@app.post("/divide")
def divide(req: DivideRequest):
    """Divides `a` by `b`."""
    return req.a / req.b

@app.post("/raise_404")
def raise_404(req: DivideRequest, a: bool = True):
    raise HTTPException(status_code=404, detail="Raising on purpose.")


some_router = APIRouter()

@some_router.get("/some_router_endpoint")
def some_router_endpoint():
    raise Exception("Exception Raised by some router endpoint.")

app.include_router(some_router)
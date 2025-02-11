import os

import pytest

from starlette.applications import Starlette
from starlette.routing import Route
from starlette.templating import Jinja2Templates


def test_templates(tmpdir, test_client_factory):
    path = os.path.join(tmpdir, "index.html")
    with open(path, "w") as file:
        file.write("<html>Hello, <a href='{{ url_for('homepage') }}'>world</a></html>")

    async def homepage(request):
        return templates.TemplateResponse("index.html", {"request": request})

    app = Starlette(
        debug=True,
        routes=[Route("/", endpoint=homepage)],
    )
    templates = Jinja2Templates(directory=str(tmpdir))

    client = test_client_factory(app)
    response = client.get("/")
    assert response.text == "<html>Hello, <a href='http://testserver/'>world</a></html>"
    assert response.template.name == "index.html"
    assert set(response.context.keys()) == {"request"}


def test_template_response_requires_request(tmpdir):
    templates = Jinja2Templates(str(tmpdir))
    with pytest.raises(ValueError):
        templates.TemplateResponse("", {})


def test_async_templates(tmpdir, test_client_factory):
    path = os.path.join(tmpdir, "index.html")
    with open(path, "w") as file:
        file.write("<html>Hello,{{ get_name() }}</html>")

    async def get_name():
        return "world"

    async def homepage(request):
        return await templates.AsyncTemplateResponse("index.html", {"request": request})

    app = Starlette(
        debug=True,
        routes=[Route("/", endpoint=homepage)],
    )
    templates = Jinja2Templates(directory=str(tmpdir), enable_async=True)
    templates.env.globals["get_name"] = get_name
    client = test_client_factory(app)
    response = client.get("/")
    assert response.text == "<html>Hello,world</html>"
    assert response.template.name == "index.html"
    assert set(response.context.keys()) == {"request"}


@pytest.mark.anyio
async def test_async_template_response_requires_request(tmpdir):
    templates = Jinja2Templates(str(tmpdir), enable_async=True)
    with pytest.raises(ValueError):
        await templates.AsyncTemplateResponse("", {})

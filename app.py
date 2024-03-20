from fastapi.responses import RedirectResponse
from fastapi.requests import Request
from fastapi import FastAPI
from nicegui import Client, app, ui
from urllib.parse import unquote_plus
from dotenv import load_dotenv
import requests
import uvicorn
import base64
import ssl
import os


load_dotenv()
main = FastAPI()


def get_authorization_url() -> str:
    """
    Returns the authorization URL for GitHub
    :return: The authorization URL"""
    state = unquote_plus(base64.b64encode(os.urandom(16)).decode("utf-8"))
    app.storage.user["state"] = state
    return f"https://github.com/login/oauth/authorize?client_id={os.getenv('CLIENT_ID')}&redirect_uri={os.getenv('REDIRECT_URI')}&scope=user&state={state}"

def fetch_access_token(code: str) -> str:
    """
    Fetches the access token from the GitHub API
    :param code: The code from GitHub
    :return: The access token"""
    data = {
        'client_id': os.getenv('CLIENT_ID'),
        'client_secret': os.getenv('CLIENT_SECRET'),
        'code': code,
        'redirect_uri': os.getenv('REDIRECT_URI'),
    }
    response = requests.post('https://github.com/login/oauth/access_token', data=data)
    response_data = response.text.split("&")
    return response_data[0].split("=")[1]

def fetch_user_data(access_token: str) -> dict:
    """
    Fetches the user data from the GitHub API
    :param access_token: The access token
    :return: The user data"""
    headers = {'Authorization': f'token {access_token}'}
    response = requests.get('https://api.github.com/user', headers=headers)
    print(response.text)
    return response.json()

@ui.page("/login/github/authorized")
async def api_gh_callback(request: Request):
    """
    Handles the callback from GitHub
    :param request: The request from GitHub"""
    code = request.query_params.get("code", "")
    state = request.query_params.get("state", "")
    if state != app.storage.user["state"]:
        ui.notify(message=f"Invalid state: {state}")
        return
    access_token = fetch_access_token(code)
    if user_data := fetch_user_data(access_token):
        app.storage.user["authenticated"] = True
        app.storage.user["data"] = user_data
        return RedirectResponse("/")
    else:
        return RedirectResponse("/login")


@ui.page("/login")
async def ui_login(client: Client):
    """
    Handles the login page"""
    await client.connected()
    with ui.card().classes("fixed-center"):
        ui.label(text="Login").classes("font-bold text-2xl")
        ui.input(label="Username").classes("w-full")
        ui.input(label="Password", password=True, password_toggle_button=True).classes("w-full")
        with ui.row().classes("w-full"):
            ui.button("Login", on_click=lambda: 1).props("flat").classes("disabled")
            ui.button("Login with Github", on_click=lambda: ui.navigate.to(target=get_authorization_url(), new_tab=True)).props("flat")

@ui.page("/")
def ui_index():
    """
    Handles the index page"""
    if not app.storage.user.get("authenticated", False):
        return RedirectResponse(url="/login")
    
    with ui.header():
        ui.label("NiceGHLogin").classes("font-bold text-2xl")
        with ui.image(source=app.storage.user["data"].get("avatar_url", "")).classes("w-8 rounded-full ml-auto mt-auto mb-auto cursor-pointer"):
            with ui.menu():
                ui.menu_item("Logout", on_click=lambda: (app.storage.user.update({"authenticated": False}) , app.storage.user.update({"data": {}}), ui.navigate.to("/login")))
    ui.label(text=f"Hello {app.storage.user['data']['name']}")


if __name__ in {'__main__', '__mp_main__'}:
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(certfile="./cert.pem", keyfile="./key.pem")
    ui.run_with(main, storage_secret=os.urandom(128))
    uvicorn.run(app, host="127.0.0.1", port=5000, ssl_keyfile="./key.pem", ssl_certfile="./cert.pem")

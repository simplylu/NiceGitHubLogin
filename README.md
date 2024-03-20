NiceGHLogin
===
This is just a sample implementation of the GitHub OAuth login flow within [NiceGui](https://nicegui.io). I followed [this](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps) documentation to learn about the flow.

### Usage
1. [Create an OAuth app on Github](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/creating-an-oauth-app)
2. Copy your `CLIENT_ID`, `CLIENT_SECRET` and `CALLBACK_URL` to the `.env.bak` file and remove the .bak extension
3. Generate some SSL Certificates (`openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key
.pem -days 365`)
4. Start the appliction with `python3 app.py`

### Important
You need to provide SSL certificates using Uvicorn or a Traefik reverse Proxy, as GitHub does not allow insecure callback URLs with HTTP.
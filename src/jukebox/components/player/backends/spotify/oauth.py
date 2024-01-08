import bottle


def create_oauth_website(auth_manager):
    app = bottle.Bottle()

    @app.route('/')
    def index():
        access_token = ""

        token_info = auth_manager.validate_token(auth_manager.cache_handler.get_cached_token())

        if token_info:
            print("Found cached token!")
            access_token = token_info['access_token']
        else:
            url = bottle.request.url
            code = auth_manager.parse_response_code(url)
            if code != url:
                print("Found Spotify auth code in Request URL! Trying to get valid access token...")
                print(f"code: {code}")
                token_info = auth_manager.get_access_token(code)
                access_token = token_info['access_token']

        if access_token:
            print("Access token available! Trying to get user information...")
            return access_token

        else:
            return get_login_button()

    def get_login_button():
        auth_url = get_auth_url()
        login_button = "<a href='" + auth_url + "'>Login to Spotify</a>"
        return login_button

    def get_auth_url():
        auth_url = auth_manager.get_authorize_url()
        return auth_url
    return app

import json
import re
import urllib.parse
import urllib.request


IG_URL = "https://www.instagram.com"
MAGIC_USER_AGENT = "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"


""" --- Objects --- """


class Queries:
    def init(self):
        self.USER: str
        self.QUERY_ID: str


""" --- Errors --- """


class InvalidUserError(Exception):
    pass


class RateLimitError(Exception):
    pass


class LoginRedirectionError(Exception):
    pass


""" --- Util --- """


def http_get(url: str, headers: dict = None):
    if not headers:
        headers = {"user-agent": MAGIC_USER_AGENT}
    else:
        headers = headers.copy()
        for k, v in headers.items():
            del headers[k]
            headers[k.lower()] = v
        if "user-agent" not in headers.keys():
            headers["user-agent"] = MAGIC_USER_AGENT

    http = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(http)
    content = response.read()
    text = content.decode("utf-8", "ignore")

    return dict(text=text, content=content)


def handle_json(request: dict) -> dict:
    try:
        data = json.loads(request["text"])
        if "message" in data and data["message"] == "rate limited":
            raise RateLimitError(
                "You are being rate limited by Instagram for this route.")
    except json.decoder.JSONDecodeError:
        raise LoginRedirectionError(
            "You are being redirected to the login page. Please, create an issue and describe what happened at https://github.com/Quatrecentquatre-404/instagram-guest-api/issues/new.")
    else:
        return data


def perform_graphql(query_hash: str, variables: dict) -> dict:
    url = IG_URL + "/graphql/query/?query_hash=" + query_hash + "&variables=" + urllib.parse.quote(json.dumps(variables).replace(" ", ""))
    request = http_get(url)
    return handle_json(request)


""" --- Core --- """


def fetch_queries_hash() -> Queries:
    """
    Returns a ``Queries`` object which contains many string keys to interact with the GraphQL API.
    """

    request = http_get(IG_URL + "/accounts/login")

    script_id = re.search(
        r"static/bundles/(metro|es6)/ConsumerLibCommons.js/[a-f0-9]+.js", request["text"]).group(0)
    script = http_get(IG_URL + '/' + script_id)
    queries = re.findall(r"\w+=\"[a-f0-9]{32}\"", script["text"])
    query_id = re.search(r"queryId:\"([a-f0-9]+)\"", script["text"]).group(1)

    o = Queries()
    for i in range(len(queries)):
        queries[i] = re.search(r"\"([a-f0-9]{32})\"", queries[i]).group(1)

    o.USER = queries[3]
    o.QUERY_ID = query_id

    return o


def fetch_user(username: str) -> dict:
    """
    :Params:
    ``username`` : str

    Returns a JSON object of type ``instagram_guest_api/types/users/user.json``.
    """

    request = http_get(IG_URL + "/" + username + "/channel/?__a=1")
    data = handle_json(request)
    return data


def fetch_user_stories(query_hash: str, user_id: str) -> dict:
    """
    :Params:
    ``query_hash`` : Queries.USER (str)
    ``user_id`` : str

    Returns a JSON object of type ``instagram_guest_api/types/users/stories.json``.
    """

    intents = dict(
        include_chaining=True,
        include_reel=True,
        include_suggested_users=True,
        include_logged_out_extras=True,
        include_highlight_reels=True,
        include_live_status=True,
        has_threaded_comments=True
    )

    response = perform_graphql(query_hash, dict(
        user_id=user_id, **intents))
    data = response["data"]
    feed = data["user"]

    if feed is None:
        raise InvalidUserError(
            "The content for the entered user ID was not found ! (%s)" % (user_id))

    return response


def fetch_user_posts(query_hash: str, profile_id: str, first: int = 12, after: str = '') -> dict:
    """
    :Params:
    ``query_hash`` : Queries.QUERY_ID (str)
    ``profile_id`` : str
    ``first`` : int (default set to 12)
    ``after`` : str (default set as empty)

    Returns a JSON object of type ``instagram_guest_api/types/posts/posts.json``.
    """

    data = perform_graphql(query_hash, dict(id=profile_id, first=first,
                   after=after if after is not None else ""))

    return data


def fetch_post_properties(short_code: str) -> dict:
    """
    :Params:
    ``short_code``: str

    Returns a JSON object of type ``instagram_guest_api/types/posts/post_properties.json``.
    """

    request = http_get(IG_URL + "/p/" + short_code + "/?__a=1")
    data = handle_json(request)
    return data

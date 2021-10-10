import json
import re
import api.util as util
import api.errors as errors


IG_URL = "https://www.instagram.com"


def fetch_queries_hash() -> util.Queries:
    """
    Returns a ``Queries`` object which contains many string keys to interact with the GraphQL API.
    """

    request = util.http_get(IG_URL + "/account/login")

    script_id = re.search(
        r"static/bundles/(metro|es6)/ConsumerLibCommons.js/[a-f0-9]+.js", request["text"]).group(0)
    script = util.http_get(IG_URL + '/' + script_id)
    queries = re.findall(r"\w+=\"[a-f0-9]{32}\"", script["text"])
    query_id = re.search(r"queryId:\"([a-f0-9]+)\"", script["text"]).group(1)

    o = util.Queries()
    for i in range(len(queries)):
        queries[i] = re.search(r"\"([a-f0-9]{32})\"", queries[i]).group(1)

    o.USER = queries[3]
    o.QUERY_ID = query_id

    return o


def fetch_user(username: str) -> dict:
    """
    :Params:
    ``username`` : str

    Returns a JSON object of type ``types/users/user.json``.
    """

    request = util.http_get(IG_URL + "/" + username + "/channel/?__a=1")
    data = util.handle_json(request)
    return data


def fetch_user_stories(query_hash: str, user_id: str) -> dict:
    """
    :Params:
    ``query_hash`` : Queries.USER (str)
    ``user_id`` : str

    Returns a JSON object of type ``types/users/stories.json``.
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

    response = util.perform_graphql(query_hash, dict(
        user_id=user_id, **intents))
    data = response["data"]
    feed = data["user"]

    if feed is None:
        raise errors.InvalidUserError(
            "The content for the entered user ID was not found ! (%s)" % (user_id))

    return response


def fetch_user_posts(query_hash: str, profile_id: str, first: int = 12, after: str = '') -> dict:
    """
    :Params:
    ``query_hash`` : Queries.QUERY_ID (str)
    ``profile_id`` : str
    ``first`` : int (default set to 12)
    ``after`` : str (default set as empty)

    Returns a JSON object of type ``types/posts/posts.json``.
    """

    url = IG_URL + "/graphql/query/?query_hash=" + query_hash + "&variables=" + \
        json.dumps(dict(id=profile_id, first=first,
                   after=after if after is not None else ""))

    request = util.http_get(url)
    data = util.handle_json(request)
    return data


def fetch_post_properties(short_code: str) -> dict:
    """
    :Params:
    ``short_code``: str

    Returns a JSON object of type ``types/posts/post_properties.json``.
    """

    request = util.http_get(IG_URL + "/p/" + short_code + "/?__a=1")
    data = util.handle_json(request)
    return data

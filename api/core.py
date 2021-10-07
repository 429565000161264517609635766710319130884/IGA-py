import json
import re
import api.util as util
import api.errors as errors



IG_URL = "https://www.instagram.com"


def fetch_csrf_token() -> str:
    """ Returns a string containing a CSRF token generated from Instagram allowing the script to access public information from the API. It's required to go futher. """
    request = util.http_get(IG_URL)
    shared_data = re.search(
        r"<script type=\"text/javascript\">window._sharedData = (.*);</script>", request["text"]).group(1)
    data = json.loads(shared_data)
    csrf_token = data["config"]["csrf_token"]
    return csrf_token


def fetch_queries_hash(csrf_token: str) -> util.Queries:
    """ Returns a ``Queries`` object which contains many key. These are about ``query_hash`` variable in GraphQL requests where each of them points to different endpoint. """
    request = util.http_get(IG_URL + "/account/login",
                            headers=dict(cookie="csrftoken=" + csrf_token + ";"))
    script_id = re.search(
        r"static/bundles/metro/ConsumerLibCommons.js/[a-f0-9]+.js", request["text"]).group(0)
    script = util.http_get(IG_URL + '/' + script_id)
    queries = re.findall(r"\w+=\"[a-f0-9]{32}\"", script["text"])
    query_id = re.search(r"queryId:\"([a-f0-9]+)\"", script["text"]).group(1)

    o = util.Queries()
    for i in range(len(queries)):
        queries[i] = re.search(r"\"([a-f0-9]{32})\"", queries[i]).group(1)

    o.FEED = queries[0]
    o.SUL = queries[1]
    o.MYSELF = queries[2]
    o.USER = queries[3]
    o.QUERY_ID = query_id
    return o


def fetch_home_feed(query_id: str, profile_id: str, csrf_token: str, first: int = 12, after: str = None) -> dict:
    """ Returns a JSON object which includes the first ``first`` posts after the ``after (or None)`` posts. """
    url = IG_URL + "/graphql/query/?query_hash=" + query_id + "&variables=" + \
        json.dumps(dict(id=profile_id, first=first,
                   after=after if after is not None else ""))

    request = util.http_get(url, headers=dict(
        cookie="csrftoken=" + csrf_token + ";"))
    data = util.handle_json(request)
    return data


def fetch_home_feed_properties_from(short_code: str, csrf_token: str) -> dict:
    """ Returns a JSON object which includes all informations about a post from it's ``short_code``. """
    request = util.http_get(IG_URL + "/p/" + short_code + "/?__a=1",
                            headers=dict(cookie="csrftoken=" + csrf_token + ";"))
    data = util.handle_json(request)
    return data


def fetch_user(username: str, csrf_token: str) -> dict:
    """ Returns a JSON object which includes pretty all public informations extracted from a profile. """
    url = IG_URL + "/" + username + "/?__a=1"
    request = util.http_get(url, headers=dict(
        cookie="csrftoken=" + csrf_token + ";"))
    data = util.handle_json(request)
    return data


def fetch_user_feed(query_hash: str, user_id: str, csrf_token: str) -> dict:
    """ Returns a JSON object which includes the highlights, reel, and some other, from a profile. """
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
        user_id=user_id, **intents), csrf_token)
    data = response["data"]
    feed = data["user"]

    if feed is None:
        raise errors.InvalidUserError(
            "The content for the entered user ID was not found ! (%s)" % (user_id))

    return response

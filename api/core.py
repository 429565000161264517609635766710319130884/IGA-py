import re
import json
import typing
import urllib3


MAGIC_USER_AGENT = "Mozilla/5.0 (Linux; Android 9; SM-A102U Build/PPR1.180610.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36 Instagram 155.0.0.37.107 Android (28/9; 320dpi; 720x1468; samsung; SM-A102U; a10e; exynos7885; en_US; 239490550)"


class Queries:
    def __init__(self, queries: typing.List[str], query_id: str):
        self.FEED: str = queries[0]
        self.SUL: str = queries[1]
        self.MYSELF: str = queries[2]
        self.USER: str = queries[3]
        self.QUERY_ID: str = query_id


class User:
    def __init__(self):
        self.biography: str = ""
        self.country_block: bool = False
        self.external_url: str = ""
        self.external_url_linkshimmed: str = ""
        self.followers_count: int = 0
        self.fbid: str = ""
        self.following_count: int = 0
        self.full_name: str = ""
        self.highlight_reel_count: int = 0
        self.hide_like_and_view_counts: bool = False
        self.id: str = ""
        self.is_joined_recently: bool = False
        self.category_name: str = ""
        self.is_private: bool = False
        self.is_verified: bool = False
        self.profile_pic_url: str = ""
        self.profile_pic_url_hd: str = ""
        self.username: str = ""
        self.connected_fb_page = None
        self.pronouns: typing.List[str] = []


class UserFeedHighlight:
    def __init__(self):
        self.id: str = ""
        self.cover_media: dict = dict(thumbnail_src="")
        self.cover_media_cropped_thumbnail: dict = dict(url="")
        self.owner: dict = dict(id="", profile_pic_url="", username="")
        self.title: str = ""


class UserFeedReel:
    def __init__(self):
        self.id: str = ""
        self.expiring_at: int = 0
        self.has_pride_media: bool = False
        self.latest_reel_media = None
        self.user: dict = dict(id="", profile_pic_url="", username="")
        self.owner: dict = dict(id="", profile_pic_url="", username="")


class UserFeed:
    def __init__(self, reel: UserFeedReel, highlights: typing.List[UserFeedHighlight], has_public_story: bool = False, is_live: bool = False, viewer=None):
        self.reel: UserFeedReel = reel
        self.is_live: bool = is_live
        self.has_public_story: bool = has_public_story
        self.highlights: typing.List[UserFeedHighlight] = highlights
        self.viewer = viewer


def __http_get(url: str, headers: dict = None):
    http = urllib3.PoolManager()
    default_user_agent = MAGIC_USER_AGENT
    if not headers:
        headers = {"user-agent": default_user_agent}
    else:
        headers = headers.copy()
        for k, v in headers.items():
            del headers[k]
            headers[k.lower()] = v
        if "user-agent" not in headers.keys():
            headers["user-agent"] = default_user_agent

    response = http.request("GET", url, headers=headers)
    content = response.__dict__.get("_body")
    return dict(text=content.decode("utf-8", "ignore"), content=content)


class InstagramRatelimitError(Exception):
    pass


def handle_json(request: dict) -> dict:
    try:
        return json.loads(request["text"])
    except:
        raise InstagramRatelimitError("You're being rate limited by Instagram for this route ! Please, try again in a hour.")

def fetch_csrf_token() -> str:
    request = __http_get("https://instagram.com/")
    shared_data = re.search(
        r"<script type=\"text/javascript\">window._sharedData = (.*);</script>", request["text"]).group(1)
    data = handle_json(shared_data)
    csrf_token = data["config"]["csrf_token"]
    return csrf_token


def fetch_queries_hash(csrf_token: str) -> Queries:
    request = __http_get("https://instagram.com/account/login",
                         headers=dict(cookie="csrftoken=" + csrf_token + ";"))
    script_id = re.search(
        r"static/bundles/metro/ConsumerLibCommons.js/[a-f0-9]+.js", request["text"]).group(0)
    script = __http_get("https://instagram.com/" + script_id)
    queries = re.findall(r"\w+=\"[a-f0-9]{32}\"", script["text"])
    query_id = re.search(r"queryId:\"([a-f0-9]+)\"", script["text"]).group(1)

    for i in range(len(queries)):
        queries[i] = re.search(r"\"([a-f0-9]{32})\"", queries[i]).group(1)

    return Queries(queries, query_id)


def fetch_homepage_content_properties(short_code: str, csrf_token: str) -> dict:
    request = __http_get("https://www.instagram.com/p/" + short_code +
                         "/?__a=1", headers=dict(cookie="csrftoken=" + csrf_token + ";"))
    data = handle_json(request)
    return data


def fetch_homepage_content(query_id: str, profile_id: str, csrf_token: str, first: int = 12, after: str = None) -> dict:
    url = "https://www.instagram.com/graphql/query/?query_hash=" + query_id + "&variables=" + \
        json.dumps(dict(id=profile_id, first=first,
                   after=after if after is not None else ""))

    request = __http_get(url, headers=dict(
        cookie="csrftoken=" + csrf_token + ";"))
    data = handle_json(request)
    return data


def perform_graphql(query_hash: str, variables: dict, csrf_token: str) -> dict:
    url = "https://www.instagram.com/graphql/query/?query_hash=" + \
        query_hash + "&variables=" + json.dumps(variables)
    request = __http_get(url, headers=dict(
        cookie="csrftoken=" + csrf_token + ";"))
    return handle_json(request)


def fetch_user(username: str, csrf_token: str) -> User:
    url = "https://www.instagram.com/" + username + "/?__a=1"
    request = __http_get(url, headers=dict(
        cookie="csrftoken=" + csrf_token + ";"))
    data = handle_json(request)
    graphql = data["graphql"]
    user = None
    editted_fields = dict(followers_count="edge_followed_by",
                          following_count="edge_follow")
    if "user" in graphql:
        user = User()
        for k in user.__dict__.keys():
            value = None
            if not k in editted_fields.keys():
                value = graphql["user"][k]
            else:
                value = graphql["user"][editted_fields[k]]["count"]
            setattr(user, k, value)
    return user


def fetch_user_feed(query_hash: str, user_id: str, csrf_token: str) -> UserFeed:
    intents = dict(
        include_chaining=True,
        include_reel=True,
        include_suggested_users=True,
        include_logged_out_extras=True,
        include_highlight_reels=True,
        include_live_status=True
    )

    response = perform_graphql(query_hash, dict(
        user_id=user_id, **intents), csrf_token)
    data = response["data"]
    feed = data["user"]
    reel = None
    highlights = None

    if "reel" in feed:
        reel = UserFeedReel()
        for k in reel.__dict__.keys():
            setattr(reel, k, feed["reel"][k])

    if "edge_highlight_reels" in feed:
        highlights_reel = feed["edge_highlight_reels"]
        highlights = [None] * len(highlights_reel["edges"])
        for i in range(len(highlights)):
            highlight = UserFeedHighlight()
            for k in highlight.__dict__.keys():
                setattr(highlight, k, highlights_reel["edges"][i]["node"][k])
            highlights[i] = highlight

    result = UserFeed(reel, highlights,
                      feed["has_public_story"], feed["is_live"])
    return result

import json
import api.errors as errors
import urllib.parse
import urllib3


urllib3.disable_warnings()
MAGIC_USER_AGENT = "Mozilla/5.0 (Linux; Android 9; SM-A102U Build/PPR1.180610.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36 Instagram 155.0.0.37.107 Android (28/9; 320dpi; 720x1468; samsung; SM-A102U; a10e; exynos7885; en_US; 239490550)"


class Queries:
    def init(self):
        self.FEED: str
        self.SUL: str
        self.MYSELF: str
        self.USER: str
        self.QUERY_ID: str

def http_get(url: str, headers: dict = None):
    http = urllib3.PoolManager()
    if not headers:
        headers = {"user-agent": MAGIC_USER_AGENT}
    else:
        headers = headers.copy()
        for k, v in headers.items():
            del headers[k]
            headers[k.lower()] = v
        if "user-agent" not in headers.keys():
            headers["user-agent"] = MAGIC_USER_AGENT

    response = http.request("GET", url, headers=headers)
    content = response.__dict__.get("_body")
    return dict(text=content.decode("utf-8", "ignore"), content=content)


def handle_json(request: dict) -> dict:
    try:
        return json.loads(request["text"])
    except json.decoder.JSONDecodeError:
        raise errors.RateLimitError(
            "You are being rate limited by Instagram for this route ! Please, try again in a hour.")


def perform_graphql(query_hash: str, variables: dict, csrf_token: str) -> dict:
    url = "https://www.instagram.com/graphql/query/?query_hash=" + \
        query_hash + "&variables=" + \
        urllib.parse.quote(json.dumps(variables).replace(' ', '').strip())

    request = http_get(url, headers=dict(
        cookie="csrftoken=" + csrf_token + ";"))
    return handle_json(request)
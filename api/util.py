import json
import api.errors as errors
import urllib.parse
import urllib3


urllib3.disable_warnings()
MAGIC_USER_AGENT = "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"


class Queries:
    def init(self):
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
    text = content.decode("utf-8", "ignore")

    return dict(text=text, content=content)


def handle_json(request: dict) -> dict:
    try:
        data = json.loads(request["text"])
        if "message" in data and data["message"] == "rate limited":
            raise errors.RateLimitError(
                "You are being rate limited by Instagram for this route.")
    except json.decoder.JSONDecodeError:
        raise errors.LoginRedirectionError(
            "You are being redirected to the login page. Please, create an issue and describe what happened at https://github.com/Quatrecentquatre-404/instagram-guest-api/issues/new.")
    else:
        return data


def perform_graphql(query_hash: str, variables: dict) -> dict:
    url = "https://www.instagram.com/graphql/query/?query_hash=" + \
        query_hash + "&variables=" + \
        urllib.parse.quote(json.dumps(variables).replace(' ', '').strip())
    request = http_get(url)
    return handle_json(request)

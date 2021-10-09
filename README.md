# Instagram Guest API
This API is unofficial. It allows you to interact with many things that your browser displays such as likes, followers, biography, websites, comments, and more. The goal is to access these data without haivng to login.

# Example
```python
import api.core


def get_lanarhoades():
    data = api.core.fetch_user("lanarhoades")
    profile = data["graphql"]["user"]

    # All ``profile`` dict keys and values are showcased in outputs/user.sample.json
    print("Username : " + profile["username"])
    print("Biography : " + profile["biography"])
    print("Followed by %d people, following %d people." % (profile["edge_followed_by"]["count"], profile["edge_follow"]["count"]))


def get_lanarhoades_home_feed():
    queries = api.core.fetch_queries_hash()
    data = api.core.fetch_home_feed(queries.QUERY_ID, "3312648204", first=1)
    last_feed = data["data"]["user"]["edge_owner_to_timeline_media"]["edges"][0]["node"]

    # All ``last_feed`` dict keys and values are showcased in outputs/home_feed.sample.json
    source_url = last_feed["display_resources"][0]["src"]
    if last_feed["is_video"]:
        source_url = last_feed["video_url"]

    print("Source URL : " + source_url)
    print("%d people liked it." % (last_feed["edge_media_preview_like"]["count"]))


def main():
    print("USER :")
    get_lanarhoades()
    print("\nLAST FEED FROM IT'S HOMEPAGE :")
    get_lanarhoades_home_feed()


if __name__ == "__main__":
    main()

```

Output :
<img src="./assets/Lana RHOADES example with home page feed and user.png" alt="Lana RHOADES example with home page feed and user">
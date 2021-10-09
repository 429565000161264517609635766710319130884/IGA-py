# Instagram Guest API
This API is unofficial. It allows you to interact with many things that your browser displays such as likes, followers, biography, websites, comments, and more. The goal is to access these data without haivng to login.

# Example
```python
import api.core


def main():
    data = api.core.fetch_user("lanarhoades")
    profile = data["graphql"]["user"]

    # All ``profile`` dict keys and values are showcased in outputs/user.sample.json
    print("Username : " + profile["username"])
    print("Biography : " + profile["biography"])
    print("Followed by %d people, following %d people." % (profile["edge_followed_by"]["count"], profile["edge_follow"]["count"]))


if __name__ == "__main__":
    main()

```
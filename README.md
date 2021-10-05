# Instagram Guest API
This API is unofficial. It allows you to interact with many things that your browser displays such as likes, followers, biography, websites, comments, and more. The goal is to access these data without haivng to login.

# Example
```python
import api.core

def main():
    csrf_token = api.core.fetch_csrf_token()

    user = api.core.fetch_user("drake", csrf_token)

    print("The user %s follows %d people and is followed by %d people. It's biography is : %s" % (user.username, user.following_count, user.followers_count, user.biography))


main()
```
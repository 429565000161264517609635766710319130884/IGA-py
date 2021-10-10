# Instagram Guest API
This API is unofficial. It allows you to interact with many things that your browser displays such as likes, followers, biography, websites, comments, and more. The goal is to access these data without haivng to login.

# Installation
Setup :
```bash
git clone https://github.com/quatrecentquatre-404/instagram-guest-api.git
cd instagram-guest-api
chmod +x ./build.bash
./build.bash
```

# Example
```python
import instagram_guest_api as Instagram


def main():
    target = "github"
    user = Instagram.fetch_user(target)["graphql"]["user"]
    print("The %s biography is '%s'." % (target, user["biography"].replace('\n', '\\n')))
    print("It follows %d people and is followed by %d people." % (user["edge_followed_by"]["count"], user["edge_follow"]["count"]))
    print("Also, this account %s a business one." % ("is" if user["is_business_account"] else "is not"))
    print("Finally, this account %s verified." % ("is" if user["is_verified"] else "is not"))


if __name__ == "__main__":
    main()

```

Output :
<img src="./assets/example.png" alt="GitHub example">
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

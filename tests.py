import api.core
import json
import os


def write_output(output_name: str, data: dict):
    with open(os.path.join("outputs", output_name + ".json"), "w+") as stream:
        stream.write(json.dumps(data))
    stream.close()


def main():
    data = api.core.fetch_user("lanarhoades")
    profile = data["graphql"]["user"]

    # All ``profile`` dict keys and values are showcased in outputs/user.sample.json
    print("Username : " + profile["username"])
    print("Biography : " + profile["biography"])
    print("Followed by %d people, following %d people." % (profile["edge_followed_by"]["count"], profile["edge_follow"]["count"]))


if __name__ == "__main__":
    main()

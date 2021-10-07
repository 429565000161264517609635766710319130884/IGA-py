import api.core
import json
import os


def write_output(output_name: str, data: dict):
    with open(os.path.join("outputs", output_name + ".json"), "w+") as stream:
        stream.write(json.dumps(data))
    stream.close()


def main():
    csrf_token = api.core.fetch_csrf_token()

    # THE USER DICT OBJECT CAN BE SEE IN outputs/user.sample.json
    data = api.core.fetch_user("drake", csrf_token)
    profile = data["graphql"]["user"]
    print("Username : %s\nBiography : %s" % (profile["username"], profile["biography"]))

main()

import api.core
import json
import os


global QUERIES
QUERIES = api.core.fetch_queries_hash()


def write_output(output_name: str, data: dict):
    with open(os.path.join("types", output_name + ".json"), "w+") as stream:
        stream.write(json.dumps(data))
    stream.close()


def getLanaRhoadesUser():
    """ All ``profile`` dict keys and values are showcased in ``types/user.json`` """

    data = api.core.fetch_user("lanarhoades")
    profile = data["graphql"]["user"]

    print("Username : " + profile["username"])
    print("Biography : " + profile["biography"])
    print("Followed by %d people, following %d people." % (profile["edge_followed_by"]["count"], profile["edge_follow"]["count"]))


def getLanaRhoadesLastPost():
    """ All ``post`` dict keys and values are showcased in ``types/user_posts.json`` """

    data = api.core.fetch_user_posts(QUERIES.QUERY_ID, "3312648204", first=1)
    post = data["data"]["user"]["edge_owner_to_timeline_media"]["edges"][0]["node"]

    source_url = post["display_resources"][0]["src"]
    if post["is_video"]:
        source_url = post["video_url"]

    print("Source URL : " + source_url)
    print("%d people liked it." % (post["edge_media_preview_like"]["count"]))

    return post

def getLanaRhoadesLastPostProperties(post = None):
    """ All ``properties`` dict keys and values are showcased in ``types/post_properties.json`` """

    if post is None:
        post = getLanaRhoadesLastPost()

    data = api.core.fetch_post_properties(post["shortcode"])
    properties = data["graphql"]["shortcode_media"]

    comments_disabled = "Comments under this post have been disabled."
    if not properties["comments_disabled"]:
        comments_disabled = "Comments under this post are allowed."

    is_ad = "This post is an ad"
    if not properties["is_ad"]:
        is_ad = "This post is not an ad."

    print("Shortcode : " + properties["shortcode"])
    print(comments_disabled)
    print(is_ad)


def getLanaRhoadesStories():
    """ All ``stories`` dict keys and values are showcased in ``types/user_stories.json`` """

    data = api.core.fetch_user_stories(QUERIES.USER, "3312648204")
    stories = data["data"]["user"]["edge_highlight_reels"]["edges"]

    print("This user has %d saved / highlighted stories" % (len(stories)))
    for story in stories:
        print("- " + story["node"]["title"])

    return stories

def main():
    post = getLanaRhoadesLastPost()
    getLanaRhoadesLastPostProperties(post)
    getLanaRhoadesStories()

if __name__ == "__main__":
    main()

import sys

from bs4 import BeautifulSoup
from cleantext import clean
import pandas as pd
import requests


def scrape_sub(sub_name: str, posts_to_scrape: int) -> pd.DataFrame:
    """Scan reddit for posts ignoring promotions
    --------------------------------------------
    sub_name (str): sub name to scrape (without the r/)
    posts_to_scrape (int): number of posts to get.
    --------------------------------------------
    Return:
        pd.DataFrame
    """
    base_url = "https://old.reddit.com/r/"
    count = "?count="
    after = ""  # Id for building a link
    page = 0  # Current page
    cur_posts = 0
    data = {"title": [], "content": []}
    print("Now scraping: ", sub_name)
    while cur_posts < posts_to_scrape:

        url = base_url + sub_name + count + str(page) + after
        try:
            resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(resp.text, "html.parser")
            posts = soup.find_all("div", "thing")
        except:
            sys.exit("Subreddit probably does not exist :(")

        # Go inside each post and read it
        for post in posts:

            if "promoted" in post["class"]:
                continue

            post_url = post["data-url"].lower().replace("/r/" + sub_name, "")
            post_id = post["data-fullname"]

            print(base_url + sub_name + post_url)
            post_resp = requests.get(
                base_url + sub_name + post_url, headers={"User-Agent": "Mozilla/5.0"}
            )
            post_soup = BeautifulSoup(post_resp.text, "html.parser")

            post_raw = post_soup.find("div", "id-" + post_id)
            post_title = post_raw.find("a", "title")
            post_body = post_raw.find("div", "md")
            # Handling of missing data
            # Title and body is missig so skip
            if not post_body and not post_title:
                continue

            if post_title:
                post_title = post_title.text
            else:
                post_title = ""
            if post_body:
                post_body = post_body.text
            else:
                post_body = ""
            print(post_title, post_body)

            data["title"].append(
                clean(
                    post_title,
                    no_line_breaks=True,
                    no_urls=True,
                    no_emails=True,
                    no_phone_numbers=True,
                    no_numbers=True,
                    no_digits=True,
                    no_currency_symbols=True,
                    no_punct=True,
                )
            )
            data["content"].append(
                clean(
                    post_title,
                    no_line_breaks=True,
                    no_urls=True,
                    no_emails=True,
                    no_phone_numbers=True,
                    no_numbers=True,
                    no_digits=True,
                    no_currency_symbols=True,
                    no_punct=True,
                )
            )

            cur_posts += 1
            print(cur_posts, " out of ", posts_to_scrape)

            if cur_posts >= posts_to_scrape:
                break

        # Find the last post id for the links
        try:
            after = "&after=" + str(posts[-1]["data-fullname"])
        except:
            sys.exit("Something went wrong. Check our arguments")
        page += 25

    df = pd.DataFrame(data)
    return df

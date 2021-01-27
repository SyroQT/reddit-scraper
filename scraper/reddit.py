from bs4 import BeautifulSoup
from cleantext import clean
import pandas as pd
import requests


def scrape_sub(sub_name: str, words_to_scrape: int) -> pd.DataFrame:
    """Scan reddit for posts ignoring promotions
    --------------------------------------------
    sub_name (str): sub name to scrape (without the r/)
    words_to_scrape (int): number of words to get. Will be a bit higher then specified
    --------------------------------------------
    Return:
        pd.DataFrame
    """
    base_url = "https://old.reddit.com/r/"
    count = "?count="
    after = ""  # Id for building a link
    page = 0  # Current page
    cur_words = 0
    data = []
    print("Now scraping: ", sub_name)
    while cur_words <= words_to_scrape:

        url = base_url + sub_name + count + str(page) + after
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        posts = soup.find_all("div", "thing")

        # Go inside each post and read it
        for post in posts:

            if "promoted" in post["class"]:
                continue

            post_url = post["data-url"].replace("/r/" + sub_name, "")

            post_resp = requests.get(
                base_url + sub_name + post_url, headers={"User-Agent": "Mozilla/5.0"}
            )
            post_soup = BeautifulSoup(post_resp.text, "html.parser")
            # Post body could be empty
            try:
                text = post_soup.find_all("div", "usertext-body")[1].text
            except IndexError:
                continue

            data.append(
                clean(
                    text,
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
            cur_words += len(text.split(" "))

            print(cur_words, " out of ", words_to_scrape)
            if cur_words > words_to_scrape:
                break

        # Find the last post id for the links
        after = "&after=" + str(posts[-1]["data-fullname"])
        page += 25

    df = pd.DataFrame(data)
    return df


if __name__ == "__main__":
    scrape_sub("ask", 300)
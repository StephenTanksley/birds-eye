import os
import sys
import json
from playwright.async_api import async_playwright, BrowserContext
from asyncio import gather, run as async_run, Semaphore
from time import perf_counter
from datetime import datetime, timezone, date
from urllib.parse import urljoin, urlparse
from wordcloud import STOPWORDS

# import list of URLs from urls.py module
from configs.urls import urls

MAX_CONCURRENT_PAGES = 5

"""
    This module scrapes from news organizations to extract raw data from them - headlines and URLs
"""

async def fetch_html(context: BrowserContext, url: str, sem: Semaphore) -> dict[str, list[str]]:
    """Fetch all links + headline text from a single page."""
    async with sem:  # limit concurrency to only as many sources as we define in MAX_CONCURRENT_PAGES
        start_time = perf_counter()
        print(f"{datetime.now()} || [{start_time:.3f}] starting {url}")

        links = []
        seen = set()
        page = await context.new_page()
        stopwords = set(STOPWORDS)
        try:
            await page.goto(url, wait_until="domcontentloaded")

            # Collect anchor elements
            anchors = await page.locator("a").element_handles()
            for anchor in anchors:
                href = await anchor.get_attribute("href")
                text = (await anchor.inner_text()).strip()

                if not href:
                    continue

                # Normalize relative URLs
                href = urljoin(url, href)

                # We don't want to add duplicate URLs
                if href in seen:
                    continue

                # Filter out non-HTTP links
                if not href.startswith("http"):
                    continue

                # Skip empty or non-informative link text
                if not text:
                    continue

                if len(text.split(" ")) < 8:
                    continue

                if '.mp3' in text or '.mp3' in href:
                    continue

                if 'a4b6' in href:
                    continue

                # Filtering conditions - If the URL ends with a trailing slash, get rid of the slash
                if href[-1] == '/':
                    href = href.rstrip('/')

                if href.endswith('.html'):
                    href = href.rstrip('.html')

                # Filtering conditions - If the URL ends with numbers, strip the numbers out
                if href[-1].isnumeric():
                    href = href.rsplit('/')[-2]

                keywords = urlparse(href).path
                keywords = keywords.rsplit("/", maxsplit=1)[-1]
                # keywords = [word for word in keywords.split('-') if word.isalpha() and word not in stopwords]
                keywords = [word for word in keywords.split('-') if word not in stopwords]

                if len(keywords) < 4:
                    continue

                # Add items - Add the url to seen and then the full object to links
                seen.add(href)
                links.append({
                    "url": href,
                    # "headline": text,
                    "timestamp": str(datetime.now(timezone.utc)),
                    "keywords": keywords
                })

            end_time = perf_counter()
            print(f"{datetime.now()} || [{end_time:.3f}] finished {url} with {len(links)} links in {end_time - start_time:.2f}s")

        except Exception as e:
            print(f"Error fetching {url}: {e}")
        finally:
            await page.close()

        return {url: links}


async def main(outlet_urls: list[str] = None, results_dict: dict = None) -> None:
    """
    Fetch all inks
    :param outlet_urls:
    :param results_dict:
    :return: No return, but an update of a global state object which will be written to a versioned JSON file
    """

    start_time = perf_counter()
    sem = Semaphore(MAX_CONCURRENT_PAGES)

    async with async_playwright() as async_plwr:
        browser = await async_plwr.firefox.launch(headless=True)
        context = await browser.new_context()

        tasks = [fetch_html(context, url, sem) for url in urls]
        all_results = await gather(*tasks)

        await browser.close()

    # Display a summary of results
    # for site, links in zip(urls, all_results):
    #     if site not in results_dict:
    #         results_dict[site] = links

        for item in all_results:
            for site, links in item.items():
                if site not in results_dict:
                    results_dict[site] = links

        print(f"{datetime.now()} || \n {site}: {len(links)} valid links found")
        for link in links:
            print(f"  - {link['url']}")

    total_time = perf_counter() - start_time
    print(f"{datetime.now()} || \nTotal execution time: {total_time:.2f}s")


if __name__ == "__main__":
    working_dir = os.getcwd().rsplit(sep='/', maxsplit=1)[0]
    data_dir = os.listdir(os.path.join(working_dir, 'data'))
    if f"{date.today()}.json" not in data_dir:
        print(f"{datetime.now()} || No URLs detected for current date, adding now")
        results = {} # This gets passed in to main
        async_run(main(outlet_urls=urls, results_dict=results))

        new_json_file = os.path.join(working_dir, 'data', f"{date.today()}.json")

        with open(new_json_file, "w+") as file:
            json.dump(results, file)
    else:
        print(f"{datetime.now()} || Current headlines found, closing")

# URL classifiers - Turns out a lot of the internet is built on WordPress and the keywords are built into the URLs themselves.
#   I could just scrape URLs and get relevant keywords from that.
# GPT4 - Does pretty well off of URLs, not quite free. I could use this to get subjects the overall vibe from the things in the URL itself.
# Figure out a way of approaching subject "stickiness" in news and how it persists over time. Maybe a SCD2 table which tracks top subjects.
# Take a look at implementing a clustering algorithm which will take (Combination of NLP and graph theory) - connected components in David's book is worth another read.
# Take a look at GraphRAG and how it relates to my problem space.

# David makes a distinction between short term, long term memory and a "simulation" capability. Simulation in this case being the idea to "imagine"
# Check out Cogni and knowledge graphs. How can I use a knowledge graph to get accurate information?

# https://github.com/itsgorain/100DaysOfNLP/blob/master/twitter_trump_hostile_clf_interpretable_extreme.ipynb
# https://github.com/itsgorain/100DaysOfNLP/blob/master/nlp_different_authors.ipynb

# It would be super cool to see how this plays out over time.

# https://www.artiba.org/blog/named-entity-recognition-in-nltk-a-practical-guide
# https://towardsdatascience.com/nlp-topic-modeling-to-identify-clusters-ca207244d04f/

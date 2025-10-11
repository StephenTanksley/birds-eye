import os
import json
from playwright.async_api import async_playwright, BrowserContext
from asyncio import gather, run as async_run, Semaphore
from time import perf_counter
from datetime import datetime, timezone, date
from urllib.parse import urljoin

# import list of URLs from urls.py module
from configs.urls import urls

MAX_CONCURRENT_PAGES = 5

"""
    This module scrapes from news organizations to extract raw data from them - headlines and URLs
"""

async def fetch_html(context: BrowserContext, url: str, sem: Semaphore) -> list[dict[str, str]]:
    """Fetch all links + headline text from a single page."""
    async with sem:  # limit concurrency to only as many sources as we define in MAX_CONCURRENT_PAGES
        start_time = perf_counter()
        print(f"{datetime.now()} || [{start_time:.3f}] starting {url}")

        links = []

        page = await context.new_page()
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

                # Filter out non-HTTP links
                if not href.startswith("http"):
                    continue

                # Skip empty or non-informative link text
                if not text:
                    continue

                links.append({
                    "url": href,
                    "headline": text,
                    "timestamp": str(datetime.now(timezone.utc))
                })

            end_time = perf_counter()
            print(f"{datetime.now()} || [{end_time:.3f}] finished {url} with {len(links)} links in {end_time - start_time:.2f}s")

        except Exception as e:
            print(f"⚠️ Error fetching {url}: {e}")
        finally:
            await page.close()

        return links




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
    for site, links in zip(urls, all_results):
        if site not in results_dict:
            results_dict[site] = links

        print(f"{datetime.now()} || \n🔗 {site}: {len(links)} valid links found")
        for l in links[:5]:  # print a few sample links per site
            print(f"  - {l['headline'][:60]} → {l['url']}")

    total_time = perf_counter() - start_time
    print(f"{datetime.now()} || \nTotal execution time: {total_time:.2f}s")


if __name__ == "__main__":
    if f"{date.today()}.json" not in os.listdir("../data/"):
        print(f"{datetime.now()} || No headlines detected for current date, adding now")
        results = {} # This gets passed in to main
        async_run(main(outlet_urls=urls, results_dict=results))

        with open(f"../data/{date.today()}.json", "w+") as file:
            json.dump(results, file)
    else:
        print(f"{datetime.now()} || Current headlines found, closing")

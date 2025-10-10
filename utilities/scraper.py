import os
import json
from playwright.async_api import async_playwright, BrowserContext
from asyncio import gather, run as async_run, Semaphore
from time import perf_counter
from datetime import datetime, timezone, date
from urllib.parse import urljoin

MAX_CONCURRENT_PAGES = 5

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




async def main(results_dict: dict) -> None:
    """
    Fetch all inks
    :param results_dict:
    :return: No return, but an update of a global state object which will be written to a versioned JSON file
    """
    url_list = [
        "https://www.npr.org",
        "https://www.foxnews.com",
        "https://www.nytimes.com"
    ]

    start_time = perf_counter()
    sem = Semaphore(MAX_CONCURRENT_PAGES)

    async with async_playwright() as async_plwr:
        browser = await async_plwr.firefox.launch(headless=True)
        context = await browser.new_context()

        tasks = [fetch_html(context, url, sem) for url in url_list]
        all_results = await gather(*tasks)

        await browser.close()

    # Display a summary of results
    for site, links in zip(url_list, all_results):
        if site not in results_dict:
            results_dict[site] = links

        print(f"{datetime.now()} || \n🔗 {site}: {len(links)} valid links found")
        for l in links[:5]:  # print a few sample links per site
            print(f"  - {l['headline'][:60]} → {l['url']}")

    total_time = perf_counter() - start_time
    print(f"{datetime.now()} || \nTotal execution time: {total_time:.2f}s")


if __name__ == "__main__":
    if f"{datetime.now()} || headline_data_{date.today()}.json" not in os.listdir("../data/"):
        print("No headlines detected for current date, adding now")
        results = {} # This gets passed in to main
        async_run(main(results_dict=results))

        with open(f"../data/headline_data_{date.today()}.json", "w+") as file:
            json.dump(results, file)
    else:
        print(f"{datetime.now()} || Current headlines found, closing")


# from playwright.async_api import async_playwright, BrowserContext, Locator
# from asyncio import gather, run as async_run
# from time import perf_counter
# from datetime import datetime
#
#
# raw_results = []
# refined_results = []
#
#
# async def fetch_html(context: BrowserContext, url: str) -> list[Locator]:
#     # Start the performance timer to measure the fetch duration
#     start_time = perf_counter()
#     print(f'[{start_time:.3f}] starting {url}')
#
#     # Create a new web browser context
#     web_page = await context.new_page()
#
#     # Navigate and wait until network is idle (no more than 2 connections for at least 500 ms)
#     await web_page.goto(url, wait_until='domcontentloaded')
#
#     # Print the duration of the fetch operation
#     end_time = perf_counter()
#     fetch_duration = end_time - start_time
#     print(f'[{end_time:.3f}] finished {url} in {fetch_duration:.2f}s')
#
#     # Return the HTML content
#     return await web_page.locator('a').all()
#
#
# async def main() -> None:
#     url_lst = [
#         "https://www.npr.org",
#         "https://www.foxnews.com",
#         "https://www.nytimes.com"
#     ]
#
#     # Start the performance timer to measure the total execution duration
#     start_time = perf_counter()
#
#     # Create an async Playwright instance and create a new browser context
#     async with async_playwright() as async_plwr:
#         browser = await async_plwr.firefox.launch(headless=True)
#         context = await browser.new_context()
#         tasks = [fetch_html(context, url) for url in url_lst]
#
#         all_items = await gather(*tasks)
#
#         # Close the browser
#         await browser.close()
#
#     for item in all_items:
#         raw_results.append(item)
#
#     # Print the duration of the total execution
#     total_duration = perf_counter() - start_time
#     print(f'Total execution time: {total_duration:.2f}s')
#
#
# if __name__ == '__main__':
#     async_run(main())
#
#
#
# # async def scrape_links_from_page(
# #         playwright: PlaywrightContextManager,
# #         source_url: str = "",
# #         config: str = ""
# # ) -> None:
# #     results = []
# #     firefox = playwright.firefox
# #     browser = await firefox.launch()
# #     page = await browser.new_page()
# #     await page.goto(source_url, wait_until='domcontentloaded')
# #
# #     links = [item for item in page.locator('a').all() if len(item.inner_text().split()) >= 8]
# #
# #     await browser.close()
# #
# #     return links
# #
# #
# # async def main(source_url: str = ""):
# #     async with async_playwright() as playwright:
# #         items = await scrape_links_from_page(playwright=playwright, source_url=source_url)
# #     results = [(item[0].strip(), item[-1]) for item in items if len(item[0].split()) >= 8]
# #
# #     return results
# #
# #
# # if __name__ == '__main__':
# #     sources = ["https://www.npr.org", "https://www.foxnews.com"]
# #     for source in sources:
# #         print(source)
# #         values = asyncio.run(main(source_url=source))
# #
# #         for value in values:
# #             print("\t", value)
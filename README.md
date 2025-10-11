# Bird's Eye

Bird's Eye is an attempt to integrate data engineering, Machine Learning (hereafter ML) and Natural Language Processing (hereafter NLP) to provide a 30,000 foot view of the news and cultural reflections of the day. This is not intended to be in-depth analysis - rather, Bird's Eye is intended to provide snapshots into cultural zeitgeist as evidenced by the tone of discourse in published media, blogs, social media, etc.

Here's what I imagine:

1. Navigate to the homepage of various news organizations, scrape all links to articles within subheadings
2. Write to a PostgreSQL database for each organization with the following metadata (organization, URL, timestamp) and data (headline)
3. Run aggregation jobs on all organizations, do sentiment analysis on each headline, assign it a positive/negative score.
4. Keep track of significant words which pop up across global state, use that global state to populate word cloud.
5. Find a way to visualize the word cloud. 
   - Other ideas would be to link words in the cloud to the articles which generated those impressions and to embed the metadata into a popup for each word.



PROBLEMS:

The scraping profile for each page is going to be a little bit different for every one. 
I'll probably have to create a different set of metadata in a config for each source.
The idea here will be to have a list of all sources, then use the source type to load up the appropriate config.



Step 1: Create a scraper.
# Bird's Eye

Bird's Eye is an attempt to integrate data engineering, Machine Learning (hereafter ML) and Natural Language Processing (hereafter NLP) to provide a 30,000 foot view of the news and cultural reflections of the day. This is not intended to be in-depth analysis - rather, Bird's Eye is intended to provide snapshots into cultural zeitgeist as evidenced by the tone of discourse in published media, blogs, social media, etc.

Here's what I imagine:

1. Navigate to the homepage of various news organizations, scrape all links to articles within subheadings
2. Push JSON to a Kafka topic for each organization with the following metadata (organization, URL, date) and data (headline)
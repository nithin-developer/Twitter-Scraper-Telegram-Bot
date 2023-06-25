# Twitter Scraper Telegram Bot

![Twitter Scraper Telegram Bot](bot_image.png)

The Twitter Scraper Telegram Bot is a Python-based bot developed to scrape tweets from influencers' Twitter accounts and send them via Telegram. This bot utilizes the `snscrape` library to fetch tweets and the Telegram Bot API to send the scraped tweets to specified Telegram channels or users.

## Features

- **Tweet Scraping**: The bot uses the `snscrape` library to scrape tweets from Twitter profiles of influencers.

- **Flexible Configuration**: You can easily configure the bot to scrape tweets from specific influencers, specify the number of tweets to fetch, and set the scraping frequency.

- **Telegram Integration**: The bot integrates with the Telegram Bot API to send the scraped tweets to specified Telegram channels or users.

- **Customizable Message Formatting**: You can customize the format of the message that is sent to Telegram, including the tweet content, username, timestamp, and any additional information you require.

- **Error Handling**: The bot includes error handling to ensure smooth operation and notify you in case of any issues encountered during the scraping process.

## Installation

1\. Clone the repository to your local machine:

```bash

git clone https://github.com/your-username/Twitter-Scraper-Telegram-Bot.git

```

2\. Install the required dependencies using pip:

```bash

cd Twitter-Scraper-Telegram-Bot

pip install -r requirements.txt

```

3\. Obtain Twitter API credentials:

   - Create a Twitter Developer account and create a new app to obtain the required API credentials (consumer key, consumer secret, access token, and access token secret).

   - Set these credentials in the `config.py` file.

4\. Obtain Telegram Bot API credentials:

   - Create a new bot using the BotFather on Telegram to obtain the bot token.

   - Set the bot token in the `config.py` file.

5\. Configure the scraping settings in the `config.py` file:

   - Specify the Twitter profiles of the influencers you want to scrape.

   - Set the number of tweets to fetch per scraping cycle.

   - Configure the scraping frequency (e.g., every hour, once a day).

## Usage

1\. Start the bot by running the `bot.py` script:

```bash

python bot.py

```

2\. The bot will start scraping tweets from the specified Twitter profiles according to the configured settings.

3\. The scraped tweets will be sent to the specified Telegram channels or users as per the configured settings.

Note: It is recommended to run the bot on a server or in the background to ensure continuous scraping and message delivery.

## Contributions

Contributions to the Twitter Scraper Telegram Bot are welcome! If you have any suggestions, bug reports, or feature requests, feel free to submit them as issues or create a pull request.

## License

This project is licensed under the [MIT License](LICENSE). You are free to use, modify, and distribute the code in accordance with the terms of the license.

## Acknowledgements

The Twitter Scraper Telegram Bot makes use of the following libraries:

- [snscrape](https://github.com/JustAnotherArchivist/snscrape) - A Python library for scraping social media websites (including Twitter).

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - A Python wrapper for the Telegram Bot API.

Special thanks to the developers of these libraries for their contributions.

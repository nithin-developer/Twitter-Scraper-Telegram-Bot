import json
import datetime
import threading
import pytz
import telebot
from telebot import types
import random
import snscrape.modules.twitter as sntwitter
from tqdm import tqdm
import schedule
import time

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
bot_token = '6285308929:AAFHF1mwb83XXt2MJhTzosY17d-m1nVqHMo'

# File path for storing data
enabled_groups_file = 'enabled_groups.json'
influencers_file = 'influencers.json'
templates_file = 'templates.json'
message_ids_file = 'message_ids.json'
admins_file = 'admins.json'

bot = telebot.TeleBot(bot_token)


def twitter_scraper():
    with open('influencers.json', 'r') as json_file:
        usernames = json.load(json_file)

    n_tweets = 20

    time_limit = datetime.datetime.now(
        pytz.utc) - datetime.timedelta(minutes=5)

    all_tweets_data = {}

    for username in usernames:
        tweets_data = []

        scraper = sntwitter.TwitterUserScraper(username)

        for i, tweet in tqdm(enumerate(scraper.get_items()), total=n_tweets):
            if tweet.date.replace(tzinfo=pytz.UTC) < time_limit:
                break

            data = {
                "id": tweet.id,
                "url": tweet.url,
                "username": username
            }

            tweets_data.append(data)
            if i + 1 >= n_tweets:
                break

        obj_data = {
            "tweets": tweets_data
        }

        all_tweets_data[username] = tweets_data

    with open('tweets-data.json', "w") as json_file:
        json.dump(all_tweets_data, json_file)

        # Send Tweets
    if not all_tweets_data:  # Check if no tweets are available for any username
        print("No tweets available.")
        return

    print("Preparing Tweets...........")

    with open('tweets-data.json', 'r') as file:
        data = json.load(file)

    with open('advertisement.json', 'r', encoding='utf-8-sig') as ads_file:
        ads_data = json.loads(ads_file.read())

    random_ad = random.choice(ads_data["adsList"])

    templates = load_templates()

    enabled_groups = load_enabled_groups()

    for chat_id, group_info in enabled_groups.items():
        chat_id_str = str(chat_id)
        if chat_id_str in templates:
            template_text = templates[chat_id_str]["template_text"]
        else:
            template_text = ""

        if group_info.get("enabled", False):
            ad_message = f"Ad: [{random_ad['text']}]({random_ad['link']})"

            title = "🚀 Let's Raid these new tweets\n\n"

            message = ""

            for name, profiles in data.items():
                for profile in profiles:
                    if 'id' in profile and 'username' in profile:
                        url = "https://twitter.com/intent/tweet?text=" + \
                            str(template_text) + "&in_reply_to=" + \
                            str(profile['id'])
                        username = profile['username']
                        message += f"[{username}]({url}) || "

            message = message.rstrip(" || ")

            # Empty Message
            if not message:
                print("No tweets available.")
                continue

            combined_message = title + message + '\n\n' + ad_message

            print(combined_message)

            print("Sending Tweets...........")

            send_message_with_link(chat_id, combined_message)
        else:
            print(f"Group {chat_id} is disabled. Skipping...")

    print("---------------Tweets Sent! --------------")


def load_enabled_groups():
    try:
        with open(enabled_groups_file, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_enabled_groups(enabled_groups):
    with open(enabled_groups_file, 'w') as file:
        json.dump(enabled_groups, file)


def load_influencers():
    try:
        with open(influencers_file, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_influencers(influencers):
    with open(influencers_file, 'w') as file:
        json.dump(influencers, file)


def load_templates():
    try:
        with open(templates_file, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_templates(templates):
    with open(templates_file, 'w') as file:
        json.dump(templates, file)


def load_admins():
    try:
        with open('admins.json', 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


admins = load_admins()


def load_selected_group():
    try:
        with open('selected_groups.json', 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


selected_groups = load_selected_group()


def save_admins(admins):
    with open('admins.json', 'w') as file:
        json.dump(admins, file)


def is_group_admin(message: telebot.types.Message):
    user_id = message.from_user.id
    chat_member = bot.get_chat_member(message.chat.id, user_id)
    name = chat_member.user.username
    print(name)
    if chat_member.status in ['administrator', 'creator']:
        return True

@bot.message_handler(commands=['enable'])
def enable_bot_messages(message: telebot.types.Message):

    if message.chat.type == 'private':
        username = message.from_user.username
        group = selected_groups.get(username)
        enabled_groups = load_enabled_groups()
        if group:
            group_id = group['group_id']

            if group_id in enabled_groups:
                enabled_groups[group_id]['enabled'] = True
            else:
                enabled_groups[group_id] = {
                    'name': group['group_name'],
                    'enabled': True
                }

            with open('enabled_groups.json', 'w') as file:
                json.dump(enabled_groups, file)

            bot.send_message(
                message.chat.id,
                'Bot messages enabled for the selected group.'
            )
        else:
            bot.send_message(
                message.chat.id,
                'No group selected. Use the /start command to select a group first.'
            )

    else:

        if not is_group_admin(message):
            bot.reply_to(message, "You are not an admin.")
            return

        admins = load_admins()

        chat_id = str(message.chat.id)
        admin_username = message.from_user.username
        print(chat_id)

        if admin_username not in admins:
            admins[admin_username] = {}

        if chat_id not in admins[admin_username]:
            admins[admin_username][chat_id] = {
                'group_name': message.chat.title,  # Store the group name
                'group_id': chat_id
            }
            save_admins(admins)

        chat_id = message.chat.id
        enabled_groups = load_enabled_groups()
        enabled_groups[str(chat_id)] = {
            'name': message.chat.title,  # Store the group name
            'enabled': True
        }
        save_enabled_groups(enabled_groups)
        bot.reply_to(message, "Bot messages enabled.")


@bot.message_handler(commands=['disable'])
def disable_bot_messages(message: telebot.types.Message):

    if message.chat.type == 'private':
        username = message.from_user.username
        group = selected_groups.get(username)
        enabled_groups = load_enabled_groups()
        if group:
            group_id = group['group_id']

            if group_id in enabled_groups:
                enabled_groups[group_id]['enabled'] = False
            else:
                enabled_groups[group_id] = {
                    'name': group['group_name'],
                    'enabled': False
                }

            with open('enabled_groups.json', 'w') as file:
                json.dump(enabled_groups, file)

            bot.send_message(
                message.chat.id,
                'Bot messages disabled for the selected group.'
            )
        else:
            bot.send_message(
                message.chat.id,
                'No group selected. Use the /start command to select a group first.'
            )

    else:

        if not is_group_admin(message):
            bot.reply_to(message, "You are not an admin.")
            return

        chat_id = message.chat.id
        enabled_groups = load_enabled_groups()
        enabled_groups[str(chat_id)] = {
            'name': message.chat.title,  # Store the group name
            'enabled': False
        }
        save_enabled_groups(enabled_groups)
        bot.reply_to(message, "Bot messages disabled.")


@bot.message_handler(commands=['add_influencer'])
def add_influencer(message: telebot.types.Message):

    selected_groups = load_selected_group()
    username = message.from_user.username

    if message.chat.type == 'private':
        group = selected_groups.get(username)
        if not group:
            bot.reply_to(message, "No group selected. Use the /start command to select a group first.")
            return
        chat_id = group['group_id']

        influencer_name = ' '.join(message.text.split()[1:]).strip()
        if influencer_name:
            influencers = load_influencers()
            if influencer_name in influencers:
                bot.reply_to(message, f"Influencer '{influencer_name}' already exists.")
            else:
                influencers.append(influencer_name)
                save_influencers(influencers)
                bot.reply_to(message, f"Influencer '{influencer_name}' added successfully. ✅")
        else:
            bot.reply_to(message, "Please provide the name of the influencer.")

    else:

        if not is_group_admin(message):
            bot.reply_to(message, "You are not an admin.")
            return

        influencer_name = ' '.join(message.text.split()[1:]).strip()
        if influencer_name:
            influencers = load_influencers()
            if influencer_name in influencers:
                bot.reply_to(message, f"Influencer '{influencer_name}' already exists.")
            else:
                influencers.append(influencer_name)
                save_influencers(influencers)
                bot.reply_to(message, f"Influencer '{influencer_name}' added successfully. ✅")
        else:
            bot.reply_to(message, "Please provide the name of the influencer.")


@bot.message_handler(commands=['view_influencers'])
def view_influencers(message: telebot.types.Message):

    selected_groups = load_selected_group()
    username = message.from_user.username

    if message.chat.type == 'private':
        group = selected_groups.get(username)
        if not group:
            bot.reply_to(message, "No group selected. Use the /start command to select a group first.")
            return
        chat_id = group['group_id']

        influencers = load_influencers()
        if influencers:
            influencers_list = '\n'.join(influencers)
            bot.reply_to(message, f"List of influencers:\n{influencers_list}")
        else:
            bot.reply_to(message, "No influencers found.")

    else:

        if not is_group_admin(message):
            bot.reply_to(message, "You are not an admin.")
            return

        influencers = load_influencers()
        if influencers:
            influencers_list = '\n'.join(influencers)
            bot.reply_to(message, f"List of influencers:\n{influencers_list}")
        else:
            bot.reply_to(message, "No influencers found.")


@bot.message_handler(commands=['set_template'])
def set_template(message: telebot.types.Message):

    selected_groups = load_selected_group()
    username = message.from_user.username

    if message.chat.type == 'private':
        group = selected_groups.get(username)
        if not group:
            bot.reply_to(message, "No group selected. Use the /start command to select a group first.")
            return
        chat_id = group['group_id']
        template_text = ' '.join(message.text.split()[1:])
        chat = bot.get_chat(chat_id)
        group_name = chat.title if chat.title else "Unknown Group"
        if template_text:
            templates = load_templates()
            templates[chat_id] = {
                "group_name": group_name, 
                "username": username,
                "template_text": template_text
            }
            save_templates(templates)
            bot.reply_to(message, "Template set successfully for the selected group.")
        else:
            templates = load_templates()
            templates[chat_id] = {
                "group_name": group_name, 
                "username": username,
                "template_text": ""
            }
            save_templates(templates)
            bot.reply_to(message, "Empty template set Success for the selected group!.")

    else:

        if not is_group_admin(message):
            bot.reply_to(message, "You are not an admin.")
            return

        chat_id = str(message.chat.id)
        username = message.from_user.username
        template_text = ' '.join(message.text.split()[1:])
        if template_text:
            templates = load_templates()
            templates[chat_id] = {
                "group_name": message.chat.title,    
                "username": username,
                "template_text": template_text
            }
            save_templates(templates)
            bot.reply_to(message, "Template set successfully.")
        else:
            templates = load_templates()
            templates[chat_id] = {
                "group_name": message.chat.title, 
                "username": username,
                "template_text": ""
            }
            save_templates(templates)
            bot.reply_to(message, "Empty template set Success!.")


@bot.message_handler(commands=['view_templates'])
def view_templates(message: telebot.types.Message):

    selected_groups = load_selected_group()
    username = message.from_user.username

    if message.chat.type == 'private':
        group = selected_groups.get(username)
        if not group:
            bot.reply_to(message, "No group selected. Use the /start command to select a group first.")
            return
        chat_id = group['group_id']

        templates = load_templates()
        template_data = None

        for newid, data in templates.items():
            group_name = data.get("group_name")

            if newid == chat_id or group_name == message.chat.title:
                template_data = data
                break

        if template_data:
                template_text = template_data.get("template_text")
                bot.reply_to(message, f"Template:\n{template_text}")
        else:
            bot.reply_to(message, "No template found for this group.")

    else:
        if not is_group_admin(message):
            bot.reply_to(message, "You are not an admin.")
            return

        username = message.from_user.username
        chat_id = str(message.chat.id)
        print(chat_id)
        templates = load_templates()
        template_data = None

        for newid, data in templates.items():
            group_name = data.get("group_name")

            if newid == chat_id or group_name == message.chat.title:
                template_data = data
                break

        if template_data:
                template_text = template_data.get("template_text")
                bot.reply_to(message, f"Template:\n{template_text}")
        else:
            bot.reply_to(message, "No template found for this group.")


def send_message_with_link(chat_id, message):

    message_id = get_saved_message_id(chat_id)

    if message_id:
        # Delete the previous message
        bot.delete_message(chat_id, message_id)

    # Send the new message
    sent_message = bot.send_message(
        chat_id, message, parse_mode='Markdown', disable_web_page_preview=True)

    # Retrieve the message ID
    message_id = sent_message.message_id

    # Save the message ID for future use
    save_message_id(chat_id, message_id)

    return message_id


def delete_previous_message(chat_id):
    # Retrieve the saved message ID
    message_id = get_saved_message_id(chat_id)

    if message_id:
        # Delete the previous message
        bot.delete_message(chat_id, message_id)


def save_message_id(chat_id, message_id):
    # Load the existing message IDs from JSON
    message_ids = load_message_ids()

    # Update the message ID for the chat ID
    message_ids[str(chat_id)] = message_id

    # Save the updated message IDs to JSON
    save_message_ids(message_ids)


def get_saved_message_id(chat_id):
    # Load the existing message IDs from JSON
    message_ids = load_message_ids()

    # Retrieve the message ID for the chat ID
    return message_ids.get(str(chat_id))


def load_message_ids():
    try:
        with open(message_ids_file, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_message_ids(message_ids):
    with open(message_ids_file, 'w') as file:
        json.dump(message_ids, file)


# Function to run the Twitter scraper repeatedly
def run_twitter_scraper():
    schedule.every(5).minutes.do(twitter_scraper)
    while True:
        schedule.run_pending()
        time.sleep(1)

# Handle the '/start' command


@bot.message_handler(commands=['start'])
def handle_start_command(message):
    username = message.from_user.username
    if message.chat.type == 'private':
        if username in admins:
            admin_details = admins[username]

            # Create a keyboard markup to display the available groups
            markup = telebot.types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)

            for group_id, group_details in admin_details.items():
                if group_id != 'group_name' and group_id != 'group_id':
                    group_name = group_details['group_name']
                    markup.add(telebot.types.KeyboardButton(group_name))

            bot.send_message(
                message.chat.id,
                'Select a group:',
                reply_markup=markup
            )
        else:
            bot.send_message(
                message.chat.id,
                'You are not authorized to use this bot.'
            )
# Handle group selection


@bot.message_handler(func=lambda message: message.chat.type == 'private')
def handle_group_selection(message):
    username = message.from_user.username
    selected_group_name = message.text

    if username in admins:
        admin_groups = admins[username]

        selected_group = None
        for group_id, group_details in admin_groups.items():
            if group_details['group_name'] == selected_group_name:
                selected_group = {
                    'group_name': group_details['group_name'],
                    'group_id': group_id
                }
                break

        if selected_group:
            selected_groups[username] = selected_group

            with open('selected_groups.json', 'w') as file:
                json.dump(selected_groups, file)

            bot.send_message(
                message.chat.id,
                f'Success! Selected group: {selected_group["group_name"]}'
            )
        else:
            bot.send_message(
                message.chat.id,
                'Invalid group selection.'
            )
    else:
        bot.send_message(
            message.chat.id,
            'You are not authorized to use this bot.'
        )


# Create a thread for running the Twitter scraper
twitter_thread = threading.Thread(target=run_twitter_scraper)
twitter_thread.start()

bot.polling(none_stop=True, timeout=123)

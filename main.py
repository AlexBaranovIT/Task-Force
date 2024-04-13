import openai
import telebot
import os
import base64
import schedule
import time
import threading
import yfinance as yf
import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend
import matplotlib.pyplot as plt
import io
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import dateutil.parser
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import requests
import html
import re
import urllib.parse
import random
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from keepalive import keep_alive
from openai import OpenAI

TOKEN = 'YOUR_TELEGRAM_API' # From @BotFather in Telegram 
api_key = 'YOUR_API' # From openai.com
client = OpenAI(api_key=api_key)
NEWS_API_KEY = 'YOUR_NEWS_API' # From https://newsapi.org
open_weather_token = 'YOUR_WEATHER_API' # From https://openweathermap.org/api

bot = telebot.TeleBot(TOKEN)

# State management
user_state = {}

# User stock preferences
user_stocks = {}

# Temperature reminders
temp_reminders = {}

# List of users subscribed for the interesting facts
subscribed_users_for_facts = set()

user_tasks = {}

user_editing_state = {}

subscribed_users_for_quotes = set()

keep_alive()

interesting_facts = [
    "Honey never spoils. Archaeologists have found pots of honey in 3,000-year-old Egyptian tombs that are still good to eat.",
    "A single cloud can weigh more than 1 million pounds.",
    "A human could swim through the blood vessels of a blue whale.",
    "Cows have best friends and become stressed if they are separated.",
    "Octopuses have three hearts and their blood is blue.",
    "The Eiffel Tower can be 15 cm taller during the summer due to the expansion of the iron on hot days.",
    "A group of flamingos is called a 'flamboyance'.",
    "Bananas are berries, but strawberries aren't.",
    "There are more possible iterations of a game of chess than there are atoms in the known universe.",
    "A day on Venus is longer than a year on Venus. It takes longer to rotate on its axis than it does to orbit the sun.",
    "Humans share 50% of their DNA with bananas.",
    "A single lightning bolt has enough energy to toast 100,000 slices of bread.",
    "The shortest war in history was between Britain and Zanzibar on August 27, 1896. Zanzibar surrendered after 38 minutes.",
    "The inventor of the frisbee was turned into a frisbee after he died.",
    "Polar bear fur is actually transparent, not white. It appears white because it reflects visible light.",
    "The heart of a blue whale is so large that a human can swim through the arteries.",
    "An octopus has nine brains - one central brain and eight in each of its arms.",
    "A group of crows is known as a murder.",
    "Butterflies taste with their feet.",
    "The tongue of a blue whale weighs as much as an adult elephant.",
    "Snails can sleep for up to three years.",
    "The first computer virus was created in 1986 and was called Brain.",
    "A cat has 32 muscles in each ear.",
    "A crocodile cannot stick out its tongue.",
    "A shrimp's heart is in its head.",
    "In Ancient Rome, when a man testified in court he would swear on his testicles.",
    "It is impossible for most people to lick their own elbow. (Try it!)",
    "A rhinoceros' horn is made of hair.",
    "It is physically impossible for pigs to look up into the sky.",
    "The 'dot' over the letter 'i' is called a tittle.",
    "A duck's quack doesn't echo, and no one knows why.",
    "Each king in a deck of playing cards represents a great king from history.",
    "Elephants are the only animals that can't jump.",
    "Women blink nearly twice as much as men.",
    "It's impossible to sneeze with your eyes open.",
    "The main library at Indiana University sinks over an inch every year because when it was built, engineers failed to take into account the weight of all the books that would occupy the building.",
    "A snail can sleep for three years.",
    "No word in the English language rhymes with 'MONTH'.",
    "Our eyes are always the same size from birth, but our nose and ears never stop growing.",
    "The electric chair was invented by a dentist.",
    "All polar bears are left-handed.",
    "In France, it is legal to marry a dead person.",
    "The shortest complete sentence in the English language is 'Go.'",
    "A group of frogs is called an army.",
    "The average person walks the equivalent of five times around the world in a lifetime.",
    "The Bible is the most shoplifted book in the world.",
    "In 1386, a pig in France was executed by public hanging for the murder of a child.",
    "A cockroach can live several weeks with its head cut off.",
    "The total weight of all the ants on Earth is about the same as the weight of all the humans on the planet.",
    "A sneeze travels about 100 miles per hour.",
    "Earth is the only planet not named after a god.",
    "It's against the law to burp, or sneeze in a church in Nebraska, USA.",
    "Some worms will eat themselves if they can't find any food.",
    "Dolphins sleep with one eye open.",
    "It is illegal to climb trees in Oshawa, a town in Ontario, Canada.",
    "The shortest war in history was between Britain and Zanzibar on August 27, 1896; Zanzibar surrendered after 38 minutes.",
    "A jiffy is an actual unit of time for 1/100th of a second.",
    "Leonardo Da Vinci invented scissors.",
    "Minus 40 degrees Celsius is exactly the same as minus 40 degrees Fahrenheit.",
    "The word 'set' has more definitions than any other word in English.",
    "A 'jiffy' is an actual unit of time: 1/100th of a second.",
    "One quarter of the bones in your body are in your feet.",
    "The average human dream lasts only 2 to 3 seconds.",
    "The first alarm clock could only ring at 4 a.m.",
    "Birds don't urinate.",
    "The most common name in the world is Mohammed.",
    "The strongest muscle in the body is the tongue.",
    "Ants never sleep.",
    "Cats have over one hundred vocal sounds, while dogs only have about ten.",
    "The longest one-syllable word in the English language is 'screeched.'",
    "All the clocks in the movie 'Pulp Fiction' are stuck on 4:20.",
    "No piece of square dry paper can be folded in half more than 7 times.",
    "The giant squid has the largest eyes in the world.",
    "In England, the Speaker of the House is not allowed to speak.",
    "The microwave was invented after a researcher walked by a radar tube and a chocolate bar melted in his pocket.",
    "The average person falls asleep in seven minutes.",
    "There are 336 dimples on a regulation golf ball.",
    "The average human eats 8 spiders in their lifetime at night.",
    "A bear has 42 teeth.",
    "An ostrich's eye is bigger than its brain.",
    "Lemons contain more sugar than strawberries.",
    "The longest recorded flight of a chicken is 13 seconds.",
    "Slugs have four noses.",
    "Olympic gold medals are actually made mostly of silver.",
    "Honey is the only natural food that never spoils.",
    "Months that begin on a Sunday will always have a 'Friday the 13th.'",
    "Coca-Cola was originally green.",
    "The first owner of the Marlboro Company died of lung cancer.",
    "Walt Disney was afraid of mice.",
    "Pearls melt in vinegar.",
    "The three most valuable brand names on earth are Marlboro, Coca-Cola, and Budweiser, in that order.",
    "It is possible to lead a cow upstairs but not downstairs.",
    "The first product to have a barcode was Wrigley’s gum.",
    "Venus is the only planet that rotates clockwise.",
    "The strongest animal in the world is the dung beetle.",
    "One in every five adults believes that aliens are hiding in our planet disguised as humans.",
    "You cannot hum while holding your nose closed.",
    "The total length of your circulatory system stretches an astonishing 60,000 miles.",
    "Bananas are curved because they grow towards the sun.",
    "Billy goats urinate on their own heads to smell more attractive to females.",
    "The inventor of the Pringles can is now buried in one.",
    "In 2015, more people were killed from injuries caused by taking a selfie than by shark attacks.",
    "The chances of you dying on the way to get lottery tickets is actually greater than your chances of winning.",
    "Cherophobia is the irrational fear of fun or happiness.",
    "If you lift a kangaroo’s tail off the ground, it can’t hop.",
    "Hippopotamus milk is pink.",
    "Movie trailers were originally shown after the movie, which is why they were called 'trailers'.",
    "The top six foods that make you fart are beans, corn, bell peppers, cauliflower, cabbage, and milk.",
    "There’s a species of spider called the Hobo Spider.",
    "A baby spider is called a spiderling.",
    "You cannot snore and dream at the same time.",
    "The following can be read forward and backwards: Do geese see God?",
    "A baby octopus is about the size of a flea when it is born.",
    "A sheep, a duck, and a rooster were the first passengers in a hot air balloon.",
    "In Uganda, 50% of the population is under 15 years of age.",
    "Hitler’s mother considered abortion but the doctor persuaded her to keep the baby.",
    "Arab women can initiate a divorce if their husbands don’t pour coffee for them.",
    "Recycling one glass jar saves enough energy to watch TV for 3 hours.",
    "Smearing a small amount of dog feces on an insect bite will relieve the itching and swelling.",
    "Catfish are the only animals that naturally have an odd number of whiskers.",
    "Facebook, Skype, and Twitter are all banned in China.",
    "95% of people text things they could never say in person.",
    "The Titanic was the first ship to use the SOS signal.",
    "In Poole, England, you can be fined up to $1000 for failing to pick up dog poop.",
    "About 8,000 Americans are injured by musical instruments each year.",
    "The French language has seventeen different words for 'surrender'.",
    "Nearly three percent of the ice in Antarctic glaciers is penguin urine.",
    "Bob Dylan’s real name is Robert Zimmerman.",
    "A crocodile can’t poke its tongue out.",
    "Sea otters hold hands when they sleep to keep from drifting apart.",
    "When hippos are upset, their sweat turns red.",
    "The first alarm clock could only ring at 4 am.",
    "Birds don’t urinate.",
    "Dying is illegal in the Houses of Parliaments.",
    "The most venomous jellyfish in the world is the Irukandji.",
    "The 20th of March is Snowman Burning Day.",
    "An eagle can kill a young deer and fly away with it.",
    "In the Caribbean there are oysters that can climb trees.",
    "Worms eat their own poo.",
    "Squirrels forget where they hide about half of their nuts.",
    "Millions of trees are accidentally planted by squirrels who bury nuts and then forget where they hid them.",
    "Elvis Presley’s manager sold 'I Hate Elvis' badges as a way to make money from people who weren’t Elvis fans.",
]

company_to_ticker = {
    'APPLE': 'AAPL',
    'MICROSOFT': 'MSFT',
    'GOOGLE': 'GOOGL',
    'AMAZON': 'AMZN',
    'FACEBOOK': 'FB',
    'TESLA': 'TSLA',
    'NETFLIX': 'NFLX',
    'ALIBABA': 'BABA',
    'BERKSHIRE HATHAWAY': 'BRK.A',
    'JOHNSON & JOHNSON': 'JNJ',
    'JPMORGAN CHASE': 'JPM',
    'EXXON MOBIL': 'XOM',
    'VISA': 'V',
    'WALMART': 'WMT',
    'BANK OF AMERICA': 'BAC',
    'PROCTER & GAMBLE': 'PG',
    'MASTERCARD': 'MA',
    'DISNEY': 'DIS',
    'CISCO': 'CSCO',
    'VERIZON': 'VZ',
    'CHEVRON': 'CVX',
    'COCA-COLA': 'KO',
    'INTEL': 'INTC',
    'HOME DEPOT': 'HD',
    'PFIZER': 'PFE',
    'PEPSICO': 'PEP',
    'MCDONALD\'S': 'MCD',
    '3M': 'MMM',
    'IBM': 'IBM',
    'NIKE': 'NKE',
    'MERCK': 'MRK',
    'GOLDMAN SACHS': 'GS',
    'BOEING': 'BA',
    'AMERICAN EXPRESS': 'AXP',
    'AT&T': 'T',
    'STARBUCKS': 'SBUX',
    'ORACLE': 'ORCL',
    'UNITEDHEALTH': 'UNH',
    'CITIGROUP': 'C',
    'GENERAL ELECTRIC': 'GE',
    'MORGAN STANLEY': 'MS',
    'QUALCOMM': 'QCOM',
    'FORD': 'F',
    'ABBOTT LABORATORIES': 'ABT',
    'GENERAL MOTORS': 'GM',
    'AIG': 'AIG',
    'DELL': 'DELL',
    'CATERPILLAR': 'CAT',
    'DU PONT': 'DD',
    'TARGET': 'TGT',
    'TIME WARNER': 'TWX',
    'METLIFE': 'MET',
    'LOCKHEED MARTIN': 'LMT',
    'AMERICAN AIRLINES': 'AAL',
    'DELTA AIR LINES': 'DAL',
    'SOUTHWEST AIRLINES': 'LUV',
    'GILEAD SCIENCES': 'GILD',
    'RAYTHEON': 'RTN',
    'HONEYWELL': 'HON',
    'COLGATE-PALMOLIVE': 'CL',
    'TEXAS INSTRUMENTS': 'TXN',
    'MARRIOTT': 'MAR',
    'MONDELEZ': 'MDLZ',
    'CONOCOPHILLIPS': 'COP',
    'FEDEX': 'FDX',
    'SCHLUMBERGER': 'SLB',
    'SYMANTEC': 'SYMC',
    'NORTHROP GRUMMAN': 'NOC',
    'DOW CHEMICAL': 'DOW',
    'PHILIP MORRIS': 'PM',
    'BRISTOL-MYERS SQUIBB': 'BMY',
    'GOLDMAN SACHS GROUP': 'GS',
    'HALLIBURTON': 'HAL',
    'KRAFT HEINZ': 'KHC',
    'BLACKROCK': 'BLK',
    'AMGEN': 'AMGN',
    'FREEPORT-MCMORAN': 'FCX',
    'GENERAL DYNAMICS': 'GD',
    'HERSHEY': 'HSY',
    'ALTRIA GROUP': 'MO',
    'AMERICAN TOWER': 'AMT',
    'CUMMINS': 'CMI',
    'DUKE ENERGY': 'DUK',
    'EQUINIX': 'EQIX',
    'EXELON': 'EXC',
    'HUMANA': 'HUM',
    'INTUIT': 'INTU',
    'KIMBERLY-CLARK': 'KMB',
    'KROGER': 'KR',
    'LOWE\'S': 'LOW',
    'MARATHON PETROLEUM': 'MPC',
    'NEXTERA ENERGY': 'NEE'
}

inspirational_quotes = [
    "Believe you can and you're halfway there. – Theodore Roosevelt",
    "The only way to do great work is to love what you do. – Steve Jobs",
    "Success is not final, failure is not fatal: It is the courage to continue that counts. – Winston Churchill",
    "Your time is limited, don't waste it living someone else's life. – Steve Jobs",
    "You miss 100% of the shots you don't take. – Wayne Gretzky",
    "Strive not to be a success, but rather to be of value. – Albert Einstein",
    "I am not a product of my circumstances. I am a product of my decisions. – Stephen Covey",
    "Life is what happens when you're busy making other plans. – John Lennon",
    "The best revenge is massive success. – Frank Sinatra",
    "The mind is everything. What you think you become. – Buddha",
    "The best time to plant a tree was 20 years ago. The second best time is now. – Chinese Proverb",
    "An unexamined life is not worth living. – Socrates",
    "Eighty percent of success is showing up. – Woody Allen",
    "Your life only gets better when you get better. – Brian Tracy",
    "Change your thoughts and you change your world. – Norman Vincent Peale",
    "The only person you are destined to become is the person you decide to be. – Ralph Waldo Emerson",
    "Go confidently in the direction of your dreams! Live the life you've imagined. – Henry David Thoreau",
    "Life shrinks or expands in proportion to one's courage. – Anaïs Nin",
    "Believe you can and you're halfway there. – Theodore Roosevelt",
    "The only limit to our realization of tomorrow will be our doubts of today. – Franklin D. Roosevelt",
    "Do what you can, with what you have, where you are. – Theodore Roosevelt",
    "Everything you've ever wanted is on the other side of fear. – George Addair",
    "Success is going from failure to failure without losing your enthusiasm. – Winston Churchill",
    "It does not matter how slowly you go as long as you do not stop. – Confucius",
    "The best way to predict the future is to invent it. – Alan Kay",
    "Don’t watch the clock; do what it does. Keep going. – Sam Levenson",
    "A dream doesn't become reality through magic; it takes sweat, determination, and hard work. – Colin Powell",
    "It's not whether you get knocked down, it's whether you get up. – Vince Lombardi",
    "The only place where success comes before work is in the dictionary. – Vidal Sassoon",
    "The way to get started is to quit talking and begin doing. – Walt Disney",
    "The road to success and the road to failure are almost exactly the same. – Colin R. Davis",
    "Life is 10% what happens to us and 90% how we react to it. – Charles R. Swindoll",
    "Do not wait to strike till the iron is hot; but make it hot by striking. – William Butler Yeats",
    "Whether you think you can or think you can’t, you’re right. – Henry Ford",
    "The most common way people give up their power is by thinking they don’t have any. – Alice Walker",
    "The most difficult thing is the decision to act, the rest is merely tenacity. – Amelia Earhart",
    "You become what you believe. – Oprah Winfrey",
    "Dream big and dare to fail. – Norman Vaughan",
    "You must be the change you wish to see in the world. – Mahatma Gandhi",
    "What you do speaks so loudly that I cannot hear what you say. – Ralph Waldo Emerson",
    "There is only one way to avoid criticism: do nothing, say nothing, and be nothing. – Aristotle",
    "Ask and it will be given to you; search, and you will find; knock and the door will be opened for you. – Jesus",
    "The only person you should try to be better than is the person you were yesterday. – Unknown",
    "Everything has beauty, but not everyone can see. – Confucius",
    "How wonderful it is that nobody need wait a single moment before starting to improve the world. – Anne Frank",
    "When I let go of what I am, I become what I might be. – Lao Tzu",
    "Life is not measured by the number of breaths we take, but by the moments that take our breath away. – Maya Angel"]


def send_daily_quotes():
    for user_id in subscribed_users_for_quotes:
        send_quote(user_id)


def send_quote(user_id):
    quote = random.choice(inspirational_quotes)
    bot.send_message(user_id, quote)


def run_scheduler():
    schedule.every().day.at("09:00").do(send_daily_quotes)  # Set your desired time
    while True:
        schedule.run_pending()
        time.sleep(60)


def get_weather(city_name):
    encoded_city_name = urllib.parse.quote(city_name)  # URL-encode the city name
    url = f"https://api.openweathermap.org/data/2.5/weather?q={encoded_city_name}&appid={open_weather_token}&units=metric"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for unsuccessful status codes

        weather_data = response.json()
        main = weather_data['main']
        weather = weather_data['weather'][0]
        wind = weather_data['wind']
        sys = weather_data['sys']

        # Convert Unix timestamp to local time for sunrise and sunset
        sunrise_time = datetime.fromtimestamp(sys['sunrise']).strftime('%H:%M')
        sunset_time = datetime.fromtimestamp(sys['sunset']).strftime('%H:%M')

        # Emojis for weather report
        weather_emojis = {
            'Clear': '☀️',
            'Clouds': '☁️',
            'Rain': '🌧️',
            'Snow': '❄️',
            'Thunderstorm': '⛈️',
            'Drizzle': '🌦️',
            'Mist': '🌫️'
        }
        emoji = weather_emojis.get(weather['main'], '🌈')

        # Enhanced weather message with bold text and double line breaks
        return (f"<b>{emoji} Weather in {city_name} {emoji}</b>\n\n"
                f"<b>Condition:</b> {weather['main']} ({weather['description']})\n\n"
                f"<b>🌡️ Temperature:</b> {main['temp']}°C\n\n"
                f"<b>🌬️ Wind Speed:</b> {wind['speed']} m/s\n\n"
                f"<b>💧 Humidity:</b> {main['humidity']}%\n\n"
                f"<b>🔺 High:</b> {main['temp_max']}°C\n\n"
                f"<b>🔻 Low:</b> {main['temp_min']}°C\n\n"
                f"<b>Pressure:</b> {main['pressure']} hPa\n\n"
                f"<b>🌅 Sunrise:</b> {sunrise_time}\n\n"
                f"<b>🌇 Sunset:</b> {sunset_time}")
    except requests.exceptions.HTTPError as err:
        print(f"HTTP Error: {err}")
        return "Sorry, I couldn't retrieve the weather data. 🌧️"
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return "An error occurred while fetching the weather data. 🚫"


def send_daily_facts():
    for user_id in subscribed_users_for_facts:
        send_fact(user_id)


# Schedule this function to run at a specific time every day
schedule.every().day.at("09:00").do(send_daily_facts)


def remove_html_tags(text):
    """Remove html tags from a string"""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def fetch_news():
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        articles = response.json().get('articles', [])
        news_summaries = []
        for article in articles[:5]:
            title = article.get('title')
            description = article.get('description', 'No description available.')
            article_url = article.get('url', '#')

            # Ensure title and description are not None
            title = html.unescape(title) if title else "No title available"
            description = html.unescape(description) if description else "No description available"

            news_item = f"• <b>{title}</b>\n{description}\n<a href=\"{article_url}\">Read more</a>"
            news_summaries.append(news_item)
        return "\n\n".join(news_summaries)
    else:
        return "Failed to fetch news."


def handle_toggle_action(user_id, task_index, call):
    toggle_task_completion(user_id, task_index)
    bot.answer_callback_query(call.id, "Task status updated.")
    update_task_list_message(call)


def handle_delete_action(user_id, task_index, call):
    delete_task(user_id, task_index)
    bot.answer_callback_query(call.id, "Task deleted.")
    update_task_list_message(call)


def handle_edit_action(user_id, task_index, call):
    start_editing_task(call, task_index)
    bot.answer_callback_query(call.id, "Editing task. Please enter the new description.")


# Task management functions
def add_task(user_id, task):
    if user_id not in user_tasks:
        user_tasks[user_id] = []
    user_tasks[user_id].append({"task": task, "completed": False})


def delete_task(user_id, task_index):
    if user_id in user_tasks and len(user_tasks[user_id]) > task_index:
        del user_tasks[user_id][task_index]


def toggle_task_completion(user_id, task_index):
    if user_id in user_tasks and len(user_tasks[user_id]) > task_index:
        user_tasks[user_id][task_index]["completed"] = not user_tasks[user_id][task_index]["completed"]


def edit_task(user_id, task_index, new_task):
    if user_id in user_tasks and len(user_tasks[user_id]) > task_index:
        user_tasks[user_id][task_index]["task"] = new_task


# Inline keyboard generation for tasks
def generate_task_markup(user_id):
    markup = InlineKeyboardMarkup()
    if user_id in user_tasks:
        for index, task in enumerate(user_tasks[user_id]):
            task_label = f"{'✅ ' if task['completed'] else ''}{task['task']}"
            markup.add(InlineKeyboardButton(task_label, callback_data=f"label_{user_id}_{index}"))
            done_button = InlineKeyboardButton("✅ Done", callback_data=f"toggle_{user_id}_{index}")
            edit_button = InlineKeyboardButton("✏️ Edit", callback_data=f"edit_{user_id}_{index}")
            delete_button = InlineKeyboardButton("🗑️ Delete", callback_data=f"delete_{user_id}_{index}")
            markup.add(done_button, edit_button, delete_button)
    return markup


# Handling task addition
@bot.message_handler(commands=['addtask'])
def handle_add_task(message):
    msg = bot.send_message(message.chat.id, "Please enter the task description:")
    bot.register_next_step_handler(msg, receive_task_description, message.chat.id)


def receive_task_description(message, user_id):
    add_task(user_id, message.text)
    bot.send_message(user_id, "Task added successfully!")


# Displaying tasks
@bot.message_handler(commands=['tasks'])
def handle_tasks(message):
    user_id = message.chat.id
    bot.send_message(user_id, "Your tasks:", reply_markup=generate_task_markup(user_id))


# Callback query handler
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    action, user_id_str, task_index_str = call.data.split('_')
    user_id = int(user_id_str)
    task_index = int(task_index_str)

    if action == 'toggle':
        handle_toggle_action(user_id, task_index, call)
    elif action == 'delete':
        handle_delete_action(user_id, task_index, call)
    elif action == 'edit':
        handle_edit_action(user_id, task_index, call)
    else:
        bot.answer_callback_query(call.id, "Unknown action.")


# Function to start the task editing process
def start_editing_task(call, task_index):
    user_editing_state[call.message.chat.id] = task_index
    msg = bot.send_message(call.message.chat.id, "Enter the new task description:")
    bot.register_next_step_handler(msg, receive_new_task_description, call.message.chat.id, task_index)


# Function to receive new task description and update the task
def receive_new_task_description(message, user_id, task_index):
    edit_task(user_id, task_index, message.text)
    del user_editing_state[user_id]  # Clear user's editing state
    bot.send_message(user_id, "Task updated successfully!")
    bot.send_message(user_id, "Your tasks:", reply_markup=generate_task_markup(user_id))


# Function to update the task list message
def update_task_list_message(call):
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Your tasks:",
        reply_markup=generate_task_markup(call.message.chat.id)
    )


@bot.message_handler(commands=['stock_bot'])
def stock_bot_command(message):
    bot.send_message(message.chat.id,
                     "This is Stock Assistant. What stock would you like to add? Please enter the ticker or company name.")
    bot.register_next_step_handler(message, process_stock_input)


def process_stock_input(message):
    input_text = message.text.upper()
    stock_ticker = get_ticker_from_company_name(input_text) or input_text

    if is_valid_stock(stock_ticker):
        if add_stock_for_user(message.chat.id, stock_ticker):
            bot.send_message(message.chat.id, f"{stock_ticker} added. You can add up to 3 stocks.")
            send_stock_info(message.chat.id, stock_ticker)  # Send info immediately
        else:
            bot.send_message(message.chat.id, "You can only track up to 3 stocks.")
    else:
        bot.send_message(message.chat.id, "Invalid ticker or company name. Please check and enter again.")
        bot.register_next_step_handler(message, process_stock_input)


def get_stock_info(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return info if 'currentPrice' in info else None
    except Exception as e:
        print(f"Error fetching stock info for {ticker}: {e}")
        return None


def format_stock_message(stock_ticker, stock_info):
    if stock_info and 'currentPrice' in stock_info:
        current_price = stock_info['currentPrice']
        return f"{stock_ticker}: Current Price: {current_price}"
    return f"Could not retrieve information for {stock_ticker}."


def send_daily_stock_updates():
    for user_id, stocks in user_stocks.items():
        for stock in stocks:
            send_stock_info(user_id, stock)


def fetch_stock_data(stock_symbol):
    try:
        stock = yf.Ticker(stock_symbol)
        hist = stock.history(period="1wk")
        return hist['Close']
    except Exception as e:
        print(f"Error fetching historical data for {stock_symbol}: {e}")
        return None


def create_stock_graph(stock_symbol):
    data = fetch_stock_data(stock_symbol)
    if data is not None:
        plt.figure(figsize=(10, 6))
        plt.plot(data.index, data, marker='o', color='b')

        # Formatting the date on the x-axis
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator())
        plt.xticks(rotation=45)

        # Formatting the price on the y-axis
        plt.gca().yaxis.set_major_formatter(mticker.StrMethodFormatter('${x:,.2f}'))

        plt.title(f'Weekly Stock Prices for {stock_symbol}')
        plt.xlabel('Date')
        plt.ylabel('Price (USD)')
        plt.grid(True)
        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plt.close()
        return buffer
    else:
        return None


def set_user_state(user_id, state):
    user_state[user_id] = state


def get_user_state(user_id):
    return user_state.get(user_id, None)


def get_ticker_from_company_name(company_name):
    company_name_upper = company_name.upper()
    return company_to_ticker.get(company_name_upper, None)


# Add a stock for the user if there's room
def add_stock_for_user(user_id, stock_ticker):
    if user_id not in user_stocks:
        user_stocks[user_id] = []
    if len(user_stocks[user_id]) < 3 and stock_ticker not in user_stocks[user_id]:
        user_stocks[user_id].append(stock_ticker)
        return True
    return False


def is_valid_stock(ticker):
    try:
        stock = yf.Ticker(ticker)
        # Check if the ticker has valid historical data
        hist = stock.history(period="1d")
        return not hist.empty
    except Exception as e:
        print(f"Error checking stock validity: {e}")
        return False


def send_stock_info(chat_id, stock_ticker):
    try:
        stock_info = get_stock_info(stock_ticker)
        if stock_info:
            message_to_user = format_stock_message(stock_ticker, stock_info)
            bot.send_message(chat_id, message_to_user)

            graph_buffer = create_stock_graph(stock_ticker)
            bot.send_photo(chat_id, graph_buffer)
        else:
            bot.send_message(chat_id, f"Could not retrieve information for {stock_ticker}.")
    except Exception as e:
        print(f"Error in send_stock_info for {stock_ticker}: {e}")
        bot.send_message(chat_id, "An error occurred while retrieving stock information.")


@bot.message_handler(commands=['start'])
def start(message):
    # Creating a custom keyboard
    markup = telebot.types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    btn_chatgpt = telebot.types.KeyboardButton('/chatgpt')
    btn_dalle = telebot.types.KeyboardButton('/dalle')
    btn_news = telebot.types.KeyboardButton('/news')
    btn_weather = telebot.types.KeyboardButton('/weather')
    btn_quote = telebot.types.KeyboardButton('/quotes')
    btn_facts = telebot.types.KeyboardButton('/facts')
    btn_reminder = telebot.types.KeyboardButton('/reminder')
    btn_stock = telebot.types.KeyboardButton('/stock_bot')
    btn_tasks = telebot.types.KeyboardButton('/tasks')
    btn_support = telebot.types.KeyboardButton('/support')

    # Adding buttons to the markup
    markup.add(btn_chatgpt, btn_dalle, btn_news, btn_weather, btn_quote, btn_facts, btn_reminder, btn_stock, btn_tasks, btn_support)

    # Sending the message with the custom keyboard
    bot.send_message(message.chat.id, 'Hi! This is your smart assistant! How can I help you today?', reply_markup=markup)


def generate_image(prompt):
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="512x512",
        response_format="b64_json"
    )
    image_b64 = response['data'][0]['b64_json']
    return image_b64


def get_completion(prompt, model='gpt-4'):
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages
    )
    # Access the message content properly
    return response.choices[0].message.content


@bot.message_handler(commands=['chatgpt'])
def handle_chatgpt_input(message):
    set_user_state(message.chat.id, 'chatgpt')
    bot.send_message(message.chat.id,
                     "You are now chatting with ChatGPT. Type your messages and I'll respond. Use /stop to end the chat.")


@bot.message_handler(commands=['stop'])
def handle_stop(message):
    set_user_state(message.chat.id, None)
    bot.send_message(message.chat.id, "ChatGPT session ended. How can I assist you further?")


def generate_dalle_image(prompt):
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )

        # Accessing the image URL
        image_url = response.data[0].url
        return image_url
    except Exception as e:
        print(f"Error in generating image: {e}")
        return None

@bot.message_handler(commands=['dalle'])
def handle_dalle_input(message):
    set_user_state(message.chat.id, 'dalle')
    msg = bot.send_message(message.chat.id, "Enter a prompt for image generation:")
    bot.register_next_step_handler(msg, receive_dalle_prompt)


def receive_dalle_prompt(message):
    user_id = message.chat.id
    prompt = message.text
    image_url = generate_dalle_image(prompt)
    if image_url:
        bot.send_photo(user_id, image_url)
    else:
        bot.send_message(user_id, "Sorry, I couldn't generate an image right now.")
    set_user_state(user_id, None)  # Reset state after processing


@bot.message_handler(commands=['quotes'])
def subscribe_quotes(message):
    user_id = message.chat.id
    if user_id not in subscribed_users_for_quotes:
        subscribed_users_for_quotes.add(user_id)
        bot.send_message(user_id, "You've subscribed to daily inspirational quotes!")
        send_quote(user_id)  # Send an initial quote immediately upon subscription
    else:
        bot.send_message(user_id, "You're already subscribed to daily quotes.")


@bot.message_handler(commands=['unsubscribe_quotes'])
def unsubscribe_quotes(message):
    user_id = message.chat.id
    if user_id in subscribed_users_for_quotes:
        subscribed_users_for_quotes.remove(user_id)
        bot.send_message(user_id, "You've unsubscribed from daily inspirational quotes.")
    else:
        bot.send_message(user_id, "You are not subscribed to daily quotes.")


@bot.message_handler(commands=['weather'])
def handle_weather_command(message):
    msg = bot.send_message(message.chat.id, "Which city's weather would you like to check?")
    bot.register_next_step_handler(msg, send_weather)


def send_weather(message):
    city_name = message.text
    weather_report = get_weather(city_name)
    bot.send_message(message.chat.id, weather_report, parse_mode='HTML')


@bot.message_handler(commands=['facts'])
def subscribe_facts(message):
    user_id = message.chat.id
    if user_id not in subscribed_users_for_facts:
        subscribed_users_for_facts.add(user_id)
        bot.send_message(user_id, "You've subscribed to daily interesting facts! Here's your first fact:")
        send_fact(user_id)
    else:
        bot.send_message(user_id, "You're already subscribed to daily interesting facts.")


def send_fact(user_id):
    # Send a random fact from the list
    fact = random.choice(interesting_facts)
    bot.send_message(user_id, fact)


@bot.message_handler(commands=['reminder'])
def handle_reminder_command(message):
    bot.send_message(message.chat.id, "What would you like me to remind you about?")
    set_user_state(message.chat.id, 'reminder_message')


def process_reminder_message(message):
    if get_user_state(message.chat.id) == 'reminder_message':
        # Store the reminder message
        temp_reminders[message.chat.id] = {'message': message.text}
        bot.send_message(message.chat.id, "Please enter the date and time for the reminder (format: MM-DD HH:MM):")
        set_user_state(message.chat.id, 'reminder_datetime')


def process_reminder_datetime(message):
    if get_user_state(message.chat.id) == 'reminder_datetime':
        try:
            current_year = datetime.now().year
            reminder_datetime_str = f"{current_year}-{message.text}"
            reminder_datetime = datetime.strptime(reminder_datetime_str, "%Y-%m-%d %H:%M")

            if reminder_datetime < datetime.now():
                bot.send_message(message.chat.id, "Please enter a future date and time.")
                return

            # Add a scheduled job to send the reminder
            schedule.every().day.at(reminder_datetime.strftime("%H:%M")).do(send_reminder, message.chat.id,
                                                                            temp_reminders[message.chat.id]['message'])
            bot.send_message(message.chat.id,
                             "Your reminder is set for " + reminder_datetime.strftime("%Y-%m-%d %H:%M"))
            set_user_state(message.chat.id, None)
            del temp_reminders[message.chat.id]
        except ValueError:
            bot.send_message(message.chat.id, "Invalid date and time format. Please use format: MM-DD HH:MM")


def send_reminder(chat_id, reminder_message):
    formatted_message = f"<b>⏰ Reminder</b>: <i>{reminder_message}</i> ⏰"
    bot.send_message(chat_id, formatted_message, parse_mode='HTML')


@bot.message_handler(commands=['news'])
def send_news(message):
    news = fetch_news()
    bot.send_message(message.chat.id, news, parse_mode='HTML')


@bot.message_handler(commands=['support'])
def support(message):
    markup = telebot.types.InlineKeyboardMarkup()
    btn = telebot.types.InlineKeyboardButton("Text support", url='https://t.me/ImMrAlex')
    markup.add(btn)

    bot.send_message(message.chat.id, 'Text support:', reply_markup=markup)


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    state = get_user_state(message.chat.id)
    if state == 'reminder_message':
        process_reminder_message(message)

    elif state == 'reminder_datetime':
        process_reminder_datetime(message)

    elif state == 'chatgpt':
        answer = get_completion(message.text)
        bot.send_message(message.chat.id, answer)

    elif state == 'dalle':
        image_b64 = generate_image(message.text)
        image_data = base64.b64decode(image_b64)
        bot.send_photo(message.chat.id, image_data)
        set_user_state(message.chat.id, None)  # Reset state after processing

    elif state == 'stock_bot':
        stock_ticker = message.text.upper()
        if is_valid_stock(stock_ticker):
            if add_stock_for_user(message.chat.id, stock_ticker):
                bot.send_message(message.chat.id, f"{stock_ticker} added. You can add up to 3 stocks.")
            else:
                bot.send_message(message.chat.id, "You can only track up to 3 stocks.")
            set_user_state(message.chat.id, None)  # Reset state after processing
        else:
            bot.send_message(message.chat.id, "Invalid ticker or company name. Please check and enter again.")
            # Keep the state as 'stock_bot' for re-entry

    else:
    # Creating a custom regular keyboard
        markup = telebot.types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
        buttons = [
            telebot.types.KeyboardButton('/chatgpt'),
            telebot.types.KeyboardButton('/dalle'),
            telebot.types.KeyboardButton('/news'),
            telebot.types.KeyboardButton('/stock_bot'),
            telebot.types.KeyboardButton('/weather'),
            telebot.types.KeyboardButton('/addtask'),
            telebot.types.KeyboardButton('/tasks'),
            telebot.types.KeyboardButton('/quotes'),
            telebot.types.KeyboardButton('/unsubscribe_quotes'),
            telebot.types.KeyboardButton('/reminder'),
            telebot.types.KeyboardButton('/facts'),
            telebot.types.KeyboardButton('/support'),
        ]

        # Adding buttons to the markup
        markup.add(*buttons)
    
        # Sending the message with the custom regular keyboard
        bot.send_message(message.chat.id, 'Choose an option:', reply_markup=markup)


def send_daily_news():
    # Assuming you have a way to store subscribed users' chat IDs
    for chat_id in subscribed_users:
        news = fetch_news()
        bot.send_message(chat_id, news)


schedule.every().day.at("08:00").do(send_daily_news)  # Set your desired time


# Start the scheduler thread
threading.Thread(target=run_scheduler).start()


# Scheduler setup
def run_scheduler():
    schedule.every().day.at("09:00").do(send_daily_stock_updates)
    while True:
        schedule.run_pending()
        time.sleep(1)


# Run the scheduler in a separate thread
threading.Thread(target=run_scheduler).start()

bot.polling(none_stop=True)

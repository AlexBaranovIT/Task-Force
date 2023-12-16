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
    bot.send_message(message.chat.id, 'Hi! This is your smart assistant! How can I help you today?')


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
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        max_tokens=2040,
        temperature=0,
    )
    return response.choices[0].message["content"]


@bot.message_handler(commands=['chatgpt'])
def handle_chatgpt_input(message):
    set_user_state(message.chat.id, 'chatgpt')
    bot.send_message(message.chat.id,
                     "You are now chatting with ChatGPT. Type your messages and I'll respond. Use /stop to end the chat.")


@bot.message_handler(commands=['stop'])
def handle_stop(message):
    set_user_state(message.chat.id, None)
    bot.send_message(message.chat.id, "ChatGPT session ended. How can I assist you further?")


@bot.message_handler(commands=['dalle'])
def handle_dalle_input(message):
    set_user_state(message.chat.id, 'dalle')
    bot.send_message(message.chat.id, "Enter a prompt for image generation:")


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
        bot.send_message(
            message.chat.id, 'Use one of these to continue:\n\n'
            "/chatgpt - Chat with an AI-based chatbot.\n"
            "/dalle - Generate images based on your prompts.\n"
            "/news - Get the latest news headlines.\n"
            "/stock_bot - Track and receive updates on your favorite stocks.\n"
            "/weather - Get current weather information for a specified city.\n"
            "/addtask - Add a task to your to-do list.\n"
            "/tasks - View and manage your tasks.\n"
            "/quotes - Receive daily inspirational quotes.\n"
            "/unsubscribe_quotes - Unsubscribe from daily quotes.\n"
            "/reminder - Set up a personal reminder.\n"
            "/subscribe_facts - Get daily interesting facts.\n"
            "/unsubscribe_facts - Stop receiving daily facts.\n"
            "/support - Get support and help information."
        )


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

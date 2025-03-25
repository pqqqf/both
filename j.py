import requests
import telebot

# Bot access token
TOKEN = '7747763304:AAFfSx8yM56K-ghrqbonrTK_DvyfBaA7fEM'
bot = telebot.TeleBot(TOKEN)

# LeakCheck API key
API_KEY = '40d83bc02b71f93664bc55113e51485cf0a7aba4'

# List of authorized user IDs
authorized_users = set()  # Using a set for easy addition and removal

# Owner ID (can be changed to the actual owner's ID)
OWNER_ID = 1628318629

@bot.message_handler(commands=['add_user'])
def add_user(message):
    if message.from_user.id == OWNER_ID:
        try:
            parts = message.text.split()
            user_id = int(parts[1])
            authorized_users.add(user_id)
            bot.reply_to(message, f"User {user_id} added successfully.")
        except (IndexError, ValueError):
            bot.reply_to(message, "Please provide a valid user ID to add.")
    else:
        bot.reply_to(message, "You are not authorized to add users.")

@bot.message_handler(commands=['remove_user'])
def remove_user(message):
    if message.from_user.id == OWNER_ID:
        try:
            parts = message.text.split()
            user_id = int(parts[1])
            authorized_users.discard(user_id)
            bot.reply_to(message, f"User {user_id} removed successfully.")
        except (IndexError, ValueError):
            bot.reply_to(message, "Please provide a valid user ID to remove.")
    else:
        bot.reply_to(message, "You are not authorized to remove users.")

@bot.message_handler(commands=['Jid'])
def handle_allD_command(message):
    if message.from_user.id in authorized_users or message.from_user.id == OWNER_ID:
        try:
            parts = message.text.split()
            query = parts[1]  # Email or username
        except IndexError:
            bot.reply_to(message, "Please enter the email or username after the command.")
            return

        # Set up headers for the request
        headers = {
            'Accept': 'application/json',
            'X-API-Key': API_KEY
        }

        # Send request to LeakCheck API
        response = requests.get(f'https://leakcheck.io/api/v2/query/{query}', headers=headers)

        # Check response status and process data
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success') and data['found'] > 0:
                    reply_message = f"🔍 Search results for: {query}\n\n"

                    for result in data['result']:
                        source = result.get('source', {})
                        source_name = source.get('name', 'Unknown')
                        breach_date = source.get('breach_date', 'None')
                        ip_address = result.get('ip', 'N/A')
                        origin = result.get('origin', 'N/A')

                        # Prepare message with all possible fields
                        result_message = (
                            f"📛 Source: {source_name}\n"
                            f"📅 Breach Date: {breach_date}\n"
                            f"🌐 IP Address: {ip_address}\n"
                            f"🌐 Leak Location: {origin}\n"
                            f"📧 Email: {result.get('email', 'N/A')}\n"
                            f"👤 Username: {result.get('username', 'N/A')}\n"
                            f"🔑 Password: {result.get('password', 'N/A')}\n"
                            f"👥 First Name: {result.get('first_name', 'N/A')}\n"
                            f"👥 Last Name: {result.get('last_name', 'N/A')}\n"
                            f"🎂 Date of Birth: {result.get('dob', 'N/A')}\n"
                            f"🏠 Address: {result.get('address', 'N/A')}\n"
                            f"📦 Zip Code: {result.get('zip', 'N/A')}\n"
                            f"📞 Phone: {result.get('phone', 'N/A')}\n"
                            f"📝 Name: {result.get('name', 'N/A')}\n"
                            "-----------------------------------\n\n"  # Separator between leaks
                        )
                        reply_message += result_message

                    bot.reply_to(message, reply_message)
                else:
                    bot.reply_to(message, "No results found for this search.")
            except ValueError:
                bot.reply_to(message, "Received a non-JSON response.")
        else:
            # Handle errors based on status codes
            if response.status_code == 401:
                bot.reply_to(message, "Missing or invalid X-API-Key. Please check your API key.")
            elif response.status_code == 400:
                bot.reply_to(message, "Invalid request. Please check the query format and try again.")
            elif response.status_code == 403:
                bot.reply_to(message, "Access denied. Active plan required or limit reached.")
            elif response.status_code == 429:
                bot.reply_to(message, "Too many requests. Please try again later.")
            elif response.status_code == 422:
                bot.reply_to(message, "Could not determine search type automatically. Please specify the type.")
            else:
                bot.reply_to(message, f"Failed to connect to LeakCheck. Status code: {response.status_code}")
    else:
        bot.reply_to(message, "You are not authorized to perform this action.")

# Start the bot using polling
bot.polling()

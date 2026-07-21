import logging
import random
import datetime
import json
import os
import asyncio
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- CONFIGURATIONS ---
BOT_TOKEN = "8691022341:AAG5od4i35q5n4OiQpd1T7K_OqhRwQoEWcQ"
OWNER_ID = 598309360

# Aapke channels/groups ki chat IDs (Line-by-line mapping)
CHANNELS = {
    "store_list": -1002405454804,
    "main_channel": -1002225044624,
    "community_group": -1002416347078,
    "backup_channel": -1002350788057,
    "main_reship": -1002625225887,
    "vouch_channel": -1002652451009,
    "rapid_cashouts": -1004310102304,
    "cashout_vouches": -1002107259762,
    "extra_channel": -1003053857216,
}

# Simple JSON User Storage
USERS_FILE = "bot_users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_user(user_id):
    users = load_users()
    if user_id not in users:
        users.add(user_id)
        try:
            with open(USERS_FILE, "w", encoding="utf-8") as f:
                json.dump(list(users), f)
        except Exception as e:
            logger.error(f"Error saving user: {e}")

# Dictionary to store user math quiz sessions
USER_QUIZ = {}

# --- SET MENU COMMANDS (Blue Button) ---
async def post_init(application):
    commands = [
        ("start", "Start the bot & solve puzzle")
    ]
    await application.bot.set_my_commands(commands)

# --- 1. START COMMAND & RANDOM MATH QUIZ ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user:
        save_user(user.id)
    
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    operator = random.choice(["+", "-"])
    if operator == "+":
        correct_answer = num1 + num2
    else:
        if num1 < num2:
            num1, num2 = num2, num1
        correct_answer = num1 - num2

    if user:
        USER_QUIZ[user.id] = {"answer": correct_answer}

    options = [correct_answer]
    while len(options) < 3:
        fake = correct_answer + random.choice([-2, -1, 1, 2, 3])
        if fake != correct_answer and fake >= 0 and fake not in options:
            options.append(fake)
    random.shuffle(options)

    keyboard = [
        [
            InlineKeyboardButton(str(options[0]), callback_data=f"ans_{options[0]}"),
            InlineKeyboardButton(str(options[1]), callback_data=f"ans_{options[1]}"),
            InlineKeyboardButton(str(options[2]), callback_data=f"ans_{options[2]}"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    quiz_text = (
        f"🔒 **Solve to get invites:**\n"
        f"`{num1} {operator} {num2} = ?`"
    )

    if update.message:
        await update.message.reply_text(quiz_text, reply_markup=reply_markup, parse_mode="Markdown")
    elif update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(quiz_text, reply_markup=reply_markup, parse_mode="Markdown")

# --- 2. HANDLE QUIZ ANSWER ---
async def handle_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    save_user(user_id)

    data = query.data
    if not data or not data.startswith("ans_"):
        return

    try:
        selected_ans = int(data.split("_")[1])
    except (IndexError, ValueError):
        return

    if user_id not in USER_QUIZ:
        await start(update, context)
        return

    correct_ans = USER_QUIZ[user_id]["answer"]

    if selected_ans == correct_ans:
        expire_time = datetime.datetime.now() + datetime.timedelta(seconds=60)
        
        links = {}
        for key, chat_id in CHANNELS.items():
            try:
                invite = await context.bot.create_chat_invite_link(
                    chat_id=chat_id,
                    member_limit=1,
                    expire_date=expire_time
                )
                links[key] = invite.invite_link
            except Exception as e:
                logger.error(f"Error creating link for {key} ({chat_id}): {e}")
                links[key] = "https://t.me/+_EjOLmtb1bZmZWU1"

        caption_text = (
            "⚡️ **RAPID REFUNDS** ⚡️\n"
            "Reship Like a Pro. Control Like a Boss.\n\n"
            "⸻\n\n"
            "🌟 **Warm Greetings from the RAPID Team!** 🌟\n"
            "Welcome to the most trusted and efficient reship & refund network — where precision, privacy, and professionalism meet speed and reliability.\n\n"
            "⸻\n\n"
            "📦 **Official RAPID Network Links:**\n\n"
            "🔹 **Store List:**\n"
            f"👉 {links.get('store_list', '#')}\n\n"
            "🔹 **Main Channel:**\n"
            f"👉 {links.get('main_channel', '#')}\n\n"
            "🔹 **Community Group:**\n"
            f"👉 {links.get('community_group', '#')}\n\n"
            "🔹 **Backup Channel:**\n"
            f"👉 {links.get('backup_channel', '#')}\n\n"
            "⸻\n\n"
            "💝 **Main Reship Channel:**\n"
            f"👉 {links.get('main_reship', '#')}\n\n"
            "🔥 **Vouch Channel:**\n"
            f"👉 {links.get('vouch_channel', '#')}\n\n"
            "⸻\n\n"
            "💸 **Rapid Cashouts:**\n"
            f"👉 {links.get('rapid_cashouts', '#')}\n\n"
            "💰 **Cashout Vouches:**\n"
            f"👉 {links.get('cashout_vouches', '#')}\n\n"
            "⸻\n"
            "📨 **Your links (60s valid):**\n\n"
            "1. Click the Link and Join\n"
            "2. Make sure to join all the groups above by clicking the links'\n"
            "3. If you missed any, re-enter /start\n\n"
            "👑 **Founder & Refunder:**\n"
            "👉 @RapidRefunder"
        )

        photo_path = "logo.jpg"
        
        try:
            if os.path.exists(photo_path):
                with open(photo_path, "rb") as photo_file:
                    await query.message.reply_photo(
                        photo=photo_file,
                        caption=caption_text,
                        parse_mode="Markdown"
                    )
                await query.message.delete()
            else:
                await query.edit_message_text(caption_text, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Error sending photo message: {e}")
            await query.edit_message_text(caption_text, parse_mode="Markdown")

        if user_id in USER_QUIZ:
            del USER_QUIZ[user_id]

    else:
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        operator = random.choice(["+", "-"])
        if operator == "+":
            correct_answer = num1 + num2
        else:
            if num1 < num2:
                num1, num2 = num2, num1
            correct_answer = num1 - num2

        USER_QUIZ[user_id]["answer"] = correct_answer

        options = [correct_answer]
        while len(options) < 3:
            fake = correct_answer + random.choice([-2, -1, 1, 2, 3])
            if fake != correct_answer and fake >= 0 and fake not in options:
                options.append(fake)
        random.shuffle(options)

        keyboard = [
            [
                InlineKeyboardButton(str(options[0]), callback_data=f"ans_{options[0]}"),
                InlineKeyboardButton(str(options[1]), callback_data=f"ans_{options[1]}"),
                InlineKeyboardButton(str(options[2]), callback_data=f"ans_{options[2]}"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"❌ **Galat jawab! Naya puzzle solve karein:**\n\n"
            f"🔒 **Solve to get invites:**\n"
            f"`{num1} {operator} {num2} = ?`",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

# --- 3. OWNER / ADMIN PANEL & BROADCAST ---
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        return

    users = load_users()
    total_users = len(users)

    text = (
        f"👑 **Owner Admin Panel** 👑\n\n"
        f"📊 **Total Bot Users:** `{total_users}`\n\n"
        f"📢 **Broadcast Command:**\n"
        f"Use `/broadcast [Your Message]` to send message to all users."
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        return

    if not context.args:
        await update.message.reply_text("⚠️ Please provide a message to broadcast!\nExample: `/broadcast Hello everyone!`", parse_mode="Markdown")
        return

    broadcast_text = " ".join(context.args)
    users = load_users()
    
    success_count = 0
    fail_count = 0

    status_msg = await update.message.reply_text(f"🚀 Broadcasting message to {len(users)} users...")

    for uid in users:
        try:
            await context.bot.send_message(chat_id=uid, text=broadcast_text, parse_mode="Markdown")
            success_count += 1
        except Exception:
            fail_count += 1

    await status_msg.edit_text(
        f"✅ **Broadcast Completed!**\n\n"
        f"📤 Successfully Sent: `{success_count}`\n"
        f"❌ Failed (Blocked bot): `{fail_count}`",
        parse_mode="Markdown"
    )

# --- FLASK WEB SERVER (For Render Web Service Live URL) ---
web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "🤖 Rapid Refunds Bot is Alive and Running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    # Disable reloader and debug to avoid event loop conflicts in production
    web_app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

async def main():
    # Flask ko alag thread me proper daemon mode par start karein
    import threading
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Telegram bot application build karein
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()

    # Handlers register karein
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("broadcast", broadcast_message))
    app.add_handler(CallbackQueryHandler(handle_quiz, pattern="^ans_"))

    print("🤖 Rapid Refunds Bot & Web Server started successfully!")
    
    # Modern async initialize aur start (Python 3.14 compatible)
    await app.initialize()
    await app.start()
    await app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
    
    # Keep the application running indefinitely
    stop_event = asyncio.Event()
    await stop_event.wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass



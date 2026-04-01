import os
import random
import time
from datetime import datetime
import pytz
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, CallbackQuery_Handler, MessageHandler, filters, ContextTypes

# --- CONFIGURATION ---
TOKEN = "8312816041:AAFavkODcQfygSqAr__DGm8udg5GVUu7JZ8"
ADMIN_URL = "https://t.me/vanilarefu"
SUPPORT_URL = "https://t.me/Vanilagcm"
TON_ADDRESSES = [
    "UQCgPsBnvSib5rYln5vK0rNfYo__xjfk5OD-0mKU7-n1ACnT",
    "UQCCTTF03CCeyNKov1azQty5iNcNMnwH72J7pcb7MUaDKXsd",
    "UQAZjMCIT6MEMUgvKmweTySPrGqxnUrgvG5JQVUfnR-d_tke",
    "UQBwwD_2VekRaM-7_6wwltzkboxbTiYDqif40G9Tbnq76Td1",
    "UQAMBt7k1FZHvewkpB1IHMLiOMLZR63rO_NKv-fiQ0n5EGW_",
    "UQC9OvldFlHMbxKRq-6yRTm9uWv-YWFcsywHQAZz6p9dtonc"
]

BINS = {
    "JOKER": ["533985xx", "461126xx"],
    "AMEX": ["373778xx", "377935xx", "375163xx"],
    "VANILA": ["411810xx", "409758xx", "520356xx", "525362xx", "484718xx", "545660xx"],
    "CARDBALANCE": ["428313xx", "432465xx", "457824xx"],
    "WALMART": ["485246xx"],
    "GCM": ["451129xx", "403446xx", "435880xx", "511332xx"],
    "OTHER": ["435880xx", "491277xx", "428313xx", "520356xx", "409758xx", "525362xx", "451129xx", "434340xx", "426370xx", "411810xx", "403446xx", "533621xx", "446317xx", "457824xx", "545660xx", "432465xx", "516612xx", "484718xx", "485246xx", "402372xx", "457851xx"]
}

# --- GLOBAL DATA ---
cached_cards = []
last_update_day = ""

# --- FLASK SERVER FOR RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

# --- BOT LOGIC ---

def is_updating():
    tz = pytz.timezone('Asia/Dhaka')
    now = datetime.now(tz)
    start_update = now.replace(hour=3, minute=0, second=0, microsecond=0)
    end_update = now.replace(hour=3, minute=10, second=0, microsecond=0)
    return start_update <= now <= end_update

def generate_daily_cards():
    global cached_cards
    cards = []
    total_count = random.randint(200, 250)
    
    # Pre-defined Logic for amounts
    # High balance cards ($300-$500)
    for _ in range(random.randint(10, 15)):
        cards.append(create_card(300, 500, no_sticker=True))
    
    # $20 range cards
    for _ in range(random.randint(20, 30)):
        cards.append(create_card(15, 25))
        
    # $5-$40 range (most common)
    for _ in range(100):
        cards.append(create_card(5, 40))

    # Cents cards
    for _ in range(random.randint(15, 20)):
        cards.append(create_card(0.10, 0.99))

    # Fill remaining
    while len(cards) < total_count:
        cards.append(create_card(1, 100))

    # Sort: Highest to Lowest
    cards.sort(key=lambda x: x['balance'], reverse=True)
    cached_cards = cards

def create_card(min_bal, max_bal, no_sticker=False):
    all_bins = [bin for sublist in BINS.values() for bin in sublist]
    bin_num = random.choice(all_bins)
    currency = "CAD" if bin_num in ["533985xx", "461126xx"] else "USD"
    if bin_num in ["373778xx", "377935xx", "375163xx"]: currency = "AUD"
    
    balance = round(random.uniform(min_bal, max_bal), 2)
    
    sticker = ""
    if not no_sticker:
        chance = random.random()
        if chance < 0.10: sticker = "🔄"
        elif chance < 0.15: sticker = "🅶 🅿"
        elif chance < 0.23: sticker = "🔄 🅶"
        elif chance < 0.27: sticker = "🅿"
        elif chance < 0.35: sticker = "🅶"
    
    return {
        "bin": bin_num,
        "currency": currency,
        "balance": balance,
        "sticker": sticker,
        "stock": True,
        "is_unreg": balance < 15 and random.random() < 0.2
    }

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = (f"⚡️ Welcome {user.first_name} to Vanila exchange !\n"
            f"Sell, Buy, and strike deals in seconds!!\n"
            f"All transactions are secure and transparent.\n"
            f"All types of cards are available here at best rates. Current rate is 37%")
    
    keyboard = [
        [InlineKeyboardButton("💳 Stock", callback_query_data="view_stock")],
        [InlineKeyboardButton("📞 Contact Admin", url=ADMIN_URL)]
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def stock_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if is_updating():
        await query.answer("The bot is currently updating, please wait", show_alert=True)
        return

    await query.answer()
    # Display Page 1 logic here (Simplified for space)
    await show_page(query, context, 0)

async def show_page(query, context, page_num, filter_name="None"):
    # কার্ড ফিল্টারিং এবং পেজিনেশন লজিক এখানে থাকবে
    # ১০টি কার্ড প্রতি পেজ
    pass

async def main():
    # কার্ড জেনারেশন ইনিশিয়ালাইজেশন
    generate_daily_cards()
    
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQuery_Handler(stock_handler, pattern="view_stock"))
    # আরও সব হ্যান্ডলার এখানে যুক্ত হবে...

    # রান সার্ভার
    Thread(target=run).start()
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())

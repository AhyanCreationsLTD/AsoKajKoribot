import asyncio
import time
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ================= CONFIGURATION =================
TOKEN = "8825404684:AAF1MU7h671S_-oz7HnIjzZyWEHVwd1VAE8"            # এখানে আপনার BotFather-এর টোকেন দিন
DB_CHANNEL_ID = -1004439983806           # এখানে আপনার প্রাইভেট ডাটাবেস চ্যানেলের আইডি দিন (মাইনাস সহ)
MINI_APP_URL = "https://asokajkori.pages.dev"  # GitHub Pages বা হোস্টিং লিংক
# =================================================

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ৩৫০ মিনিট = ৫ ঘণ্টা ৫৫ মিনিট (GitHub Actions লুপের জন্য)
MAX_RUN_TIME = 355 * 60
start_time = time.time()
user_message_map = {}

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    
    # চ্যানেলে ইউজারের ডাটা ইনিশিয়ালাইজ বা ট্র্যাক করা
    if user_id not in user_message_map:
        text = f"[USER_DATA]\nUser ID: {user_id}\nName: {name}\nBalance: 0.00 TK\nAds Watched: 0"
        try:
            sent_msg = await bot.send_message(chat_id=DB_CHANNEL_ID, text=text)
            user_message_map[user_id] = sent_msg.message_id
        except Exception as e:
            print(f"Channel Error: {e}")

    builder = InlineKeyboardBuilder()
    builder.button(text="🚀 AsoKajKoribot Mini App", web_app=types.WebAppInfo(url=MINI_APP_URL))
    builder.button(text="💰 আমার ব্যালেন্স", callback_data="balance")
    builder.button(text="💸 উইথড্র করুন", callback_data="withdraw_menu")
    builder.adjust(1)
    
    await message.answer(
        f"স্বাগতম {name}!\n\n**AsoKajKoribot** এ আপনাকে স্বাগতম। নিচে থেকে মিনি অ্যাপ ওপেন করে বিজ্ঞাপন দেখে ইনকাম করুন এবং উইথড্র দিন।",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "balance")
async def balance_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    msg_id = user_message_map.get(user_id)
    if msg_id:
        try:
            chat_msg = await bot.get_message(chat_id=DB_CHANNEL_ID, message_id=msg_id)
            await callback.answer(f"আপনার বর্তমান তথ্য:\n{chat_msg.text}", show_alert=True)
        except:
            await callback.answer("ডেটা পাওয়া যায়নি, দয়া করে আবার /start দিন।", show_alert=True)
    else:
        await callback.answer("সেশন রিসেট হয়েছে, দয়া করে /start দিন।", show_alert=True)

@dp.callback_query(F.data == "withdraw_menu")
async def withdraw_menu_handler(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="🌐 উইথড্র পেজে যান", web_app=types.WebAppInfo(url=f"{MINI_APP_URL}/withdraw.html"))
    builder.button(text="« ফিরে যান", callback_data="back_home")
    builder.adjust(1)
    await callback.message.edit_text("উইথড্র করতে নিচের মিনি অ্যাপ বাটনে ক্লিক করুন:", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "back_home")
async def back_home_handler(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="🚀 AsoKajKoribot Mini App", web_app=types.WebAppInfo(url=MINI_APP_URL))
    builder.button(text="💰 আমার ব্যালেন্স", callback_data="balance")
    builder.button(text="💸 উইথড্র করুন", callback_data="withdraw_menu")
    builder.adjust(1)
    await callback.message.edit_text("মেনু:", reply_markup=builder.as_markup())

async def check_uptime():
    while True:
        await asyncio.sleep(60)
        if time.time() - start_time >= MAX_RUN_TIME:
            await bot.session.close()
            exit(0)

async def main():
    asyncio.create_task(check_uptime())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

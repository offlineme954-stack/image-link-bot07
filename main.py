import os
import time
import requests
from telebot import TeleBot

# Environment Variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID")

bot = TeleBot(BOT_TOKEN)

# ডেটাবেজ সাপোর্ট (ইউজার ও আপলোড ট্র্যাক রাখার জন্য)
user_list = set()
total_uploads = 0

# Start Command with Animated Message
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    user_list.add(user_id)
    
    # Intro Animation
    msg = bot.reply_to(message, "⚡ **Loading Bot Services...**", parse_mode="Markdown")
    time.sleep(0.8)
    
    bot.edit_message_text("✨ **স্বাগতম ইমেজ টু লিংক সার্ভিস বটের!** ✨", chat_id=message.chat.id, message_id=msg.message_id, parse_mode="Markdown")
    time.sleep(0.8)

    welcome_text = (
        "📸 **আপনার যেকোনো ছবি আমাকে পাঠান!**\n\n"
        "আমি সাথে সাথে সেটির একটি **Direct Image Link** তৈরি করে দেব।\n"
        "*(লিংকটি আপনি যেকোনো ওয়েবসাইট বা ব্লগে ব্যবহার করতে পারবেন)*"
    )
    bot.edit_message_text(welcome_text, chat_id=message.chat.id, message_id=msg.message_id, parse_mode="Markdown")

# Admin Panel Command
@bot.message_handler(commands=['admin', 'stats'])
def admin_panel(message):
    user_id = str(message.chat.id)
    
    # শুধুমাত্র নির্দিষ্ট Admin আইডি থেকেই কাজ করবে
    if user_id == str(ADMIN_CHAT_ID):
        admin_text = (
            "👑 **— Admin Panel Dashboard —** 👑\n\n"
            f"👤 **Total Bot Users:** `{len(user_list)}` 人\n"
            f"🖼️ **Total Images Processed:** `{total_uploads}` টি\n"
            f"⚡ **Bot Status:** Active & Online 🟢\n\n"
            f"🆔 **Your Admin ID:** `{ADMIN_CHAT_ID}`"
        )
        bot.reply_to(message, admin_text, parse_mode="Markdown")
    else:
        bot.reply_to(message, "⚠️ আপনি এই বটের এডমিন নন!")

# Image Handler with Percentage Animation & Auto-Delete Source Photo
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    global total_uploads
    user_list.add(message.chat.id)
    
    # Progress Animation Messages
    status_msg = bot.reply_to(message, "⏳ **ছবি গ্রহণ করা হয়েছে...**", parse_mode="Markdown")
    time.sleep(0.8)
    
    bot.edit_message_text("🔄 **প্রসেসিং শুরু হচ্ছে... [▒▒▒▒▒▒▒▒▒▒] 20%**", chat_id=message.chat.id, message_id=status_msg.message_id, parse_mode="Markdown")
    time.sleep(0.8)

    try:
        # টেলিগ্রাম থেকে ছবি ডাউনলোড
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        bot.edit_message_text("📤 **ক্লাউডে হোস্ট করা হচ্ছে... [██████▒▒▒▒] 60%**", chat_id=message.chat.id, message_id=status_msg.message_id, parse_mode="Markdown")
        
        # Catbox Direct Image Host API
        response = requests.post(
            'https://catbox.moe/user/api.php', 
            data={'reqtype': 'fileupload'}, 
            files={'fileToUpload': downloaded_file}
        )

        bot.edit_message_text("🌐 **ডাইরেক্ট লিংক তৈরি প্রায় শেষ... [██████████] 100%**", chat_id=message.chat.id, message_id=status_msg.message_id, parse_mode="Markdown")
        time.sleep(0.5)

        if response.status_code == 200:
            direct_link = response.text.strip()
            total_uploads += 1
            
            final_response = (
                "🎉 **আপনার ছবির ডাইরেক্ট লিংক তৈরি সম্পন্ন!**\n\n"
                f"🔗 **Direct URL:**\n`{direct_link}`\n\n"
                "💡 *(লিংকটি কপি করে যেকোনো জায়গায় ব্যবহার করতে পারবেন)*"
            )
            bot.edit_message_text(final_response, chat_id=message.chat.id, message_id=status_msg.message_id, parse_mode="Markdown")
            
            # ইউজারের পাঠানো ছবিটি অটো-ডিলিট করে দেওয়া
            try:
                bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            except Exception:
                pass # পারমিশন না থাকলে স্কিপ করবে

        else:
            bot.edit_message_text("❌ আপলোড ব্যর্থ হয়েছে! অনুগ্রহ করে আবার চেষ্টা করুন।", chat_id=message.chat.id, message_id=status_msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"⚠️ কোনো সমস্যা ঘটেছে: `{str(e)}`", chat_id=message.chat.id, message_id=status_msg.message_id, parse_mode="Markdown")

if __name__ == "__main__":
    bot.infinity_polling()

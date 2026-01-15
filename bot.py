import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
import yt_dlp
import re
from urllib.parse import urlparse

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot Token
BOT_TOKEN = "8416985766:AAGLFZgqvpjnxJTg_TcutTnLrdFMSdmn4dA"

# Channel information
CHANNEL_USERNAME = "@tradingword007"  # आपका channel username
CHANNEL_LINK = "https://t.me/tradingword007"  # आपका channel link

# Download directory
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Store user verification status (in production, use database)
user_status = {}

def is_valid_url(url):
    """Check if the given string is a valid URL"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

async def check_channel_membership(user_id: int, context: CallbackContext) -> bool:
    """Check if user is member of the channel"""
    try:
        chat_member = await context.bot.get_chat_member(
            chat_id=CHANNEL_USERNAME,
            user_id=user_id
        )
        return chat_member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logger.error(f"Error checking membership: {e}")
        return False

async def start(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    user = update.effective_user
    user_id = user.id
    
    # Check if user is already verified
    if user_id in user_status and user_status[user_id]:
        await send_welcome_message(update, user)
        return
    
    # Check channel membership
    is_member = await check_channel_membership(user_id, context)
    
    if is_member:
        user_status[user_id] = True
        await send_welcome_message(update, user)
    else:
        await ask_to_join_channel(update, context)

async def send_welcome_message(update: Update, user):
    """Send welcome message to verified user"""
    await update.message.reply_text(
        f'नमस्ते {user.first_name}! 👋\n\n'
        '✅ **Channel subscription verified!**\n\n'
        '🎬 **Video Downloader Bot** में आपका स्वागत है!\n\n'
        '📌 **कैसे उपयोग करें:**\n'
        '1. किसी भी YouTube video का link भेजें\n'
        '2. या किसी अन्य वेबसाइट का video link भेजें\n'
        '3. मैं video download करके आपको भेज दूंगा\n\n'
        '📱 **Supported sites:** YouTube, Facebook, Instagram, Twitter, TikTok, Dailymotion, Vimeo, और 1000+ sites\n\n'
        '⚠️ **Note:** 50MB से छोटे videos भेज सकता हूँ\n\n'
        '📞 **Support Channel:** @tradingword007'
    )

async def ask_to_join_channel(update: Update, context: CallbackContext):
    """Ask user to join channel"""
    keyboard = [
        [
            InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK),
            InlineKeyboardButton("✅ I've Joined", callback_data="check_membership")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        '👋 **Welcome to Video Downloader Bot!**\n\n'
        '📋 **To use this bot, you need to join our channel first:**\n\n'
        f'📢 **Channel:** {CHANNEL_USERNAME}\n'
        f'🔗 **Link:** {CHANNEL_LINK}\n\n'
        '📌 **Steps:**\n'
        '1. Click "Join Channel" button below\n'
        '2. Join the channel\n'
        '3. Come back and click "I\'ve Joined"\n\n'
        '✅ After joining, you can download unlimited videos!',
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: CallbackContext):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if query.data == "check_membership":
        # Check if user has joined
        is_member = await check_channel_membership(user_id, context)
        
        if is_member:
            user_status[user_id] = True
            await query.edit_message_text(
                f'✅ **Subscription verified successfully!**\n\n'
                f'नमस्ते {query.from_user.first_name}! 👋\n\n'
                '🎬 अब आप Video Downloader Bot का उपयोग कर सकते हैं!\n\n'
                '📌 **कैसे उपयोग करें:**\n'
                'बस किसी भी video का link भेजें और मैं उसे download करके आपको भेज दूंगा।\n\n'
                '🌐 **Example:** https://www.youtube.com/watch?v=...\n\n'
                '📞 **Support Channel:** @tradingword007'
            )
        else:
            keyboard = [
                [
                    InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK),
                    InlineKeyboardButton("✅ I've Joined", callback_data="check_membership")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                '❌ **You have not joined the channel yet!**\n\n'
                f'कृपया पहले हमारे channel से join करें: {CHANNEL_USERNAME}\n\n'
                '📌 **Steps:**\n'
                '1. Click "Join Channel" button below\n'
                '2. Join the channel\n'
                '3. Come back and click "I\'ve Joined"\n\n'
                '✅ After joining, you can download unlimited videos!',
                reply_markup=reply_markup
            )

async def help_command(update: Update, context: CallbackContext):
    """Send help message."""
    user_id = update.effective_user.id
    
    # Check if user is verified
    if user_id not in user_status or not user_status[user_id]:
        await ask_to_join_channel(update, context)
        return
    
    await update.message.reply_text(
        '🆘 **Help Guide**\n\n'
        '📥 **Video भेजने के लिए:**\n'
        'बस किसी भी video का link भेज दें\n\n'
        '🌐 **Example links:**\n'
        '• https://www.youtube.com/watch?v=...\n'
        '• https://youtu.be/...\n'
        '• https://www.instagram.com/reel/...\n'
        '• https://vm.tiktok.com/...\n\n'
        '⚙️ **Commands:**\n'
        '/start - बॉट शुरू करें\n'
        '/help - मदद देखें\n'
        '/about - बॉट के बारे में जानें\n\n'
        f'📢 **Channel:** {CHANNEL_USERNAME}\n'
        '📞 **Support:** @tradingword007'
    )

async def about_command(update: Update, context: CallbackContext):
    """Send about message."""
    user_id = update.effective_user.id
    
    # Check if user is verified
    if user_id not in user_status or not user_status[user_id]:
        await ask_to_join_channel(update, context)
        return
    
    await update.message.reply_text(
        '🤖 **About This Bot**\n\n'
        '✨ **Features:**\n'
        '• 1000+ websites से videos download\n'
        '• High quality videos\n'
        '• Fast download speed\n'
        '• User-friendly interface\n\n'
        '🛠 **Technology:**\n'
        '• Python Telegram Bot\n'
        '• yt-dlp library\n'
        '• Async programming\n\n'
        f'📢 **Channel:** {CHANNEL_USERNAME}\n'
        '👨‍💻 **Developer:** Rahul\n'
        '📅 **Version:** 3.0'
    )

async def download_video(update: Update, context: CallbackContext):
    """Download video from URL"""
    user_id = update.effective_user.id
    
    # Check if user is verified
    if user_id not in user_status or not user_status[user_id]:
        await ask_to_join_channel(update, context)
        return
    
    url = update.message.text.strip()
    
    # Check if it's a valid URL
    if not is_valid_url(url):
        await update.message.reply_text(
            "❌ **Invalid URL**\n\n"
            "कृपया एक valid video link भेजें।\n"
            "Example: https://www.youtube.com/watch?v=...\n\n"
            f"📢 Don't forget to join: {CHANNEL_USERNAME}"
        )
        return
    
    # Get video info first
    info_msg = await update.message.reply_text("🔍 Video information fetch कर रहा हूँ...")
    
    try:
        # Get video info without downloading
        ydl_info_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_info_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            info_text = (
                f"📹 **{info.get('title', 'Unknown Title')}**\n"
                f"👤 Uploader: {info.get('uploader', 'Unknown')}\n"
                f"⏱ Duration: {info.get('duration', 0)//60}:{info.get('duration', 0)%60:02d}\n"
                f"👁 Views: {info.get('view_count', 0):,}\n\n"
                f"📥 Download शुरू कर रहा हूँ...\n\n"
                f"📢 {CHANNEL_USERNAME}"
            )
            await info_msg.edit_text(info_text)
    except:
        await info_msg.edit_text("📥 Video download शुरू हो रहा है...")
    
    try:
        # Download options
        ydl_opts = {
            'format': 'best[filesize<50M]',  # 50MB से कम size वाला video
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title).100s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [lambda d: None],
        }
        
        # Download video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_title = info.get('title', 'video')
            video_file = ydl.prepare_filename(info)
            
            # Check if file exists
            if os.path.exists(video_file):
                # Get file size
                file_size = os.path.getsize(video_file)
                
                if file_size > 50 * 1024 * 1024:
                    await info_msg.edit_text(
                        f"⚠️ **File Too Large**\n\n"
                        f"File size: {file_size/(1024*1024):.1f}MB\n"
                        f"Telegram limit: 50MB\n\n"
                        "कृपया छोटे video का link भेजें।\n\n"
                        f"📢 {CHANNEL_USERNAME}"
                    )
                    os.remove(video_file)
                    return
                
                # Send video
                progress_msg = await update.message.reply_text(
                    f"📤 Uploading video... ({(file_size/(1024*1024)):.1f}MB)\n\n"
                    f"📢 {CHANNEL_USERNAME}"
                )
                
                try:
                    with open(video_file, 'rb') as video:
                        await update.message.reply_video(
                            video=video,
                            caption=f"🎬 **{video_title}**\n\n"
                                   f"✅ Successfully downloaded!\n"
                                   f"📊 Size: {(file_size/(1024*1024)):.1f}MB\n"
                                   f"🤖 @VideoDownloaderBot\n"
                                   f"📢 {CHANNEL_USERNAME}",
                            supports_streaming=True,
                            read_timeout=60,
                            write_timeout=60
                        )
                    await progress_msg.delete()
                    await info_msg.delete()
                    
                except Exception as send_error:
                    await info_msg.edit_text(
                        f"❌ Upload Error: {str(send_error)}\n\n"
                        f"📢 {CHANNEL_USERNAME}"
                    )
                
                # Clean up
                if os.path.exists(video_file):
                    os.remove(video_file)
            else:
                await info_msg.edit_text(
                    f"❌ Video download failed. File not found.\n\n"
                    f"📢 {CHANNEL_USERNAME}"
                )
                
    except yt_dlp.utils.DownloadError as e:
        await info_msg.edit_text(
            f"❌ Download Error: {str(e)}\n\n"
            f"📢 {CHANNEL_USERNAME}"
        )
    except Exception as e:
        await info_msg.edit_text(
            f"❌ Unknown Error: {str(e)}\n\n"
            f"📢 {CHANNEL_USERNAME}"
        )

async def error_handler(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    logger.error(f'Update {update} caused error {context.error}')

def main():
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the Bot
    print("=" * 50)
    print("✅ Video Downloader Bot Started Successfully!")
    print(f"📢 Channel: {CHANNEL_USERNAME}")
    print("🤖 Bot is now running...")
    print("📱 Users must join channel to use the bot")
    print("=" * 50)
    
    # Run the bot
    application.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES,
        close_loop=False
    )

if __name__ == '__main__':
    # Windows पर event loop policy सेट करें
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # Run the bot
    main()
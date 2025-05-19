import os
import logging
import re
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from telegram.constants import ChatType, MessageEntityType

# 配置日志
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 从环境变量获取 Token，如果没有则用默认值
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN_HERE")

# 维护提示信息
MAINTENANCE_MESSAGE = "🤖 机器人正在维护中，请稍后再试。"

class MaintenanceBot:
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理所有消息"""
        message = update.message
        user = update.effective_user

        if message.chat.type == ChatType.PRIVATE:
            # 私聊：直接回复
            await self.reply_maintenance(message)
        else:
            bot_username = context.bot.username
            if not bot_username:
                return

            # 群组：只响应 @mention
            mention_pattern = re.compile(rf"@{re.escape(bot_username)}", re.IGNORECASE)
            if mention_pattern.search(message.text):
                await self.reply_maintenance(message)

    async def reply_maintenance(self, message):
        """发送维护提示"""
        await message.reply_text(MAINTENANCE_MESSAGE)

    async def handle_all_commands(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """统一处理所有命令"""
        message = update.message
        await message.reply_text(MAINTENANCE_MESSAGE)

async def main():
    try:
        bot = MaintenanceBot()

        application = ApplicationBuilder() \
            .token(TELEGRAM_TOKEN) \
            .concurrent_updates(True) \
            .build()

        # 添加一个通用的消息处理器，匹配所有非命令文本
        text_handler = MessageHandler(
            filters.TEXT & ~filters.COMMAND &
            (filters.ChatType.PRIVATE | filters.Entity(MessageEntityType.MENTION)),
            bot.handle_message
        )

        # 添加一个命令处理器，匹配所有命令
        command_handler = MessageHandler(
            filters.COMMAND,
            bot.handle_all_commands
        )

        application.add_handlers([
            text_handler,
            command_handler
        ])

        logger.info("🔧 维护模式 Bot 启动中...")
        await application.initialize()
        await application.start()
        await application.updater.start_polling()

        # 保持主循环运行
        while True:
            await asyncio.sleep(3600)
    except Exception as e:
        logger.critical(f"致命错误: {str(e)}")
    finally:
        await application.stop()
        await application.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
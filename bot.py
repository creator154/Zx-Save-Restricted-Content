
# Don't Remove Credit Tg - @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import asyncio
from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN, STRING_SESSION, LOGIN_SYSTEM

TechVJUser = None


class Bot(Client):

    def __init__(self):
        super().__init__(
            "techvj login",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="TechVJ"),
            workers=150,
            sleep_threshold=5
        )

    async def start(self):
        global TechVJUser

        await super().start()

        if STRING_SESSION and not LOGIN_SYSTEM:
            TechVJUser = Client(
                "TechVJ",
                api_id=API_ID,
                api_hash=API_HASH,
                session_string=STRING_SESSION
            )

            try:
                await TechVJUser.start()
            except Exception:
                await super().stop()
                raise

        print("Bot Started Powered By @VJ_Bots")

    async def stop(self, *args):
        global TechVJUser

        try:
            if TechVJUser and TechVJUser.is_connected:
                await TechVJUser.stop()
                TechVJUser = None
        finally:
            try:
                if self.is_connected:
                    await super().stop()
            finally:
                print("Bot Stopped Bye")


if __name__ == "__main__":
    bot = Bot()
    bot.run()

# Don't Remove Credit Tg - @VJ_Bots

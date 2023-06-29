from collections import defaultdict
import os
import palm
from dotenv import load_dotenv
from datetime import datetime
import discord
from icecream import ic

# load from .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
channel_history = defaultdict(list[str])  # channel id, list of messages


def should_reply(client: discord.Client, message: discord.Message) -> bool:
    """Decides if Client should reply to a message

    Keyword arguments:
    client -- Discord Client
    message -- Discord message
    Return: Boolean if Client should reply
    """

    # Check permissions and if message is from bot
    if (
        message.author.bot
        or not message.channel.permissions_for(message.guild.me).send_messages
    ):
        return False

    return client.user.mentioned_in(message)


class Client(discord.Client):
    async def on_ready(self: discord.Client):
        print(f"Logged in as {self.user} (ID: {self.user.id})")

    async def on_message(self, message: discord.Message):
        if should_reply(self, message):
            # prepare and add to limit
            prepared_message = (
                f"{message.author.display_name}: {message.content.strip()}"
            )

            # insert into channel history
            channel_history[message.channel.id].append(prepared_message)

            try:
                reply = await palm.reply(channel_history[message.channel.id], self)

                bot_reply = f"{self.user.display_name}: {reply.strip()}"
                channel_history[message.channel.id].append(bot_reply)

                await message.reply(reply, mention_author=False)

            except Exception as e:
                ic(e)

                await message.reply(
                    "Uh oh, something went wrong, try again later!",
                    mention_author=False,
                )

                # pop last message
                channel_history[message.channel.id].pop()


def main():
    intents = discord.Intents.default()
    intents.message_content = True

    client = Client(intents=intents)
    client.run(TOKEN)


if __name__ == "__main__":
    main()

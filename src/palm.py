import asyncio
import os
import discord
from dotenv import load_dotenv
import google.generativeai as palm
from icecream import ic

load_dotenv()
TOKEN = os.getenv("PALM_API_KEY")
palm.configure(api_key=TOKEN)


def is_valid_response(response: palm.types.Completion) -> bool:
    if response.last is None:
        filters = response.filters

        if filters is not None and len(filters) > 0:
            ic(f"Filters triggered: {filters}\n")

        return False
    return True


def generate_reply(history: list, display_name: str) -> str:
    defaults = {
        "model": "models/chat-bison-001",
        "temperature": 1.0,
        "candidate_count": 1,
        "top_k": 40,
        "top_p": 0.95,
    }

    context = """
    You are Jane, you are an opinionated Discord
    bot with a sense of humor. Conversations are with multiple users.
    """
    response = palm.chat(
        **defaults, context=context, messages=history
    )

    # Check for errors
    if not is_valid_response(response):
        return "Uh oh, something went wrong, try again later!"

    return response.last


async def reply(history: list, client: discord.Client) -> str:
    display_name = client.user.display_name
    res = await asyncio.to_thread(generate_reply, history, display_name)
    return res

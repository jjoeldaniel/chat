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
    if response.result is None:
        filters = response.filters
        safety_feedback = response.safety_feedback

        err_res = ""

        if filters is not None and len(filters) > 0:
            err_res += f"Filters triggered: {filters}\n"

            if safety_feedback is not None and len(safety_feedback) > 0:
                err_res += f"Safety feedback triggered: {safety_feedback}\n"

        if err_res != "":
            ic(err_res)

        return False
    return True


def generate_reply(history: list, display_name: str) -> str:
    defaults = {
        "model": "models/text-bison-001",
        "temperature": 1.0,
        "candidate_count": 1,
        "top_k": 100,
        "top_p": 0.95,
        "max_output_tokens": 5120,
        "stop_sequences": [],
        "safety_settings": [
            {"category": "HARM_CATEGORY_DEROGATORY", "threshold": 3},
            {"category": "HARM_CATEGORY_TOXICITY", "threshold": 3},
            {"category": "HARM_CATEGORY_VIOLENCE", "threshold": 3},
            {"category": "HARM_CATEGORY_SEXUAL", "threshold": 3},
            {"category": "HARM_CATEGORY_MEDICAL", "threshold": 3},
            {"category": "HARM_CATEGORY_DANGEROUS", "threshold": 3},
        ],
    }

    message_history = "\n".join(history)

    prompt = f"""
    You are {display_name}, you are a highly opinionated
    chatbot with a sense of humor.

    Given this list of Discord messages,
    reply to the last message with a message of your own.

    {message_history}

    Reply: """

    response = palm.generate_text(**defaults, prompt=prompt)

    # Check for errors
    if not is_valid_response(response):
        return "Uh oh, something went wrong, try again later!"

    # Check if response includes own name
    first_word = response.result.split(" ")[0]
    if ":" in first_word:
        return response.result[len(first_word) + 1 :]

    return response.result


async def reply(history: list, client: discord.Client) -> str:
    display_name = client.user.display_name
    res = await asyncio.to_thread(generate_reply, history, display_name)
    return res

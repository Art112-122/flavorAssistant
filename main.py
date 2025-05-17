from functools import partial
from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from app.command import (
    BOT_START_COMMAND
)
from app.state import State_Reg
from app.connection import get_mysql_connection, create_tables
from dotenv import load_dotenv

import aiomysql
import asyncio
import json
import os
import logging
import sys
import cohere

load_dotenv()

dp = Dispatcher()

API_KEY = os.environ.get("API_KEY")

co = cohere.Client(API_KEY)

TOKEN = os.environ.get("BOT_TOKEN")

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


async def generate_async(prompt: str):
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        partial(co.generate, model="command", prompt=prompt, max_tokens=200)
    )
    return response


@dp.message(State_Reg.age)
async def age_reg(message: Message, state: FSMContext) -> None:
    try:
        age = int(message.text)
        try:
            connection = await get_mysql_connection()
            cursor = await connection.cursor()
            await cursor.execute("SELECT id FROM users WHERE user_id = %s;", (message.from_user.id,))
            resp = await cursor.fetchone()
            if isinstance(resp, tuple):
                try:
                    connection = await get_mysql_connection()
                    cursor: aiomysql.Cursor = await connection.cursor()
                    await cursor.execute(
                        """UPDATE users
                      SET name = %s, age = %s
                      WHERE user_id = %s;""",
                        (message.from_user.full_name, age, message.from_user.id)
                    )
                    await connection.commit()
                except aiomysql.Error as e:
                    await message.answer("Something gone wrong🤒")
                    raise e
                await message.answer(
                    f"Great! Reregistration completed! Let's find a movie, song, or book for you.\n"
                    f"For more accurate results, specify a genre!\n"
                    f"{html.bold('Example:')} Action film about vampires"
                    f"{html.bold('REMEMBER! Bot can make mistakes')}")
                await state.clear()
            else:
                try:
                    connection = await get_mysql_connection()
                    cursor: aiomysql.Cursor = await connection.cursor()
                    await cursor.execute(
                        """
                        INSERT INTO users (user_id, name, age)
                        VALUES (%s, %s, %s)
                        """,
                        (message.from_user.id, message.from_user.full_name, age)
                    )
                    await connection.commit()
                except aiomysql.Error as e:
                    await message.answer("Something gone wrong🤒")
                    raise e
                await message.answer(
                    f"Great! Registration completed! Let's find a movie, song, or book for you.\n"
                    f"For more accurate results, specify a genre!\n"
                    f"{html.bold('Example:')} Action film about vampires")
                await state.clear()
        except aiomysql.Error as e:
            raise e

    except ValueError:
        await message.answer("❌ This is not a whole number. Please enter an integer.")


@dp.message(F.text != "/start")
async def echo_handler(message: Message) -> None:
    try:
        connection = await get_mysql_connection()
        cursor = await connection.cursor()
        await cursor.execute("SELECT age FROM users WHERE user_id = %s;", (message.from_user.id,))
        age = await cursor.fetchone()
    except aiomysql.Error as e:
        await message.answer("Something gone wrong🤒")
        raise e
    try:
        prompt = (
            f"Find {message.text} for people aged {age} in STRICTLY VALID JSON format.\n"
            "Do not include explanations, markdown, or text around the JSON.\n"
            "Only return one object in this JSON list.\n"
            "Each object must have: title, genre, rating, description.\n"
            "Use only English. Format:\n"
            "[\n"
            "  {\n"
            "    \"title\": \"...(date)\",\n"
            "    \"genre\": \"...\",\n"
            "    \"rating\": \"1-10\",\n"
            "    \"description\": \"...\"\n"
            "  }\n"
            "]"
        )

        message_ans = await message.answer('Processing your request ⌛')

        response = await generate_async(prompt)

        await bot.delete_message(chat_id=message_ans.chat.id, message_id=message_ans.message_id)

        answer = json.loads(response.generations[0].text.strip())[0]
        await message.answer("So, I found something for you🔎:\n"
                             f"🎖     {html.bold(answer.get('title', 'Error❌'))}\n"
                             f"📂 Genre: {html.bold(answer.get('genre', 'Error❌'))}\n"
                             f"⭐ Rating: {html.bold(answer.get('rating', 'Error❌'))}/10\n"
                             f"📝 Description: {html.bold(answer.get('description', 'Error❌'))}")
    except json.JSONDecodeError:
        await message.answer("Bad request🤒. Try something else")


@dp.message(CommandStart)
async def start(message: Message, state: FSMContext) -> None:
    await message.answer(
        f"Hello, {html.italic(html.bold(message.from_user.full_name))}!\n"
        f"I'm a bot that will help you find movies, books, or songs!\n\n"
        f"I can recommend based on mood, time of day, and other criteria!")
    await asyncio.sleep(1)
    await message.answer("Let's configure the search options for you!")
    await asyncio.sleep(0.7)
    await state.set_state(State_Reg.age)
    await message.answer("How old are you?")


async def main() -> None:
    await bot.set_my_commands([
        BOT_START_COMMAND,
    ]
    )
    await create_tables()
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

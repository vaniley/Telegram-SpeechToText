import asyncio
import logging
import sys
from os import getenv, remove, mkdir

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile

from dotenv import load_dotenv
from openai import AsyncOpenAI


load_dotenv()
TOKEN = getenv("BOT_TOKEN")

client = AsyncOpenAI(
    api_key=getenv("OPENAI_API_KEY"),
    base_url=getenv("OPENAI_BASE_URL"),
)


dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(getenv("START_MASSAGE"))


@dp.message(F.voice)
async def voice_handler(message: Message) -> None:
    file_id = message.voice.file_id
    file = await message.bot.get_file(file_id)
    file_path = file.file_path

    file_name = f"voices/voice_{file_id}.ogg"
    await message.bot.download_file(file_path, file_name)

    try:
        with open(file_name, "rb") as audio_file:
            transcription = await client.audio.transcriptions.create(
                model=getenv("MODEL_NAME"), file=audio_file
            )
        await message.reply(transcription.text)
    finally:
        audio_file.close()
        try:
            remove(file_name)
        except PermissionError:
            ...


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        mkdir("voices")
    except:
        ...
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

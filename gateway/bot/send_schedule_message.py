from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from .states import EnterData
from .start import dispatcher, bot


async def get_chat_id(username):
    chat = await bot.get_chat(chat_id=username)

    await bot.send_message(
        chat_id=chat.id,
        text="""Всем привет,я буду присылать сюда уведомления о проведении хакатона, можете не благодарить
        """
    )

    return chat


@dispatcher.message(Command(commands=["start"]))
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="""Если еще не добавили бота в канал, добавьте
Отправьте название канала в формате: @название_канала\n
             """
    )

    await state.set_state(EnterData.get_id)


@dispatcher.message(EnterData.get_id)
async def chat_id_handler(message: types.Message, state: FSMContext):
    if "@" in message.text:
        await message.answer(
            text="""
            Получаем информацию о канале...
            """
        )
        chat = await get_chat_id(message.text)
        await state.update_data(channel_name=message.text)
        await state.update_data(channel_id=chat.id)
        await state.clear()
        await message.answer(
            text="""
            Канал успешно добавлен, дальше я все сделаю сам :)
            """
        )
        # Здесь нужно сохранять chat_id channel_name в бд, чтобы потом забирая отложенное сообщение с бд send_schedule_message
        # отправляла его в конкретный чат

        await send_schedule_message("hello", chat.id)
    else:
        await message.answer(
            text="""
                Пожалуйста введите корректное название канала
            """
        )


async def send_schedule_message(message, chat_id):
    await bot.send_message(chat_id=chat_id, text=message)

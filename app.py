import aiogram
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
import asyncio
import config
import database
import messages


bot_token = config.getToken()
bot = aiogram.Bot(token=bot_token)
dp = aiogram.Dispatcher()
channel_id = config.getChannel()
db = database.Database()
action = ""
message_buff = []


def get_main_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👋 Без подписки", callback_data="hello"),
                InlineKeyboardButton(text="👋 С подпиской", callback_data="hellosub"),
            ],
            [
                InlineKeyboardButton(text="📢 Рассылка", callback_data="send"),
                InlineKeyboardButton(text="📊 Статистика", callback_data="stats"),
            ],
            [
                InlineKeyboardButton(text="📥 Установленные сообщения", callback_data="info")
            ]
        ]
    )
    return keyboard


def get_confirm_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Подтвердить", callback_data="accept"),
                InlineKeyboardButton(text="❌ Отменить", callback_data="decline"),
            ]
        ]
    )
    return keyboard


def admin_required(func):
    async def wrapper(message):
        if message.from_user.username not in config.getAdm():
            return await message.answer(f"Привет! Я всего лишь бот - можешь написать /start.\nПо конкретным вопросам пиши Максу лично: @{config.getAdm()[0]}")
        elif config.getAdmChat() == "":
            config.setAdmChat(message.from_user.id)
        return await func(message)
    return wrapper


@dp.callback_query(lambda c: c.data.startswith("check_"))
async def start_callback(callback: aiogram.types.CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    if await check_sub(user_id) == True:
        await sendMessages(messages.getMessageWSub(), user_id)
        return 
    else: await callback.answer("❌ Вы не подписаны", show_alert=True)


@dp.callback_query()
@admin_required
async def handle_callback(callback: aiogram.types.CallbackQuery):
    global action, message_buff
    
    match callback.data:
        case "info":
            await callback.message.answer(
                "📌 Приветственный текст для подписчиков (hellosub):"
            )
            await sendMessages(messages.getMessageWSub(), int(config.getAdmChat()))
            await callback.message.answer(
                "📌 Приветственный текст для новых пользователей (hello):"
            )
            await sendMessages(messages.getMessageWNoSub(), int(config.getAdmChat()))

        case "hellosub":
            await callback.message.answer(
                "Вы в режиме hellosub!\nОтправьте сообщения, которые будут отправляться новым пользователям с подпиской",
                reply_markup=get_confirm_keyboard()
            )
            action = "hellosub"
            message_buff.clear()
            
        case "hello":
            await callback.message.answer(
                "Вы в режиме hello!\nОтправьте сообщения, которые будут отправляться новым пользователям без подписки",
                reply_markup=get_confirm_keyboard()
            )
            action = "hello"
            message_buff.clear()
            
        case "send":
            await callback.message.answer(
                "Вы в режиме send!\nОтправьте сообщения, которые хотите отправить всем подписчикам канала",
                reply_markup=get_confirm_keyboard()
            )
            action = "send"
            message_buff.clear()
            
        case "accept":
            match action:
                case "hellosub":
                    messages.setMessageWSub(message_buff)
                    message_buff.clear()
                    action = ""
                    await callback.message.answer("✅ Сообщения сохранены!")
                    
                case "hello":
                    messages.setMessageWNoSub(message_buff)
                    message_buff.clear()
                    action = ""
                    await callback.message.answer("✅ Сообщения сохранены!")
                    
                case "send":
                    usrs = db.get_all_users()
                    users_list = [usr["chat_id"] for usr in usrs if usr.get("user_tag") != config.getAdm()]
                    await sendMessages(message_buff, users_list)
                    message_buff.clear()
                    action = ""
                    await callback.message.answer(f"✅ Сообщения отправлены {len(users_list)} пользователям!")
                    
                case _:
                    await callback.message.answer(f"Неизвестное действие: {action}")
            
        case "decline":
            await callback.message.answer("❌ Команда отменена.")
            action = ""
            message_buff.clear()
            
        case "stats":
            all_users = db.get_all_users()
            total_users = len(all_users)
            subscribed = len([u for u in all_users if u.get("subscribe")])
            await callback.message.answer(
                f"📊 Статистика:\n"
                f"Всего пользователей: {total_users}\n"
                f"Подписаны на канал: {subscribed}\n"
                f"Не подписаны: {total_users - subscribed}"
            )
    
    await callback.answer()


@dp.message(Command("hellosub"))
@admin_required
async def helloSubMessageCommand(message: aiogram.types.Message):
    await message.answer(
        "Вы в режиме /hellosub!\nОтправьте сообщения, которые будут отправляться новым пользователям с подпиской",
        reply_markup=get_confirm_keyboard()
    )
    global action
    action = "hellosub"
    message_buff.clear()


@dp.message(Command("hello"))
@admin_required
async def helloMessageCommand(message: aiogram.types.Message):
    await message.answer(
        "Вы в режиме /hello!\nОтправьте сообщения, которые будут отправляться новым пользователям без подписки",
        reply_markup=get_confirm_keyboard()
    )
    global action
    action = "hello"
    message_buff.clear()


@dp.message(Command("send"))
@admin_required
async def sendMessageCommand(message: aiogram.types.Message):
    await message.answer(
        "Вы в режиме /send!\nОтправьте сообщения, которые хотите отправить всем подписчикам канала",
        reply_markup=get_confirm_keyboard()
    )
    global action
    action = "send"
    message_buff.clear()


@dp.message(Command("accept"))
@admin_required
async def acceptMessageCommand(message: aiogram.types.Message):
    global action, message_buff
    match action:
        case "hellosub":
            messages.setMessageWSub(message_buff)
            message_buff.clear()
            action = ""
            await message.answer("✅ Сообщения сохранены!")
        case "hello":
            messages.setMessageWNoSub(message_buff)
            message_buff.clear()
            action = ""
            await message.answer("✅ Сообщения сохранены!")
        case "send":
            usrs = db.get_all_users()
            users_list = [usr["chat_id"] for usr in usrs if usr.get("user_tag") != config.getAdm()]
            await sendMessages(message_buff, users_list)
            message_buff.clear()
            action = ""
            await message.answer(f"✅ Сообщения отправлены {len(users_list)} пользователям!")
        case _:
            await message.answer(f"Неизвестное действие: {action}")


@dp.message(Command("decline"))
@admin_required
async def declineMessageCommand(message: aiogram.types.Message):
    await message.answer("❌ Команда отменена.")
    global action
    action = ""
    message_buff.clear()


@dp.message(Command("menu"))
@admin_required
async def show_menu(message: aiogram.types.Message):
    await message.answer(
        "📱 Главное меню администратора:\nВыберите действие:",
        reply_markup=get_main_keyboard()
    )


@dp.message(lambda message: not message.text or not message.text.startswith('/'))
@admin_required
async def handle_source_message(message: aiogram.types.Message):
    global message_buff
    if action != "":
        message_buff.append(message.message_id)


@dp.message(Command("start"))
async def startCommand(message: aiogram.types.Message):
    subscribed = await check_sub(message.from_user.id)
    db.add_user(message.from_user.username, message.from_user.id, subscribed)
    
    if subscribed:
        await sendMessages(messages.getMessageWSub(), message.from_user.id)
    else:
        await sendMessages(messages.getMessageWNoSub(), message.from_user.id)
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📢 Подписаться на канал", url=f"{config.getChannelLink()}")],
                [InlineKeyboardButton(text="🔄 Проверить подписку", callback_data=f"check_{message.from_user.id}")]
            ]
        )
        await message.answer("Подпишись и нажми кнопку ниже 👇", reply_markup=keyboard)
        

async def check_sub(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(channel_id, user_id)
        if member.status not in ['member', 'administrator', 'creator']:
            return False
        return True
    except Exception as e:
        print(f"Ошибка при проверке подписки: {e}")
        return False


async def sendMessages(msgs: list, users):
    adm_chat = config.getAdmChat()
    
    if not msgs:
        print("Нет сообщений для отправки")
        return
    
    if isinstance(users, int):
        users_list = [users]
    else:
        users_list = users
    
    for user in users_list:
        try:
            await bot.copy_messages(
                chat_id=user,
                from_chat_id=adm_chat,
                message_ids=msgs
            )
        except Exception as e:
            print(f"Ошибка при отправке сообщения пользователю {user}: {e}")


async def main():
    print("Бот запущен и готов к работе!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
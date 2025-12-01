from aiogram import Router
from aiogram.types import Message
from utils.members import (
    add_member, update_member_name, load_members, set_active,
    make_circle, set_active_by_name, get_active_mentions,
    update_member_birthday, list_birthdays, get_birthdays_today
)   
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.letters import load_letter_state, save_letter_state, send_letter_assignments
from aiogram import F, types


router = Router()

def render_letter_keyboard(chat_id):
    members = load_members(chat_id)
    state = load_letter_state(chat_id)
    selected = state.get("selected", [])

    buttons = []
    for m in members:
        name = m["name"]
        tid = str(m["telegram_id"])
        active = tid in selected
        emoji = "☀️" if active else "🌙"
        buttons.append([InlineKeyboardButton(text=f"{emoji} {name}", callback_data=f"toggle_{tid}")])

    buttons.append([InlineKeyboardButton(text="Подтвердить", callback_data="confirm_letters")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@router.callback_query(F.data.startswith("toggle_"))
async def toggle_participant(callback_query: types.CallbackQuery):
    chat_id = callback_query.message.chat.id
    tid = callback_query.data.split("_")[1]
    state = load_letter_state(chat_id)
    selected = state.get("selected", [])

    if tid in selected:
        selected.remove(tid)
    else:
        selected.append(tid)

    save_letter_state(chat_id, {"selected": selected})
    await callback_query.answer("Выбор обновлён.")
    keyboard = render_letter_keyboard(chat_id)
    await callback_query.message.edit_reply_markup(reply_markup=keyboard)


@router.callback_query(F.data == "confirm_letters")
async def confirm_letters(callback_query: types.CallbackQuery):
    chat_id = callback_query.message.chat.id
    state = load_letter_state(chat_id)
    selected = state.get("selected", [])
    members = {str(m["telegram_id"]): m["name"] for m in load_members(chat_id)}

    if len(selected) < 2:
        await callback_query.answer("Нужно минимум 2 участницы.")
        return

    success = await send_letter_assignments(callback_query.bot, chat_id, members, selected)
    if success:
        await callback_query.message.edit_text("Сообщения разосланы!")
    else:
        await callback_query.message.edit_text("Не удалось распределить пары")

@router.message()
#async def debug_chat_id(message: Message):
 #   await message.answer(f"ID этой группы: {message.chat.id}")

async def handle_all(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    name = message.from_user.first_name
    text = message.text.strip()

    added = add_member(chat_id, user_id, name)
    if added:
        await message.reply(f"{name}, ты добавлена в молитвенный круг! Добро пожаловать в семью❤️")


    if text.startswith("/name"):
        name_text = text.replace("/name", "").strip()
        if not name_text:
            await message.answer("Напиши своё имя после команды. Например:\n<code>/name (укажи желаеммое имя)</code>")
        else:
            updated = update_member_name(chat_id, user_id, name_text)
            if updated:
                await message.answer(f"Имя обновлено! Теперь ты — {name_text}")
            else:
                await message.answer("Ты ещё не в списке. Напиши что-нибудь в группе, чтобы я тебя добавил.")

    if text == "/list":
        
        print("Команда /mdkd получена")
        members = load_members(chat_id) 
        text = "<b>Список участниц:</b>\n\n"
        for m in members:
            name = m["name"] or "— без имени —"
            status = "☀️" if m.get("active", True) else "🌙"
            text += f"• {name} {status}\n"
        await message.answer(text)


    if text == "/pray":
        circle = make_circle(chat_id)

        if not circle:
            await message.answer("Нужно минимум 2 участницы")
            return

        text = "<b>Молитвенный круг этой недели:</b>\n\n"
        for giver, receiver in circle:
            text += f"• {giver} молится за {receiver}\n"
        await message.answer(text)

    if text == "/inactive":
        updated = set_active(chat_id, user_id, False)
        if updated:
            await message.answer("Ты временно исключена из круга. Отдыхай спокойно.")
        else:
            await message.answer("Ты ещё не в списке. Напиши что-нибудь в группе, чтобы я тебя добавил.")

    if text == "/active":
        updated = set_active(chat_id, user_id, True)
        if updated:
            await message.answer("Добро пожаловать обратно в круг! Ты снова активна.")
        else:
            await message.answer("Ты ещё не в списке. Напиши что-нибудь в группе, чтобы я тебя добавил.")

    if text.startswith("/lull"):
        parts = text.split()
        if len(parts) < 2:
            await message.answer("Укажи имя участницы: /lull имя)")
            return

        target_name = parts[1].lstrip("@")
        success = set_active_by_name(chat_id, target_name, False)
        if success:
            await message.answer(f"{target_name} теперь неактивна и временно исключена из круга.")
        else:
            await message.answer(f"Не удалось найти участницу с именем {target_name}.")

    if text.startswith("/wakeup"):
        parts = text.split()
        if len(parts) < 2:
            await message.answer("Укажи имя участницы: /wakeup имя")
            return

        target_name = parts[1].lstrip("@")
        success = set_active_by_name(chat_id, target_name, True)
        if success:
            await message.answer(f"{target_name} снова активна и участвует в круге.")
        else:
            await message.answer(f"Не удалось найти участницу с именем {target_name}.")


    if text == "/all":
        mentions = get_active_mentions(chat_id)
        if not mentions:
            await message.answer("Список участниц пуст.")
            return
        call_text = (
       ", ".join([f" {m}" for m in mentions])

        )
        await message.answer(call_text, parse_mode="HTML")

    if text == "/letters":
        members = load_members(chat_id)
        state = load_letter_state(chat_id)
        selected = state.get("selected", [])

        if not members:
            await message.answer("Список участниц пуст.")
            return

        buttons = []
        for m in members:
            name = m["name"]
            tid = str(m["telegram_id"])
            active = tid in selected
            emoji = "☀️" if active else "🌙"
            buttons.append([InlineKeyboardButton(text=f"{emoji} {name}", callback_data=f"toggle_{tid}")])

        buttons.append([InlineKeyboardButton(text="Подтвердить", callback_data="confirm_letters")])
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

        await message.answer("Выбери участниц:", reply_markup=keyboard)

    if text.startswith("/birthday"):
            parts = text.split()
            if len(parts) < 2:
                await message.answer("Укажи дату в формате ДД-ММ. Например: /birthday 01-12")
            else:
                bday = parts[1]
                updated = update_member_birthday(chat_id, user_id, bday)
                if updated:
                    await message.answer(f"Дата рождения сохранена: {bday}")
                else:
                    await message.answer("Ты ещё не в списке. Напиши что-нибудь в группе, чтобы я тебя добавил.")

    if text == "/listofbirthdays":
            bdays = list_birthdays(chat_id)
            if bdays:
                await message.answer("<b>Дни рождения:</b>\n" + "\n".join(bdays))
            else:
                await message.answer("Дни рождения ещё не сохранены.")

    if text == "/today":
            today_birthdays = get_birthdays_today(chat_id)
            if today_birthdays:
                for m in today_birthdays:
                    await message.answer(f"🎉 Сегодня день рождения у {m['name']}! Давайте её поздравим!🌸")
            else:
                await message.answer("Сегодня ни у кого нет дня рождения.")




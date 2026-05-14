import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# --- SOZLAMALAR ---
API_TOKEN = '8622338016:AAH1aGyovhrZyZVZRWIOj59x_oDP1tFFMsU'
ADMIN_ID = 6589997966

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


class OrderUC(StatesGroup):
    waiting_for_id = State()
    waiting_for_photo = State()


def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.button(text="💎 UC Narxlari")
    builder.button(text="👨‍💻 Bog'lanish")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


def uc_prices_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="60 UC - 12 000 so'm", callback_data="buy_60UC"))
    builder.row(types.InlineKeyboardButton(text="325 UC - 55 000 so'm", callback_data="buy_325UC"))
    builder.row(types.InlineKeyboardButton(text="660 UC - 105 000 so'm", callback_data="buy_660UC"))
    return builder.as_markup()


@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        f"Salom {message.from_user.full_name}! PUBG Mobile UC botiga xush kelibsiz.",
        reply_markup=main_menu()
    )


@dp.message(F.text == "💎 UC Narxlari")
async def show_prices(message: types.Message):
    payment_info = (
        "<b>💳 To'lov uchun karta ma'lumotlari:</b>\n\n"
        "🔢 Karta: <code>5614681911018624</code>\n"
        "(Raqam ustiga bossangiz nusxalanadi)\n\n"
        "👤 Ega: <b>Masharipov Quvondiq</b>\n"
        "🏦 Bank: <b>NBU (Milliy Bank)</b>\n\n"
        "⚠️ To'lovni qiling, paketni tanlang va chekni yuboring!"
    )
    await message.answer(payment_info, parse_mode="HTML")
    await message.answer("Sotib olmoqchi bo'lgan paketni tanlang:",
                         reply_markup=uc_prices_keyboard())


@dp.callback_query(F.data.startswith("buy_"))
async def process_buy(callback: types.CallbackQuery, state: FSMContext):
    package = callback.data.split("_")[1]
    await state.update_data(chosen_package=package)
    await callback.message.answer(f"Siz <b>{package}</b> tanladingiz.\n\nIltimos, PUBG ID yuboring:", parse_mode="HTML")
    await state.set_state(OrderUC.waiting_for_id)
    await callback.answer()


@dp.message(OrderUC.waiting_for_id)
async def process_id(message: types.Message, state: FSMContext):
    if message.text and message.text.isdigit():
        await state.update_data(pubg_id=message.text)
        await message.answer("To'lov cheki rasmini (screenshot) yuboring:")
        await state.set_state(OrderUC.waiting_for_photo)
    else:
        await message.answer("⚠️ Faqat raqamlardan iborat PUBG ID yuboring!")


@dp.message(OrderUC.waiting_for_photo, F.photo)
async def process_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    package = data.get("chosen_package")
    pubg_id = data.get("pubg_id")
    user = message.from_user

    admin_text = (
        f"🔔 <b>YANGI BUYURTMA!</b>\n\n"
        f"📦 Paket: <b>{package}</b>\n"
        f"🆔 PUBG ID: <code>{pubg_id}</code>\n"
        f"👤 Kimdan: @{user.username or 'No Username'}\n"
        f"🔢 User ID: <code>{user.id}</code>"
    )

    try:
        await bot.send_photo(ADMIN_ID, photo=message.photo[-1].file_id, caption=admin_text, parse_mode="HTML")
        await message.answer("✅ Rahmat! Buyurtma adminga yuborildi. 15 daqiqa ichida UC tushadi va admin xabar qiladi.", reply_markup=main_menu())
    except Exception as e:
        await message.answer("❌ Xatolik yuz berdi.")
        print(f"Xato: {e}")

    await state.clear()


@dp.message(F.text == "👨‍💻 Bog'lanish")
async def contact(message: types.Message):
    await message.answer("Savollar bo'yicha operator: @Karimov_0912")


async def main():
    print("Bot muvaffaqiyatli ishga tushdi!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

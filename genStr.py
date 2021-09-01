import asyncio

from bot import bot, HU_APP
from pyromod import listen
from asyncio.exceptions import TimeoutError

from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    SessionPasswordNeeded, FloodWait,
    PhoneNumberInvalid, ApiIdInvalid,
    PhoneCodeInvalid, PhoneCodeExpired
)

API_TEXT = """Hi Bro, {}.
Ini adalah Bot Pembangkit Sesi String Pyrogram Bro. Saya akan menghasilkan Sesi String dari Akun Telegram Anda.

By @Update_Grouppp

Sekarang kirim `API_ID` lu bro yang sama dengan `APP_ID` ​​untuk Memulai Sesi Pembuatan."""
HASH_TEXT = "Sekarang kirim `API_HASH`.\n\nPress /batal ke Batalkan Tugas."
PHONE_NUMBER_TEXT = (
    "Sekarang kirim nomor telepon akun Telegram lu bro dalam Format Internasional. \n"
    "Termasuk kode negara. Example: **+14154566376**\n\n"
    "Tekan /batal untuk Membatalkan Tugas."
)

@bot.on_message(filters.private & filters.command("start"))
async def genStr(_, msg: Message):
    chat = msg.chat
    api = await bot.ask(
        chat.id, API_TEXT.format(msg.from_user.mention)
    )
    if await is_cancel(msg, api.text):
        return
    try:
        check_api = int(api.text)
    except Exception:
        await msg.reply("`API_ID` is Invalid.\nPress /start to Start again.")
        return
    api_id = api.text
    hash = await bot.ask(chat.id, HASH_TEXT)
    if await is_cancel(msg, hash.text):
        return
    if not len(hash.text) >= 30:
        await msg.reply("`API_HASH` is Invalid.\nPress /start to Start again.")
        return
    api_hash = hash.text
    while True:
        number = await bot.ask(chat.id, PHONE_NUMBER_TEXT)
        if not number.text:
            continue
        if await is_cancel(msg, number.text):
            return
        phone = number.text
        confirm = await bot.ask(chat.id, f'`nomorlu bro "{phone}" udahbener? (y/n):` \n\nkirim: `y` (kalo emangbener)\nkirim: `n` (kalo salah)')
        if await is_cancel(msg, confirm.text):
            return
        if "y" in confirm.text:
            break
    try:
        client = Client("my_account", api_id=api_id, api_hash=api_hash)
    except Exception as e:
        await bot.send_message(chat.id ,f"**ERROR:** `{str(e)}`\nPress /mulai ulang Bro.")
        return
    try:
        await client.connect()
    except ConnectionError:
        await client.disconnect()
        await client.connect()
    try:
        code = await client.send_code(phone)
        await asyncio.sleep(1)
    except FloodWait as e:
        await msg.reply(f"You have Floodwait of {e.x} Seconds")
        return
    except ApiIdInvalid:
        await msg.reply("API ID and API Hash are Invalid.\n\nPress /start mulai ulang Bro.")
        return
    except PhoneNumberInvalid:
        await msg.reply("Your Phone Number is Invalid.\n\nPress /start mulai ulang Bro.")
        return
    try:
        otp = await bot.ask(
            chat.id, ("OTP dikirim ke nomor telepon lu bro, "
                      "masukan OTP nya bro contoh `1 2 3 4 5` format. __(kasih Spasi di antara setiap angka!)__ \n\n"
                      "Jika bot tidak mengirim OTP Coba  /restart dan Mulai Tugas lagi dengan /start command to Bot.\n"
                      "Press /cancel to Cancel."), timeout=300)

    except TimeoutError:
        await msg.reply("Time limit reached of 5 min.\nPress /start to Start again.")
        return
    if await is_cancel(msg, otp.text):
        return
    otp_code = otp.text
    try:
        await client.sign_in(phone, code.phone_code_hash, phone_code=' '.join(str(otp_code)))
    except PhoneCodeInvalid:
        await msg.reply("Invalid Code.\n\nPress /start to Start again.")
        return
    except PhoneCodeExpired:
        await msg.reply("Code is Expired.\n\nPress /start to Start again.")
        return
    except SessionPasswordNeeded:
        try:
            two_step_code = await bot.ask(
                chat.id, 
                "Jangan kasih Verifikasi Dua Langkah Bro.\nSilakan masukkan Kata Sandi Anda.\n\nTekan /cancel to Cancel.",
                timeout=300
            )
        except TimeoutError:
            await msg.reply("`Batas waktu tercapai 5 menit.\n\nTekan /start mulai ulang bro.`")
            return
        if await is_cancel(msg, two_step_code.text):
            return
        new_code = two_step_code.text
        try:
            await client.check_password(new_code)
        except Exception as e:
            await msg.reply(f"**ERROR:** `{str(e)}`")
            return
    except Exception as e:
        await bot.send_message(chat.id ,f"**ERROR:** `{str(e)}`")
        return
    try:
        session_string = await client.export_session_string()
        await client.send_message("me", f"#PYROGRAM #STRING_SESSION\n\n```{session_string}``` \n\nBy [@StringSessionGen_Bot](tg://openmessage?user_id=1472531255) \nA Bot By @Update_Grouppp")
        await client.disconnect()
        text = "String Session is Successfully Generated.\nClick on Below Button."
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="Show String Session", url=f"tg://openmessage?user_id={chat.id}")]]
        )
        await bot.send_message(chat.id, text, reply_markup=reply_markup)
    except Exception as e:
        await bot.send_message(chat.id ,f"**ERROR:** `{str(e)}`")
        return


@bot.on_message(filters.private & filters.command("restart"))
async def restart(_, msg: Message):
    await msg.reply("Restarted Bot!")
    HU_APP.restart()


@bot.on_message(filters.private & filters.command("help"))
async def restart(_, msg: Message):
    out = f"""
Hi, {msg.from_user.mention}. This is Pyrogram Session String Generator Bot. \
I will give you `STRING_SESSION` for your UserBot.

It needs `API_ID`, `API_HASH`, Phone Number and One Time Verification Code. \
Which will be sent to your Phone Number.
You have to put **OTP** in `1 2 3 4 5` this format. __(Space between each numbers!)__

**NOTE:** If bot not Sending OTP to your Phone Number than send /restart Command and again send /start to Start your Process. 

Must Join Channel for Bot Updates !!
"""
    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton('Support Group', url='https://t.me/Update_Grouppp'),
                InlineKeyboardButton('Developer', url='https://t.me/zaenmad')
            ],
            [
                InlineKeyboardButton('Bots Updates Channel', url='https://t.me/Musicdenzchannel'),
            ]
        ]
    )
    await msg.reply(out, reply_markup=reply_markup)


async def is_cancel(msg: Message, text: str):
    if text.startswith("/cancel"):
        await msg.reply("Process Cancelled.")
        return True
    return False

if __name__ == "__main__":
    bot.run()

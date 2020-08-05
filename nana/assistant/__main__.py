import os
import time
from platform import python_version

import heroku3
from pyrogram import (
    Filters,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    errors,
    ReplyKeyboardMarkup,
)

from nana import (
    app,
    setbot,
    AdminSettings,
    DB_AVAILABLE,
    USERBOT_VERSION,
    ASSISTANT_VERSION,
    BotUsername,
    HEROKU_API,
    Owner,
    OwnerName,
    NANA_IMG,
)
from nana.__main__ import reload_userbot, restart_all


if DB_AVAILABLE:
    from nana.assistant.database.stickers_db import set_sticker_set, set_stanim_set
    from nana.modules.database.chats_db import get_all_chats


@setbot.on_message(Filters.private & ~Filters.user(AdminSettings))
async def un_auth(_client, message):
    if message.chat.id is not AdminSettings:
        msg = f"""
Hi {message.chat.first_name},
You must be looking forward on how I work.
In that case I can give you helpful links to self host me on your own.
Here are some links for you
        """
        buttons = [
            [
                InlineKeyboardButton(
                    "Documentation", url="https://aman-a.gitbook.io/nana-remix/"
                )
            ],
            [
                InlineKeyboardButton(
                    "Repository", url="https://github.com/pokurt/Nana-Remix"
                ),
                InlineKeyboardButton("Support", url="https://t.me/nanabotsupport"),
            ],
        ]
        await message.reply(msg, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        return


@setbot.on_message(Filters.user(AdminSettings) & Filters.command(["start"]))
async def start(_client, message):
    if message.chat.type != "private":
        await message.reply(f"こんにちは, {OwnerName}! ^_^")
        return
    if len(message.text.split()) >= 2:
        helparg = message.text.split()[1]
        if helparg == "help_inline":
            await message.reply(
                """**Inline Guide**
Just type `@{} (command)` in text box, and wait for response.

──「 **Get Note from Inline** 」──
-> `#note <*notetag>`
And wait for list of notes in inline, currently support Text and Button only.

──「 **Stylish Generator Inline** 」──
-> `#stylish your text`
Convert a text to various style, can be used anywhere!

* = Can be used as optional
""".format(
                    BotUsername
                )
            )
            return
    try:
        me = await app.get_me()
    except ConnectionError:
        me = None
    start_message = f"Hi {OwnerName},\n"
    start_message += "Nana is Ready at your Service!\n"
    start_message += "===================\n"
    start_message += "-> Python: `{}`\n".format(python_version())
    if not me:
        start_message += "-> Userbot: `Stopped (v{})`\n".format(USERBOT_VERSION)
    else:
        start_message += "-> Userbot: `Running (v{})`\n".format(USERBOT_VERSION)
    start_message += "-> Assistant: `Running (v{})`\n".format(ASSISTANT_VERSION)
    start_message += "-> Database: `{}`\n".format(DB_AVAILABLE)
    if DB_AVAILABLE:
        start_message += f"-> Group joined: `{len(get_all_chats())} groups`\n"
    start_message += "===================\n"
    start_message += "`For more about the bot press button down below`"
    buttons = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text="Help", callback_data="help_back")]]
    )
    if NANA_IMG:
        await setbot.send_photo(
            Owner, NANA_IMG, caption=start_message, reply_markup=buttons
        )
    else:
        await setbot.send_message(Owner, start_message, reply_markup=buttons)


@setbot.on_message(Filters.user(Owner) & Filters.command(["getme"]))
async def get_myself(client, message):
    try:
        me = await app.get_me()
    except ConnectionError:
        message.reply("Bot is currently turned off!")
        return
    getphoto = await client.get_profile_photos(me.id)
    getpp = None if len(getphoto) == 0 else getphoto[0].file_id
    text = "**ℹ️ Your profile:**\n"
    text += "First name: {}\n".format(me.first_name)
    if me.last_name:
        text += "Last name: {}\n".format(me.last_name)
    text += "User ID: `{}`\n".format(me.id)
    if me.username:
        text += "Username: @{}\n".format(me.username)
    text += "Phone number: `{}`\n".format(me.phone_number)
    text += "`Nana Version    : v{}`\n".format(USERBOT_VERSION)
    text += "`Manager Version : v{}`".format(ASSISTANT_VERSION)
    button = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Hide phone number", callback_data="hide_number")]]
    )
    if me.photo:
        await client.send_photo(
            message.chat.id, photo=getpp, caption=text, reply_markup=button
        )
    else:
        await message.reply(text, reply_markup=button)


@setbot.on_message(
    Filters.user(Owner) & Filters.command(["settings"]) & Filters.private
)
async def settings(_client, message):
    try:
        me = await app.get_me()
    except ConnectionError:
        me = None
    text = "**⚙️ Welcome to Nana Settings!**\n"
    if not me:
        text += "-> Userbot: `Stopped (v{})`\n".format(USERBOT_VERSION)
    else:
        text += "-> Userbot: `Running (v{})`\n".format(USERBOT_VERSION)
    text += "-> Assistant: `Running (v{})`\n".format(ASSISTANT_VERSION)
    text += "-> Database: `{}`\n".format(DB_AVAILABLE)
    text += "-> Python: `{}`\n".format(python_version())
    text += "\nJust setup what you need here"
    list_button = [
        [
            InlineKeyboardButton("Stop Bot", callback_data="toggle_startbot"),
            InlineKeyboardButton("Restart Bot", callback_data="restart_bot"),
        ],
        [InlineKeyboardButton("Set Sticker", callback_data="setsticker")],
    ]
    if HEROKU_API:
        list_button.append(
            [InlineKeyboardButton("Heroku Config Vars", callback_data="heroku_vars")]
        )
        list_button.append(
            [InlineKeyboardButton("Restart Heroku app", callback_data="restart_heroku")]
        )
        list_button.append(
            [InlineKeyboardButton("Change Repo Source", callback_data="change_repo")]
        )
    button = InlineKeyboardMarkup(list_button)
    await message.reply(text, reply_markup=button)


# For callback query button
def dynamic_data_filter(data):
    return Filters.create(
        lambda flt, query: flt.data == query.data,
        data=data,  # "data" kwarg is accessed with "flt.data" above
    )


@setbot.on_callback_query(dynamic_data_filter("hide_number"))
async def get_myself_btn(client, query):
    try:
        me = await app.get_me()
    except ConnectionError:
        await client.answer_callback_query(
            query.id, "Bot is currently turned off!", show_alert=True
        )
        return

    if query.message.caption:
        text = query.message.caption.markdown
    else:
        text = query.message.text.markdown

    num = ["*" * len(me.phone_number)]
    if "***" not in text.split("Phone number: `")[1].split("`")[0]:
        text = text.replace(
            "Phone number: `{}`\n".format(me.phone_number),
            "Phone number: `{}`\n".format("".join(num)),
        )
        button = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Show phone number", callback_data="hide_number")]]
        )
    else:
        text = text.replace(
            "Phone number: `{}`\n".format("".join(num)),
            "Phone number: `{}`\n".format(me.phone_number),
        )
        button = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Hide phone number", callback_data="hide_number")]]
        )

    if query.message.caption:
        await query.message.edit_caption(caption=text, reply_markup=button)
    else:
        await query.message.edit(text, reply_markup=button)


@setbot.on_callback_query(dynamic_data_filter("toggle_startbot"))
async def start_stop_bot(client, query):
    try:
        pass
    except ConnectionError:
        await reload_userbot()
        text = "**⚙️ Welcome to Nana Settings!**\n"
        text += "-> Userbot: `Running (v{})`\n".format(USERBOT_VERSION)
        text += "-> Assistant: `Running (v{})`\n".format(ASSISTANT_VERSION)
        text += "-> Database: `{}`\n".format(DB_AVAILABLE)
        text += "-> Python: `{}`\n".format(python_version())
        text += "\n✅ Bot was started!"
        list_button = [
            [
                InlineKeyboardButton("Stop Bot", callback_data="toggle_startbot"),
                InlineKeyboardButton("Restart Bot", callback_data="restart_bot"),
            ]
        ]
        if HEROKU_API:
            list_button.append(
                [
                    InlineKeyboardButton(
                        "Restart Heroku app", callback_data="restart_heroku"
                    )
                ]
            )
            list_button.append(
                [
                    InlineKeyboardButton(
                        "Change Repo Source", callback_data="change_repo"
                    )
                ]
            )
        button = InlineKeyboardMarkup(list_button)
        try:
            await query.message.edit_text(text, reply_markup=button)
        except errors.exceptions.bad_request_400.MessageNotModified:
            pass
        await client.answer_callback_query(query.id, "Bot was started!")
        return
    await app.stop()
    text = "**⚙️ Welcome to Nana Settings!**\n"
    text += "-> Userbot: `Stopped (v{})`\n".format(USERBOT_VERSION)
    text += "-> Assistant: `Running (v{})`\n".format(ASSISTANT_VERSION)
    text += "-> Database: `{}`\n".format(DB_AVAILABLE)
    text += "-> Python: `{}`\n".format(python_version())
    text += "\n❎ Bot was stopped!"
    list_button = [
        [
            InlineKeyboardButton("Stop Bot", callback_data="toggle_startbot"),
            InlineKeyboardButton("Restart Bot", callback_data="restart_bot"),
        ]
    ]
    if HEROKU_API:
        list_button.append(
            [InlineKeyboardButton("Restart Heroku app", callback_data="restart_heroku")]
        )
        list_button.append(
            [InlineKeyboardButton("Change Repo Source", callback_data="change_repo")]
        )
    button = InlineKeyboardMarkup(list_button)
    try:
        await query.message.edit_text(text, reply_markup=button)
    except errors.exceptions.bad_request_400.MessageNotModified:
        pass
    await client.answer_callback_query(query.id, "Bot was stopped!")


@setbot.on_callback_query(dynamic_data_filter("report_errors"))
async def report_some_errors(client, query):
    app.join_chat("@AyraSupport")
    text = "Hi @AyraHikari, i got an error for you.\nPlease take a look and fix it if possible.\n\nThank you ❤️"
    err = query.message.text
    open("nana/cache/errors.txt", "w").write(err)
    await query.message.edit_reply_markup(reply_markup=None)
    await app.send_document("AyraSupport", "nana/cache/errors.txt", caption=text)
    os.remove("nana/cache/errors.txt")
    await client.answer_callback_query(query.id, "Report was sent!")


@setbot.on_callback_query(dynamic_data_filter("restart_bot"))
async def reboot_bot(client, query):
    await restart_all()
    text = "**⚙️ Welcome to Nana Settings!**\n"
    text += "-> Userbot: `Running (v{})`\n".format(USERBOT_VERSION)
    text += "-> Assistant: `Running (v{})`\n".format(ASSISTANT_VERSION)
    text += "-> Database: `{}`\n".format(DB_AVAILABLE)
    text += "-> Python: `{}`\n".format(python_version())
    text += "\n✅ Bot was restarted!"
    list_button = [
        [
            InlineKeyboardButton("Stop Bot", callback_data="toggle_startbot"),
            InlineKeyboardButton("Restart Bot", callback_data="restart_bot"),
        ]
    ]
    if HEROKU_API:
        list_button.append(
            [InlineKeyboardButton("Restart Heroku app", callback_data="restart_heroku")]
        )
        list_button.append(
            [InlineKeyboardButton("Change Repo Source", callback_data="change_repo")]
        )
    button = InlineKeyboardMarkup(list_button)
    try:
        await query.message.edit_text(text, reply_markup=button)
    except errors.exceptions.bad_request_400.MessageNotModified:
        pass
    await client.answer_callback_query(query.id, "Please wait for bot restarting...")


@setbot.on_callback_query(dynamic_data_filter("restart_heroku"))
async def reboot_heroku(client, query):
    try:
        me = await app.get_me()
    except ConnectionError:
        me = None
    text = "**⚙️ Welcome to Nana Settings!**\n"
    if not me:
        text += "-> Userbot: `Stopped (v{})`\n".format(USERBOT_VERSION)
    else:
        text += "-> Userbot: `Running (v{})`\n".format(USERBOT_VERSION)
    text += "-> Assistant: `Running (v{})`\n".format(ASSISTANT_VERSION)
    text += "-> Database: `{}`\n".format(DB_AVAILABLE)
    text += "-> Python: `{}`\n".format(python_version())
    togglestart = "Start Bot" if not me else "Stop Bot"
    list_button = [
        [
            InlineKeyboardButton(togglestart, callback_data="toggle_startbot"),
            InlineKeyboardButton("Restart Bot", callback_data="restart_bot"),
        ]
    ]
    if HEROKU_API:
        list_button.append(
            [InlineKeyboardButton("Restart Heroku app", callback_data="restart_heroku")]
        )
        list_button.append(
            [InlineKeyboardButton("Change Repo Source", callback_data="change_repo")]
        )
    button = InlineKeyboardMarkup(list_button)
    if HEROKU_API is not None:
        text += "\nPlease wait..."
        try:
            await query.message.edit_text(text, reply_markup=button)
        except errors.exceptions.bad_request_400.MessageNotModified:
            pass
        await client.answer_callback_query(
            query.id, "Please wait for Heroku App restarting..."
        )
        heroku = heroku3.from_key(HEROKU_API)
        heroku_applications = heroku.apps()
        if len(heroku_applications) >= 1:
            heroku_app = heroku_applications[0]
            heroku_app.restart()
        else:
            text += "No heroku application found, but a key given? 😕 "
    try:
        await query.message.edit_text(text, reply_markup=button)
    except errors.exceptions.bad_request_400.MessageNotModified:
        pass
    await client.answer_callback_query(
        query.id, "No heroku application found, but a key given?"
    )


@setbot.on_callback_query(dynamic_data_filter("heroku_vars"))
async def vars_heroku(_client, query):
    text = (
        "**⚙️ Welcome to Heroku Vars Settings!**\n"
        "`Setting your heroku config vars here!`\n"
    )
    list_button = [
        [
            InlineKeyboardButton("⬅ back️", callback_data="back"),
            InlineKeyboardButton("➕  add️", callback_data="add_vars"),
        ]
    ]
    if HEROKU_API:
        heroku = heroku3.from_key(HEROKU_API)
        heroku_applications = heroku.apps()
        if len(heroku_applications) >= 1:
            app = heroku_applications[0]
            config = app.config()
            # if config["api_id"]:
            #     list_button.insert(0, [InlineKeyboardButton("api_id✅", callback_data="api_id")])
            # else:
            #     list_button.insert(0, [InlineKeyboardButton("api_id🚫", callback_data="api_id")])
            configdict = config.to_dict()
            for x, _ in configdict.items():
                list_button.insert(
                    0, [InlineKeyboardButton("{}✅".format(x), callback_data="tes")]
                )
    button = InlineKeyboardMarkup(list_button)
    await query.message.edit_text(text, reply_markup=button)


namevars = ""
valuevars = ""


@setbot.on_callback_query(dynamic_data_filter("add_vars"))
async def add_vars(_client, query):
    global namevars
    await query.message.edit_text("Send Name Variable :")
    setbot.on_message()


@setbot.on_callback_query(dynamic_data_filter("back"))
async def back(_client, message):
    try:
        me = await app.get_me()
    except ConnectionError:
        me = None
    text = "**⚙️ Welcome to Nana Settings!**\n"
    if not me:
        text += "-> Userbot: `Stopped (v{})`\n".format(USERBOT_VERSION)
    else:
        text += "-> Userbot: `Running (v{})`\n".format(USERBOT_VERSION)
    text += "-> Assistant: `Running (v{})`\n".format(ASSISTANT_VERSION)
    text += "-> Database: `{}`\n".format(DB_AVAILABLE)
    text += "-> Python: `{}`\n".format(python_version())
    text += "\nJust setup what you need here"
    list_button = [
        [
            InlineKeyboardButton("Stop Bot", callback_data="toggle_startbot"),
            InlineKeyboardButton("Restart Bot", callback_data="restart_bot"),
        ]
    ]
    if HEROKU_API:
        list_button.append(
            [InlineKeyboardButton("Heroku Config Vars", callback_data="heroku_vars")]
        )
        list_button.append(
            [InlineKeyboardButton("Restart Heroku app", callback_data="restart_heroku")]
        )
        list_button.append(
            [InlineKeyboardButton("Change Repo Source", callback_data="change_repo")]
        )
    button = InlineKeyboardMarkup(list_button)
    await message.message.edit_text(text, reply_markup=button)


async def name_vars(_client, message):
    global namevars
    namevars = message.text


#
# Settings For Sticker
#

TEMP_KEYBOARD = []
USER_SET = {}
TODEL = {}


@setbot.on_message(Filters.user(AdminSettings) & Filters.command(["setsticker"]))
async def get_stickers(_client, message):
    if not DB_AVAILABLE:
        await message.edit("Your database is not avaiable!")
        return
    global TEMP_KEYBOARD, USER_SET
    await app.send_message("@Stickers", "/stats")
    # app.read_history("@Stickers")
    time.sleep(0.2)
    keyboard = await app.get_history("@Stickers", limit=1)
    keyboard = keyboard[0].reply_markup.keyboard
    for x in keyboard:
        for y in x:
            TEMP_KEYBOARD.append(y)
    await app.send_message("@Stickers", "/cancel")
    msg = await message.reply(
        "Select your stickers for set as kang sticker",
        reply_markup=ReplyKeyboardMarkup(keyboard),
    )
    USER_SET[message.from_user.id] = msg.message_id
    USER_SET["type"] = 1


# app.read_history("@Stickers")


@setbot.on_message(Filters.user(AdminSettings) & Filters.command(["setanimation"]))
async def get_stickers_animation(_client, message):
    if not DB_AVAILABLE:
        await message.edit("Your database is not avaiable!")
        return
    global TEMP_KEYBOARD, USER_SET
    await app.send_message("@Stickers", "/stats")
    # app.read_history("@Stickers")
    time.sleep(0.2)
    keyboard = await app.get_history("@Stickers", limit=1)
    keyboard = keyboard[0].reply_markup.keyboard
    for x in keyboard:
        for y in x:
            TEMP_KEYBOARD.append(y)
    await app.send_message("@Stickers", "/cancel")
    msg = await message.reply(
        "Select your stickers for set as kang animation sticker",
        reply_markup=ReplyKeyboardMarkup(keyboard),
    )
    USER_SET[message.from_user.id] = msg.message_id
    USER_SET["type"] = 2


# app.read_history("@Stickers")


def get_stickerlist(message):
    if not DB_AVAILABLE:
        return
    global TEMP_KEYBOARD, USER_SET
    if message.from_user and message.from_user.id in list(USER_SET):
        return True
    else:
        TEMP_KEYBOARD = []
        USER_SET = {}


@setbot.on_message(get_stickerlist)
async def set_stickers(client, message):
    if not DB_AVAILABLE:
        await message.edit("Your database is not avaiable!")
        return
    global TEMP_KEYBOARD, USER_SET
    if message.text in TEMP_KEYBOARD:
        await client.delete_messages(message.chat.id, USER_SET[message.from_user.id])
        if USER_SET["type"] == 1:
            set_sticker_set(message.from_user.id, message.text)
        elif USER_SET["type"] == 2:
            set_stanim_set(message.from_user.id, message.text)
        status = "Ok, sticker was set to `{}`".format(message.text)
    else:
        status = "Invalid pack selected."
    USER_SET = {}
    TEMP_KEYBOARD = []
    try:
        me = await app.get_me()
    except ConnectionError:
        me = None
    text = "**⚙️ Welcome to Nana Settings!**\n"
    if not me:
        text += "-> Userbot: `Stopped (v{})`\n".format(USERBOT_VERSION)
    else:
        text += "-> Userbot: `Running (v{})`\n".format(USERBOT_VERSION)
    text += "-> Assistant: `Running (v{})`\n".format(ASSISTANT_VERSION)
    text += "-> Database: `{}`\n".format(DB_AVAILABLE)
    text += "-> Python: `{}`\n".format(python_version())
    text += "\n{}".format(status)
    list_button = [
        [
            InlineKeyboardButton("Stop Bot", callback_data="toggle_startbot"),
            InlineKeyboardButton("Restart Bot", callback_data="restart_bot"),
        ],
        [InlineKeyboardButton("Set Sticker", callback_data="setsticker")],
    ]
    if HEROKU_API:
        list_button.append(
            [InlineKeyboardButton("Heroku Config Vars", callback_data="heroku_vars")]
        )
        list_button.append(
            [InlineKeyboardButton("Restart Heroku app", callback_data="restart_heroku")]
        )
        list_button.append(
            [InlineKeyboardButton("Change Repo Source", callback_data="change_repo")]
        )
    button = InlineKeyboardMarkup(list_button)
    await message.reply(text, reply_markup=button)


@setbot.on_callback_query(dynamic_data_filter("setsticker"))
async def settings_sticker(_client, message):
    if not DB_AVAILABLE:
        await message.edit("Your database is not avaiable!")
        return
    global TEMP_KEYBOARD, USER_SET
    await app.send_message("@Stickers", "/stats")
    # app.read_history("@Stickers")
    time.sleep(0.2)
    try:
        keyboard = await app.get_history("@Stickers", limit=1)
        keyboard = keyboard[0].reply_markup.keyboard
    except Exception as e:
        print(e)
        message.message.edit_text(
            "You dont have any sticker pack!\nAdd stickers pack in @Stickers "
        )
        return
    for x in keyboard:
        for y in x:
            TEMP_KEYBOARD.append(y)
    await app.send_message("@Stickers", "/cancel")
    await message.message.delete()
    msg = await setbot.send_message(
        Owner,
        "Select your stickers for set as kang animation sticker",
        reply_markup=ReplyKeyboardMarkup(keyboard),
    )
    USER_SET[message.from_user.id] = msg.message_id
    USER_SET["type"] = 2

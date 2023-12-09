import contextlib

from .dbf import *
from telethon import Button, events
from telethon.errors.rpcerrorlist import (
    PeerIdInvalidError,
    UserAlreadyParticipantError,
    UserIsBlockedError,
)
from telethon.utils import get_peer_id
from telethon.tl.functions.messages import HideChatJoinRequestRequest, HideAllChatJoinRequestsRequest
from telethon.tl.types import UpdateBotChatInviteRequester
from asyncio.exceptions import TimeoutError


async def start_bot(token: str) -> None:
    await client.start(bot_token=token)
    client.me = await client.get_me()
    print(client.me.username, "is Online Now.")


client.loop.run_until_complete(start_bot(BOT_TOKEN))


bot_username = "@" + client.me.username

BTN = [
    [Button.text("Change Bot Start Msg", resize=True)],
    [Button.text("Change Chat Welcome Msg", resize=True)],
    [Button.text("Add Chats For Mangment", resize=True)],
    [Button.text("Remove Chats From Mangment", resize=True)],
    [Button.text("List of Chats In Mangment", resize=True)],
    [Button.text("Boardcast", resize=True)],
    [Button.text("Edit Contact Owner", resize=True)],
]

@client.on(events.NewMessage(incoming=True, pattern=f"^/start({bot_username})?$"))
async def starters(event):
    buttons = None
    await add_user(event.chat_id)
    if event.sender_id in ADMINS:
        # buttons = [
        #     [Button.inline("Change Bot Start Msg", "csm")], ook
        #     [Button.inline("Change Chat Welcome Msg", "cwm")], ook
        #     [Button.inline("Add Chats For Mangment", "aca")], ook
        #     [Button.inline("Remove Chats From Mangment", "rca")], ook
        #     [Button.inline("List of Chats In Mangment", "lca")], ok
        #     [Button.inline("Edit Contact Owner", "eco")],
        # ]
        buttons = [
            [Button.text("Change Bot Start Msg", resize=True)],
            [Button.text("Change Chat Welcome Msg", resize=True)],
            [Button.text("Add Chats For Mangment", resize=True)],
            [Button.text("Remove Chats From Mangment", resize=True)],
            [Button.text("List of Chats In Mangment", resize=True)],
            [Button.text("Boardcast", resize=True)],
            [Button.text("Edit Contact Owner", resize=True)],
        ]
    else:
        buttons =[
            [Button.text("☎️ Contact Us", resize=True)]
        ]
    await event.reply(
        await get_start_msg(),
        buttons=buttons,
        link_preview=False,
    )

@client.on(events.NewMessage(incoming=True))
async def all_func(event):
    if event.text == "Boardcast":
        if event.sender_id not in ADMINS:
            return
        users = await get_users()
        await event.reply("Please use his feature Responsibly⚠️")
        await event.reply(
            f"Send a single Message To Broadcast😉`\n``\n`There are {len(users)} users currently using me👉🏻.\n\nPress Cancel Button to Cancel Process And Done to Start The Process.",
        )
        async with event.client.conversation(event.sender_id) as cv:
            reply = cv.wait_event(events.NewMessage(from_users=event.sender_id))
            repl = await reply
            await cv.send_message("Your Post Will Look Like This:\nIf u Wana Broadcast The Press Done else cancel",buttons=[[Button.text("Cancel", resize=True)], [Button.text("Done", resize=True)]])
            await cv.send_message(repl.message)
            reply = cv.wait_event(events.NewMessage(from_users=event.sender_id))
            re_repl = await reply
            if re_repl.text and re_repl.text.startswith("Cancel"):
                return await repl.reply("Broadcast cancel", buttons=BTN)
        sent = await repl.reply("Broadcasting msg...", buttons=BTN)
        done, er = 0, 0
        for user in users:
            try:
                if repl.poll:
                    await repl.forward_to(user)
                else:
                    await client.send_message(user, repl.message)
                await asyncio.sleep(0.2)
                done += 1
            except BaseException as ex:
                er += 1
                print(str(ex))
        await sent.edit(f"Broadcast Completed To {done} users\n[Error in {er} users]")
    elif event.text == "Add Chats For Mangment":
        if event.sender_id not in ADMINS:
            return
        try:
            async with client.conversation(event.sender_id, timeout=2000) as conv:
                await conv.send_message(
                    "Send Chat Username or Id\n__make sure bot is admin there__"
                )
                res = await conv.get_response()
                try:
                    chat = int(res.text)
                except BaseException:
                    chat = res.text.strip().split("/")[-1]
                try:
                    chat = await client.get_entity(chat)
                    await set_chat_list(str(chat.id))
                    return await conv.send_message("Added Successfully.")
                except Exception as err:
                    await conv.send_message(str(err))
                    return await conv.send_message("Wrong Username/id")
        except TimeoutError:
            pass
    elif event.text == "List of Chats In Mangment":
        if event.sender_id not in ADMINS:
            return
        chats = await get_chat_list()
        txt = ""
        if chats:
            repl = await event.reply("Processing...")
            txt += "Mangment Chat List\n\n"
            for chat in chats:
                try:
                    ent = await client.get_entity(int(chat))
                    txt += f"__{ent.title}__\n`{chat}`\n\n"
                except BaseException:
                    pass
            await repl.edit(txt)
        else:
            return await event.reply("No Chat List Found")
    elif event.text == "Remove Chats From Mangment":
        if event.sender_id not in ADMINS:
            return
        chats = await get_chat_list()
        if not chats:
            return await event.answer("No Chat List Found")
        try:
            async with client.conversation(event.sender_id, timeout=2000) as conv:
                await conv.send_message("Give Chat Username or Id To remove from List.")
                res = await conv.get_response()
                try:
                    chat = int(res.text)
                except BaseException:
                    chat = res.text.strip().split("/")[-1]
                try:
                    chat = await client.get_entity(chat)
                    await rem_chat_list(str(chat.id))
                    return await conv.send_message("Removed Successfully.")
                except BaseException:
                    return await conv.send_message("Wrong Username/id")
        except TimeoutError:
            pass
    elif event.text == "Change Chat Welcome Msg":
        if event.sender_id not in ADMINS:
            return
        try:
            async with client.conversation(event.sender_id, timeout=2000) as conv:
                await conv.send_message(
                    "Send the new welcome message you want to be sent to a user when he is approved into your channel.",
                )
                msg = await conv.get_response()
                if not msg.text:
                    return await event.reply("You can only set a text message!")
                await set_wlcm_msg(msg.text)
                await conv.send_message(f"Welcome message has been changed successfully!")
        except TimeoutError:
            pass
    elif event.text == "Change Bot Start Msg":
        if event.sender_id not in ADMINS:
            return
        try:
            async with client.conversation(event.sender_id, timeout=2000) as conv:
                await conv.send_message(
                    "Send the new Bot Start message.",
                )
                msg = await conv.get_response()
                if not msg.text:
                    return await event.reply("You can only set a text message!")
                await set_start_msg(msg.text)
                await conv.send_message(f"Start message has been changed successfully!")
        except TimeoutError:
            pass
    elif event.text == "Edit Contact Owner":
        if event.sender_id not in ADMINS:
            return
        try:
            async with client.conversation(event.sender_id, timeout=2000) as conv:
                await conv.send_message(
                    "Send Telegram Link",
                )
                tg_link = await conv.get_response()
                if not tg_link.text:
                    return await event.reply("You can only set a text message!")
                await conv.send_message(
                    "Send Youtube Link",
                )
                yt_link = await conv.get_response()
                if not yt_link.text:
                    return await event.reply("You can only set a text message!")
                await conv.send_message(
                    "Send WhatsApp Link",
                )
                wa_link = await conv.get_response()
                if not wa_link.text:
                    return await event.reply("You can only set a text message!")
                data = {"tg_link": tg_link.text, "yt_link": yt_link.text, "wa_link": wa_link.text}
                await db.set("CONTACTS", str(data))
                await conv.send_message("Succesfully Added Contact Details.")
        except TimeoutError:
            pass
    elif event.text == "☎️ Contact Us":
        buttons =[
            [Button.text("TeleGram 📬", resize=True)],
            [Button.text("YouTube ▶️", resize=True)],
            [Button.text("WhatsApp 📞", resize=True)],
        ]
        await event.reply("Contact Me via?", buttons=buttons)
    elif event.text == "TeleGram 📬":
        data = eval((await db.get("CONTACTS")) or "{}")
        await event.reply(f'{data.get("tg_link")}')
    elif event.text == "YouTube ▶️":
        data = eval((await db.get("CONTACTS")) or "{}")
        await event.reply(f'{data.get("yt_link")}')
    elif event.text == "WhatsApp 📞":
        data = eval((await db.get("CONTACTS")) or "{}")
        await event.reply(f'{data.get("wa_link")}')
    else:
        pass


@client.on(events.Raw(UpdateBotChatInviteRequester))
async def approver(event):
    chat = event.peer.channel_id
    if not str(chat) in (await get_chat_list()):
        return
    with contextlib.suppress(UserIsBlockedError, PeerIdInvalidError):
        await client.send_message(
            event.user_id,
            await get_wlcm_msg(),
            buttons=[Button.text("☎️ Contact Us", resize=True)],
        )
        await add_user(event.user_id)
    with contextlib.suppress(UserAlreadyParticipantError):
        await client(
            HideChatJoinRequestRequest(approved=True, peer=chat, user_id=event.user_id)
        )


client.run_until_disconnected()
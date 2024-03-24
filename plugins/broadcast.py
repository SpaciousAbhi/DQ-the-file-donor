
from pyrogram import Client, filters
import datetime
import asyncio
from database.users_chats_db import db
from info import ADMINS
from utils import broadcast_messages

@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast_to_users(bot, message):
    users = await db.get_all_users()
    b_msg = message.reply_to_message
    sts = await message.reply_text(
        text='Broadcasting your messages...'
    )
    start_time = datetime.datetime.now()
    total_users = await db.total_users_count()
    success = 0
    blocked = 0
    deleted = 0
    failed = 0

    async def send_message(user):
        nonlocal success, blocked, deleted, failed
        pti, sh = await broadcast_messages(int(user['id']), b_msg)
        if pti:
            success += 1
        elif pti == False:
            if sh == "Blocked":
                blocked += 1
            elif sh == "Deleted":
                deleted += 1
            elif sh == "Error":
                failed += 1

    tasks = [send_message(user) for user in users]
    await asyncio.gather(*tasks)

    time_taken = datetime.datetime.now() - start_time
    await sts.edit(f"Broadcast Completed:\nCompleted in {time_taken.total_seconds()} seconds.\n\nTotal Users {total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}\nFailed: {failed}")

@Client.on_message(filters.command("grp_broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast_to_groups(bot, message):
    chats = await db.get_all_chats()
    b_msg = message.reply_to_message
    sts = await message.reply_text(
        text='Broadcasting your messages...'
    )
    start_time = datetime.datetime.now()
    total_chats = await db.total_chat_count()
    success = 0
    failed = 0

    async def send_message(chat):
        nonlocal success, failed
        pti, sh = await broadcast_messages(int(chat['id']), b_msg)
        if pti:
            success += 1
        elif pti == False:
            failed += 1

    tasks = [send_message(chat) for chat in chats]
    await asyncio.gather(*tasks)

    time_taken = datetime.datetime.now() - start_time
    await sts.edit(f"Broadcast Completed:\nCompleted in {time_taken.total_seconds()} seconds.\n\nTotal Chats {total_chats}\nSuccess: {success}\nFailed: {failed}")

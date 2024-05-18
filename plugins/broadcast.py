from pyrogram import Client, filters
import datetime
import asyncio
from database.users_chats_db import db
from info import ADMINS
from utils import broadcast_messages

async def broadcast_entities(entities, message, entity_type):
    """
    Helper function to broadcast a message to a list of entities (users or chats).
    """
    start_time = datetime.datetime.now()
    success = 0
    blocked = 0
    deleted = 0
    failed = 0

    async def send_message(entity):
        nonlocal success, blocked, deleted, failed
        try:
            pti, sh = await broadcast_messages(int(entity['id']), message)
            if pti:
                success += 1
            elif sh == "Blocked":
                blocked += 1
            elif sh == "Deleted":
                deleted += 1
            else:
                failed += 1
        except Exception as e:
            print(f"Error broadcasting to {entity_type} {entity['id']}: {e}")
            failed += 1

    tasks = [send_message(entity) for entity in entities]
    await asyncio.gather(*tasks)

    time_taken = datetime.datetime.now() - start_time
    return success, blocked, deleted, failed, time_taken

@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast_to_users(bot, message):
    users = await db.get_all_users()
    b_msg = message.reply_to_message
    sts = await message.reply_text(
        text='Broadcasting your messages to users...'
    )

    success, blocked, deleted, failed, time_taken = await broadcast_entities(users, b_msg, "user")
    total_users = await db.total_users_count()
    
    await sts.edit(f"Broadcast Completed:\nCompleted in {time_taken.total_seconds()} seconds.\n\nTotal Users: {total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}\nFailed: {failed}")

@Client.on_message(filters.command("grp_broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast_to_groups(bot, message):
    chats = await db.get_all_chats()
    b_msg = message.reply_to_message
    sts = await message.reply_text(
        text='Broadcasting your messages to groups...'
    )

    success, blocked, deleted, failed, time_taken = await broadcast_entities(chats, b_msg, "chat")
    total_chats = await db.total_chat_count()
    
    await sts.edit(f"Broadcast Completed:\nCompleted in {time_taken.total_seconds()} seconds.\n\nTotal Chats: {total_chats}\nSuccess: {success}\nFailed: {failed}")

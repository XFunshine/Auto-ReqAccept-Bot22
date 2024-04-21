from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid
from pyrogram import Client, filters
from pyrogram.types import *
from motor.motor_asyncio import AsyncIOMotorClient  
from os import environ as env
import asyncio, datetime, time


ACCEPTED_TEXT = "👋 𝗛𝗲𝗹𝗹𝗼 {mention}, Welcome to 𝗔𝗻𝗶𝗺𝗲𝗔𝗿𝗶𝘀𝗲 \n 🔰 𝗪𝗵𝗮𝘁 𝘆𝗼𝘂 𝘄𝗶𝗹𝗹 𝗴𝗲𝘁 𝗯𝘆 𝗝𝗼𝗶𝗻𝗶𝗻𝗴 𝗔𝗻𝗶𝗺𝗲𝗔𝗿𝗶𝘀𝗲? \n 1⃣ All your favourite anime in different audio like English Hindi Tamil etc \n 2⃣ Anime with a Complete Season or Ongoing Episode \n 3⃣ Watch Now and Download link of all the anime \n\n ✊ 𝗕𝗲𝗰𝗼𝗺𝗲 𝗮 𝗺𝗲𝗺𝗯𝗲𝗿 𝗼𝗳 𝗼𝘂𝗿 𝗔𝗻𝗶𝗺𝗲𝗔𝗿𝗶𝘀𝗲 𝗖𝗼𝗺𝗺𝘂𝗻𝗶𝘁𝘆? \n 1⃣ Request any anime which you want to watch. \n 2⃣ If the anime is available our Bot will provide you the link. \n 3⃣ Chat with Other Anime Lovers. \n\n 🔰 Anime online dekhe Hindi English Tamil etc languages me \n\n ♥️ Our Community Joining Link 👇\n\n https://t.me/AnimeArise \n https://t.me/AnimeArise \n https://t.me/AnimeArise \n\n 🔰 𝗦𝗲𝗻𝗱 /start 𝘁𝗼 𝗸𝗻𝗼𝘄 𝗺𝗼𝗿𝗲 𝗮𝗯𝗼𝘂𝘁 𝘁𝗵𝗶𝘀 𝗯𝗼𝘁."
START_TEXT = "Hai {}\n\nI am Auto Request Accept Bot With Working For All Channel. Add Me In Your Channel To Use"

API_ID = int(env.get('API_ID'))
API_HASH = env.get('API_HASH')
BOT_TOKEN = env.get('BOT_TOKEN')
DB_URL = env.get('DB_URL')
ADMINS = int(env.get('ADMINS'))

Dbclient = AsyncIOMotorClient(DB_URL)
Cluster = Dbclient['Cluster0']
Data = Cluster['users']
Bot = Client(name='AutoAcceptBot', api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
       
      
     
@Bot.on_message(filters.command("start") & filters.private)                    
async def start_handler(c, m):
    user_id = m.from_user.id
    if not await Data.find_one({'id': user_id}): await Data.insert_one({'id': user_id})
    button = [[        
        InlineKeyboardButton('Updates', url='https://t.me/mkn_bots_updates'),
        InlineKeyboardButton('Support', url='https://t.me/MKN_BOTZ_DISCUSSION_GROUP')
    ]]
    return await m.reply_text(text=START_TEXT.format(m.from_user.mention), disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup(button))
          

@Bot.on_message(filters.command(["broadcast", "users"]) & filters.user(ADMINS))  
async def broadcast(c, m):
    if m.text == "/users":
        total_users = await Data.count_documents({})
        return await m.reply(f"Total Users: {total_users}")
    b_msg = m.reply_to_message
    sts = await m.reply_text("Broadcasting your messages...")
    users = Data.find({})
    total_users = await Data.count_documents({})
    done = 0
    failed = 0
    success = 0
    start_time = time.time()
    async for user in users:
        user_id = int(user['id'])
        try:
            await b_msg.copy(chat_id=user_id)
            success += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await b_msg.copy(chat_id=user_id)
            success += 1
        except InputUserDeactivated:
            await Data.delete_many({'id': user_id})
            failed += 1
        except UserIsBlocked:
            failed += 1
        except PeerIdInvalid:
            await Data.delete_many({'id': user_id})
            failed += 1
        except Exception as e:
            failed += 1
        done += 1
        if not done % 20:
            await sts.edit(f"Broadcast in progress:\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nFailed: {failed}")    
    time_taken = datetime.timedelta(seconds=int(time.time()-start_time))
    await sts.delete()
    await message.reply_text(f"Broadcast Completed:\nCompleted in {time_taken} seconds.\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nFailed: {failed}", quote=True)

  
 
@Bot.on_chat_join_request()
async def req_accept(c, m):
    user_id = m.from_user.id
    chat_id = m.chat.id
    if not await Data.find_one({'id': user_id}): await Data.insert_one({'id': user_id})
    await c.approve_chat_join_request(chat_id, user_id)
    try: await c.send_message(user_id, ACCEPTED_TEXT.format(user=m.from_user.mention, chat=m.chat.title))
    except Exception as e: print(e)
   
   

Bot.run()




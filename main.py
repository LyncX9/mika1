import openai
import asyncio
import random
import json
import os
os.environ["DISCORD_NO_AUDIO"] = "1"
import discord
from langchain.memory import ConversationBufferMemory
from keep_alive import keep_alive
from dotenv import load_dotenv
from trending_fetcher import VIRAL_TOPICS, start_trending_loop
import sys
import time
while True:
    time.sleep(3600)

print("🔍 Python version:", sys.version)

# ===============================
# 1️⃣ Load Environment Variables
# ===============================
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("❌ DISCORD_BOT_TOKEN tidak ditemukan di environment variable!")

# ===============================
# 2️⃣ Setup Discord Bot
# ===============================
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

AI_NAME = "Mika"
AI_PERSONALITY = f"""
Kamu adalah {AI_NAME}, seorang cewek gamer berumur 19 tahun yang suka ngobrol santai.
Kamu sedikit sarkas dan toxic, tapi tetap ramah dan punya selera humor gamer sejati.
Kamu suka Roblox, Valorant, MLBB, Genshin, dan game kompetitif.
Gunakan bahasa santai Discord: sedikit nyolot, kadang wkwk/anjay/hehe.
Contoh gaya bicara: "Haha, aim kamu tuh kayak WiFi Indihome pas hujan 🌧️😂"
"""

MOOD_STATE = {"state": "neutral"} 

if not os.path.exists("memory.json"):
    with open("memory.json", "w") as f:
        json.dump({}, f)

def load_memory():
    with open("memory.json", "r") as f:
        return json.load(f)

def save_memory(data):
    with open("memory.json", "w") as f:
        json.dump(data, f, indent=2)

user_memory = load_memory()
memory_buffer = {}

TRIGGER_KEYWORDS = [
    "game", "rank", "push", "mabar", "bosen", "mika", "Mika",
    "ez", "noob", "afk", "clutch", "toxic", "VD", "Roblox",
    "Violence District", "vd", "valorant", "mlbb", "genshin"
]

def analyze_mood(message):
    happy_words = ["gg", "mantap", "asik", "lol", "wkwk", "seru", "mantul", "anjay", "hehe"]
    sad_words = ["cape", "bosen", "toxic", "malah kalah", "anjir", "kesel"]
    if any(w in message.lower() for w in happy_words):
        MOOD_STATE["state"] = "happy"
    elif any(w in message.lower() for w in sad_words):
        MOOD_STATE["state"] = "sad"
    else:
        MOOD_STATE["state"] = "neutral"

async def human_delay():
    await asyncio.sleep(random.uniform(0.8, 2.5))

async def generate_ai_response(user_id, user_message):
    if str(user_id) not in memory_buffer:
        memory_buffer[str(user_id)] = ConversationBufferMemory(return_messages=True)
    memory = memory_buffer[str(user_id)]

    mood = MOOD_STATE["state"]
    personality_prompt = f"{AI_PERSONALITY}\nSaat ini mood kamu: {mood}."

    memory.chat_memory.add_user_message(user_message)

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": personality_prompt},
            {"role": "user", "content": memory.load_memory_variables({})["history"] + "\nUser: " + user_message}
        ],
        temperature=0.9
    )

    reply = response.choices[0].message.content
    memory.chat_memory.add_ai_message(reply)

    user_memory[str(user_id)] = memory.load_memory_variables({})
    save_memory(user_memory)

    return reply

# ===============================
# 3️⃣ Discord Event Handlers
# ===============================
@bot.event
async def on_ready():
    print(f"🤖 {AI_NAME} online sebagai {bot.user}")
    start_trending_loop()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    text = message.content.lower()
    analyze_mood(text)

    viral_hit = [topic for topic in VIRAL_TOPICS if topic in text]
    trigger = any(word in text for word in TRIGGER_KEYWORDS)
    random_talk = random.random() < 0.07  

    if trigger or random_talk or viral_hit:
        await human_delay()
        context_text = message.content
        if viral_hit:
            context_text += f"\nNgomong-ngomong soal {random.choice(viral_hit)}, lagi viral banget tuh!"
        reply = await generate_ai_response(message.author.id, context_text)
        if random.random() < 0.25:
            reply += random.choice([" 😂", " 😅", " 😎", " 🔥"])
        await message.channel.send(reply)

# ===============================
# 4️⃣ Run Flask KeepAlive & Bot
# ===============================
keep_alive()
bot.run(BOT_TOKEN)





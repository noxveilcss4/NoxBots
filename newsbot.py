import discord
from discord.ext import commands, tasks
import requests
from deep_translator import GoogleTranslator

TOKEN = 'bot token'
CHANNEL_ID = 'channel ID'

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

translator = GoogleTranslator(source='en', target='tr')

posted_ids = set()

@tasks.loop(minutes=10)
async def fetch_news():
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        return

    try:
        ids_url = "https://hacker-news.firebaseio.com/v0/newstories.json"
        ids = requests.get(ids_url).json()

        for story_id in ids[:5]:
            if story_id not in posted_ids:
                item_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                story = requests.get(item_url).json()

                title_en = story.get('title')
                link = story.get('url')

                if title_en and link:
                    try:
                        title_tr = translator.translate(title_en)
                    except:
                        title_tr = title_en

                    embed = discord.Embed(
                        title="Hacker News (TR)",
                        description=f"**{title_tr}**",
                        color=0x2f3136
                    )
                    embed.add_field(name="Orijinal", value=title_en, inline=False)
                    embed.add_field(name="Bağlantı", value=f"[Habere Git]({link})", inline=False)
                    embed.set_footer(text="Küresel Akış")
                    
                    await channel.send(embed=embed)
                    posted_ids.add(story_id)

    except Exception as e:
        print(f"Hata oluştu: {e}")

@bot.event
async def on_ready():
    print(f'--- {bot.user.name} SİSTEME GİRİŞ YAPTI ---')
    print(f'haber akışı başlatılıyor...')
    fetch_news.start()

bot.run(TOKEN)

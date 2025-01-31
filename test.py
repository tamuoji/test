import discord
import random
import requests
import re
from discord.ext import commands
from bs4 import BeautifulSoup
from cachetools import TTLCache

TOKEN = "YOUR_BOT_TOKEN_HERE"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

BASE_URL = "https://www.pokemon-card.com"
SEARCH_URL = "https://www.pokemon-card.com/card-search/"

# キャッシュ設定（カード情報を1時間キャッシュ）
cache = TTLCache(maxsize=100, ttl=3600)

# 俳句生成関数
def generate_haiku(pokemon_name):
    haiku_templates = [
        f"{pokemon_name}  \n草むらの奥  \nひそみおる",
        f"旅人よ  \n{pokemon_name}  \n道の影",
        f"{pokemon_name}  \n夕暮れの森  \n風が吹く",
        f"夏の空  \n{pokemon_name}  \n羽ばたけり",
        f"霧の朝  \n静かに眠る  \n{pokemon_name}",
        f"月夜かな  \n{pokemon_name}の影  \n揺れ動く"
    ]
    return random.choice(haiku_templates)

# ポケモンの俳句を作るコマンド
@bot.command()
async def haiku(ctx, *, name: str):
    if name in cache:
        card_info = cache[name]
    else:
        params = {"keyword": name, "search": "search"}
        response = requests.get(SEARCH_URL, params=params)

        if response.status_code != 200:
            await ctx.send("検索に失敗したぞい。")
            return

        soup = BeautifulSoup(response.text, "html.parser")
        card_list = soup.find_all("a", class_="card-search__link")

        if not card_list:
            await ctx.send(f"「{name}」に該当するポケモンはおらんようじゃな…。")
            return

        first_card_url = BASE_URL + card_list[0]["href"]
        card_response = requests.get(first_card_url)

        if card_response.status_code != 200:
            await ctx.send("ポケモン情報の取得に失敗したぞい…。")
            return

        card_soup = BeautifulSoup(card_response.text, "html.parser")
        card_name = card_soup.find("h1", class_="card-detail__name").text.strip()

        haiku = generate_haiku(card_name)

        await ctx.send(f"ほう、{card_name}か…面白いのぉ！\n\n{haiku}")

# カード検索（オーキド博士風）
@bot.command()
async def card(ctx, *, name: str):
    if name in cache:
        card_info = cache[name]
    else:
        params = {"keyword": name, "search": "search"}
        response = requests.get(SEARCH_URL, params=params)

        if response.status_code != 200:
            await ctx.send("データの取得に失敗したのじゃ。")
            return

        soup = BeautifulSoup(response.text, "html.parser")
        card_list = soup.find_all("a", class_="card-search__link")

        if not card_list:
            await ctx.send(f"「{name}」はワシの研究データにはないのじゃ…。")
            return

        first_card_url = BASE_URL + card_list[0]["href"]
        card_response = requests.get(first_card_url)

        if card_response.status_code != 200:
            await ctx.send("データの取得に失敗したのじゃ…。")
            return

        card_soup = BeautifulSoup(card_response.text, "html.parser")
        card_name = card_soup.find("h1", class_="card-detail__name").text.strip()
        card_img = card_soup.find("img", class_="card-detail__image")["src"]

        # レア度・拡張パック情報取得
        card_set = card_soup.find("p", class_="card-detail__set").text.strip()
        card_rarity = card_soup.find("p", class_="card-detail__rarity").text.strip() if card_soup.find("p", class_="card-detail__rarity") else "不明"

        card_info = {
            "name": card_name,
            "url": first_card_url,
            "image": card_img,
            "set": card_set,
            "rarity": card_rarity
        }

        # キャッシュに保存
        cache[name] = card_info

    embed = discord.Embed(title=f"ほう…{card_info['name']}じゃな！", url=card_info["url"], description=f"拡張パック: {card_info['set']}\nレア度: {card_info['rarity']}")
    embed.set_image(url=card_info["image"])
    await ctx.send(embed=embed)

# コイントス（複数回対応、オーキド博士風）
@bot.command()
async def coin(ctx, times: int = 1):
    if times < 1 or times > 100:
        await ctx.send("コイントスの回数は1回以上100回以下にせんといかんぞい。")
        return
    results = [random.choice(["表", "裏"]) for _ in range(times)]
    await ctx.send(f"ほう、コイントスを{times}回試したのじゃな。\n結果: {', '.join(results)}")

# BOT起動時の処理（オーキド博士風）
@bot.event
async def on_ready():
    print(f"ワシじゃよ！{bot.user}がログインしたぞい！")

bot.run(TOKEN)

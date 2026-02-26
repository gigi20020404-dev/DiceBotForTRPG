import random
import re
import discord
from discord.ext import commands

class FunCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # 避免機器人自己回覆自己
        if message.author == self.bot.user:
            return

        processing_text = message.content.strip()
        author_mention = message.author.mention

        # -------------------------
        # 指令 1：隨機顏色
        # -------------------------
        match_color = re.match(r"^(.*?)隨機顏色\s*$", processing_text)
        if match_color:
            remark = match_color.group(1).strip()
            # 如果有備註就顯示備註，沒有就顯示預設標題
            title = f"🎨 隨機顏色 ({remark})" if remark else "🎨 隨機顏色"
            # 產生 0x000000 到 0xFFFFFF 之間的隨機整數
            color_int = random.randint(0, 0xFFFFFF)
            # 轉成 6 位數的 hex 字串 (例如: 1a2b3c)
            color_hex = f"{color_int:06x}"
            
            # 建立 Embed，並直接將側邊色條設定為抽出來的顏色！
            embed = discord.Embed(
                title=title,
                description=f"**HEX色碼:** `#{color_hex.upper()}`",
                color=discord.Color(color_int)
            )
            
            # 利用免費的 singlecolorimage API 產生 200x200 的純色圖卡，並設為縮圖
            image_url = f"https://singlecolorimage.com/get/{color_hex}/200x200"
            embed.set_thumbnail(url=image_url)
            
            await message.channel.send(content=author_mention, embed=embed)
            return

        # -------------------------
        # 指令 2：隨機 / 隨機x
        # -------------------------
        # ^隨機(\d*) 捕捉「隨機」後面可選的數字；\s+(.+) 捕捉空格後面的所有選項
        match_random = re.match(r"^(.*?)隨機(\d*)\s+(.+)", processing_text)
        if match_random:
            remark = match_random.group(1).strip()
            count_str = match_random.group(2)
            options = match_random.group(3).split()
            # 如果沒有寫數字 (例如純打 "隨機")，預設就是抽 1 個；否則轉成整數
            x = int(count_str) if count_str else 1
            
            # 防呆機制：確保 x 最少是 1，且不能超過總選項的數量
            x = max(1, min(x, len(options)))
            
            # random.sample 可以從陣列中抽出不重複的 x 個項目
            chosen = random.sample(options, x)

            title = f"🎲 隨機抽選{x}項 ({remark})" if remark else f"🎲 隨機抽選 ({x} 項)"
            
            embed = discord.Embed(color=discord.Color.green(), title=title)
            embed.add_field(name="所有選項", value=", ".join(options), inline=False)
            embed.add_field(name=f"最終結果", value=", ".join(chosen), inline=False)
            
            await message.channel.send(content=author_mention, embed=embed)
            return

        # -------------------------
        # 指令 3：排列
        # -------------------------
        match_shuffle = re.match(r"^(.*?)排列\s+(.+)", processing_text)
        if match_shuffle:
            remark = match_shuffle.group(1).strip()
            options = match_shuffle.group(2).split()
            
            title = f"🔀 隨機排列 ({remark})" if remark else "🔀 隨機排列"
            
            # random.shuffle 會直接把原本的陣列順序打亂
            random.shuffle(options)
            
            # 將打亂後的陣列加上編號，並用換行符號組合 (1. 蘋果 \n 2. 香蕉)
            result_text = " → ".join([f"{opt}" for i, opt in enumerate(options)])
            
            embed = discord.Embed(color=discord.Color.orange(), title=title)
            embed.description = result_text
            
            await message.channel.send(content=author_mention, embed=embed)
            return

# 用來載入 Cog 的非同步函數
async def setup(bot):
    await bot.add_cog(FunCog(bot))
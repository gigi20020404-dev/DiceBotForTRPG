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

        original_text = message.content
        processing_text = original_text.strip()
        author_mention = message.author.mention

        # --- 第一步：攔截暗骰與指定對象 (與 COCdice 保持一致) ---
        is_secret = False
        target_users = set()

        if processing_text.lower().startswith("dr"):
            is_secret = True
            processing_text = processing_text[2:].strip()

            for user in message.mentions:
                if not user.bot:
                    target_users.add(user)
            for role in message.role_mentions:
                for member in role.members:
                    if not member.bot:
                        target_users.add(member)
            if not target_users:
                target_users.add(message.author)

            # 清除指令中的標記代碼，避免干擾選項
            processing_text = re.sub(r'<@&?\d+>', '', processing_text).strip()

        # --- 第二步：定義娛樂指令的正則表達式 ---
        # 隨機(\d*) 可以同時匹配 "隨機" (數字為空) 和 "隨機3" (數字為3)
        random_pattern = r"^隨機(\d*)\s+(.+)"
        shuffle_pattern = r"^排列\s+(.+)"

        title = ""
        pool_str = ""
        result_str = ""

        # --- 第三步：分流處理 ---
        if match := re.match(random_pattern, processing_text):
            count_str = match.group(1)
            options = match.group(2).split()
            
            # 如果沒有輸入數字，預設抽 1 個
            count = int(count_str) if count_str else 1
            # 防呆機制：抽取數量不能小於 1，且不能超過選項的總數量
            count = max(1, min(count, len(options)))
            
            # random.sample 可以從列表中抽出不重複的多個項目
            chosen = random.sample(options, count)
            
            title = f"隨機抽選 ({count}項)"
            pool_str = "、".join(options)
            result_str = "、".join(chosen)

        elif match := re.match(shuffle_pattern, processing_text):
            options = match.group(1).split()
            pool_str = "、".join(options)
            
            # 打亂列表順序
            random.shuffle(options)
            
            title = "隨機排列"
            result_str = " ➡️ ".join(options)

        # 如果都不是娛樂指令，直接結束
        if not title:
            return

        # --- 第四步：包裝成Embed ---
        embed = discord.Embed(color=discord.Color.green(), title=f"🎲 {title}")
        embed.set_author(name=f"{message.author.display_name} 的娛樂擲骰", icon_url=message.author.display_avatar.url)
        embed.add_field(name="選項池", value=pool_str, inline=False)
        embed.add_field(name="最終結果", value=f"🎉 **{result_str}**", inline=False)

        # --- 第五步：發送結果 (處理暗骰與明骰) ---
        if is_secret:
            success_mentions = []
            failed_mentions = []
            
            for target in target_users:
                try:
                    await target.send(embed=embed)
                    success_mentions.append(target.mention)
                except discord.Forbidden:
                    failed_mentions.append(target.mention)
            
            if message.author in target_users and len(target_users) == 1:
                msg = f"{author_mention} 進行了暗骰"
            else:
                target_str = " ".join(success_mentions)
                msg = f"{author_mention} 進行了暗骰，目標為：{target_str}"

            if failed_mentions:
                fail_str = " ".join(failed_mentions)
                msg += f"\n❌ 無法傳送私訊給 {fail_str} (對方可能關閉了伺服器成員私訊功能)"

            await message.channel.send(msg)
        else:
            await message.channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(FunCog(bot))
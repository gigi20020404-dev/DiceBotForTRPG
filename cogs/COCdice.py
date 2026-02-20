import random
import re
import discord
from discord.ext import commands
from simpleeval import simple_eval

# -------------------------
# 1. 核心共用與運算函式
# -------------------------

def parse_math_expression(expr):
    """萬用算式解析器：將字串中的 XdY 替換為數字並計算總和"""
    display_formula = expr.replace('*', '×') 
    eval_formula = expr
    
    for m in re.finditer(r"(\d+)d(\d+)", expr, re.I):
        count, sides = int(m.group(1)), int(m.group(2))
        count = min(count, 100)
        
        results = [random.randint(1, sides) for _ in range(count)]
        total = sum(results)
        results_str = ", ".join(str(r) for r in results)
        
        eval_formula = eval_formula.replace(m.group(0), str(total), 1)
        display_formula = display_formula.replace(m.group(0), f"{total}({results_str})", 1)
        
    try:
        final_total = int(simple_eval(eval_formula))
        return display_formula, final_total
    except Exception:
        return display_formula, None

# -------------------------
# 2. 各類型檢定處理函式
# -------------------------

def process_general_roll(text):
    """處理一般擲骰與數學運算"""
    parts = text.split(" ", 1)
    remark = "" if len(parts) == 1 else " " + parts[1]
    formula = parts[0]
    
    display_formula, final_total = parse_math_expression(formula)
    
    if final_total is None:
         return f"🎲 算式似乎有點問題喔！ {remark}"
    return f"🎲 {display_formula} = **{final_total}** {remark}"

def process_cc_roll(match):
    """處理 CC 技能檢定與獎懲骰"""
    bp_str = match.group(1) 
    skill_value = int(match.group(2))
    remark = "" if match.group(3) is None else match.group(3)

    hard_value = skill_value // 2
    extreme_value = skill_value // 5

    bp_type = bp_str[0].upper() if bp_str else None
    bp_count = int(bp_str[1]) if bp_str else 0

    units = random.randint(0, 9)
    tens_list = [random.randint(0, 9) for _ in range(bp_count + 1)]

    if 0 in tens_list and units == 0:
        tens_list = [10 if x == 0 else x for x in tens_list]

    roll_list = [x * 10 + units for x in tens_list]

    if bp_type == 'B':
        roll = min(roll_list)
        roll_display = f"{roll_list} -> {roll}"
    elif bp_type == 'P':
        roll = max(roll_list)
        roll_display = f"{roll_list} -> {roll}"
    else:
        roll = roll_list[0]
        roll_display = f"{roll}"

    if roll == 1:
        result_text = "大成功"
    elif (skill_value < 50 and roll >= 96) or (skill_value >= 50 and roll == 100):
        result_text = "大失敗"
    elif roll <= extreme_value:
        result_text = "極難成功"
    elif roll <= hard_value:
        result_text = "困難成功"
    elif roll <= skill_value:
        result_text = "通常成功"
    else:
        result_text = "失敗"

    return f"🎲 {roll_display} / {skill_value} -> **{result_text}** {remark}"

def process_sc_roll(match):
    """處理 SC 理智檢定"""
    san = int(match.group(1))
    succ_expr = match.group(2).strip()
    fail_expr = match.group(3).strip()
    
    roll = random.randint(1, 100)
    
    if roll <= san:
        status = "成功"
        loss_expr = succ_expr
    else:
        status = "失敗"
        loss_expr = fail_expr
        
    display_loss, loss_val = parse_math_expression(loss_expr)
    if loss_val is None:
        loss_val = 0
        display_loss = "算式錯誤(0)"
        
    return (f"🎲 理智檢定 {roll} / {san} -> **{status}**！\n"
            f"　 扣除理智：{display_loss} = {loss_val} 點\n"
            f"　 剩餘理智：**{san - loss_val}** 點")

def process_dp_roll(match):
    """處理 DP 成長檢定"""
    tokens = match.group(1).split()
    results = ["📈 成長檢定："]
    i = 0
    
    while i < len(tokens):
        # 【修正邏輯】確保前一個詞不是數字且後一個詞是數字，才能判定為「技能名稱 數值」
        if i + 1 < len(tokens) and not tokens[i].isdigit() and tokens[i+1].isdigit():
            skill_name = tokens[i]
            skill_val = int(tokens[i+1])
            i += 2
        # 如果單純只有數字，就以預設的「技能」作為名稱
        elif tokens[i].isdigit():
            skill_name = "技能"
            skill_val = int(tokens[i])
            i += 1
        else:
            i += 1
            continue
        
        roll = random.randint(1, 100)
        if roll > skill_val or roll >= 96:
            growth = random.randint(1, 10)
            results.append(f"　 • {skill_name}({skill_val}) -> 🎲 {roll}，**成長成功**！增加 {growth} 點 -> **{skill_val + growth}** 點")
        else:
            results.append(f"　 • {skill_name}({skill_val}) -> 🎲 {roll}，成長失敗。")
            
    if len(results) == 1:
        return "❌ 成長檢定格式錯誤，請使用 `.dp 技能名 數值` 或 `.dp 數值`"
    return "\n".join(results)

# -------------------------
# 3. Discord Cog 機器人區塊
# -------------------------

class DiceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        original_text = message.content
        processing_text = original_text.strip()
        author_mention = message.author.mention

        # --- 第一步：攔截暗骰標記 (dr) ---
        is_secret = False
        if processing_text.lower().startswith("dr"):
            is_secret = True
            processing_text = processing_text[2:].strip()

        # --- 第二步：攔截多重擲骰標記 (次數.) ---
        repeat_count = 1
        repeat_match = re.match(r"^(\d+)\.(.*)", processing_text)
        if repeat_match:
            repeat_count = int(repeat_match.group(1))
            repeat_count = min(max(repeat_count, 1), 10) 
            processing_text = repeat_match.group(2).strip()

        # --- 第三步：定義純淨的正則表達式 ---
        cc_pattern = r"^CC([BP][12])?\s*(\d+)(\s.*)?"
        sc_pattern = r"^\.sc\s*(\d+)\s+([^/]+)/(.+)"
        # 【修正正則表達式】將 \s+ 改為 \s*，這樣即使玩家打 .dp50 也能成功識別
        dp_pattern = r"^\.dp\s*(.+)"
        general_pattern = r"^[\d\(\)\+\-\*\/]*\d+[dD]\d+" 

        # --- 第四步：依據重複次數執行擲骰 ---
        results = []
        for _ in range(repeat_count):
            if sc_match := re.match(sc_pattern, processing_text, re.I):
                results.append(process_sc_roll(sc_match))
            elif dp_match := re.match(dp_pattern, processing_text, re.I):
                results.append(process_dp_roll(dp_match))
            elif cc_match := re.match(cc_pattern, processing_text, re.I):
                results.append(process_cc_roll(cc_match))
            elif re.match(general_pattern, processing_text, re.I):
                results.append(process_general_roll(processing_text))
        
        # 如果都不是擲骰指令，直接結束
        if not results:
            return

        # --- 第五步：將結果包裝成漂亮的 Embed 嵌入式訊息 ---
        embed = discord.Embed(color=discord.Color.blue())
        embed.set_author(name=f"{message.author.display_name} 的擲骰結果", icon_url=message.author.display_avatar.url)

        if repeat_count == 1:
            embed.description = results[0]
        else:
            embed.title = f"執行多重擲骰 ({repeat_count}次)"
            embed_text = ""
            for i, res in enumerate(results, 1):
                embed_text += f"**第 {i} 次** -> {res}\n"
            embed.description = embed_text

        # --- 第六步：發送結果 (處理暗骰與明骰) ---
        if is_secret:
            try:
                await message.author.send(embed=embed)
                await message.channel.send(f"{author_mention} 進行了暗骰指令：`{original_text}`")
            except discord.Forbidden:
                await message.channel.send(f"{author_mention} 你的私訊接收功能未開啟，無法將暗骰結果傳送給你！")
        else:
            await message.channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(DiceCog(bot))
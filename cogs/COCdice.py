import random
import re
import os
import json
import discord
from discord.ext import commands
from simpleeval import simple_eval

# -------------------------
# 0. 讀取瘋狂症狀資料表
# -------------------------
MADNESS_FILE = "madness.json"

# 預設的 CoC 7 版瘋狂症狀字典 (包含即時、總結、恐懼症與狂躁症)
DEFAULT_MADNESS = {
    "real_time": [
        "失憶：調查員失去自上次處於安全狀態以來的記憶。",
        "假性殘疾：調查員陷入了心理性的失明、失聰或缺失肢體感覺。",
        "暴力傾向：陷入紅霧中，對周圍的敵友進行無差別的暴力攻擊。",
        "偏執：調查員患上嚴重的偏執狂，認為所有人都想害他。",
        "重要之人：重新審視背景中的重要之人，為其做任何事。",
        "昏厥：調查員當場昏厥。",
        "逃跑：調查員陷入恐慌，盡一切可能逃離現在的地點。",
        "歇斯底里：表現出大笑、哭泣、尖叫等過激的情緒反應。",
        "恐懼：調查員患上了一種新的恐懼症。",
        "狂躁：調查員患上了一種新的狂躁症。"
    ],
    "summary": [
        "失憶：調查員發現自己身處陌生之地，失去了這段時間的記憶。",
        "被盜：調查員發現自己毫髮無傷，但身上的財物與重要物品不翼而飛。",
        "遍體鱗傷：調查員發現自己受了傷（扣除最大生命值一半的HP），卻想不起原因。",
        "暴力：調查員發現自己渾身是血，身邊可能有被自己攻擊的人或無辜者。",
        "意識形態：調查員的重要信念或意識形態發生了極端的扭曲。",
        "重要之人：調查員為了背景中的重要之人，做出了誇張或危險的事。",
        "收容：調查員在精神病院的病房或警察局的牢房中醒來。",
        "逃亡：調查員發現自己正在遠離原本所在地的交通工具（火車、車輛等）上。",
        "恐懼：調查員患上了一種新的恐懼症。",
        "狂躁：調查員患上了一種新的狂躁症。"
    ],
    "phobias": [
        "黑暗恐懼症", "高處恐懼症", "飛行恐懼症", "幽閉恐懼症", "蜘蛛恐懼症",
        "血液恐懼症", "火焰恐懼症", "深海恐懼症", "巨大恐懼症", "密集恐懼症"
    ],
    "manias": [
        "洗手狂躁症", "囤積狂躁症", "工作狂躁症", "拔毛狂躁症", "縱火狂躁症",
        "偷竊狂躁症", "算術狂躁症", "宗教狂躁症", "清潔狂躁症", "破壞狂躁症"
    ]
}

def load_madness():
    """讀取 madness.json，如果不存在則自動建立一個預設的"""
    if os.path.exists(MADNESS_FILE):
        with open(MADNESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        with open(MADNESS_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_MADNESS, f, ensure_ascii=False, indent=4)
        return DEFAULT_MADNESS

MADNESS_SYMPTOMS = load_madness()

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

def process_madness_roll(match):
    """處理臨時瘋狂檢定 (CCRT / CCSU)"""
    cmd = match.group(1).upper()
    remark = "" if match.group(2) is None else " " + match.group(2).strip()
    duration = random.randint(1, 10)

    # 根據指令選擇戰鬥中(real_time)還是總結(summary)的表單
    if cmd == "CCRT":
        title = "臨時瘋狂 (即時)"
        time_str = f"**{duration}** 輪"
        symptom_list = MADNESS_SYMPTOMS.get("real_time", [])
    else: # CCSU
        title = "臨時瘋狂 (總結)"
        time_str = f"**{duration}** 小時"
        symptom_list = MADNESS_SYMPTOMS.get("summary", [])

    # 防呆：如果 json 被改壞導致列表是空的，提供預設文字
    if not symptom_list:
        return f"🎲 {title}{remark}\n⚠️ 瘋狂症狀表遺失，請檢查 madness.json！"

    symptom = random.choice(symptom_list)

    # 【新邏輯】檢查是否抽到了恐懼或狂躁，有的話再從子表單抽一項附加進去
    if "恐懼" in symptom and "phobias" in MADNESS_SYMPTOMS:
        sub_symptom = random.choice(MADNESS_SYMPTOMS["phobias"])
        symptom = f"{symptom} \n->{sub_symptom}"
    elif "狂躁" in symptom and "manias" in MADNESS_SYMPTOMS:
        sub_symptom = random.choice(MADNESS_SYMPTOMS["manias"])
        symptom = f"{symptom} \n->{sub_symptom}"

    return (f"🎲 {title}{remark}\n"
            f"\n{symptom}\n\n"
            f"持續：1D10 -> {time_str}")

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
            f"扣除理智：{display_loss} = {loss_val} 點\n"
            f"剩餘理智：**{san - loss_val}** 點")

def process_dp_roll(match):
    """處理 DP 成長檢定"""
    tokens = match.group(1).split()
    results = ["📈 成長檢定："]
    i = 0
    
    while i < len(tokens):
        if i + 1 < len(tokens) and not tokens[i].isdigit() and tokens[i+1].isdigit():
            skill_name = tokens[i]
            skill_val = int(tokens[i+1])
            i += 2
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
            results.append(f"• {skill_name}({skill_val}) -> 🎲 {roll}，**成長成功**！增加 {growth} 點 -> **{skill_val + growth}** 點")
        else:
            results.append(f"• {skill_name}({skill_val}) -> 🎲 {roll}，成長失敗。")
            
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

        # --- 第一點五步：處理「指定暗骰對象」 ---
        target_users = set()  # 使用 set 避免重複 (例如標記了身分組又單獨標記同個人)
        if is_secret:
            # 1. 抓取直接標記的用戶
            for user in message.mentions:
                if not user.bot: # 排除機器人，機器人不能互傳私訊
                    target_users.add(user)
            
            # 2. 抓取標記身分組裡的所有用戶
            for role in message.role_mentions:
                for member in role.members:
                    if not member.bot:
                        target_users.add(member)
            
            # 3. 如果沒有標記任何人，預設對象就是發送者自己 (傳統暗骰)
            if not target_users:
                target_users.add(message.author)
            
            # 4. 清除指令中的標記代碼 (<@123456> 或 <@&123456>)，避免干擾判定或跑到備註裡
            processing_text = re.sub(r'<@&?\d+>', '', processing_text).strip()

        # --- 第二步：攔截多重擲骰標記 (次數.) ---
        repeat_count = 1
        repeat_match = re.match(r"^(\d+)\.(.*)", processing_text)
        if repeat_match:
            repeat_count = int(repeat_match.group(1))
            repeat_count = min(max(repeat_count, 1), 10) 
            processing_text = repeat_match.group(2).strip()

        # --- 第三步：定義各擲骰指令的正則表達式 ---
        madness_pattern = r"^(CCRT|CCSU)(?:\s+(.+))?"  
        cc_pattern = r"^CC([BP][12])?\s*(\d+)(\s.*)?"
        sc_pattern = r"^\.sc\s*(\d+)\s+([^/]+)/(.+)"
        dp_pattern = r"^\.dp\s*(.+)"
        general_pattern = r"^[\d\(\)\+\-\*\/]*\d+[dD]\d+" 

        # --- 第四步：依據重複次數執行擲骰 ---
        results = []
        for _ in range(repeat_count):
            if madness_match := re.match(madness_pattern, processing_text, re.I):
                results.append(process_madness_roll(madness_match))
            elif sc_match := re.match(sc_pattern, processing_text, re.I):
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

        # --- 第五步：將結果包裝成 Embed 嵌入式訊息 ---
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
            success_mentions = []
            failed_mentions = []
            
            # 分別私訊給所有目標對象
            for target in target_users:
                try:
                    await target.send(embed=embed)
                    success_mentions.append(target.mention)
                except discord.Forbidden:
                    failed_mentions.append(target.mention)
            
            # 準備頻道內的公開提示訊息
            if message.author in target_users and len(target_users) == 1:
                # 情況 A：只有傳給自己
                msg = f"{author_mention} 進行了暗骰"
            else:
                # 情況 B：傳給別人
                target_str = " ".join(success_mentions)
                msg = f"{author_mention} 進行了暗骰，目標為：{target_str} "

            # 加上防呆報錯訊息 (如果有人關閉了私訊功能)
            if failed_mentions:
                fail_str = " ".join(failed_mentions)
                msg += f"\n❌ 無法傳送私訊給 {fail_str} (對方可能關閉了伺服器成員私訊功能)"

            await message.channel.send(msg)
        else:
            await message.channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(DiceCog(bot))
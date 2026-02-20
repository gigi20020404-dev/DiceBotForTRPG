# DiceBotForTRPG
Discord用跑團骰子機器人，目前以COC 7th為主要開發方向
## 指令一覽
以下指令字母大小寫通用
### COC7擲骰
#### 一般擲骰

`xDy` 擲x個y面骰

#### 檢定擲骰

`CC x` 擲一次1D100，技能小於等於x

`CCBx y` 擲一次1D100，x顆獎勵骰(bonus)，技能小於等於y，x最大為2

`CCPx y` 擲一次1D100，x顆懲罰骰(penalty)，技能小於等於y，x最大為2

#### 多重擲骰

任何擲骰指令前綴`要重複骰的次數.`，例如骰3次1D6的指令為:`3.1D6`，上限為10
#### 暗骰

任何擲骰指令前綴`dr`，可以和多重擲骰疊加使用，如:`dr3.1d6`
#### 成長檢定
以下兩種方式皆可

`.dpx y z`

`.dpx 技能A y 技能B z 技能C`

#### san check檢定

`.sc(SAN值) (成功)/(失敗)`
## 環境
- 語言: python 3.13.12
- 伺服器: Google Cloud Compute Engine
## 參考文章
https://hackmd.io/@smallshawn95/python_discord_bot_base
https://hackmd.io/@smallshawn95/python_discord_bot_cog
https://docs.discord.com/developers/intro
https://docs.freeserver.tw/
https://home.gamer.com.tw/artwork.php?sn=5988825

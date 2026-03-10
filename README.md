# DiceBotForTRPG
Discord用跑團骰子機器人，目前以COC 7th為主要開發方向
## 指令一覽
以下指令字母大小寫通用
### COC7擲骰
#### 一般擲骰

`xDy` 擲x個y面骰，支持基本四則運算

#### 檢定擲骰

`CC x` 擲一次1D100，技能小於等於x

`CCBx y` 擲一次1D100，x顆獎勵骰(bonus)，技能小於等於y，x最大為2

`CCPx y` 擲一次1D100，x顆懲罰骰(penalty)，技能小於等於y，x最大為2

#### 多重擲骰

任何擲骰指令前綴`要重複骰的次數.`，例如骰3次1D6的指令為:`3.1D6`，上限為10
#### 暗骰

任何擲骰指令前綴`dr`，可以和多重擲骰疊加使用，如:`dr3.1d6`

在擲骰指令後方@暗骰對象可指定暗骰結果傳送對象(可為單一用戶或身分組)，副數暗骰目標則各目標之間以半形空格隔開。如果有標記暗骰對象的話就不會把結果傳送到擲骰人那裡，除非暗骰對象列表裡面包含擲骰人，如:`dr cc 50 @KP`

#### 成長檢定
以下兩種方式皆可

`.dp x y z`

`.dp 技能A x 技能B y 技能C z`

#### san check檢定

`.sc(SAN值) (成功)/(失敗)`

#### 瘋狂症狀

`CCRT` 即時症狀

`CCSU` 總結症狀

### 其他擲骰指令

`隨機 選項A 選項B 選項C` 在選項中隨機選擇1項

`隨機x 選項A 選項B 選項C` 在選項中隨機選擇x項，x不超過總選項數量

`排列 選項A 選項B 選項C` 將各選項隨機排列

`隨機顏色` 隨機給出一串hex色碼，並給出該色碼的圖卡圖片

## 環境
- 語言: python 3.13.12
- 伺服器: Google Cloud Compute Engine
## 參考文章

https://hackmd.io/@smallshawn95/python_discord_bot_base

https://hackmd.io/@smallshawn95/python_discord_bot_cog

https://docs.discord.com/developers/intro

https://docs.freeserver.tw/

https://home.gamer.com.tw/artwork.php?sn=5988825

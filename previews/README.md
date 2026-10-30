# 設計預覽存檔

每個檔案都是一個獨立的預覽頁，內含範例資料，可以直接在瀏覽器打開，也可以從 GitHub Pages 看：
`https://yujie0212.github.io/tw-stock-dashboard/previews/<檔名>`

| 檔案 | 內容 |
|---|---|
| `v4-cyberpunk.html` | 賽博龐克版（2026-10-30 起為正式網站的樣子）：霓虹配色、切角面板、掃描線、標題干擾動畫；版面與 v3 相同 |
| `v3-board.html` | 活潑版第 2 版：跑馬燈、今日盤勢大字、報價看板、精簡選股卡片、驗證圓環、排程倒數 |
| `v2-cards.html` | 活潑版第 1 版：頂部行情卡片、彩色漲跌色塊、策略代表色、可互動走勢圖、數字跳動動畫；選股表格不含千張大戶欄 |

要換回某一版，跟 Claude 說「把正式網站改成 previews/檔名 那一版」即可。

## 儲存點（備份分支）

正式網站每次換風格，都會把當下的狀態存成一個 `backup/` 分支。分支不會隨正式網站變動，可以隨時拿回來：

| 分支 | 正式網站的樣子 |
|---|---|
| `backup/style-v3-board` | 活潑版 v3（報價看板、選股卡片） |
| `backup/style-v4-cyberpunk` | 賽博龐克版 |

還原方式：`git checkout origin/<分支> -- index.html`，再 commit 推上去；或直接跟 Claude 說「還原到 v3」。

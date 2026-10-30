# 資料檔格式（schema_version 1）

網頁讀取 `data/latest.json`。這份檔案由選股系統在每日流程結束後產生並推上來，網頁本身不做任何計算。

- `data/latest.json`：最新一份，網頁預設讀這份。
- `data/history/YYYY-MM-DD.json`：每天另存一份，內容和 `latest.json` 相同，供日後查歷史。
- `data/example.json`：範例資料，網址加上 `#demo` 才會顯示，不要讓系統覆寫它。

完整範例見 `data/example.json`。沒有資料的欄位填 `null`，不要填假的數字；網頁會顯示「—」或「尚無資料」。

## 頂層

| 欄位 | 型別 | 說明 |
|---|---|---|
| `schema_version` | 整數 | 固定為 `1`。格式有不相容的修改時才加 1，網頁遇到不認得的版本會停止顯示 |
| `generated_at` | 字串 | 產生時間，ISO 8601 含時區，例如 `2026-10-28T18:52:10+08:00` |
| `trade_date` | 字串 | 資料所屬交易日，`YYYY-MM-DD` |
| `universe_count` | 整數 | 當天選股母體檔數（上市櫃普通股） |
| `channel` | 字串 | `test`（測試頻道）或 `live`（正式推播） |
| `pipeline` | 物件 | 當天流程狀態，見下方 |
| `strategies` | 物件 | 各策略的選股結果，key 為策略代號 |
| `market` | 物件 | 大盤資料 |
| `validation` | 物件 | 策略驗證關卡 |
| `schedule` | 陣列 | 每日排程狀態 |
| `backfill` | 陣列或 `null` | 歷史回補進度；回補全部完成後可填 `null`，網頁就會隱藏這區 |

## `pipeline`

| 欄位 | 說明 |
|---|---|
| `status` | `done`、`running`、`failed` |
| `finished_at` | 完成時間 `HH:MM`，未完成填 `null` |
| `error` | 失敗原因，一句話；成功填 `null` |

## `strategies.<代號>`

代號建議用 `short`、`swing`、`long`，網頁的分頁順序就是物件裡的順序。

| 欄位 | 說明 |
|---|---|
| `label` | 顯示名稱，例如 `短線` |
| `status` | `active` 或 `paused` |
| `holding` | 預計持有期間，例如 `1–5 個交易日` |
| `note` | 補充說明，可為 `null` |
| `picks` | 選股陣列，見下方；沒有股票時給空陣列 |

`picks[]`：

| 欄位 | 說明 |
|---|---|
| `code` | 股票代號（字串，保留前導 0） |
| `name` | 股票名稱 |
| `close` | 收盤價 |
| `change_pct` | 漲跌幅（%），例如 `2.36` |
| `reason` | 選入原因，一句話 |
| `tags` | 字串陣列，例如法人動向 `["外資連 3 買"]` |
| `big_holder_pct` | 千張大戶持股比例（%），沒有資料為 `null` |
| `big_holder_week_change` | 與上一週的差（百分點），沒有上一週資料為 `null` |

## `market`

| 欄位 | 說明 |
|---|---|
| `taiex`、`otc` | 加權指數、櫃買指數：`close`、`change`（點數）、`change_pct`（%）、`history`（近 20 個交易日 `[{date, close}]`，由舊到新） |
| `institutional` | 三大法人買賣超，單位**億元**：`foreign`、`trust`、`dealer`，賣超為負數 |
| `margin` | 融資餘額（只供顯示）：`date`（資料日）、`balance_100m`（上市＋上櫃合計，億元）、`change_100m`（較前日，億元）；沒有資料為 `null` |
| `fx` | 美元兌台幣（只供顯示）：`date`、`usd_twd`（期交所參考匯率，數字或字串）、`usd_twd_change_pct`（%，**正數代表台幣貶值**）；沒有資料為 `null` |
| `big_holder_week` | 集保股權分散表的資料週 `YYYY-MM-DD`，網頁顯示在大戶欄標題 |

三大法人三個值都是 `null` 時，網頁會隱藏法人區塊。

## `validation`

| 欄位 | 說明 |
|---|---|
| `status` | `pending`（回測未完成）、`passed`、`failed` |
| `note` | 補充說明，可為 `null` |
| `rules` | 通過條件，字串陣列 |
| `strategies.<代號>` | `label`、`status`（同上三種）、`periods` |

`periods[]`：

| 欄位 | 說明 |
|---|---|
| `label` | 期間名稱，例如 `2023 H2–2024` |
| `excess_return_pct` | 扣成本後相對大盤的超額報酬（%） |
| `net_return_pct` | 扣成本後的報酬（%） |
| `samples` | 完整結果筆數 |
| `passed` | `true`、`false`，未判定填 `null` |

## `schedule[]`

| 欄位 | 說明 |
|---|---|
| `time` | `HH:MM` 或文字，例如 `明日` |
| `name` | 項目名稱 |
| `detail` | 說明 |
| `status` | `done`、`sent`、`running`、`scheduled`、`pending`、`failed`、`skipped` |

## `backfill[]`

| 欄位 | 說明 |
|---|---|
| `name` | 項目名稱 |
| `status` | `done`、`running`、`pending`、`failed` |
| `done`、`total`、`unit` | 進度，例如 `16`、`90`、`批`；沒有可計數的進度時填 `null` |
| `range` | 完成時顯示的資料範圍，例如 `2023-01 → 2026-10` |
| `note` | 補充說明 |

# 個股與指數資料檔（schema_version 1）

點選股卡片或加權、櫃買指數時，網頁讀取下列檔案畫 K 線與基本資料。檔案不存在時，個股會顯示「還沒有個股資料檔」，指數會改用 `latest.json` 裡近 20 日收盤價畫走勢線。

- `data/stocks/<代號>.json`：每檔**當天入選**的股票一份。
- `data/indices/TAIEX.json`、`data/indices/OTC.json`：加權指數、櫃買指數。
- `data/example-stocks/`、`data/example-indices/`：範例資料（`#demo` 用），不要讓系統覆寫。

範例見 `data/example-stocks/2330.json`、`data/example-indices/TAIEX.json`。沒有的資料填 `null` 或省略，不要填估計值。

| 欄位 | 說明 |
|---|---|
| `schema_version` | 固定 `1` |
| `code` | 股票代號（字串）；指數為 `TAIEX` 或 `OTC` |
| `name` | 名稱 |
| `trade_date` | 最後一根日 K 的日期 `YYYY-MM-DD` |
| `market` | 個股：`上市` 或 `上櫃` |
| `industry` | 個股：產業別，例如 `半導體業` |
| `listed_on` | 個股：上市（櫃）日期 `YYYY-MM-DD` |
| `candles` | 日 K，由舊到新，建議至少 500 個交易日（週 K、月 K 由網頁從日 K 合併）：`[{date, open, high, low, close, volume, turnover}]`。原始價（未還原）。`volume` 單位**股**（網頁 ÷1000 顯示張數），`turnover` 單位**元**。指數沒有 `volume`，只給 `turnover` |
| `intraday_5m` | 最近 5 個交易日的 5 分 K，由舊到新：`[{t, open, high, low, close, volume, turnover}]`，`t` 為**台灣時間**該根的開始時間 `YYYY-MM-DDTHH:MM`（09:00～13:25）。15 分、60 分 K 由網頁合併。沒有分鐘資料時省略或給空陣列，網頁會停用分 K 按鈕 |
| `fundamentals` | 個股：`{date, pe, pb, dividend_yield}`，本益比、股價淨值比、殖利率（%），`date` 為資料日 |

目前後端實際提供的內容（2026-10-30）：

- 指數日 K 只有開高低收，沒有 `turnover`；網頁會隱藏成交金額與下方的量柱。
- `TAIEX.json` 有 `intraday_5m`（只有開高低收）；`OTC.json` 沒有，櫃買指數的分 K 按鈕會停用。
- 個股沒有 `intraday_5m`（分 K 需付費來源），個股的分 K 按鈕會停用。

# 我的持股（加密，schema v1）

「我的持股」分頁的資料由使用者電腦上的 `tools/portfolio_upload.py` 加密後上傳。網站只存放密文，瀏覽器輸入密碼後才在本機解密。

- `data/portfolio/index.json`：`{v, kdf: {name, salt, iter}, check: {iv, ct}, days: ["YYYY-MM-DD", ...]}`。`kdf` 為 PBKDF2-SHA256，`check` 用來確認密碼是否正確。
- `data/portfolio/YYYY-MM-DD.json`：`{v, iv, ct}`，AES-256-GCM 密文（`ct` 含驗證標籤，base64）。解密後為 `{date, sj, report}`：`sj` 是當天的 `sj_YYYYMMDD.json`（已移除 `diag`），`report` 是當天健診報告的 Markdown 原文；沒有的一方為 `null`。
- `data/portfolio-example/`：範例資料（`#demo-pf`，密碼 `demo1234`），不要讓系統覆寫。
- 原始檔的欄位說明見使用者的「每日持股資料：檔案規格說明」。
- 帳戶總覽用 `sj.account_summary`（規格第 3.6 節）：大字顯示淨值 `net_value`，報酬率用 `return_on_own_pct`（分母是自備成本），總市值與融資金額用小字註明。舊檔沒有 `account_summary` 時，網頁照第 3.6 節的公式從 `positions` 自行計算。數字旁標示「以券商 App 為準」。

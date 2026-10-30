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

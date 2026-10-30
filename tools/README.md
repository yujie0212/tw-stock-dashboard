# tools

## portfolio_upload.py

在使用者的 Windows 電腦上執行：把每天的 `sj_YYYYMMDD.json` 與健診報告加密後，上傳到這個 repo 的 `data/portfolio/`，給網站的「我的持股」分頁使用。

- 只讀取 `SOURCE_DIR` 裡的 `sj_*.json` 和 `reports/*.md`，不會開啟 `sj.env` 或其他檔案。
- 設定寫在同資料夾的 `portfolio_upload.env`（不要提交到任何 repo）：

```
GITHUB_TOKEN=github_pat_...        # fine-grained token：只授權 tw-stock-dashboard，Contents 讀寫
PORTFOLIO_PASSWORD=...             # 網站上輸入的密碼，建議 12 字以上
SOURCE_DIR=C:\Users\User\OneDrive\桌面\策略\claude股票報告1030\output
DAYS=30
```

- 執行：`python portfolio_upload.py`（需要 `pip install cryptography`）。只會上傳新的日期和最近 3 天（同一天重跑會覆蓋），所有檔案合成一個 commit。
- 密碼和網站上現有資料不同時會停止。要換密碼：刪除 repo 的 `data/portfolio/` 後再執行一次 `--all`。

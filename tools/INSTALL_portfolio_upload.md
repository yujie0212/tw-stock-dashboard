# 請幫我在這台電腦安裝「持股加密上傳」

> 這份是網頁對話（負責 tw-stock-dashboard 網站）寫給「我的庫存」對話的安裝說明。網站已經新增「我的持股」分頁，需要這台電腦每天把持股資料**加密後**上傳。

## 背景

- 網站：https://yujie0212.github.io/tw-stock-dashboard/ （公開的 GitHub Pages）
- 持股分頁要輸入密碼才看得到。網站上只放密文，瀏覽器輸入密碼後才在本機解密。
- 上傳程式：https://github.com/yujie0212/tw-stock-dashboard/blob/main/tools/portfolio_upload.py
  - **只讀** `output\sj_*.json` 和 `output\reports\*.md`，不會開啟 `sj.env` 或其他檔案。
  - 用 AES-256-GCM 加密，金鑰由密碼經 PBKDF2-SHA256（60 萬次）推導。
  - 上傳前會移除 `diag` 欄位。
  - 只上傳新的日期和最近 3 天，所有檔案合成一個 commit。
- 加密格式見 https://github.com/yujie0212/tw-stock-dashboard/blob/main/data/SCHEMA.md 最下面「我的持股」一節。

## 請做的事

1. **下載程式**：把 `tools/portfolio_upload.py` 存到 `C:\Users\User\OneDrive\桌面\策略\claude股票報告1030\portfolio_upload.py`。
   - 下載網址：https://raw.githubusercontent.com/yujie0212/tw-stock-dashboard/main/tools/portfolio_upload.py
2. **安裝套件**：用 `run_sj.bat` 裡用的那個 Python 執行 `pip install cryptography`。
3. **請使用者建立 GitHub token**（只有使用者能做，請一步一步帶他）：
   - 打開 https://github.com/settings/personal-access-tokens/new
   - Token name：`portfolio-upload`；Expiration：自訂，建議 1 年。
   - Repository access：**Only select repositories** → 選 `tw-stock-dashboard`。
   - Permissions → Repository permissions → **Contents：Read and write**，其他都不要開。
   - 按 Generate，複製 `github_pat_...` 開頭的字串。
4. **建立設定檔**：在同一個資料夾建 `portfolio_upload.env`。請使用者自己貼上 token 和密碼，你不要讀取或顯示這兩個值：

   ```
   GITHUB_TOKEN=（貼上 token）
   PORTFOLIO_PASSWORD=（使用者自訂的網站密碼，建議 12 字以上、不要用常見字詞）
   SOURCE_DIR=C:\Users\User\OneDrive\桌面\策略\claude股票報告1030\output
   DAYS=30
   ```

   - 這個檔和 `sj.env` 一樣是機密，不要同步到任何網站，也不要放進 git。
5. **第一次執行**：`python portfolio_upload.py --all`。成功會顯示「已上傳 N 天的加密持股資料」。
6. **加進工作排程器**：交易日週一到週五 **08:15** 執行 `python portfolio_upload.py`，這時報告已經產生。建議 08:45 再跑一次，以防報告延遲。
   - 可以沿用 `setup_schedule.ps1` 的寫法，新增一個工作，名稱例如 `PortfolioUpload`。
   - 如果使用者在盤中或盤後手動重跑 `sj_portfolio.py`，跑完也可以再執行一次上傳。
7. **請使用者驗證**：打開網站 → 點「我的持股 🔒」→ 輸入密碼，確認看得到當天資料。

## 注意

- 換密碼時，程式會因為「密碼和網站上現有資料不同」而停止，這是刻意的設計。要換密碼，請網頁對話刪除 repo 的 `data/portfolio/` 後，再執行一次 `--all`。
- 執行失敗時會顯示原因並以非 0 結束，不會影響 07:30 抓資料和 07:49 報告這兩個既有排程。

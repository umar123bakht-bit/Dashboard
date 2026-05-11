# Daily Dashboard (Streamlit)

A one-page dashboard your manager visits to see what's happening and approve creatives. Hosted on Streamlit Community Cloud, code lives on GitHub, **creatives auto-pulled from a Drive folder**, decisions land in a Google Sheet you own.

## How it works

- **Updates (manual):** you edit `data.json` once a day and push to GitHub.
- **Creatives (automatic):** you drop files into a designated Drive folder. The dashboard reads that folder every time it loads — new files show up without any code change.
- **Decisions:** manager clicks Approve/Disapprove → row appended to a Google Sheet you own → the dashboard reads the Sheet back and shows status inline + a "Recent decisions" table.

## One-time setup (~15 minutes)

### 1. Push this folder to GitHub

```
cd C:\Users\Asus\dashboard
git init
git add .
git commit -m "Initial dashboard"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/dashboard.git
git push -u origin main
```

### 2. Create the pending-creatives Drive folder

1. In Drive, create a folder named **Dashboard — pending**.
2. Right-click → **Share** → General access → **Anyone with the link** → Viewer. (This is required so thumbnails load in your manager's browser. The folder isn't discoverable — only people with the URL can see it.)
3. Open the folder; copy the ID from the URL (the part after `/folders/`). You'll paste this in step 4.

### 3. Create the decisions Sheet

1. Go to [sheets.new](https://sheets.new). Name it **Dashboard decisions**.
2. In row 1, add headers: `timestamp`, `creative_id`, `creative`, `decision`.
3. File → Share → **Publish to the web** → choose this sheet, format **Comma-separated values (.csv)** → Publish. Copy the URL — this is your `SHEET_CSV_URL`.

### 4. Wire up the Apps Script

1. In the Sheet: Extensions → Apps Script.
2. Delete the placeholder code, paste the contents of [`apps_script.gs`](apps_script.gs).
3. Replace `REPLACE_WITH_DRIVE_FOLDER_ID` (line 6) with the folder ID from step 2. Save.
4. **Deploy → New deployment** → gear icon → **Web app**.
5. Execute as: **Me**. Who has access: **Anyone**. Click Deploy.
6. Authorize when prompted (you'll see scary "unverified" warnings — click Advanced → "Go to (unsafe)". Apps Script always shows this for personal scripts).
7. Copy the Web app URL — this is your `WEBHOOK_URL`.

### 5. Deploy on Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub.
2. **New app** → pick your `dashboard` repo, branch `main`, file `app.py`. Deploy.
3. Once it boots: **Settings → Secrets**, paste:
   ```
   SHEET_CSV_URL = "paste from step 3"
   WEBHOOK_URL = "paste from step 4"
   ```
4. Reboot the app. Share the Streamlit URL with your manager.

## Your daily flow

**For updates:**
1. Open `data.json`.
2. Update `date`, replace `updates`.
3. `git add . && git commit -m "Update YYYY-MM-DD" && git push`.

**For creatives:**
1. Drop the file in your **Dashboard — pending** Drive folder. Name the file what you want shown as the title.
2. (Optional) Right-click the file → File information → Edit description. Whatever you write appears as the creative's description on the dashboard.
3. The card appears on the dashboard within ~1 minute (60s cache). Or click the "🔄 Refresh from Drive" button to pull immediately.

## Approval flow (what your manager sees)

1. She opens the Streamlit URL (bookmarked).
2. She sees today's updates, then each pending creative with its preview, description, Drive link, and **✅ Approve / ❌ Disapprove** buttons.
3. She clicks one → the card flips to show ✅/❌ with the timestamp. No refresh needed.
4. At the bottom, "Recent decisions" shows the full log.

## What you see

- **In the dashboard itself:** each creative shows its current status (pending, ✅, or ❌), and the "Recent decisions" table at the bottom lists the last 15 decisions with timestamps.
- **In the Google Sheet:** the full audit log — every click is a row, sortable and exportable.

## Cleanup

Creatives stay on the dashboard as long as they're in the Drive folder, even after being approved (just with the ✅ badge). When you're done with one, drag it to an archive folder in Drive — it disappears from the dashboard on the next load. The decision row stays in the Sheet forever.

## Files

- `app.py` — the Streamlit app
- `data.json` — daily updates (the only thing you edit daily for updates)
- `requirements.txt` — Python deps
- `apps_script.gs` — paste into Apps Script (one-time)
- `.streamlit/secrets.toml.example` — secrets template (real secrets go in Streamlit Cloud's UI)
- `.github/workflows/daily-reminder.yml` — opens a GitHub issue at 9am on weekdays to nudge you to update `data.json`

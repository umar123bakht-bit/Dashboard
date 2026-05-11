// Paste into script.google.com (one-time setup).
// Then: Deploy → New deployment → Type: Web app → Execute as: Me → Who has access: Anyone.
// Copy the resulting URL into Streamlit secrets as WEBHOOK_URL.

// === CONFIGURE THIS ===
// Open your Drive folder, copy the ID from the URL (the part after /folders/).
const PENDING_FOLDER_ID = "REPLACE_WITH_DRIVE_FOLDER_ID";

// POST: record an Approve / Disapprove decision into the active Sheet.
function doPost(e) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const body = JSON.parse(e.postData.contents);
  sheet.appendRow([
    body.timestamp || new Date().toISOString(),
    body.creative_id || "",
    body.creative || "",
    body.decision || ""
  ]);
  return ContentService
    .createTextOutput(JSON.stringify({ok: true}))
    .setMimeType(ContentService.MimeType.JSON);
}

// GET: list files currently sitting in the pending-creatives Drive folder.
function doGet(e) {
  const folder = DriveApp.getFolderById(PENDING_FOLDER_ID);
  const files = folder.getFiles();
  const list = [];
  while (files.hasNext()) {
    const f = files.next();
    list.push({
      id: f.getId(),
      title: f.getName(),
      description: f.getDescription() || "",
      thumbnail: "https://drive.google.com/thumbnail?id=" + f.getId() + "&sz=w800",
      view_url: f.getUrl(),
      modified: f.getLastUpdated().toISOString()
    });
  }
  list.sort(function(a, b) { return b.modified.localeCompare(a.modified); });
  return ContentService
    .createTextOutput(JSON.stringify(list))
    .setMimeType(ContentService.MimeType.JSON);
}

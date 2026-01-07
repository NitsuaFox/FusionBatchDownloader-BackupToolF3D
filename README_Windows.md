# Fusion 360 - F3D ONLY batch exporter (Windows)
# Exports all cloud Fusion designs (.f3d datafiles) as native .f3d archives
# Mirrors Hub/Project/Folder structure on disk and closes docs safely.

import adsk.core
import adsk.fusion
import traceback
import os
import re
import time

# ======================
# SETTINGS (Windows)
# ======================
# Tip: Prefer a short, local path (avoid OneDrive/Desktop/Documents if Defender blocks writes)
EXPORT_ROOT = r"D:\Fusion_F3D_Archive"  # <-- CHANGE THIS (e.g. r"C:\Temp\Fusion_F3D_Archive")
SLEEP_SEC = 0.25
SKIP_IF_EXISTS = True

# ======================
# HELPERS
# ======================

def safe_name(name: str) -> str:
    """Make filesystem-safe names for Windows."""
    name = (name or "").strip()
    name = re.sub(r'[\\/:*?"<>|]+', "_", name)  # Windows invalid chars
    name = re.sub(r"\s+", " ", name)
    # Windows has reserved device names; append underscore if hit
    reserved = {"CON","PRN","AUX","NUL","COM1","COM2","COM3","COM4","COM5","COM6","COM7","COM8","COM9",
                "LPT1","LPT2","LPT3","LPT4","LPT5","LPT6","LPT7","LPT8","LPT9"}
    if name.upper() in reserved:
        name = name + "_"
    return name[:150] if len(name) > 150 else name

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def log(msg: str):
    """Log to Fusion's Text Commands palette."""
    app = adsk.core.Application.get()
    ui = app.userInterface
    pal = ui.palettes.itemById("TextCommands")
    if pal:
        pal.isVisible = True
        pal.writeText(msg)

# ======================
# EXPORT LOGIC
# ======================

def export_f3d_from_doc(doc: adsk.core.Document, export_dir: str):
    """Export the currently opened document as .f3d using design.exportManager."""
    ensure_dir(export_dir)
    out_path = os.path.join(export_dir, safe_name(doc.name) + ".f3d")

    if SKIP_IF_EXISTS and os.path.exists(out_path) and os.path.getsize(out_path) > 0:
        log(f"↷ exists, skipping: {out_path}")
        return

    # Ensure doc is active (helps activeProduct be the right Design)
    try:
        doc.activate()
    except:
        pass

    time.sleep(SLEEP_SEC)

    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    if not design:
        raise RuntimeError(f"No active Fusion Design for doc: {doc.name}")

    exportMgr = design.exportManager
    opts = exportMgr.createFusionArchiveExportOptions(out_path)
    res = exportMgr.execute(opts)

    log(f"✔ exported: {out_path} (res={res})")

def open_export_close(datafile: adsk.core.DataFile, export_dir: str):
    """Open one cloud DataFile, export F3D, close it, always."""
    app = adsk.core.Application.get()

    # Only export Fusion design files
    ext = (datafile.fileExtension or "").lower()
    if ext != "f3d":
        return

    doc = None
    try:
        log(f"→ Opening: {datafile.name}")
        doc = app.documents.open(datafile)
        time.sleep(SLEEP_SEC)

        export_f3d_from_doc(doc, export_dir)

    except:
        log(f"✖ FAILED: {datafile.name}")
        log(traceback.format_exc())

    finally:
        if doc:
            try:
                doc.close(False)  # False = do not save changes
                log(f"← Closed: {datafile.name}")
            except:
                log(f"⚠ Could not close: {datafile.name}")
                log(traceback.format_exc())
        time.sleep(SLEEP_SEC)

def walk(folder: adsk.core.DataFolder, export_dir: str):
    """Recurse through folder tree exporting .f3d datafiles."""
    for df in folder.dataFiles:
        open_export_close(df, export_dir)

    for sf in folder.dataFolders:
        sub = os.path.join(export_dir, safe_name(sf.name))
        walk(sf, sub)

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        ensure_dir(EXPORT_ROOT)

        data = app.data
        if not data:
            ui.messageBox("No Fusion data found. Are you logged in?")
            return

        for hub in data.dataHubs:
            log(f"\n=== HUB: {hub.name} ===")
            for proj in hub.dataProjects:
                log(f"\n-- Project: {proj.name}")
                base = os.path.join(EXPORT_ROOT, safe_name(hub.name), safe_name(proj.name))
                walk(proj.rootFolder, base)

        ui.messageBox(f"F3D archive complete.\nOutput: {EXPORT_ROOT}")

    except:
        if ui:
            ui.messageBox("Batch export failed:\n" + traceback.format_exc())
If Windows blocks writing (common)
If you see exports failing and you’re exporting to Desktop/Documents/OneDrive, switch to:

r"C:\Temp\Fusion_F3D_Archive" (create C:\Temp first)
or

r"D:\Fusion_F3D_Archive"

If you paste the first error stack trace from Text Commands, I’ll adjust it for whatever Fusion version/API weirdness you’re hitting.







You said:
ok give me the windows MD now


ChatGPT said:
Here’s a Windows-specific README.md you can drop straight into your repo.

md
Copy code
# Fusion 360 F3D Bulk Export Script (Windows)

A **straightforward Python script** to batch-export **all Autodesk Fusion 360 cloud designs** as native `.f3d` files on **Windows**.

Fusion does not provide a built-in way to download all of your designs in one go.  
This script exists to solve that problem.

---

## What this script does

- Walks **all Hubs → Projects → Folders** in your Fusion account
- Opens each Fusion **design (`.f3d` datafile)**
- Exports it as a **native `.f3d` archive**
- Recreates the **same folder structure** on disk
- Closes each document immediately to avoid memory issues
- Skips non-design files (drawings, etc.)
- Can skip files already exported (resume-safe)

---

## Why export `.f3d` only?

- Fastest possible export
- No geometry conversion overhead
- Full fidelity (history, parameters, assemblies)
- Best long-term archive format if you’re leaving Fusion

If you ever need STEP/STL later, you can convert from these archives.

---

## Requirements

- Autodesk Fusion 360 (any licence tier)
- Logged in to the Autodesk account that owns the files
- Windows 10 or Windows 11
- Sufficient disk space for the archive

---

## Installation / Setup (Windows)

### 1. Create the script in Fusion

1. Open **Fusion 360**
2. Go to **Utilities → Scripts and Add-Ins**
3. Open the **Scripts** tab
4. Click **+** (Create)
5. Name the script: `ExportAllF3D`
6. Replace the generated `.py` file with the script from this repository

---

### 2. Set the export directory

Edit this line near the top of the script:

```python
EXPORT_ROOT = r"D:\Fusion_F3D_Archive"
Recommended paths:

python
Copy code
r"D:\Fusion_F3D_Archive"
r"C:\Temp\Fusion_F3D_Archive"
r"C:\Users\YourName\Downloads\Fusion_F3D_Archive"
⚠️ Avoid Desktop, Documents, or OneDrive folders if Windows Defender “Controlled Folder Access” is enabled.

3. Enable logging
Make sure the Text Commands panel is visible:

pgsql
Copy code
View → User Interface → Text Commands
This shows export progress and any errors.

4. Run the script
Click Run

Fusion will:

Open a file

Export it as .f3d

Close it

Move to the next file

Large accounts may take a long time — this is normal.

Output structure
The exported archive mirrors your Fusion structure:

pgsql
Copy code
Fusion_F3D_Archive/
├── Hub Name/
│   ├── Project Name/
│   │   ├── Folder/
│   │   │   ├── DesignA.f3d
│   │   │   └── DesignB.f3d
All names are sanitised to be Windows-safe.

Known limitations
Fusion must open each design to export it (no headless mode)

Export speed depends on:

Number of files

File size

Fusion stability

Fusion may:

hang on a broken design

crash randomly

If Fusion crashes, re-run the script — already-exported files can be skipped.

Safety notes
This script does not modify your cloud data

Files are exported read-only

Documents are closed without saving

No uploads, deletes, or overwrites occur in Fusion

Troubleshooting
Folders created but no .f3d files appear
Check Text Commands output

Verify the export path is writable

Try exporting to C:\Temp or another local drive

Windows Defender blocks export
Change export path to a non-protected folder

Or allow Fusion in:

Windows Security → Ransomware Protection → Controlled Folder Access

Script opens files but doesn’t close them
This usually indicates an export exception

Check Text Commands for the error stack trace

Disclaimer
This project is not affiliated with or endorsed by Autodesk.

Fusion’s API is undocumented in places and may change without notice.
Use at your own risk.

License
MIT License — do whatever you want with it.


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

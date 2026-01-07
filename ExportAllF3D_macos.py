import adsk.core, adsk.fusion, traceback
import os, re, time

EXPORT_ROOT = r"/Users/philipaustin/Downloads/Fusion_F3D_Archive"
SLEEP_SEC = 0.25
SKIP_IF_EXISTS = True

def safe_name(name):
    name = (name or "").strip()
    name = re.sub(r'[\\/:*?"<>|]+', "_", name)
    name = re.sub(r"\s+", " ", name)
    return name[:150]

def ensure_dir(p): os.makedirs(p, exist_ok=True)

def log(msg):
    app = adsk.core.Application.get()
    ui = app.userInterface
    pal = ui.palettes.itemById('TextCommands')
    if pal:
        pal.isVisible = True
        pal.writeText(msg)

def export_f3d_from_doc(doc, export_dir):
    ensure_dir(export_dir)
    out_path = os.path.join(export_dir, safe_name(doc.name) + ".f3d")

    if SKIP_IF_EXISTS and os.path.exists(out_path) and os.path.getsize(out_path) > 0:
        log(f"↷ exists, skipping: {out_path}")
        return

    # Activate doc so its Design becomes activeProduct reliably
    try:
        doc.activate()
    except:
        pass
    time.sleep(SLEEP_SEC)

    # Get the Design (this is where exportManager lives)
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    if not design:
        raise RuntimeError(f"No active Fusion Design for doc: {doc.name}")

    exportMgr = design.exportManager
    opts = exportMgr.createFusionArchiveExportOptions(out_path)
    res = exportMgr.execute(opts)

    log(f"✔ exported: {out_path} (res={res})")

def open_export_close(datafile, export_dir):
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
                doc.close(False)
                log(f"← Closed: {datafile.name}")
            except:
                log(f"⚠ Could not close: {datafile.name}")
                log(traceback.format_exc())
        time.sleep(SLEEP_SEC)

def walk(folder, export_dir):
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
        for hub in data.dataHubs:
            log(f"\n=== HUB: {hub.name} ===")
            for proj in hub.dataProjects:
                log(f"\n-- Project: {proj.name}")
                base = os.path.join(EXPORT_ROOT, safe_name(hub.name), safe_name(proj.name))
                walk(proj.rootFolder, base)

        ui.messageBox(f"F3D archive complete.\nOutput: {EXPORT_ROOT}")
    except:
        if ui:
            ui.messageBox(traceback.format_exc())

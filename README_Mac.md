# Fusion 360 F3D Bulk Export Script

A **no-nonsense Python script** to batch-export **all Autodesk Fusion 360 cloud designs** as native `.f3d` archives.

This exists because Fusion has **no official way to bulk-download your own files** if you want to leave the platform or downgrade licences.

This script gets your data out. That’s it.

---

## What this script does

- Iterates **all Hubs → Projects → Folders** in your Fusion account
- Opens each Fusion **design file (`.f3d`)**
- Exports it as a **native `.f3d` archive**
- Mirrors the **original folder structure** on disk
- Closes each document immediately to avoid memory blow-ups
- Skips non-design files (drawings, etc.)
- Optionally skips files already exported

---

## Why `.f3d` only?

- Fastest export
- Smallest API surface
- Full fidelity (timeline, parameters, assemblies, versions)
- Future-proof (can be reopened later without cloud dependency)

If you’re leaving Fusion, **this is the safest archive format**.

---

## Requirements

- Autodesk Fusion 360 (any licence tier)
- Logged in to the Autodesk account that owns the files
- macOS or Windows
- Basic patience (Fusion’s API is… Fusion’s API)

---

## How to use

### 1. Create the script in Fusion

1. Open **Fusion 360**
2. Go to **Utilities → Scripts and Add-Ins**
3. Select the **Scripts** tab
4. Click **+** to create a new script
5. Name it something like `ExportAllF3D`
6. Replace the generated `.py` file contents with the script from this repo

---

### 2. Configure export path

Edit this line near the top of the script:

```python
EXPORT_ROOT = "/Users/yourname/Downloads/Fusion_F3D_Archive"
Choose a location with plenty of free disk space.

3. Run it

Make sure Text Commands palette is visible
(View → User Interface → Text Commands)

Run the script

Fusion will:

Open a file

Export it

Close it

Repeat until done

Go make coffee ☕.

Output structure

Your exported files will be organised like this:

Fusion_F3D_Archive/
├── Hub Name/
│   ├── Project Name/
│   │   ├── Folder/
│   │   │   ├── DesignName.f3d
│   │   │   └── AnotherDesign.f3d


Names are sanitised to be filesystem-safe.

Known limitations (Fusion quirks)

Fusion must open each file to export it (no headless mode)

Large accounts may take hours

Fusion may:

stall on a corrupt file

randomly crash (just re-run; already-exported files are skipped)

Autodesk does not provide a supported bulk-export API

This script works despite that.

Safety notes

This script does not modify your cloud data

Files are exported read-only

Documents are closed without saving

No deletes, no uploads, no changes

Still: backup important projects manually if they are mission-critical.

Why this exists

Because:

You own your designs

You should be able to download them

Fusion makes that unnecessarily painful

This script removes that friction.

License

MIT License.
Do whatever you want with it.

Disclaimer

This is not affiliated with or endorsed by Autodesk.
Use at your own risk. Fusion’s API can and will change.
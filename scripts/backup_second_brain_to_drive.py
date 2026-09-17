from pathlib import Path
import datetime as dt, hashlib, json, os, shutil, sqlite3, subprocess, sys, time, traceback, zipfile

SOURCE = Path(r"E:\第二大脑")
STAGING = Path.home() / "Documents" / "SecondBrain-DriveBackup-Staging"
MY_DRIVE = Path(r"G:\我的云端硬盘")
TARGET = MY_DRIVE / "03_第二大脑备份"
PREF_DB = Path.home() / r"AppData\Local\Google\DriveFS\root_preference_sqlite.db"
PAUSE_FILE = Path.home() / r"AppData\Local\Google\DriveFS\user-paused"
LOG_FILE = STAGING / "backup.log"
STATUS_FILE = STAGING / "last_status.json"
LOCAL_RETENTION_DAYS = 7
CLOUD_RETENTION_DAYS = 30
SAFE_STOPPED_STATE = 3
DANGEROUS_ROOTS = {os.path.normcase(os.path.normpath(r"E:\第二大脑")), os.path.normcase(os.path.normpath(r"E:\项目"))}
EXCLUDED_TOP = {".tmp.drivedownload", ".tmp.driveupload"}

STAGING.mkdir(parents=True, exist_ok=True)

def log(msg):
    line = f"{dt.datetime.now().isoformat(timespec='seconds')} {msg}"
    print(line)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(line + "\n")

def drive_roots():
    if not PREF_DB.exists():
        raise RuntimeError("Drive root preference database not found; refusing to start backup.")
    con = sqlite3.connect(f"file:{PREF_DB}?mode=ro", uri=True)
    rows = con.execute("select root_id,title,state,last_seen_absolute_path from roots order by root_id").fetchall()
    con.close()
    return rows

def unsafe_roots():
    bad = []
    for row in drive_roots():
        path = os.path.normcase(os.path.normpath(row[3] or ""))
        if path in DANGEROUS_ROOTS and row[2] != SAFE_STOPPED_STATE:
            bad.append(row)
    return bad
def stop_drive():
    subprocess.run(["taskkill", "/IM", "GoogleDriveFS.exe", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def find_drive_exe():
    base = Path(r"C:\Program Files\Google\Drive File Stream")
    candidates = sorted(base.glob("*/GoogleDriveFS.exe"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not candidates:
        raise RuntimeError("GoogleDriveFS.exe not found.")
    return candidates[0]

def ensure_drive_ready():
    if PAUSE_FILE.exists():
        raise RuntimeError("Google Drive is globally paused; refusing to report a cloud backup as successful. Resume Drive and retry.")
    bad = unsafe_roots()
    if bad:
        raise RuntimeError(f"Unsafe Drive computer-folder sync is still active: {bad}")
    if not MY_DRIVE.exists():
        subprocess.Popen([str(find_drive_exe())], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(60):
        if MY_DRIVE.exists():
            break
        time.sleep(1)
    if not MY_DRIVE.exists():
        raise RuntimeError("Google Drive virtual disk did not mount within 60 seconds.")
    time.sleep(3)
    bad = unsafe_roots()
    if bad:
        stop_drive()
        raise RuntimeError(f"Drive reactivated a dangerous source sync; Drive was stopped: {bad}")
    TARGET.mkdir(parents=True, exist_ok=True)

def iter_source_files():
    for path in SOURCE.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(SOURCE)
        if rel.parts and rel.parts[0] in EXCLUDED_TOP:
            continue
        yield path, rel
def git_snapshot():
    try:
        head = subprocess.check_output(["git", "-C", str(SOURCE), "rev-parse", "HEAD"], text=True, errors="replace").strip()
        status = subprocess.check_output(["git", "-C", str(SOURCE), "status", "--porcelain=v1"], text=True, errors="replace")
        return {"head": head, "status": status.splitlines()}
    except Exception as e:
        return {"error": str(e)}

def make_archive():
    stamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    final = STAGING / f"第二大脑_{stamp}.zip"
    partial = STAGING / f"第二大脑_{stamp}.zip.partial"
    files = list(iter_source_files())
    total_bytes = sum(p.stat().st_size for p, _ in files)
    manifest = {
        "created_at": dt.datetime.now().isoformat(timespec="seconds"),
        "source": str(SOURCE), "file_count": len(files), "total_bytes": total_bytes,
        "excluded_top": sorted(EXCLUDED_TOP), "git": git_snapshot()
    }
    errors = []
    with zipfile.ZipFile(partial, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as z:
        for path, rel in files:
            try: z.write(path, rel.as_posix())
            except Exception as e: errors.append({"path": str(path), "error": str(e)})
        z.writestr("__backup_manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    if errors:
        partial.unlink(missing_ok=True)
        raise RuntimeError(f"Backup aborted because files could not be archived: {errors[:5]}")
    with zipfile.ZipFile(partial, "r") as z:
        bad_member = z.testzip()
    if bad_member:
        partial.unlink(missing_ok=True)
        raise RuntimeError(f"ZIP integrity check failed at {bad_member}")
    partial.replace(final)
    return final, manifest
def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def copy_to_drive(archive):
    ensure_drive_ready()
    target = TARGET / archive.name
    if target.exists():
        raise RuntimeError(f"Refusing to overwrite existing cloud backup: {target}")
    shutil.copy2(archive, target)
    digest = sha256(archive)
    sidecar = STAGING / (archive.name + ".sha256")
    sidecar.write_text(f"{digest}  {archive.name}\n", encoding="utf-8")
    cloud_sidecar = TARGET / sidecar.name
    if cloud_sidecar.exists():
        raise RuntimeError(f"Refusing to overwrite existing checksum: {cloud_sidecar}")
    shutil.copy2(sidecar, cloud_sidecar)
    if not target.exists() or target.stat().st_size != archive.stat().st_size:
        raise RuntimeError("Drive target verification failed after copy.")
    return target, digest

def cleanup_retention():
    local_cutoff = time.time() - LOCAL_RETENTION_DAYS * 86400
    cloud_cutoff = time.time() - CLOUD_RETENTION_DAYS * 86400
    if STAGING.exists():
        for item in STAGING.glob("第二大脑_*.zip*"):
            try:
                if item.is_file() and item.stat().st_mtime < local_cutoff:
                    item.unlink()
            except Exception as e:
                log(f"WARN local retention cleanup failed for {item}: {e}")
    # Cloud cleanup is restricted to this dedicated backup folder and exact snapshot prefix.
    if TARGET.exists():
        for item in TARGET.glob("第二大脑_*.zip*"):
            try:
                if item.is_file() and item.stat().st_mtime < cloud_cutoff:
                    item.unlink()
            except Exception as e:
                log(f"WARN cloud retention cleanup failed for {item}: {e}")
def main():
    started = dt.datetime.now().isoformat(timespec="seconds")
    try:
        bad = unsafe_roots()
        if bad:
            raise RuntimeError(f"Backup blocked: Drive still controls source folders: {bad}")
        archive, manifest = make_archive()
        target, digest = copy_to_drive(archive)
        cleanup_retention()
        status = {
            "ok": True, "started_at": started,
            "finished_at": dt.datetime.now().isoformat(timespec="seconds"),
            "archive": str(archive), "drive_target": str(target),
            "sha256": digest, "file_count": manifest["file_count"],
            "total_bytes": manifest["total_bytes"],
            "local_retention_days": LOCAL_RETENTION_DAYS,
            "cloud_retention_days": CLOUD_RETENTION_DAYS,
            "cloud_policy": "immutable snapshots; no overwrite; delete only exact backup files older than retention"
        }
        STATUS_FILE.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")
        log(f"SUCCESS {archive.name} -> {target} files={manifest['file_count']} bytes={manifest['total_bytes']}")
        return 0
    except Exception as e:
        status = {"ok": False, "started_at": started, "finished_at": dt.datetime.now().isoformat(timespec="seconds"), "error": str(e)}
        STATUS_FILE.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")
        log("ERROR " + str(e))
        log(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main())

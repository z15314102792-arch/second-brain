from pathlib import Path
import datetime as dt
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import time
import traceback
import zipfile

SOURCE = Path(r"E:\项目")
SECOND_BRAIN = Path(r"E:\第二大脑")
STAGING = Path.home() / "Documents" / "Project-DriveBackup-Staging"
MY_DRIVE = Path(r"G:\我的云端硬盘")
TARGET = MY_DRIVE / "04_项目灾备"
BUNDLE_TARGET = MY_DRIVE / "03_第二大脑备份" / "git-bundle"
PREF_DB = Path.home() / r"AppData\Local\Google\DriveFS\root_preference_sqlite.db"
PAUSE_FILE = Path.home() / r"AppData\Local\Google\DriveFS\user-paused"
LOG_FILE = STAGING / "backup.log"
STATUS_FILE = STAGING / "last_status.json"
LOCAL_RETENTION_DAYS = 3
CLOUD_RETENTION_DAYS = 7
BUNDLE_RETENTION_DAYS = 14
SAFE_STOPPED_STATE = 3
DANGEROUS_ROOTS = {
    os.path.normcase(os.path.normpath(r"E:\第二大脑")),
    os.path.normcase(os.path.normpath(r"E:\项目")),
}
EXCLUDED_PROJECTS = {".tmp.driveupload", "AI项目", "Codex项目"}
EXCLUDED_DIR_NAMES = {
    ".tmp.driveupload", ".tmp.drivedownload", ".godot", "builds",
    "node_modules", "__pycache__", ".venv", "venv", "dist", "out",
    ".cache", ".pytest_cache", ".mypy_cache",
}
SENSITIVE_SUFFIXES = {".keystore", ".jks", ".p12", ".pfx", ".pem", ".key"}
SENSITIVE_NAMES = {".env", ".env.local", ".env.production", ".env.development"}

STAGING.mkdir(parents=True, exist_ok=True)


def log(msg):
    line = f"{dt.datetime.now().isoformat(timespec='seconds')} {msg}"
    print(line)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def drive_roots():
    if not PREF_DB.exists():
        raise RuntimeError("Drive root preference database not found; refusing backup.")
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


def find_drive_exe():
    base = Path(r"C:\Program Files\Google\Drive File Stream")
    candidates = sorted(base.glob("*/GoogleDriveFS.exe"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not candidates:
        raise RuntimeError("GoogleDriveFS.exe not found.")
    return candidates[0]


def ensure_drive_ready():
    if PAUSE_FILE.exists():
        raise RuntimeError("Google Drive is globally paused.")
    bad = unsafe_roots()
    if bad:
        raise RuntimeError(f"Unsafe Drive computer-folder sync is active: {bad}")
    if not MY_DRIVE.exists():
        subprocess.Popen([str(find_drive_exe())], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(60):
        if MY_DRIVE.exists():
            break
        time.sleep(1)
    if not MY_DRIVE.exists():
        raise RuntimeError("Google Drive virtual disk did not mount within 60 seconds.")
    time.sleep(3)
    if unsafe_roots():
        raise RuntimeError("Drive source-folder sync reactivated; backup aborted.")
    TARGET.mkdir(parents=True, exist_ok=True)
    BUNDLE_TARGET.mkdir(parents=True, exist_ok=True)


def project_dirs():
    for p in sorted(SOURCE.iterdir(), key=lambda x: x.name.lower()):
        if not p.is_dir() or p.name in EXCLUDED_PROJECTS:
            continue
        try:
            if not any(p.iterdir()):
                continue
        except OSError:
            continue
        yield p


def iter_project_files(project):
    for root, dirs, files in os.walk(project):
        root_path = Path(root)
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIR_NAMES]
        for name in files:
            path = root_path / name
            if path.is_symlink():
                continue
            rel = path.relative_to(project)
            yield path, rel


def git_snapshot(project):
    if not (project / ".git").exists():
        return {"is_repo": False}
    def run(*args):
        return subprocess.check_output(["git", "-C", str(project), *args], text=True, errors="replace").strip()
    try:
        return {
            "is_repo": True,
            "head": run("rev-parse", "HEAD"),
            "branch": run("branch", "--show-current"),
            "status": run("status", "--porcelain=v1").splitlines(),
            "remotes": run("remote", "-v").splitlines(),
        }
    except Exception as e:
        return {"is_repo": True, "error": str(e)}


def project_fingerprint(files):
    h = hashlib.sha256()
    for path, rel in sorted(files, key=lambda x: x[1].as_posix()):
        st = path.stat()
        h.update(rel.as_posix().encode("utf-8", errors="surrogatepass"))
        h.update(b"\0")
        h.update(str(st.st_size).encode())
        h.update(b"\0")
        h.update(str(st.st_mtime_ns).encode())
        h.update(b"\n")
    return h.hexdigest()


def sensitive_files(files):
    found = []
    for path, rel in files:
        low = path.name.lower()
        if path.suffix.lower() in SENSITIVE_SUFFIXES or low in SENSITIVE_NAMES:
            found.append(rel.as_posix())
    return found


def load_previous_status():
    try:
        data = json.loads(STATUS_FILE.read_text(encoding="utf-8"))
        return data.get("projects", {}) if isinstance(data, dict) else {}
    except Exception:
        return {}


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def make_project_archive(project, files, fingerprint):
    stamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    archive = STAGING / f"{project.name}_{stamp}.zip"
    partial = STAGING / f"{project.name}_{stamp}.zip.partial"
    total_bytes = sum(path.stat().st_size for path, _ in files)
    manifest = {
        "created_at": dt.datetime.now().isoformat(timespec="seconds"),
        "project": project.name,
        "source": str(project),
        "file_count": len(files),
        "total_bytes": total_bytes,
        "fingerprint": fingerprint,
        "excluded_dir_names": sorted(EXCLUDED_DIR_NAMES),
        "git": git_snapshot(project),
        "sensitive_files": sensitive_files(files),
        "note": "Sensitive project credentials may be present in this private Drive disaster snapshot; they are not intended for GitHub.",
    }
    errors = []
    with zipfile.ZipFile(partial, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as z:
        for path, rel in files:
            try:
                z.write(path, rel.as_posix())
            except Exception as e:
                errors.append({"path": str(path), "error": str(e)})
        z.writestr("__project_backup_manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    if errors:
        partial.unlink(missing_ok=True)
        raise RuntimeError(f"Archive failed: {errors[:5]}")
    with zipfile.ZipFile(partial, "r") as z:
        bad = z.testzip()
    if bad:
        partial.unlink(missing_ok=True)
        raise RuntimeError(f"ZIP integrity failure at {bad}")
    partial.replace(archive)
    return archive, manifest


def copy_project_archive(project, archive):
    project_target = TARGET / project.name
    project_target.mkdir(parents=True, exist_ok=True)
    target = project_target / archive.name
    if target.exists():
        raise RuntimeError(f"Refusing to overwrite cloud snapshot: {target}")
    shutil.copy2(archive, target)
    digest = sha256(archive)
    sidecar = STAGING / (archive.name + ".sha256")
    sidecar.write_text(f"{digest}  {archive.name}\n", encoding="utf-8")
    cloud_sidecar = project_target / sidecar.name
    if cloud_sidecar.exists():
        raise RuntimeError(f"Refusing to overwrite checksum: {cloud_sidecar}")
    shutil.copy2(sidecar, cloud_sidecar)
    if not target.exists() or target.stat().st_size != archive.stat().st_size:
        raise RuntimeError("Drive target verification failed after copy.")
    return target, digest


def backup_second_brain_bundle():
    stamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    bundle = STAGING / f"second-brain-git_{stamp}.bundle"
    subprocess.run(["git", "-C", str(SECOND_BRAIN), "bundle", "create", str(bundle), "--all"], check=True)
    verify = subprocess.run(["git", "-C", str(SECOND_BRAIN), "bundle", "verify", str(bundle)], text=True, capture_output=True)
    if verify.returncode != 0:
        bundle.unlink(missing_ok=True)
        raise RuntimeError(f"Git bundle verify failed: {verify.stderr or verify.stdout}")
    digest = sha256(bundle)
    target = BUNDLE_TARGET / bundle.name
    if target.exists():
        raise RuntimeError(f"Refusing to overwrite Git bundle: {target}")
    shutil.copy2(bundle, target)
    sidecar = STAGING / (bundle.name + ".sha256")
    sidecar.write_text(f"{digest}  {bundle.name}\n", encoding="utf-8")
    shutil.copy2(sidecar, BUNDLE_TARGET / sidecar.name)
    return {"file": str(target), "sha256": digest, "bytes": bundle.stat().st_size}


def cleanup_retention():
    local_cutoff = time.time() - LOCAL_RETENTION_DAYS * 86400
    cloud_cutoff = time.time() - CLOUD_RETENTION_DAYS * 86400
    bundle_cutoff = time.time() - BUNDLE_RETENTION_DAYS * 86400
    for item in STAGING.iterdir():
        try:
            if item.is_file() and item.name not in {LOG_FILE.name, STATUS_FILE.name} and item.stat().st_mtime < local_cutoff:
                item.unlink()
        except Exception as e:
            log(f"WARN local cleanup failed for {item}: {e}")
    if TARGET.exists():
        for project_dir in TARGET.iterdir():
            if not project_dir.is_dir():
                continue
            prefix = project_dir.name + "_"
            for item in project_dir.glob(prefix + "*.zip*"):
                try:
                    if item.is_file() and item.stat().st_mtime < cloud_cutoff:
                        item.unlink()
                except Exception as e:
                    log(f"WARN cloud cleanup failed for {item}: {e}")
    if BUNDLE_TARGET.exists():
        for item in BUNDLE_TARGET.glob("second-brain-git_*.bundle*"):
            try:
                if item.is_file() and item.stat().st_mtime < bundle_cutoff:
                    item.unlink()
            except Exception as e:
                log(f"WARN bundle cleanup failed for {item}: {e}")


def main():
    started = dt.datetime.now().isoformat(timespec="seconds")
    ensure_drive_ready()
    previous = load_previous_status()
    results = {}
    failures = []
    try:
        bundle_result = backup_second_brain_bundle()
        log(f"SUCCESS git-bundle -> {bundle_result['file']}")
    except Exception as e:
        bundle_result = {"ok": False, "error": str(e)}
        failures.append({"git_bundle": str(e)})
        log(f"ERROR git-bundle {e}")
    for project in project_dirs():
        try:
            files = list(iter_project_files(project))
            if not files:
                results[project.name] = {"skipped": True, "reason": "empty after exclusions"}
                continue
            fingerprint = project_fingerprint(files)
            prev = previous.get(project.name, {}) if isinstance(previous, dict) else {}
            prev_target = Path(prev.get("drive_target", "")) if prev.get("drive_target") else None
            if prev.get("fingerprint") == fingerprint and prev_target and prev_target.exists():
                results[project.name] = {
                    "skipped": True,
                    "reason": "unchanged",
                    "fingerprint": fingerprint,
                    "drive_target": str(prev_target),
                }
                log(f"SKIP unchanged {project.name}")
                continue
            archive, manifest = make_project_archive(project, files, fingerprint)
            target, digest = copy_project_archive(project, archive)
            results[project.name] = {
                "ok": True,
                "fingerprint": fingerprint,
                "drive_target": str(target),
                "sha256": digest,
                "file_count": manifest["file_count"],
                "total_bytes": manifest["total_bytes"],
                "git": manifest["git"],
                "sensitive_files": manifest["sensitive_files"],
            }
            log(f"SUCCESS {project.name} -> {target.name} files={manifest['file_count']} bytes={manifest['total_bytes']}")
        except Exception as e:
            results[project.name] = {"ok": False, "error": str(e)}
            failures.append({project.name: str(e)})
            log(f"ERROR {project.name}: {e}")
            log(traceback.format_exc())

    cleanup_retention()
    status = {
        "ok": not failures,
        "started_at": started,
        "finished_at": dt.datetime.now().isoformat(timespec="seconds"),
        "source": str(SOURCE),
        "cloud_target": str(TARGET),
        "excluded_projects": sorted(EXCLUDED_PROJECTS),
        "excluded_dir_names": sorted(EXCLUDED_DIR_NAMES),
        "project_retention_days": CLOUD_RETENTION_DAYS,
        "git_bundle_retention_days": BUNDLE_RETENTION_DAYS,
        "git_bundle": bundle_result,
        "projects": results,
        "failures": failures,
    }
    STATUS_FILE.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0 if not failures else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        log("FATAL " + str(e))
        log(traceback.format_exc())
        STATUS_FILE.write_text(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False, indent=2), encoding="utf-8")
        sys.exit(1)

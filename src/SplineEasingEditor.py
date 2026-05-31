"""
SplineEasingEditor.py — DaVinci Resolve launcher script
Installed automatically to: Scripts\Comp\ by the Setup installer
Run via: Workspace > Scripts > SplineEasingEditor

Mirrors KVN Rotoscope's _launch_app() method exactly.
"""
import json, os, subprocess, sys, time, traceback
from pathlib import Path

# ── Paths (same pattern as KVN Rotoscope) ─────────────────────────────────
SESSION_PATH = Path.home() / ".SplineEasingEditor" / "session.json"
RESULT_PATH  = Path.home() / ".SplineEasingEditor" / "result.json"
LOG_PATH     = Path.home() / ".SplineEasingEditor" / "launcher.log"

POLL_INTERVAL = 0.8
POLL_TIMEOUT  = 2 * 3600  # 2 hours

def _log(msg):
    line = f"[SplineEasingEditor] {msg}"
    print(line)
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

def _get_resolve():
    # Method 1: direct global (works when run from DaVinci Scripts menu)
    r = globals().get("resolve")
    if r is not None:
        return r
    # Method 2: via app global (some DaVinci versions)
    app_obj = globals().get("app")
    if app_obj is not None and hasattr(app_obj, "GetResolve"):
        r = app_obj.GetResolve()
        if r is not None:
            return r
    # Method 3: import DaVinciResolveScript
    try:
        import DaVinciResolveScript as dvr
        return dvr.scriptapp("Resolve")
    except Exception:
        return None

def _launch_app():
    """Find and launch SplineEasingEditor.exe — mirrors KVN Rotoscope method."""
    if sys.platform == "win32":
        # 1. install_path.txt written by installer (most reliable — same as KVN)
        _path_file = Path(os.environ.get("APPDATA", "")) / "SplineEasingEditor" / "install_path.txt"
        try:
            _install_dir = _path_file.read_text(encoding="utf-8").strip()
            _exe = Path(_install_dir) / "SplineEasingEditor.exe"
            if _exe.is_file():
                subprocess.Popen([str(_exe)])
                return f"Launched {_exe}"
        except Exception:
            pass

        # 2. Windows Registry (HKCU — per-user install)
        try:
            import winreg
            _reg_keys = [
                (winreg.HKEY_CURRENT_USER,
                 r"Software\Microsoft\Windows\CurrentVersion\Uninstall\SplineEasingEditor"),
                (winreg.HKEY_LOCAL_MACHINE,
                 r"Software\Microsoft\Windows\CurrentVersion\Uninstall\SplineEasingEditor"),
            ]
            for _hive, _subkey in _reg_keys:
                try:
                    _key = winreg.OpenKey(_hive, _subkey)
                    _install_dir, _ = winreg.QueryValueEx(_key, "InstallLocation")
                    winreg.CloseKey(_key)
                    _exe = Path(_install_dir) / "SplineEasingEditor.exe"
                    if _exe.is_file():
                        subprocess.Popen([str(_exe)])
                        return f"Launched {_exe}"
                except OSError:
                    continue
        except ImportError:
            pass

        # 3. Default install locations
        _candidates = [
            Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "SplineEasingEditor" / "SplineEasingEditor.exe",
            Path(os.environ.get("PROGRAMFILES", r"C:\Program Files")) / "SplineEasingEditor" / "SplineEasingEditor.exe",
        ]
        for _exe in _candidates:
            if _exe.is_file():
                subprocess.Popen([str(_exe)])
                return f"Launched {_exe}"

        return "SplineEasingEditor.exe not found. Launch it from the Start Menu or Desktop shortcut."

    # macOS
    _mac_candidates = [
        Path("/Applications/SplineEasingEditor.app"),
        Path.home() / "Applications" / "SplineEasingEditor.app",
    ]
    for _app_path in _mac_candidates:
        if _app_path.exists():
            subprocess.Popen(["open", str(_app_path)])
            return f"Launched {_app_path}"
    return "SplineEasingEditor.app not found."

def _get_animated(comp):
    out = []
    if not comp: return out
    tools = comp.GetToolList(False) or {}
    for _, tool in tools.items():
        tname = tool.GetAttrs().get("TOOLS_Name", "?")
        inps  = tool.GetInputList() or {}
        for _, inp in inps.items():
            try:
                kf = inp.GetKeyFrames()
                if not kf or len(kf) == 0: continue
                a  = inp.GetAttrs()
                nm = a.get("INPS_Name") or a.get("INPS_ID") or "param"
                fs = sorted(kf.keys())
                out.append({
                    "tool": tname, "input": nm,
                    "label": f"{tname}  →  {nm}",
                    "keyframes": fs,
                    "frame_min": fs[0], "frame_max": fs[-1],
                })
            except Exception:
                pass
    return out

def _apply(comp, r):
    tname  = r.get("tool"); iname = r.get("input")
    frm    = int(r.get("from_frame", 0)); to = int(r.get("to_frame", 99999))
    easing = r.get("easing", "ease_in_out")
    IM     = {"ease_in_out": 2, "ease_in": 2, "ease_out": 2, "linear": 1, "step": 0}
    iv     = IM.get(easing, 2)
    tools  = comp.GetToolList(False) or {}
    for _, tool in tools.items():
        if tool.GetAttrs().get("TOOLS_Name") != tname: continue
        inps = tool.GetInputList() or {}
        for _, inp in inps.items():
            a  = inp.GetAttrs()
            nm = a.get("INPS_Name") or a.get("INPS_ID", "")
            if nm != iname: continue
            try:
                kf = inp.GetKeyFrames() or {}
                comp.StartUndo("SplineEasingEditor")
                count = 0
                for frame in kf:
                    if frame < frm or frame > to: continue
                    v = inp.GetValueAtTime(frame)
                    if v is None: continue
                    if easing == "ease_in":    inp.SetValueAtTime(frame, v, 1, 2)
                    elif easing == "ease_out": inp.SetValueAtTime(frame, v, 2, 1)
                    else:                      inp.SetValueAtTime(frame, v, iv, iv)
                    count += 1
                comp.EndUndo(True)
                _log(f"Applied {easing} to {tname}/{iname} [{frm}-{to}] — {count} keyframes")
            except Exception as e:
                _log(f"Apply error: {e}")
            return

def main():
    _log("Starting SplineEasingEditor...")

    resolve  = _get_resolve()
    project  = resolve.GetCurrentProject() if resolve else None
    timeline = project.GetCurrentTimeline() if project else None
    comp     = globals().get("comp") or (resolve.GetCurrentComp() if resolve else None)

    animated = _get_animated(comp)
    _log(f"Found {len(animated)} animated inputs")

    fps=24.0; tl_end=100; tl_name=""
    if timeline:
        try:
            fps     = float(timeline.GetSetting("timelineFrameRate") or 24)
            tl_end  = int(timeline.GetEndFrame() or 100)
            tl_name = timeline.GetName() or ""
        except Exception:
            pass

    SESSION_PATH.parent.mkdir(parents=True, exist_ok=True)
    SESSION_PATH.write_text(json.dumps({
        "animated": animated, "fps": fps,
        "tl_name": tl_name, "tl_end": tl_end,
        "has_comp": comp is not None, "ts": time.time()
    }, indent=2), encoding="utf-8")
    _log(f"Session written: {SESSION_PATH}")

    try: RESULT_PATH.unlink()
    except Exception: pass

    msg = _launch_app()
    _log(msg)

    _log("Waiting for result from UI...")
    deadline = time.time() + POLL_TIMEOUT
    while time.time() < deadline:
        time.sleep(POLL_INTERVAL)
        if not RESULT_PATH.exists(): continue
        try:
            result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
        except Exception: continue
        if result.get("action") == "apply" and comp:
            _apply(comp, result)
            try: RESULT_PATH.unlink()
            except Exception: pass
        break
    _log("Done.")

try:
    main()
except Exception as exc:
    _log(f"ERROR: {exc}\n{traceback.format_exc()}")
    raise

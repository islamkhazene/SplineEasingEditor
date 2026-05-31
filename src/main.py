"""
SplineEasingEditor — External UI App
Launched automatically by DaVinci Resolve script.
Reads session.json, shows GUI, writes result.json on Apply.
"""
import json, time, threading, os
from pathlib import Path
import tkinter as tk

APP_DIR      = Path(os.environ.get("APPDATA","~")).expanduser() / "SplineEasingEditor"
SESSION_PATH = APP_DIR / "session.json"
RESULT_PATH  = APP_DIR / "result.json"

BG="#0e0e1a"; PANEL="#16162a"; PANEL2="#1c1c32"; BORDER="#2a2a4a"
ACCENT="#7c5fe6"; ACCENT_H="#6d4fd6"; ACCENT2="#a78bfa"
TEXT="#e2e0ff"; MUTED="#6b6b8f"; GREEN="#34d399"; RED="#f87171"

EASINGS = [
    ("ease_in_out","Ease In + Out",  "Smooth on both ends — most natural"),
    ("ease_in",    "Ease In",        "Starts slow, ends fast"),
    ("ease_out",   "Ease Out",       "Starts fast, ends slow"),
    ("linear",     "Linear",         "Constant speed, no easing"),
    ("step",       "Step / Hold",    "Instant jump between values"),
]

def draw_curve(canvas, eid, W=200, H=80):
    canvas.delete("all")
    canvas.configure(bg="#080814")
    pad=12; pw=W-pad*2; ph=H-pad*2
    for i in range(5):
        canvas.create_line(pad+i*pw//4, pad, pad+i*pw//4, H-pad, fill="#12122a")
        canvas.create_line(pad, pad+i*ph//4, W-pad, pad+i*ph//4, fill="#12122a")
    canvas.create_line(pad, H-pad, W-pad, pad, fill="#1e1e3e", dash=(3,4))
    def tx(t): return pad + t*pw
    def ty(v): return H - pad - max(-0.25, min(1.25, v)) * ph
    def ease(t):
        if eid=="ease_in_out": return t*t*(3-2*t)
        if eid=="ease_in":     return t*t*t
        if eid=="ease_out":    return 1-(1-t)**3
        if eid=="step":        return 0 if t < 0.999 else 1
        return t
    pts = []
    for i in range(81):
        t = i/80; pts.extend([tx(t), ty(ease(t))])
    canvas.create_line(*pts, fill=ACCENT2, width=2, smooth=(eid != "step"))
    for x, y in [(tx(0), ty(0)), (tx(1), ty(1))]:
        canvas.create_oval(x-4, y-4, x+4, y+4, fill=GREEN, outline=BG, width=2)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Spline Easing Editor  ✦  DaVinci Resolve")
        self.geometry("520x680")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.session = None
        self.animated = []
        self.sel_easing = tk.StringVar(value="ease_in_out")
        self._build()
        self._load()
        threading.Thread(target=self._poll, daemon=True).start()

    def _load(self):
        try:
            d = json.loads(SESSION_PATH.read_text(encoding="utf-8"))
            self.session = d
            self.animated = d.get("animated", [])
            mx = d.get("tl_end", 500)
            self.from_sl.config(to=mx); self.to_sl.config(to=mx)
            self.to_var.set(mx)
            self._refresh_list()
            self._status(f"Connected — {len(self.animated)} animated param(s)", GREEN)
        except:
            self._status("Waiting for DaVinci Resolve…", MUTED)

    def _poll(self):
        last = 0
        while True:
            time.sleep(1.2)
            try:
                d = json.loads(SESSION_PATH.read_text(encoding="utf-8"))
                ts = d.get("ts", 0)
                if ts != last:
                    last = ts
                    self.session = d
                    self.animated = d.get("animated", [])
                    self.after(0, self._refresh_list)
                    n = len(self.animated)
                    self.after(0, lambda n=n: self._status(f"Refreshed — {n} animated param(s)", GREEN))
            except:
                pass

    def _refresh_list(self):
        self.lb.delete(0, "end")
        for a in self.animated:
            kn = len(a.get("keyframes", []))
            self.lb.insert("end", f"  {a['label']}   [{kn} kf]")
        if self.animated:
            self.lb.selection_set(0)
            self._on_sel()

    def _build(self):
        tk.Frame(self, bg=BG, height=12).pack()
        h = tk.Frame(self, bg=BG); h.pack(fill="x", padx=18)
        tk.Label(h, text="✦  Spline Easing Editor", font=("Segoe UI",15,"bold"),
                 fg=ACCENT2, bg=BG).pack(side="left")
        tk.Label(h, text="DaVinci Resolve", font=("Segoe UI",9),
                 fg=MUTED, bg=BG).pack(side="right", pady=6)

        self.st_var = tk.StringVar(value="Waiting…")
        self.st_lbl = tk.Label(self, textvariable=self.st_var,
                               font=("Segoe UI",9), fg=MUTED, bg=BG, anchor="w")
        self.st_lbl.pack(fill="x", padx=20, pady=(2,8))
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=18)

        # Parameter list
        self._hdr("Node  →  Parameter")
        pf = self._panel()
        self.lb = tk.Listbox(pf, bg=PANEL2, fg=TEXT, selectbackground=ACCENT,
                             selectforeground="#fff", font=("Segoe UI",10),
                             relief="flat", bd=0, highlightthickness=0,
                             activestyle="none", height=5)
        self.lb.pack(fill="x", padx=2, pady=2)
        self.lb.bind("<<ListboxSelect>>", lambda e: self._on_sel())
        self.kf_lbl = tk.Label(pf, text="", font=("Segoe UI",9),
                               fg=MUTED, bg=PANEL, anchor="w")
        self.kf_lbl.pack(fill="x", padx=10, pady=(2,8))

        # Frame range
        self._hdr("Frame Range")
        rf = self._panel()
        self.from_var = tk.IntVar(value=0)
        self.to_var   = tk.IntVar(value=100)
        for lbl, var, attr in [("From Frame", self.from_var, "from_sl"),
                                ("To Frame",   self.to_var,   "to_sl")]:
            row = tk.Frame(rf, bg=PANEL); row.pack(fill="x", padx=10, pady=3)
            tk.Label(row, text=lbl, width=11, anchor="w",
                     font=("Segoe UI",10), fg=TEXT, bg=PANEL).pack(side="left")
            sl = tk.Scale(row, variable=var, from_=0, to=500, orient="horizontal",
                          length=220, showvalue=False, bg=PANEL, fg=TEXT,
                          troughcolor=BG, activebackground=ACCENT,
                          highlightthickness=0, bd=0, sliderrelief="flat")
            sl.pack(side="left")
            setattr(self, attr, sl)
            tk.Label(row, textvariable=var, width=5,
                     font=("Consolas",11,"bold"), fg=ACCENT2, bg=PANEL).pack(side="left")
        tk.Frame(rf, bg=PANEL, height=4).pack()

        # Easing
        self._hdr("Easing Curve")
        ef = self._panel()
        inner = tk.Frame(ef, bg=PANEL); inner.pack(fill="x", padx=8, pady=8)
        left  = tk.Frame(inner, bg=PANEL); left.pack(side="left", fill="y")
        right = tk.Frame(inner, bg=PANEL); right.pack(side="right", padx=(8,4))
        self.cv = tk.Canvas(right, width=200, height=80,
                            bg="#080814", highlightthickness=0)
        self.cv.pack()
        self.desc_lbl = tk.Label(right, text="", font=("Segoe UI",8),
                                 fg=MUTED, bg=PANEL, width=26,
                                 wraplength=190, justify="left")
        self.desc_lbl.pack(pady=(4,0))
        for eid, elbl, edesc in EASINGS:
            tk.Radiobutton(left, text=f"  {elbl}", variable=self.sel_easing, value=eid,
                           command=self._on_ease, font=("Segoe UI",11),
                           fg=TEXT, bg=PANEL, selectcolor=BG,
                           activebackground=PANEL, activeforeground=ACCENT2,
                           pady=4).pack(anchor="w")
        self._on_ease()

        # Buttons
        tk.Frame(self, bg=BG, height=8).pack()
        br = tk.Frame(self, bg=BG); br.pack(fill="x", padx=18)
        self.apply_btn = tk.Button(
            br, text="✦   Apply to DaVinci Resolve",
            font=("Segoe UI",12,"bold"), bg=ACCENT, fg="#fff",
            activebackground=ACCENT_H, activeforeground="#fff",
            relief="flat", cursor="hand2", pady=12, command=self._apply)
        self.apply_btn.pack(side="left", fill="x", expand=True, padx=(0,8))
        tk.Button(br, text="↻", font=("Segoe UI",12), bg=PANEL, fg=MUTED,
                  activebackground=PANEL2, relief="flat", cursor="hand2",
                  pady=12, command=self._load, width=3).pack(side="left")

        # Log
        tk.Frame(self, bg=BG, height=8).pack()
        lf = tk.Frame(self, bg=BORDER)
        lf.pack(fill="both", expand=True, padx=18, pady=(0,14))
        self.log = tk.Text(lf, bg="#060610", fg=GREEN, font=("Consolas",9),
                           relief="flat", padx=10, pady=8, wrap="word", height=6)
        self.log.pack(fill="both", expand=True)
        self._log("Ready — run the script from Workspace › Scripts in DaVinci Resolve.")

    def _hdr(self, t):
        row = tk.Frame(self, bg=BG); row.pack(fill="x", padx=18, pady=(10,2))
        tk.Label(row, text=t, font=("Segoe UI",9,"bold"),
                 fg=MUTED, bg=BG).pack(side="left")
        tk.Frame(row, bg=BORDER, height=1).pack(
            side="left", fill="x", expand=True, padx=(8,0), pady=4)

    def _panel(self):
        f = tk.Frame(self, bg=PANEL,
                     highlightbackground=BORDER, highlightthickness=1)
        f.pack(fill="x", padx=18, pady=(0,4))
        return f

    def _on_sel(self):
        s = self.lb.curselection()
        if not s or not self.animated: return
        a = self.animated[s[0]]
        fmn = a.get("frame_min", 0); fmx = a.get("frame_max", 100)
        self.from_sl.config(to=fmx+50); self.to_sl.config(to=fmx+50)
        self.from_var.set(fmn); self.to_var.set(fmx)
        kfs = a.get("keyframes", [])
        self.kf_lbl.config(text=f"  {len(kfs)} keyframes  |  frames {fmn} → {fmx}")

    def _on_ease(self):
        eid = self.sel_easing.get()
        draw_curve(self.cv, eid)
        desc = next((d for e,l,d in EASINGS if e==eid), "")
        self.desc_lbl.config(text=desc)

    def _status(self, msg, col):
        self.st_var.set(msg); self.st_lbl.config(fg=col)

    def _log(self, msg):
        self.log.insert("end", msg+"\n"); self.log.see("end")

    def _apply(self):
        if not self.animated:
            self._log("✖  No params — run the script in DaVinci first."); return
        s = self.lb.curselection()
        if not s:
            self._log("✖  Select a parameter first."); return
        a = self.animated[s[0]]
        frm = self.from_var.get(); to = self.to_var.get()
        if frm > to:
            self._log("✖  From must be ≤ To."); return
        eid  = self.sel_easing.get()
        elbl = next((l for e,l,d in EASINGS if e==eid), eid)
        try:
            RESULT_PATH.write_text(json.dumps({
                "action": "apply", "tool": a["tool"], "input": a["input"],
                "from_frame": frm, "to_frame": to, "easing": eid,
                "ts": time.time()
            }, indent=2), encoding="utf-8")
            self._log(f"✔  Sent: {a['label']}")
            self._log(f"   Easing: {elbl}  |  Frames {frm} → {to}")
            self._status(f"✔  Applied — check Spline Editor in Fusion", GREEN)
        except Exception as e:
            self._log(f"✖  Error: {e}")

if __name__ == "__main__":
    APP_DIR.mkdir(parents=True, exist_ok=True)
    App().mainloop()

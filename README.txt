╔══════════════════════════════════════════════════════════╗
║         SplineEasingEditor — Build & Install Guide      ║
║              Works on FREE DaVinci Resolve              ║
╚══════════════════════════════════════════════════════════╝

HOW IT WORKS (same as KVN Rotoscope)
──────────────────────────────────────
The installer does 2 things automatically:
  1. Installs SplineEasingEditor.exe  →  %LocalAppData%\SplineEasingEditor\
  2. Copies SplineEasingEditor.py     →  DaVinci Resolve Scripts\Comp\

After installing:
  - Open DaVinci Resolve
  - Go to Workspace > Scripts > SplineEasingEditor
  - The EXE opens automatically with all animated params listed
  - Pick easing + range → click Apply → done

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

REQUIREMENTS
────────────
  1. Python 3.8+   — https://python.org  (check "Add to PATH")
  2. Inno Setup 6  — https://jrsoftware.org/isdl.php

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BUILD STEPS (one time only)
────────────────────────────
  1. Install Python  (check "Add Python to PATH")
  2. Install Inno Setup 6
  3. Double-click  build.bat
  4. Wait ~2 minutes
  5. The installer appears in:
       installer\output\SplineEasingEditor_Setup.exe

  → Share or keep that one EXE — it installs everything!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FOLDER STRUCTURE
─────────────────
  build.bat              ← run this to build everything
  src\
    main.py              ← the GUI app code
    SplineEasingEditor.py← the DaVinci Resolve script
  installer\
    setup.iss            ← Inno Setup config

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EASING CURVES
─────────────
  Ease In + Out  → Smooth on both ends (most natural)
  Ease In        → Starts slow, ends fast
  Ease Out       → Starts fast, ends slow
  Linear         → Constant speed, no easing
  Step / Hold    → Instant jump between values

IMPORTANT: Script works on existing keyframes only.
           It does NOT add or delete keyframes.
           Must be used from inside the Fusion page.

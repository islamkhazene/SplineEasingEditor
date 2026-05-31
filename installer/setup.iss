; SplineEasingEditor — Inno Setup Script
; Mirrors KVN Rotoscope install method exactly

#define AppName "SplineEasingEditor"
#define AppVersion "1.0.0"
#define AppExeName "SplineEasingEditor.exe"
#define DaVinciScripts "{commonappdata}\Blackmagic Design\DaVinci Resolve\Fusion\Scripts\Comp"

[Setup]
AppId={{B2C3D4E5-F6A7-8901-BCDE-F12345678901}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=SplineEasingEditor
DefaultDirName={localappdata}\Programs\{#AppName}
DefaultGroupName={#AppName}
OutputDir=output
OutputBaseFilename=SplineEasingEditor_Setup
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#AppExeName}
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"
Name: "startupicon"; Description: "Launch automatically with &Windows"; GroupDescription: "Additional icons:"

[Files]
; Main application EXE
Source: "dist\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; DaVinci Resolve script — installed directly to Scripts\Comp (same as KVN)
Source: "SplineEasingEditor.py"; DestDir: "{#DaVinciScripts}"; Flags: ignoreversion

[Icons]
Name: "{group}\SplineEasingEditor";           Filename: "{app}\{#AppExeName}"
Name: "{group}\Uninstall SplineEasingEditor"; Filename: "{uninstallexe}"
Name: "{commondesktop}\SplineEasingEditor";   Filename: "{app}\{#AppExeName}"; Tasks: desktopicon
Name: "{userstartup}\SplineEasingEditor";     Filename: "{app}\{#AppExeName}"; Tasks: startupicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Launch SplineEasingEditor now"; Flags: nowait postinstall skipifsilent

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
var
  AppDataDir: String;
  InstallPathFile: String;
begin
  if CurStep = ssPostInstall then
  begin
    // Write install_path.txt — same method as KVN Rotoscope
    // The DaVinci script reads this file to find the EXE
    AppDataDir := ExpandConstant('{userappdata}\SplineEasingEditor');
    ForceDirectories(AppDataDir);
    InstallPathFile := AppDataDir + '\install_path.txt';
    SaveStringToFile(InstallPathFile, ExpandConstant('{app}'), False);
  end;
end;

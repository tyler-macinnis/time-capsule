; Inno Setup script for Time Capsule — per-user install, no admin required.
; Build with: ISCC.exe /DAppVersion=3.0.0 installer\timecapsule.iss
; (build_release.py does this automatically when Inno Setup is installed.)

#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif

#define MyAppName "Time Capsule"
#define MyAppExeName "Time Capsule.exe"
#define MyAppPublisher "Tyler MacInnis"
#define MyAppURL "https://github.com/tyler-macinnis/time-capsule"

[Setup]
AppId={{8C9F2D6B-3A41-4E7B-9D02-5F1C7A8E4B63}
AppName={#MyAppName}
AppVersion={#AppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/blob/main/docs/troubleshooting.md
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={localappdata}\Programs\{#MyAppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=..\dist
OutputBaseFilename=TimeCapsule-Setup-{#AppVersion}
SetupIconFile=..\res\time.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{userprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{userdesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

; User data in {userappdata}\TimeCapsule is intentionally left untouched on uninstall.

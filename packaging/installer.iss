#define MyAppName "H2-OBSERVER"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "H2-OBSERVER"
#define MyAppExeName "H2-OBSERVER.exe"

#ifndef DistDir
#define DistDir "..\dist\H2-OBSERVER"
#endif

[Setup]
AppId={{5109E3D1-DFD3-49CE-8556-FA46672A46A0}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\H2-OBSERVER
DefaultGroupName=H2-OBSERVER
DisableProgramGroupPage=yes
OutputDir=..\dist
OutputBaseFilename=H2-OBSERVER-Setup
SetupIconFile=..\logo.ico
UninstallDisplayIcon={app}\logo.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"; GroupDescription: "Accesos directos:"; Flags: unchecked

[Files]
Source: "{#DistDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\H2-OBSERVER"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Desinstalar H2-OBSERVER"; Filename: "{uninstallexe}"
Name: "{autodesktop}\H2-OBSERVER"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Ejecutar H2-OBSERVER ahora"; Flags: nowait postinstall skipifsilent
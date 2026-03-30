[Setup]
; Info applicazione
AppName=PyBot
AppVersion=0.2.0
AppPublisher=AmMstools
AppPublisherURL=https://github.com/ArcademMan
DefaultDirName={autopf}\PyBot
DefaultGroupName=PyBot
OutputDir=installer_output
OutputBaseFilename=PyBot_Setup_0.2.0
Compression=lzma2
SolidCompression=yes
SetupIconFile=assets\icon.ico
UninstallDisplayIcon={app}\PyBot.exe
ArchitecturesInstallIn64BitMode=x64compatible
WizardStyle=modern

; Permessi (installa senza admin se possibile)
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Copia tutto il contenuto della cartella PyInstaller
Source: "dist\PyBot\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Menu Start
Name: "{group}\PyBot"; Filename: "{app}\PyBot.exe"; IconFilename: "{app}\PyBot.exe"
Name: "{group}\Uninstall PyBot"; Filename: "{uninstallexe}"
; Desktop (opzionale)
Name: "{userdesktop}\PyBot"; Filename: "{app}\PyBot.exe"; IconFilename: "{app}\PyBot.exe"; Tasks: desktopicon

[Run]
; Lancia l'app dopo l'installazione (opzionale)
Filename: "{app}\PyBot.exe"; Description: "Launch PyBot"; Flags: nowait postinstall skipifsilent

[Setup]
AppName=Lab Clínico
AppVersion=0.0.1
AppPublisher=Tu Laboratorio Software
DefaultDirName={autopf}\LabClinico
DefaultGroupName=Lab Clínico
OutputDir=instalador
OutputBaseFilename=LabClinico-Setup-0.0.1
Compression=lzma2/max
SolidCompression=yes
PrivilegesRequired=lowest
WizardStyle=modern

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear ícono en el escritorio"

[Files]
Source: "dist\LabClinico\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Lab Clínico"; Filename: "{app}\LabClinico.exe"
Name: "{autodesktop}\Lab Clínico"; Filename: "{app}\LabClinico.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\LabClinico.exe"; Description: "Abrir Lab Clínico ahora"; Flags: nowait postinstall skipifsilent

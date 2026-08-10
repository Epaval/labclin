[Setup]
AppName=Lab Clínico
AppVersion=0.0.3
AppPublisher=Tu Laboratorio Software
DefaultDirName={autopf}\LabClinico
DefaultGroupName=Lab Clínico
OutputDir=instalador
OutputBaseFilename=LabClinico-Setup-0.0.3
Compression=lzma2/max
SolidCompression=yes
PrivilegesRequired=lowest
WizardStyle=modern

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear ícono en el escritorio"
Name: "autoiniciar"; Description: "Iniciar servidor al encender Windows"; GroupDescription: "Servidor:"; Flags: unchecked

[Files]
Source: "dist\LabClinico\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "icons\*.ico"; DestDir: "{app}\icons"; Flags: ignoreversion createallsubdirs

[Icons]
Name: "{group}\Lab Clínico"; Filename: "{app}\LabClinico.exe"; IconFilename: "{app}\icons\icono_principal.ico"
Name: "{group}\Lab Clínico Servidor (red)"; Filename: "{app}\LabClinico.exe"; Parameters: "--lan --sin-ventana"; IconFilename: "{app}\icons\icono_servidor.ico"
Name: "{group}\Lab Clínico Estación"; Filename: "{app}\LabClinico.exe"; Parameters: "--conectar"; IconFilename: "{app}\icons\icono_estacion.ico"

Name: "{autodesktop}\Lab Clínico"; Filename: "{app}\LabClinico.exe"; Tasks: desktopicon; IconFilename: "{app}\icons\icono_principal.ico"
Name: "{autodesktop}\Lab Clínico Servidor"; Filename: "{app}\LabClinico.exe"; Parameters: "--lan --sin-ventana"; Tasks: desktopicon; IconFilename: "{app}\icons\icono_servidor.ico"
Name: "{autodesktop}\Lab Clínico Estación"; Filename: "{app}\LabClinico.exe"; Parameters: "--conectar"; Tasks: desktopicon; IconFilename: "{app}\icons\icono_estacion.ico"

Name: "{userstartup}\Lab Clínico Servidor"; Filename: "{app}\LabClinico.exe"; Parameters: "--lan --sin-ventana"; Tasks: autoiniciar; IconFilename: "{app}\icons\icono_servidor.ico"

[Run]
Filename: "netsh"; Parameters: "advfirewall firewall add rule name=""Lab Clinico"" dir=in action=allow program=""{app}\LabClinico.exe"" enable=yes"; Flags: runhidden
Filename: "{app}\LabClinico.exe"; Description: "Abrir Lab Clínico ahora"; Flags: nowait postinstall skipifsilent

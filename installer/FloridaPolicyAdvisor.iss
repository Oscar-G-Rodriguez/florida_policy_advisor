[Setup]
AppName=Florida Policy Advisor
AppVersion=0.1.0
DefaultDirName={autopf}\FloridaPolicyAdvisor
DefaultGroupName=Florida Policy Advisor
OutputDir=dist
OutputBaseFilename=FloridaPolicyAdvisor-Setup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=lowest

[Files]
Source: "dist\FloridaPolicyAdvisor.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Florida Policy Advisor"; Filename: "{app}\FloridaPolicyAdvisor.exe"
Name: "{commondesktop}\Florida Policy Advisor"; Filename: "{app}\FloridaPolicyAdvisor.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Run]
Filename: "{app}\FloridaPolicyAdvisor.exe"; Description: "Launch Florida Policy Advisor"; Flags: nowait postinstall skipifsilent

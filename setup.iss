[Setup]
AppName=Civ 5 AI Advisor
AppVersion=1.0
DefaultDirName={autopf}\Civ5AIAdvisor
DefaultGroupName=Civ 5 AI Advisor
OutputDir=Output
OutputBaseFilename=Civ5_AI_Advisor_Setup
Compression=lzma
SolidCompression=yes
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
SetupIconFile=icon.ico
InfoAfterFile=User_Guide.txt

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\Civ5_AI_Advisor\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "User_Guide.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Civ 5 AI Advisor"; Filename: "{app}\Civ5_AI_Advisor.exe"
Name: "{autodesktop}\Civ 5 AI Advisor"; Filename: "{app}\Civ5_AI_Advisor.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Civ5_AI_Advisor.exe"; Description: "{cm:LaunchProgram,Civ 5 AI Advisor}"; Flags: nowait postinstall skipifsilent

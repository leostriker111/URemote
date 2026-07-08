; Inno Setup — instala uremote.exe y agrega el PATH del usuario.
#define Version "0.2.0"

[Setup]
AppName=uremote
AppVersion={#Version}
AppPublisher=Leostriker
DefaultDirName={userpf}\uremote
DefaultGroupName=uremote
OutputBaseFilename=uremote-setup
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest
ChangesEnvironment=yes

[Files]
Source: "..\dist\uremote.exe"; DestDir: "{app}"

[Icons]
Name: "{group}\uremote gui"; Filename: "{app}\uremote.exe"; Parameters: "gui"

[Registry]
Root: HKCU; Subkey: "Environment"; ValueType: expandsz; ValueName: "Path"; \
    ValueData: "{olddata};{app}"; Check: NecesitaPath(ExpandConstant('{app}'))

[Code]
function NecesitaPath(Ruta: string): boolean;
var Actual: string;
begin
  if not RegQueryStringValue(HKCU, 'Environment', 'Path', Actual) then
    Actual := '';
  Result := Pos(';' + Lowercase(Ruta) + ';',
                ';' + Lowercase(Actual) + ';') = 0;
end;

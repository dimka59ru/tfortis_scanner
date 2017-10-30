;------------------------------------------------------------------------------
;
;       ������ ������������� ������� ��� Inno Setup 5.5.5
;       (c) maisvendoo, 15.04.2015
;
;------------------------------------------------------------------------------

;------------------------------------------------------------------------------
;   ���������� ��������� ���������
;------------------------------------------------------------------------------

; ��� ����������
#define   Name       "TFortis Scanner"
; ������ ����������
#define   Version    "2.0.2"
; �����-�����������
#define   Publisher  "Fort-Telecom Ltd."
; ���� ����� ������������
#define   URL        "http://www.tfortis.ru"
; ��� ������������ ������
#define   ExeName    "tfortis.exe"

;------------------------------------------------------------------------------
;   ��������� ���������
;------------------------------------------------------------------------------
[Setup]

; ���������� ������������� ����������, 
;��������������� ����� Tools -> Generate GUID
AppId={{B5D608DE-15D7-439F-8EB8-0DC9618A9962}

; ������ ����������, ������������ ��� ���������
AppName={#Name}
AppVersion={#Version}
AppPublisher={#Publisher}
AppPublisherURL={#URL}
AppSupportURL={#URL}
AppUpdatesURL={#URL}

; ���� ��������� ��-���������
DefaultDirName={pf}\{#Name}
; ��� ������ � ���� "����"
DefaultGroupName={#Name}

; �������, ���� ����� ������� ��������� setup � ��� ������������ �����
OutputDir=C:\Users\USER\YandexDisk\Python\PSW Searcher\20170118_v2.0.2\dist
OutputBaseFileName={#Name}_{#Version}-setup

; ���� ������
SetupIconFile=C:\Users\USER\YandexDisk\Python\PSW Searcher\20170118_v2.0.2\build\exe.win32-3.4\resource\logo_tfortis.ico

; ��������� ������
Compression=lzma
SolidCompression=yes

;------------------------------------------------------------------------------
;   ����������� - ��������� ������, ������� ���� ��������� ��� ���������
;------------------------------------------------------------------------------
[Tasks]
; �������� ������ �� ������� �����
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked


;------------------------------------------------------------------------------
;   �����, ������� ���� �������� � ����� �����������
;------------------------------------------------------------------------------
[Files]

; ����������� ����
Source: "C:\Users\USER\YandexDisk\Python\PSW Searcher\20170118_v2.0.2\build\exe.win32-3.4\tfortis.exe"; DestDir: "{app}"; Flags: ignoreversion

; ������������� �������
Source: "C:\Users\USER\YandexDisk\Python\PSW Searcher\20170118_v2.0.2\build\exe.win32-3.4\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

;------------------------------------------------------------------------------
;   ��������� �����������, ��� �� ������ ����� ������
;------------------------------------------------------------------------------ 
[Icons]

Name: "{group}\{#Name}"; Filename: "{app}\{#ExeName}"

Name: "{commondesktop}\{#Name}"; Filename: "{app}\{#ExeName}"; Tasks: desktopicon
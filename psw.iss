;------------------------------------------------------------------------------
;
;       Пример установочного скрипта для Inno Setup 5.5.5
;       (c) maisvendoo, 15.04.2015
;
;------------------------------------------------------------------------------

;------------------------------------------------------------------------------
;   Определяем некоторые константы
;------------------------------------------------------------------------------

; Имя приложения
#define   Name       "TFortis Scanner"
; Версия приложения
#define   Version    "2.0.2"
; Фирма-разработчик
#define   Publisher  "Fort-Telecom Ltd."
; Сайт фирмы разработчика
#define   URL        "http://www.tfortis.ru"
; Имя исполняемого модуля
#define   ExeName    "tfortis.exe"

;------------------------------------------------------------------------------
;   Параметры установки
;------------------------------------------------------------------------------
[Setup]

; Уникальный идентификатор приложения, 
;сгенерированный через Tools -> Generate GUID
AppId={{B5D608DE-15D7-439F-8EB8-0DC9618A9962}

; Прочая информация, отображаемая при установке
AppName={#Name}
AppVersion={#Version}
AppPublisher={#Publisher}
AppPublisherURL={#URL}
AppSupportURL={#URL}
AppUpdatesURL={#URL}

; Путь установки по-умолчанию
DefaultDirName={pf}\{#Name}
; Имя группы в меню "Пуск"
DefaultGroupName={#Name}

; Каталог, куда будет записан собранный setup и имя исполняемого файла
OutputDir=C:\Users\USER\YandexDisk\Python\PSW Searcher\20170118_v2.0.2\dist
OutputBaseFileName={#Name}_{#Version}-setup

; Файл иконки
SetupIconFile=C:\Users\USER\YandexDisk\Python\PSW Searcher\20170118_v2.0.2\build\exe.win32-3.4\resource\logo_tfortis.ico

; Параметры сжатия
Compression=lzma
SolidCompression=yes

;------------------------------------------------------------------------------
;   Опционально - некоторые задачи, которые надо выполнить при установке
;------------------------------------------------------------------------------
[Tasks]
; Создание иконки на рабочем столе
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked


;------------------------------------------------------------------------------
;   Файлы, которые надо включить в пакет установщика
;------------------------------------------------------------------------------
[Files]

; Исполняемый файл
Source: "C:\Users\USER\YandexDisk\Python\PSW Searcher\20170118_v2.0.2\build\exe.win32-3.4\tfortis.exe"; DestDir: "{app}"; Flags: ignoreversion

; Прилагающиеся ресурсы
Source: "C:\Users\USER\YandexDisk\Python\PSW Searcher\20170118_v2.0.2\build\exe.win32-3.4\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

;------------------------------------------------------------------------------
;   Указываем установщику, где он должен взять иконки
;------------------------------------------------------------------------------ 
[Icons]

Name: "{group}\{#Name}"; Filename: "{app}\{#ExeName}"

Name: "{commondesktop}\{#Name}"; Filename: "{app}\{#ExeName}"; Tasks: desktopicon
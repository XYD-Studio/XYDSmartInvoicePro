[Setup]
; 软件基础信息
AppName=SmartInvoice 智能票据助手
AppVersion=1.0.0
AppPublisher=玄宇绘世设计工作室
AppPublisherURL=https://www.xy-d.top/
AppSupportURL=https://www.xy-d.top/
AppUpdatesURL=https://www.xy-d.top/

; 默认安装路径设定 (安装在用户本地 AppData 下可以避免很多管理员权限弹窗)
DefaultDirName={autopf}\SmartInvoicePro
PrivilegesRequired=admin
DefaultGroupName=SmartInvoice 智能票据助手
DisableProgramGroupPage=yes

; 许可协议书的路径 (替换为你实际存放 License.txt 的路径)
LicenseFile=F:\code_available\SmartInvoicePro\License.txt

; 最终生成的安装包存放位置和文件名
OutputDir=d:\输出路径\
OutputBaseFilename=SmartInvoice_Setup_v1.0

; 安装界面的压缩级别
Compression=lzma
SolidCompression=yes
WizardStyle=modern

; ====================================================
; >>> 核心修改：指定各种图标 (必须是 .ico 格式) <<<
; ====================================================

; 1. 指定生成的安装包文件 (Setup.exe) 自身的图标
SetupIconFile=F:\code_available\SmartInvoicePro\backend\logo.ico

; 2. 指定安装及卸载程序在 Windows 控制面板“卸载或更改程序”列表中显示的图标
UninstallDisplayIcon={app}\SmartInvoicePro.exe

[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; 打包核心：这里 Source 指向你 PyInstaller 生成的那个文件夹
; 注意路径末尾的 \* 必须保留！
Source: "F:\code_available\SmartInvoicePro\backend\dist_app\SmartInvoicePro\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; 生成开始菜单快捷方式 (IconFilename 会自动从 EXE 提取，或者你可以显式指定)
Name: "{group}\SmartInvoice 智能票据助手"; Filename: "{app}\SmartInvoicePro.exe"; IconFilename: "{app}\SmartInvoicePro.exe"
; 生成桌面快捷方式
Name: "{autodesktop}\SmartInvoice 智能票据助手"; Filename: "{app}\SmartInvoicePro.exe"; Tasks: desktopicon; IconFilename: "{app}\SmartInvoicePro.exe"

[Run]
; 安装完成后，勾选默认立刻运行软件
Filename: "{app}\SmartInvoicePro.exe"; Description: "{cm:LaunchProgram,SmartInvoice 智能票据助手}"; Flags: nowait postinstall skipifsilent
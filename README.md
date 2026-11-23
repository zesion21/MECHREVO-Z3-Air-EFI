# MECHREVO Z3 Air · macOS Tahoe EFI

机械革命 Z3 Air，i5-10300H / UHD 630 / GTX 1650 Mobile / Intel AC 9462 的 OpenCore EFI。

基于原 [zechen21/mechrevo-z3-air-efi](https://gitee.com/zechen21/mechrevo-z3-air-efi) 适配 macOS 26，并整理本机最终可用配置。**2026-11-23，本机已验证 macOS 26.7.2（25G332）启动、无线、蓝牙、声音、内屏亮度及 GTX 1650 HDMI 输出。** 其他硬件组合、系统版本需要自行验证。

**两个使用前提：** 仓库中的机器身份都是占位符，使用前必须填写自己的身份；GTX 1650 还需要在 macOS 中安装 1401 / NullMoth 驱动，仅复制 EFI 不等于已安装独显驱动。

## 实测硬件与功能

| 项目 | 配置 / 状态 |
| --- | --- |
| 笔记本 | 机械革命 Z3 Air |
| CPU / 内存 | Intel Core i5-10300H / 32 GB |
| 核显 | Intel UHD Graphics 630，系统设备 ID `0x3e9b`，Metal 3 可枚举 |
| 独显 | NVIDIA GeForce GTX 1650 Mobile，TU117，`10de:1f99`，4 GB |
| 无线 / 蓝牙 | Intel Wireless-AC 9462；Wi-Fi、蓝牙已验证可用 |
| 声音 | 内置声音已验证可用；AppleALC + SimpleHDA，`alcid=28` |
| 内屏 | 1920 × 1080，144 Hz；核显驱动；系统亮度滑块和 Fn 亮度键可用 |
| GTX 1650 | NullMoth 3.0 驱动已加载，系统枚举为独立 Metal 设备；未做性能和完整应用兼容性测试 |
| HDMI | 已验证外屏能显示；**显示器开机并接好 HDMI 后，再启动笔记本** |
| USB | USBToolBox + 本机 UTBMap；安装 U 盘所在接口可用，全部接口和 Type-C 方向未逐项验收 |
| 有线网卡 | 包含 RealtekRTL8111 驱动，未单独验收 |
| 键盘、触控板、电池信息 | 保留对应驱动和 ACPI 配置，未逐项形成验收记录 |
| 睡眠唤醒、休眠、HDMI 音频 | 未专项验证 |
| AirDrop、接力、Apple 服务、DRM、CUDA | 未验证，不能依据本 EFI 承诺支持 |

HDMI 热插拔存在限制：本机在进入 macOS 后才插线时，驱动能读取外屏信息，但系统未成功启用外屏；开机前接线已实测可用。相关上游记录见 [Issue #288](https://github.com/nullmoth/nvidia-macos-driver/issues/288)。不要把这一限制误判为驱动没有安装。

内屏目前仍由 UHD 630 驱动，因此系统设置显示 UHD 是正常现象。仓库没有启用实验性的内屏混合渲染方案，也没有验证本机存在可切换的硬件 MUX；配置文件不能改变内屏的物理接线。参考 [上游混合显卡说明](https://github.com/nullmoth/nvidia-macos-driver/blob/v3.0/docs/HYBRID-LAPTOPS.md)。

## 目录与三套配置

```text
EFI/
  BOOT/BOOTx64.efi
  OC/
    config.plist                      # 已安装 1401 后的最终可用设置，身份已脱敏
    ACPI/ Drivers/ Kexts/ Tools/
configs/
  config-UHD630.plist                  # 核显安装 / 基础功能配置，关闭独显
  config-GTX1650-preinstall.plist      # 安装独显驱动前的准备配置，保留核显和亮度
docs/
  component-downloads.json             # 适配过程所用发布包来源、版本及下载校验信息
  kext-versions.json                   # 当前 EFI 内实际 kext 版本
  SHA256SUMS.txt                       # 发布状态下 EFI 与配置的文件校验值
  validation.json                     # 本次发布前静态检查记录
scripts/validate.py                    # 静态配置、文件引用、发布占位符和校验值检查
licenses/                             # 收集的上游许可证
THIRD_PARTY.md                        # 组件来源与许可说明
```

OpenCore 实际只读取 `EFI/OC/config.plist`。`configs/` 中的文件需要复制到该位置并命名为 `config.plist` 才会生效。

默认文件保留本机 1401 安装后的 SIP、AMFI、驱动屏蔽和恢复工具设置。**新安装从 `config-UHD630.plist` 开始。** 两套辅助配置也取自本机上传的配置 / 安装前备份，未重新猜测硬件参数。

## 使用前：生成自己的机器身份

1. 下载仓库后，先复制出一份供安装使用的工作副本；保留 Git 仓库中的公开占位符。
2. 使用 [GenSMBIOS](https://github.com/corpnewt/GenSMBIOS) 生成 `MacBookPro16,1` 的机器身份，用 [ProperTree](https://github.com/corpnewt/ProperTree) 编辑 plist。
3. 在三套配置的 `PlatformInfo → Generic` 中填写**同一组**个人身份：

| 字段 | 仓库占位符 | 使用时填写 |
| --- | --- | --- |
| `SystemProductName` | `MacBookPro16,1` | 保持此型号 |
| `SystemSerialNumber` | `XXXXXXXXXXXX` | 自己生成的序列号 |
| `MLB` | `XXXXXXXXXXXXXXXXX` | 与序列号配套生成的主板序列号 |
| `SystemUUID` | `00000000-0000-0000-0000-000000000000` | 自己生成的有效 UUID |
| `ROM` | 6 字节全零，Data 类型 | 本机固定网卡的 6 字节 MAC 值，去掉分隔符后按 Data 填写 |

UUID 和 ROM 使用全零占位以保持字段格式，不能直接填入非十六进制的 `xxxxxx`。切换配置时保持身份一致；不要把个人配置、1401 备份或带身份信息的日志提交到公开仓库。`.gitignore` 不会阻止已跟踪配置被提交，发布前需要恢复占位符并检查差异。

## 新用户安装步骤

### 1. 准备 macOS 安装介质

- 自备 macOS Tahoe 安装介质。本仓库不含系统镜像；制作方式参考 [OpenCore 安装指南](https://dortania.github.io/OpenCore-Install-Guide/installer-guide/)。
- 先备份原 EFI，再把工作副本的整个 `EFI` 文件夹放到安装 U 盘的 EFI 分区根目录。避免形成 `EFI/EFI`，也不要与其他机型的旧 EFI 混合。
- 将填好身份的 `configs/config-UHD630.plist` 复制为 U 盘上的 `EFI/OC/config.plist`。
- 固件采用 UEFI 启动，关闭固件 Secure Boot；其他 BIOS 项按实际固件和 [Comet Lake 笔记本指南](https://dortania.github.io/OpenCore-Install-Guide/config-laptop.plist/coffee-lake-plus.html) 核对。这里的固件 Secure Boot 与配置中的 Apple `SecureBootModel` 是不同设置。
- 本机 USB 映射只包含 5 个通道。其他机器即使同型号，也应核对映射；安装介质不能识别时，不要直接套用所有接口均可用的假设。

### 2. 使用核显完成安装

从 U 盘的 UEFI 项进入 OpenCore，安装阶段选择 `Install macOS Tahoe`；重启后按安装进度选择 `macOS Installer` 或目标系统卷。首次完整替换旧 EFI 后可执行一次 `Reset NVRAM`，再从正确的 U 盘启动。

先确认系统启动、Wi-Fi、声音、蓝牙、内屏和 USB 基本正常。只使用核显的用户可以停在这一阶段，不需要安装 1401。驱动条目主要限定 Darwin 25，本仓库没有验证 macOS 13 / 14 / 15 的整套适配。

### 3. 开放 GTX 1650，并安装 1401

1. 保存核显配置和可启动的恢复 U 盘。
2. 将**同一身份已填写**的 `configs/config-GTX1650-preinstall.plist` 复制为当前启动 EFI 的 `EFI/OC/config.plist`，重启确认能进入系统且亮度正常。
3. 下载本机验证过的 [1401-Mac-3.0.dmg](https://github.com/nullmoth/nvidia-macos-driver/releases/download/v3.0/1401-Mac-3.0.dmg)，在 macOS 中打开 1401，运行 NVIDIA 驱动安装流程。
4. 核对 1401 选择的是实际引导本机的 OpenCore 分区，按程序提示安装并允许所需系统扩展，然后重启。安装时以及后续重启时，保留实际启动的 U 盘连接，直到已确认硬盘 EFI 可以独立引导。
5. 正常启动仍选择原来的 **macOS 系统卷**。`1401: Remove NVIDIA driver` 用于卸载，`1401: Start once without NVIDIA driver` 用于单次绕过独显驱动，它们都不是日常系统入口。
6. HDMI 显示器先开机、接线，再启动笔记本。

1401 会安装系统端驱动、Metal 插件和 GPU 固件，并修改当前 OpenCore 配置。**安装成功后保留它修改后的配置，不要再用仓库的旧配置覆盖。** 新用户以安装器实际生成的配置为准；默认最终配置主要用于说明本机已验证状态及已安装系统的迁移。

独显安装会放宽 SIP / AMFI 等安全设置；默认最终配置保留本机安装器设置，其中 `csr-active-config` 为 Data `430A0000`，`SecureBootModel=Disabled`。核显安装配置的 SIP 为 `00000000`。这些是两个安装阶段的差异，不能只改显卡名称来替代驱动安装。

驱动位于系统的 `/Library/Extensions` 和 `/Library/GPUBundles`，**不要把 NVRM / NVAccel 等再次复制到 EFI 注入**。细节见 [NullMoth 3.0 安装说明](https://github.com/nullmoth/nvidia-macos-driver/blob/v3.0/README.md)。

### 4. 固件下载中断时

如果安装器提示 `curl: (18) Transferred a partial file`，先解决下载问题，再重试安装；显示“已安装”之前仍需检查安装结果。

3.0 安装流程需要从 [NVIDIA 官方 620.70.06 包](https://download.nvidia.com/XFree86/Linux-x86_64/620.70.06/NVIDIA-Linux-x86_64-620.70.06.run) 提取固件，文件约 550 MB，SHA-256 为：

```text
29118e3abd08c07559bcca3d9c76238d039490af0362a2e5bcfcbe7204afd4b1
```

可以先完整下载并核对 SHA-256，按安装器提示把该文件放到其 `install.sh` 旁，再重试；手动安装包也支持向 `install.sh` 传入 `--run FILE`。这是供 macOS 安装器读取的固件来源，**不要执行这个 Linux `.run` 程序**。路径中有空格时使用引号，或把文件拖入终端插入实际路径。上游获取规则见 [fw_fetch.sh](https://github.com/nullmoth/nvidia-macos-driver/blob/v3.0/package/fw_fetch.sh)。

本仓库不包含 NVIDIA 固件、1401 安装包和系统端独显驱动，使用者从上游下载。

### 5. 验证与迁移到硬盘

```bash
kmutil showloaded --list-only | grep -i nullmoth
system_profiler SPDisplaysDataType
sysctl -n kern.bootargs
```

本机可看到 NVRM、NVRMFB、NVRMAGDC、NVAccel 和 NMXAudio 已加载，显示信息中同时存在 UHD 630 与 GTX 1650 4 GB。Metal 能枚举不代表所有软件、编解码、CUDA 或游戏兼容性都已验证。

确认可启动后，将**实际启动分区中安装器修改后的完整 EFI**复制到目标硬盘 EFI 分区，再在固件中选择该硬盘启动。核对无 U 盘时仍能启动，最后保留一份个人 EFI 备份。不要复制尚未填写身份的仓库模板替代已经工作的个人配置。

## 常见问题

- **HDMI 没画面：** 关机，打开显示器并切到对应输入，插好 HDMI，再开机。本机已验证该方式；登录后首次插线存在问题。
- **关于本机 / 显示设置仍显示 UHD：** 内屏仍连接核显。查看完整 `system_profiler` 输出确认独显是否出现，不能只看内屏所属 GPU。
- **开放独显后不能调亮度：** 准备配置和最终配置保留 `applbkl=1`、WhateverGreen、SSDT-PNLF / SSDT-FN；本机已验证亮度恢复。不要关闭核显来尝试“强制独显”。
- **禁止符号 / `Still waiting for root device`：** 优先核对安装介质、接口和 USB 映射。原来的 USBInjectAll + SSDT-UIAC 已换为 USBToolBox + UTBMap，不要再叠加旧方案。
- **驱动安装后启动失败：** 可先尝试 `1401: Start once without NVIDIA driver`，或用备份的核显 EFI 启动；需要卸载时使用 1401 的卸载入口。
- **系统升级：** 先保留可启动备份，核对 1401、无线和音频等上游兼容性；升级后独显驱动可能需要重新安装，不能据本机 26.7.2 结果推断后续版本。

## USB 映射范围

控制器为 Intel `8086:06ed`，映射以 `XHC` 匹配。HS / SS 名称是工具生成的标签，实际端口编号如下：

| 标签 | 硬件端口 | 类型 |
| --- | --- | --- |
| HS01 | 2 | 内部设备，255 |
| HS02 | 9 | 外部 USB 3 接口的 USB 2 通道，3 |
| HS03 | 13 | 内部设备，255 |
| HS04 | 14 | 内部设备，255 |
| SS01 | 22 | 外部 USB 3 通道，3 |

实际启用 5 个通道；`port-count=22` 是最高硬件编号，不是启用数量。类型沿用本机采集结果；全部接口、Type-C 两个方向及睡眠唤醒仍应单独测试。更换机器时可用 [USBToolBox](https://github.com/USBToolBox/tool) 重新采集。

## 发布检查与来源

本次整理保留了最终可用配置的非身份设置，以及所收录 EFI 二进制的原始内容；剔除了 1401 历史备份和 Finder 元数据。实机结果来自上述笔记本，脱敏发布模板没有重新进行安装或启动测试。

```bash
python3 scripts/validate.py
python3 scripts/validate.py --ocvalidate /path/to/ocvalidate
```

检查器面向**未个人化的发布副本**；填写个人身份后会有意报占位符差异，校验值也会变化。校验记录只证明结构、引用及发布脱敏检查，不替代实机验证。

组件与许可证见 [THIRD_PARTY.md](THIRD_PARTY.md)，当前实际版本见 [kext-versions.json](docs/kext-versions.json)，历史下载包来源见 [component-downloads.json](docs/component-downloads.json)。原 EFI 来源提交为 `1f1bb860dddb15cdd41551b74aed9886aec7049a`。第三方组件归各自作者所有，按各自许可使用。

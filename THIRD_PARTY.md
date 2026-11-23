# 第三方组件

本仓库汇集本机适配配置与第三方 EFI / kext 二进制，不将整套第三方代码重新许可。上游许可证、版权及对应源代码以各项目为准；`licenses/` 收集可获取的上游许可文本，部分组件来自原 EFI，不能据文件夹名推断其构建提交。

| 组件 | 当前版本 / 来源 |
| --- | --- |
| 原始机型 EFI、ACPI、VoodooWMI / VoodooWMIHotkey、RealtekRTL8111 | [zechen21/mechrevo-z3-air-efi](https://gitee.com/zechen21/mechrevo-z3-air-efi)，源提交 `1f1bb860dddb15cdd41551b74aed9886aec7049a`；继承的 WMI 为 1.0.0，RTL8111 为 2.4.2 |
| OpenCore、OpenRuntime、OpenHfsPlus、ResetNvramEntry | [OpenCorePkg 1.0.8](https://github.com/acidanthera/OpenCorePkg/tree/1.0.8) |
| Lilu | [1.7.2](https://github.com/acidanthera/Lilu/tree/1.7.2) |
| WhateverGreen | [1.7.1](https://github.com/acidanthera/WhateverGreen/tree/1.7.1) |
| VirtualSMC、SMCBatteryManager、SMCProcessor、SMCSuperIO | [VirtualSMC 1.3.8](https://github.com/acidanthera/VirtualSMC/tree/1.3.8) |
| AppleALC | [1.9.8](https://github.com/acidanthera/AppleALC/tree/1.9.8) |
| SimpleHDA | [laobamac 1.0.3-alpha，10e6d09](https://github.com/laobamac/SimpleHDA/releases/tag/v1.0.3-alpha) |
| RestrictEvents | [1.1.6](https://github.com/acidanthera/RestrictEvents/tree/1.1.6) |
| VoodooPS2Controller 与键盘插件 | [2.3.7](https://github.com/acidanthera/VoodooPS2/tree/2.3.7) |
| VoodooI2C、VoodooI2CHID 与相关插件 | [2.9.1](https://github.com/VoodooI2C/VoodooI2C/tree/v2.9.1)；子组件有各自版本号 |
| AirportItlwm | [laobamac Tahoe 2.4.0-alpha，7204c69](https://github.com/laobamac/itlwm/releases/tag/v2.4.0-alpha) |
| IntelBluetoothFirmware、IntelBTPatcher | [lshbluesky 2.5.3](https://github.com/lshbluesky/IntelBluetoothFirmware/tree/v2.5.3) |
| BlueToolFixup | [BrcmPatchRAM 2.7.2](https://github.com/acidanthera/BrcmPatchRAM/tree/2.7.2) |
| USBToolBox | [1.2.0](https://github.com/USBToolBox/kext/tree/1.2.0) |
| UTBMap | 本机 Windows USBToolBox 采集的 5 通道映射，Info.plist 版本 1.1 |
| AMFIPass | 1.4.1，标识 `com.dhinakg.AMFIPass`，来自本机 1401 安装后的 EFI；通过 [1401](https://github.com/nullmoth/1401) 获取，未核实独立公开源码地址 |
| NullMothSafe.efi | 本机 1401 3.0 添加的卸载 / 单次绕过工具；[1401](https://github.com/nullmoth/1401) |
| 独显系统驱动（不随本仓库分发） | [NullMoth NVIDIA driver 3.0](https://github.com/nullmoth/nvidia-macos-driver/tree/v3.0)，通过 1401 安装 |

`docs/component-downloads.json` 是适配过程中更新组件的下载记录，不是所有继承文件的完整构建溯源。`docs/kext-versions.json` 从最终 EFI 实际 Info.plist 读取；文件完整性以 `docs/SHA256SUMS.txt` 为准。

仓库不包含个人身份、系统镜像、1401 安装包、NVIDIA `.run` 包或提取的 NVIDIA 固件。上游发布包及源码链接用于使用者获取对应组件与许可。

许可证采集结果和具体来源记录在 [licenses/sources.json](licenses/sources.json)。SimpleHDA、USBToolBox、继承的 RTL8111 及 AMFIPass 未通过上游标准 LICENSE 接口取得独立许可文本；采集失败不表示没有许可，具体条款需查阅上游源码头、NOTICE 或原始发布包。

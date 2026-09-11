---
name: Godot Android APK 打包与阶段发布流程
tags: [Godot, Android, APK, 打包, 运维, 技能]
description: Godot 4.x 项目在 Windows 环境下自动化搭建 Android 构建环境、签名配置、命令行无头导出与版本覆盖升级的标准操作指南
metadata:
  node_type: memory
  type: reference
  status: 稳定有效
  modified: 2026-09-11
  version: v1.0
---

# Godot Android APK 打包与阶段发布流程

> 导航：[[MEMORY]] · [[技能/说明]]
>
> 本指南是面向 Godot 4.x 原生手机游戏（Android 平台）的**端到端标准化发布指南**。  
> 任何后续会话只需照本操作，即可在全新 Windows 开发机上完成 Android 环境初始化、密钥生成、无头导出与覆盖升级验证。

---

## 1. 核心发布原则与阶段划分

### 阶段定义与发布节奏
- **Build A0（开发试玩基线）**：环境跑通、首个可运行 APK 产生、基础签名锁定、`user://` 持久化与生命周期验证通过。
- **Build A1~An（阶段性测试包）**：不随高频 Web 测试每日打包，仅在阶段里程碑（如包 4、包 5 完成）时导出，用于真机体验与触控调优。
- **Build B0（公开测试包）**：UI 安全区、各品牌全面屏适配、性能达标、图标与启动屏规范完备。
- **Release（正式商用发布）**：开启 AAB 导出或应用商店加固、混淆与最终正式签名。

### 机械红线规则
1. **单一事实源**：APK 必须且只能从 Godot 原生项目目录导出，严禁为了打包把网页版包裹为套壳 WebView。
2. **凭据安全绝对隔离**：Keystore 必须存放于独立目录并在 `.gitignore` 机械拦截，**知识库、日志、代码中严禁记录任何私钥密码或密钥口令**。
3. **身份不可变性**：Application ID / Package Name 一旦确立（如 `com.deepmine.game`），在正式上架前禁止擅自变动，否则系统视为全新应用，将导致旧存档断裂。
4. **覆盖升级递增性**：每次导出供覆盖安装的新版本，`version/code` 必须严格单调递增（1 -> 2 -> 3...），`version/name` 保持语义化版本。

---

## 2. Windows 编译环境准备（一键就绪清单）

构建 Android 原生 APK 需要以下三大核心组件：

### 2.1 JDK 17
- **推荐版本**：Eclipse Adoptium OpenJDK 17.0.x (LTS) 64 位。
- **部署路径**：建议统一放置于 `C:\Android\jdk-17\`。
- **关键命令校验**：
  ```powershell
  & "C:\Android\jdk-17\bin\java.exe" -version
  & "C:\Android\jdk-17\bin\keytool.exe" -help
  ```

### 2.2 Android SDK 命令行工具
- **部署根目录**：`C:\Android\Sdk`。
- **必需组件**：
  - `platform-tools` (含 adb)
  - `build-tools;34.0.0` (含 `apksigner.bat` 与 `zipalign.exe`)
  - `platforms;android-34` (含 `android.jar`)
- **部署步骤**：
  1. 从 Google 官方下载 `commandlinetools-win-xxxx_latest.zip` 并解压到 `C:\Android\Sdk\cmdline-tools\latest\`；
  2. 预先写入 license 文件：
     ```powershell
     New-Item -ItemType Directory -Force -Path "C:\Android\Sdk\licenses"
     "8933bad161af4178b1185d1a37fbf41ea5269c55`nd56f5185479d6f7977d15828a6e383fc55088e1e" | Out-File -FilePath "C:\Android\Sdk\licenses\android-sdk-license" -Encoding ASCII
     ```
  3. 执行安装：
     ```powershell
     $env:JAVA_HOME = "C:\Android\jdk-17"
     & "C:\Android\Sdk\cmdline-tools\latest\bin\sdkmanager.bat" --sdk_root="C:\Android\Sdk" "platform-tools" "build-tools;34.0.0" "platforms;android-34"
     ```

### 2.3 Godot 导出模板 (Export Templates)
- **部署路径**：`%APPDATA%\Godot\export_templates\<Godot版本>.stable\`。
- **关键文件**：`android_debug.apk`, `android_release.apk`, `version.txt`。
- **解压技巧（避坑）**：
  Godot 官方提供的 `.tpz` 文件本质是标准 ZIP 文件，但包含多平台。PowerShell `Expand-Archive` 不支持 `.tpz` 扩展名。推荐用 Python `zipfile` 快速解压：
  ```python
  import zipfile, os, shutil
  tpz = r"C:\Android\downloads\export_templates.tpz"
  target = os.path.expandvars(r"%APPDATA%\Godot\export_templates\4.7.2.stable")
  with zipfile.ZipFile(tpz, "r") as zf:
      for m in zf.infolist():
          if m.filename.startswith("templates/") and not m.is_dir():
              dest = os.path.join(target, m.filename[len("templates/"):])
              os.makedirs(os.path.dirname(dest), exist_ok=True)
              with zf.open(m) as s, open(dest, "wb") as d:
                  shutil.copyfileobj(s, d)
  ```

### 2.4 配置 Godot 全局编辑器设置
在 `%APPDATA%\Godot\editor_settings-4.7.tres` 中指定全局 SDK/JDK 路径：
```ini
export/android/java_sdk_path = "C:/Android/jdk-17"
export/android/android_sdk_path = "C:/Android/Sdk"
```

---

## 3. 生成项目专用签名 Keystore

### 操作步骤
在项目根目录创建专用目录 `android/keys/`，并调用 `keytool` 生成专属 Release 密钥库：
```powershell
# 推荐使用 Python 脚本调用，规避 PowerShell 字符转义导致的密码错乱
python -c "import subprocess; subprocess.run(['C:\\\\Android\\\\jdk-17\\\\bin\\\\keytool.exe', '-genkeypair', '-v', '-keystore', 'android/keys/deepmine.keystore', '-alias', 'deepmine', '-keyalg', 'RSA', '-keysize', '2048', '-validity', '10000', '-storepass', '<口令>', '-keypass', '<口令>', '-dname', 'CN=DeepMine, OU=Game, O=DeepMine, C=CN'])"
```

### 关键检查项
1. 在项目根目录 `.gitignore` 添加：
   ```gitignore
   android/keys/
   *.keystore
   builds/
   *.apk
   ```
2. 校验密钥库指纹：
   ```cmd
   "C:\Android\jdk-17\bin\keytool.exe" -list -keystore android/keys/deepmine.keystore
   ```

---

## 4. 配置项目与导出预设

### 4.1 项目设置 `project.godot`
在 `[rendering]` 段必须启用 ASTC/ETC2 压缩支持，否则 Android 导出引擎将报错中断：
```ini
[rendering]
renderer/rendering_method="gl_compatibility"
textures/vram_compression/import_etc2_astc=true
```

### 4.2 预设文件 `export_presets.cfg`
在工程根目录维护标准 Android 预设配置：
```ini
[preset.0]

name="Android"
platform="Android"
runnable=true
advanced_options=false
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter=""
export_path="builds/android/deep-mine-a0-v0.3.2.apk"
encryption_include_filters=""
encryption_exclude_filters=""
encrypt_pck=false
encrypt_directory=false

[preset.0.options]

custom_template/debug=""
custom_template/release=""
gradle_build/use_gradle_build=false
architectures/arm64-v8a=true
architectures/armeabi-v7a=false
architectures/x86_64=false
architectures/x86=false
package/unique_name="com.deepmine.game"
package/name="深井"
package/signed=true
package/app_category=0
package/retain_data_on_uninstall=false
package/exclude_from_recents=false
package/show_in_launcher=true
package/show_in_android_tv=false
launcher_icons/main_192x192=""
launcher_icons/adaptive_foreground_432x432=""
launcher_icons/adaptive_background_432x432=""
version/code=1
version/name="0.3.2-a0"
screen/orientation=1
screen/support_small=true
screen/support_normal=true
screen/support_large=true
screen/support_xlarge=true
screen/immersive_mode=true
screen/support_multiple_displays=false
screen/aspect_ratio=0
user_data_backup/allow=false
command_line/extra_args=""
keystore/debug=""
keystore/debug_user=""
keystore/debug_password=""
keystore/release="E:/项目/deep-mine/android/keys/deepmine.keystore"
keystore/release_user="deepmine"
keystore/release_password="<密码>"
```

---

## 5. 命令行无头导出与验证流程

### 5.1 一键导出 Release APK
使用 Godot 控制台无头模式执行导出：
```cmd
godot_console --headless --path "E:\项目\deep-mine" --export-release "Android" "E:\项目\deep-mine\builds\android\deep-mine-a0-v0.3.2.apk"
```

### 5.2 官方工具校验
1. **签名有效性与 Scheme 验证**：
   ```cmd
   set JAVA_HOME=C:\Android\jdk-17
   set PATH=C:\Android\jdk-17\bin;%PATH%
   C:\Android\Sdk\build-tools\34.0.0\apksigner.bat verify --verbose builds\android\deep-mine-a0-v0.3.2.apk
   ```
   *预期输出*：`Verifies`，`Verified using v2 scheme: true`, `v3 scheme: true`。

2. **元数据、包名与版本核验**：
   ```cmd
   C:\Android\Sdk\build-tools\34.0.0\aapt2.exe dump badging builds\android\deep-mine-a0-v0.3.2.apk
   ```
   *核对要点*：
   - `package: name='com.deepmine.game'`
   - `versionCode='1'`
   - `versionName='0.3.2-a0'`
   - `native-code: 'arm64-v8a'`
   - `uses-feature: name='android.hardware.screen.portrait'`

---

## 6. 版本递增与覆盖升级标准流程

当推出下一个稳定测试包时，按以下机械步骤操作，确保真机可无缝覆盖安装且保留 `user://` 存档：

1. **更新代码/版本号**：在 `project.godot` 更新 `config/version`。
2. **递增 versionCode**：
   打开 `export_presets.cfg`，修改：
   ```ini
   export_path="builds/android/deep-mine-a0-v0.3.2-v2.apk"
   version/code=2
   version/name="0.3.2-a0"
   ```
3. **保持签名不变**：绝对不要修改 `keystore/release` 与 `keystore/release_user`。
4. **重新执行导出命令**。
5. **AAPT2 校验**：确认新的 APK 的 `versionCode` 为上一版本 +1，包名和签名与上一版本 100% 相同。

---

## 7. Android 系统级适配要点（GDScript）

在主场景代码（`main.gd`）中必须监听系统返回键与生命周期，防止崩溃或异响：

```gdscript
func _notification(what: int) -> void:
    if what == NOTIFICATION_WM_GO_BACK_REQUEST:
        _handle_android_back()
    elif what == NOTIFICATION_APPLICATION_PAUSED:
        _handle_application_paused()
    elif what == NOTIFICATION_APPLICATION_RESUMED:
        _handle_application_resumed()

func _handle_android_back() -> void:
    if show_popup:
        show_popup = false
        queue_redraw()
        return
    if is_in_title_menu:
        get_tree().quit() # 标题主页返回退出 App
    else:
        toggle_pause_menu() # 游戏中返回打开/关闭菜单

func _handle_application_paused() -> void:
    # 切后台/锁屏：自动保存 + 静音主总线
    save_game_safe()
    AudioServer.set_bus_mute(0, true)

func _handle_application_resumed() -> void:
    # 回到前台：解除静音
    AudioServer.set_bus_mute(0, false)
```

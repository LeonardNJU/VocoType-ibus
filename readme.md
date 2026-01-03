# VoCoType Linux IBus 语音输入法

<h2 align="center">Linux 专用的离线语音输入法</h2>

**VoCoType Linux IBus** 是基于 [VoCoType](https://github.com/233stone/vocotype-cli) 核心引擎开发的 **Linux IBus 输入法**。

在 AI 辅助时代，语音输入已成为提升效率的重要工具。本项目将 VoCoType 的强大离线语音识别能力集成到 Linux 的 IBus 输入法框架中，让所有 Linux 用户都能享受流畅的语音输入体验。

---

## 💡 为什么选择离线语音输入法？

### 🔒 隐私安全第一
- **100% 本地离线**，所有语音数据不上传任何服务器
- 适合处理敏感文档、工作邮件、个人日记
- 符合企业安全规范和隐私保护要求

### 🚀 提升效率利器
- 语音输入比键盘打字更快、更自然
- 适合长文本输入：文章、报告、邮件、聊天
- **特别适合开发者**：快速输入代码注释、commit message、技术文档
- **AI 时代必备**：与 ChatGPT、Claude、Cursor 等 AI 工具配合使用

### 🐧 原生 Linux 体验
- 完美融入 IBus 输入法框架
- 支持所有 Linux 发行版 (Fedora, Ubuntu, Debian, Arch 等)
- 在任何应用中都能使用：浏览器、终端、编辑器、办公软件

---

## ✨ 核心特性

基于 VoCoType 强大的核心引擎，所有原版优势完整保留：

- **🛡️ 100% 离线，隐私无忧**：所有语音识别在您的电脑本地完成，不上传任何数据
- **⚡️ 旗舰级识别引擎**：基于 FunASR Paraformer 模型，中英混合输入同样精准
- **🎯 PTT 按键说话**：按住 F9 说话，松开自动识别并输入
- **💻 轻量化设计**：仅需 700MB 内存，纯 CPU 推理，无需显卡
- **🚀 0.1 秒级响应**：感受所言即所得的畅快体验
- **🔧 交互式配置**：自动识别麦克风设备，测试录音和识别效果
- **📝 精准识别**：支持专业术语、人名、地名，识别准确率超过 95%

**Linux 专属特性：**
- **🐧 原生 IBus 集成**：完美融入 Linux 输入法体系
- **⌨️ 全局可用**：在任何支持 IBus 的应用中都能使用
- **🔄 开源透明**：代码完全开源，可审计、可定制
- **🎨 灵活选择**：纯语音版本或集成 Rime 拼音输入，按需安装

---

## 🛠️ 安装指南

VoCoType Linux IBus 提供两种版本供您选择：

| 版本 | 功能 | 适用场景 |
|------|------|---------|
| **🎤 纯语音版** | F9 语音输入 | 只需要语音输入，使用其他拼音输入法 |
| **✨ 完整版** | F9 语音 + Rime 拼音 | 一个输入法同时支持语音和拼音 |

### 📦 方式一：纯语音版（推荐新手）

**特点**：
- ✅ 仅语音输入功能（按 F9 说话）
- ✅ 依赖少，安装简单
- ✅ 可与其他拼音输入法（如 ibus-rime、fcitx-rime）配合使用
- ✅ 适合已有喜欢的拼音输入法的用户

**安装步骤**：

#### 1. 环境依赖

- **Linux 发行版**: 支持 IBus 的任何发行版 (Fedora, Ubuntu, Debian, Arch 等)
- **Python**: 3.12+
- **IBus**: 系统已安装并启用 IBus 输入法框架

#### 2. 克隆仓库

```bash
git clone https://github.com/233stone/vocotype-cli.git
cd vocotype-cli
```

#### 3. 安装 IBus 引擎

```bash
# 安装 IBus 引擎（纯语音版）
./scripts/install-ibus.sh

# 注意：安装过程会自动运行音频配置向导，
# 请按提示选择麦克风并测试录音效果
#
# 该脚本会询问使用的 Python 环境：
# - 项目虚拟环境（推荐）
# - 用户级虚拟环境 (~/.local/share/vocotype/.venv)
# - 系统 Python（省空间，需自行安装依赖）
#
# 如果系统已安装 uv，脚本会优先使用 uv 创建虚拟环境并安装依赖。

# 重启 IBus
ibus restart
```

> **模型下载**：首次运行时，程序会自动下载约 500MB 的模型文件，请确保网络连接稳定。

#### 4. 添加输入法

1. 打开系统设置 → 键盘 → 输入源
2. 点击 "+" 添加输入源
3. 滑到最底下点三个点 (⋮)
4. 搜索 "voco"，选择 "中文"
5. 选择 "VoCoType Voice Input" 并添加

#### 5. 使用方法

1. 切换到 VoCoType 输入法 (通常是 `Super + Space` 或 `Ctrl + Space`)
2. 按住 **F9** 说话
3. 松开 F9，等待识别完成
4. 识别的文字自动输入到光标位置
5. 需要拼音输入时，切换到其他拼音输入法（如 ibus-rime）

---

### 🎯 方式二：完整版（语音 + Rime 拼音）

**特点**：
- ✅ F9 语音输入
- ✅ 其他按键使用 Rime 拼音输入
- ✅ 一个输入法搞定所有需求
- ✅ 共享 ibus-rime 的配置和词库
- ⚠️ 需要额外安装 Rime 相关依赖

**安装步骤**：

#### 1. 安装系统依赖

```bash
# Fedora / RHEL / CentOS
sudo dnf install librime-devel ibus-rime

# Ubuntu / Debian
sudo apt install librime-dev ibus-rime

# Arch Linux
sudo pacman -S librime ibus-rime
```

#### 2. 克隆仓库并安装

```bash
git clone https://github.com/233stone/vocotype-cli.git
cd vocotype-cli

# 安装完整版（包含 Rime 集成）
./scripts/install-ibus.sh

# 在安装过程中，还需要手动安装 pyrime
# 根据脚本提示的虚拟环境路径执行：
# 例如：
# ~/.local/share/vocotype/.venv/bin/pip install pyrime
# 或者如果选择项目虚拟环境：
# .venv/bin/pip install pyrime

# 重启 IBus
ibus restart
```

#### 3. 添加和使用

添加输入法的步骤与纯语音版相同。

**使用方法**：
1. 切换到 VoCoType 输入法
2. **语音输入**：按住 F9 说话，松开后自动识别
3. **拼音输入**：直接打字，Rime 会处理并显示候选词
4. 在同一个输入法内无缝切换两种输入方式

**配置说明**：
- VoCoType 会使用 `~/.config/ibus/rime/` 作为配置目录
- 与 ibus-rime 共享词库和配置
- 如果已经配置过 ibus-rime，所有设置和词库都会自动继承

---

### 🆚 两种版本对比

| 功能 | 纯语音版 | 完整版 |
|------|---------|--------|
| F9 语音输入 | ✅ | ✅ |
| 拼音输入 | ❌ 需切换到其他输入法 | ✅ 内置 Rime |
| 依赖 | 少 | 多（需 librime） |
| 安装难度 | 简单 | 中等 |
| 使用便利性 | 需切换输入法 | 一个输入法全搞定 |
| 词库同步 | - | 与 ibus-rime 共享 |

**建议**：
- 🆕 新手用户：建议先安装**纯语音版**，体验语音输入功能
- 🎯 进阶用户：如果想要一个输入法同时支持语音和拼音，选择**完整版**
- 🔄 已有 ibus-rime 用户：选择**完整版**可以继承现有配置和词库

---

## 📹 使用场景

### 日常应用
- **聊天通讯**: 微信、QQ、Telegram、Slack、Discord 等
- **文档撰写**: 写文章、报告、邮件、日记、笔记
- **网页浏览**: 搜索关键词、填写表单、发表评论
- **办公软件**: LibreOffice、WPS、在线文档编辑

### 开发场景
- **编写代码注释**: 快速添加详细的函数说明和文档注释
- **Git Commit Message**: 语音输入详细的提交说明
- **技术文档**: 撰写 README、设计文档、API 文档
- **与 AI 对话**: 在 ChatGPT、Claude、Cursor 等工具中语音输入问题
- **会议记录**: 快速记录技术会议的讨论内容
- **Issue & PR**: 语音输入 GitHub Issue 描述和 Pull Request 说明

### 适合人群
- 💬 经常需要打字聊天的用户
- 📝 文字工作者、作家、记者
- 🧑‍💻 开发者、程序员
- 🔬 研究人员和学者
- 🤖 AI 工具使用者

---

## 🎯 核心优势对比

| 特性           |    ✅ **VoCoType Linux IBus**     |  云端输入法   |  系统自带   |
| :------------- | :--------------------------------: | :-----------: | :---------: |
| **隐私安全**   | **本地离线，绝不上传** | ❌ 数据需上传云端 | ⚠️ 隐私政策复杂 |
| **网络依赖**   |    **完全无需联网**    |  ❌ 必须联网使用  |  ❌ 强依赖网络  |
| **响应速度**   |      **0.1 秒级**      |  慢，受网速影响   | 慢，受网速影响  |
| **易用性**     |  **简单安装，即装即用**  |      简单       |     简单      |
| **数据安全**   |  **100% 本地，零泄露风险**  |  ❌ 存在泄密风险  |  ❌ 存在泄密风险  |

---

## 🔧 高级配置

### 重新配置音频设备

如果需要更换麦克风或重新测试音频：

```bash
.venv/bin/python scripts/setup-audio.py
```

### 自定义快捷键

默认使用 F9 作为 PTT (Push-to-Talk) 键。如需修改，请编辑 `ibus/engine.py`:

```python
PTT_KEYVAL = IBus.KEY_F9  # 修改为其他按键
```

可选按键：`IBus.KEY_F8`, `IBus.KEY_F10`, `IBus.KEY_Control_L` 等

---

## 常见问题 (FAQ)

**Q: 我的数据安全吗？**

> A: **100% 安全**。所有语音识别均在本地离线完成，您的音频数据不会上传到任何服务器。

**Q: 需要 GPU/显卡吗？资源占用如何？**

> A: **不需要 GPU，只使用 CPU**。资源占用非常轻量：
>
> **内存占用：**
> - 待机状态：200-300MB
> - 识别时峰值：约 700MB
>
> **CPU 占用：**
> - 待机状态：几乎 0%
> - 录音时：5-10%（单核）
> - 识别时：100-200%（多核，持续 0.1-0.5 秒）
>
> **磁盘占用：**
> - 模型文件：约 500MB
> - 代码和依赖：约 200-300MB
>
> **推荐配置：**
> - 最低：4GB RAM + 双核 CPU
> - 推荐：8GB RAM + 四核 CPU
> - 不需要显卡，笔记本也能轻松运行

**Q: 识别准确率如何？**

> A: 基于 FunASR (阿里巴巴达摩院) 的 Paraformer 模型，在中文普通话场景下准确率超过 95%。支持中英混合输入。

**Q: 可以在哪些应用中使用？**

> A: 任何支持文本输入的应用都可以使用，包括：
> - 终端 (Terminal)、代码编辑器 (VS Code, Vim, Emacs)
> - 浏览器 (Chrome, Firefox)
> - 办公软件 (LibreOffice, WPS)
> - 聊天工具 (Telegram, Slack, Discord)

**Q: 如何卸载？**

> A: 执行以下命令：
> ```bash
> rm -rf ~/.local/share/vocotype
> rm -rf ~/.local/share/ibus/component/vocotype.xml
> rm -rf ~/.local/libexec/ibus-engine-vocotype
> ibus restart
> ```

---

## 👨‍💻 作者

**Leonard Li** - Linux IBus 版本开发与维护

📧 联系邮箱: [leo@lsamc.website](mailto:leo@lsamc.website)

## 📞 联系我们

- **Bug 与建议**：请使用 GitHub Issues
- **原项目**：[VoCoType](https://github.com/233stone/vocotype-cli)

---

## 🙏 致谢

本项目基于以下优秀的开源项目：

- **[VoCoType](https://github.com/233stone/vocotype-cli)** - 原始项目，提供了强大的离线语音识别核心引擎
- **[FunASR](https://github.com/modelscope/FunASR)** - 阿里巴巴达摩院开源的语音识别框架，为 VoCoType 提供了强大的离线语音识别能力
- **[QuQu](https://github.com/yan5xu/ququ)** - 优秀的开源项目，为 VoCoType 提供了重要的技术参考和灵感

感谢这些开源社区的无私贡献！

---

## 📎 第三方依赖与模型许可说明

本项目依赖的第三方库与模型均受各自许可证约束。详细列表与说明见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

当前默认使用的模型包括：
- `iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-onnx`
- `iic/speech_fsmn_vad_zh-cn-16k-common-onnx`
- `iic/punc_ct-transformer_zh-cn-common-vocab272727-onnx`

使用或分发前，请确认遵守上游许可证与模型条款。

## 📄 许可证

本项目继承原 VoCoType 项目的许可证。请查看 [LICENSE](LICENSE) 文件了解详情。

![Star History Chart](https://api.star-history.com/svg?repos=LeonardNJU/VocoType-ibus&type=Date)

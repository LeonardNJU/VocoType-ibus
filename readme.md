# VoCoType Linux

<h2 align="center">Linux 全平台离线语音输入法</h2>

**VoCoType Linux** 是基于 [VoCoType](https://github.com/233stone/vocotype-cli) 核心引擎开发的 **Linux 离线语音输入法**，同时支持 IBus 和 Fcitx 5 两大输入法框架。

> **Windows / macOS 用户**：VoCoType 原作者已实现桌面版，请访问 [vocotype.com](https://vocotype.com/)

---

## 核心特性

- **100% 离线，隐私无忧** - 所有语音识别在本地完成，不上传任何数据
- **旗舰级识别引擎** - 基于 FunASR Paraformer 模型，中英混合输入精准
- **PTT 按键说话** - 按住 F9 说话，松开自动识别并输入
- **轻量化设计** - 仅需 700MB 内存，纯 CPU 推理，无需显卡
- **0.1 秒级响应** - 感受所言即所得的畅快体验
- **可选 Rime 集成** - 需要拼音时可启用 Rime，无需切换输入法

## 支持平台

| 输入法框架 | 状态 | 说明 |
|-----------|------|------|
| **IBus** | ✅ 完整支持 | 适用于 GNOME、大多数发行版默认 |
| **Fcitx 5** | ✅ 完整支持 | 适用于 KDE、偏好 Fcitx 的用户 |

两个版本**可以同时安装**，共享 VoCoType 核心引擎，各自独立运行。

---

## 快速开始

### IBus 版本

```bash
git clone https://github.com/233stone/vocotype-cli.git
cd vocotype-cli
./scripts/install-ibus.sh
ibus restart
```

详细安装说明：[ibus/README.md](ibus/README.md)

### Fcitx 5 版本

```bash
git clone https://github.com/233stone/vocotype-cli.git
cd vocotype-cli
bash fcitx5/scripts/install-fcitx5.sh
fcitx5 -r
```

详细安装说明：[fcitx5/README.md](fcitx5/README.md)

---

## 重新安装与卸载

### 重新安装

安装脚本支持重复运行，无论是：
- 安装失败需要重试
- 升级到新版本
- 变更安装参数

直接重新运行安装脚本即可，会自动覆盖之前的安装，不会有残留。

### 卸载

**IBus 版本**：
```bash
./scripts/uninstall-ibus.sh
```

卸载时可选择：
- **快速卸载**（选项 1）：保留 .venv 和模型文件，方便下次安装
- **完全卸载**（选项 2）：删除所有内容

---

## 架构设计

```
VoCoType Linux
├── app/                    # 核心引擎（共享）
│   ├── funasr_server.py    # 语音识别（FunASR）
│   └── ...
├── ibus/                   # IBus 版本
│   ├── engine.py           # IBus 引擎
│   └── README.md
└── fcitx5/                 # Fcitx 5 版本
    ├── addon/              # C++ Addon
    ├── backend/            # Python 后端
    └── README.md
```

IBus 和 Fcitx 5 是**并列独立**的实现，共享 VoCoType 核心（语音识别、音频采集）。

---

## 版本对比

| 特性 | IBus 版本 | Fcitx 5 版本 |
|-----|----------|-------------|
| 输入法框架 | IBus | Fcitx 5 |
| 实现语言 | 纯 Python | C++ + Python (IPC) |
| 安装位置 | `~/.local/share/vocotype/` | `~/.local/share/vocotype-fcitx5/` |
| 适用桌面 | GNOME 等 | KDE 等 |

---

## 使用场景

### 日常应用
- 聊天通讯：微信、QQ、Telegram、Slack、Discord
- 文档撰写：文章、报告、邮件、日记、笔记
- 网页浏览：搜索、表单、评论

### 开发场景
- 编写代码注释和文档
- Git Commit Message
- 与 AI 工具对话（ChatGPT、Claude、Cursor）
- Issue & PR 描述

---

## 核心优势

| 特性 | VoCoType Linux | 云端输入法 |
|------|---------------|-----------|
| **隐私安全** | 本地离线，绝不上传 | 数据上传云端 |
| **网络依赖** | 完全无需联网 | 必须联网 |
| **响应速度** | 0.1 秒级 | 受网速影响 |
| **数据安全** | 100% 本地 | 存在泄密风险 |

---

## 系统要求

- **操作系统**: Linux (Fedora, Ubuntu, Debian, Arch 等)
- **Python**: 3.10-3.12（onnxruntime 暂不支持 3.13+）
- **内存**: 最低 4GB，推荐 8GB
- **CPU**: 双核以上，无需 GPU

### 资源占用

| 状态 | 内存 | CPU |
|------|------|-----|
| 待机 | 200-300MB | ~0% |
| 录音 | - | 5-10% |
| 识别 | ~700MB | 100-200%（0.1-0.5秒）|

---

## 文档

- [IBus 版本安装指南](ibus/README.md)
- [Fcitx 5 版本安装指南](fcitx5/README.md)
- [Rime 拼音配置指南](RIME_CONFIG_GUIDE.md)（可选功能）

---

## 作者

**Leonard Li** - 开发与维护

📧 联系邮箱: [leo@lsamc.website](mailto:leo@lsamc.website)

## 联系我们

- **Bug 与建议**：请使用 GitHub Issues
- **原项目**：[VoCoType](https://github.com/233stone/vocotype-cli)

---

## 致谢

本项目基于以下优秀的开源项目：

- **[VoCoType](https://github.com/233stone/vocotype-cli)** - 原始项目，提供了强大的离线语音识别核心引擎
- **[FunASR](https://github.com/modelscope/FunASR)** - 阿里巴巴达摩院开源的语音识别框架
- **[QuQu](https://github.com/yan5xu/ququ)** - 优秀的开源项目，提供了重要的技术参考

---

## 第三方依赖与模型许可

本项目依赖的第三方库与模型均受各自许可证约束。详见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

使用的模型：
- `iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-onnx`
- `iic/speech_fsmn_vad_zh-cn-16k-common-onnx`
- `iic/punc_ct-transformer_zh-cn-common-vocab272727-onnx`

## 📄 许可证

本项目继承原 VoCoType 项目的许可证。请查看 [LICENSE](LICENSE) 文件了解详情。

## Star History

<a href="https://www.star-history.com/#LeonardNJU/VocoType-ibus&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=LeonardNJU/VocoType-ibus&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=LeonardNJU/VocoType-ibus&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=LeonardNJU/VocoType-ibus&type=date&legend=top-left" />
 </picture>
</a>

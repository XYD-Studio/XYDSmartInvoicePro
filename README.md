# 🧾 SmartInvoice Pro - 智能票据整理助手

<div align="center">
  <img src="https://img.shields.io/badge/Vue-3.0-blue.svg" alt="Vue 3">
  <img src="https://img.shields.io/badge/FastAPI-0.110-009688.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Status-Production_Ready-orange.svg" alt="Status">
</div>

> **本项目由 [玄宇绘世设计工作室](https://www.xy-d.top/) 开源并持续维护。**  
> 专为企业员工报销、高新项目申报材料整理等场景打造的**纯净版票据整理提效神器**。告别繁琐的手工誊写，让报销清单整理变得优雅从容。

## ✨ 核心特性 / Features

- **🚀 商业级智能提取引擎**：
  - 支持接入阿里云增值税发票专用 OCR，实现标准票据 **100% 精准提取**。
  - 支持接入通义千问、智谱等视觉大模型（LLM-VL），轻松应对非标手写收据及海外发票。
- **💻 极致的生产力桌面体验**：
  - **自由面板缩放**：左/中/右/下四大工作区大小支持鼠标自由拖拽缩放。
  - **极速核对模式**：原件图片与提取数据同屏双开，支持使用 `Alt + ↑ / ↓` 跨文件穿梭切换，解放鼠标。
  - **表头自由重排**：导出表头支持**鼠标左右拖拽排序**，所见即所得。
- **📊 完美排版 Excel 导出**：告别乱码与挤压，自动计算最优列宽、自动文本换行、自带高级报表样式，导出即可直接打印上交。
- **🔒 本地化绝对隐私**：用户自带 API Key (BYOK)，无第三方后端留存，保护商业机密。

## 🛠️ 架构与技术栈

- **前端UI**：`Vue 3` + `TypeScript` + `Tailwind` + `Splitpanes` + `ExcelJS`
- **后端核心**：`Python 3` + `FastAPI` + `Requests` + `PyMuPDF`

## 📦 极速启动

下载源码后，双击根目录下的 `start.bat` 即可一键启动（需提前安装 Node.js 与 Python3）。

## 🤝 贡献与商业合作

如果您觉得这个项目极大提升了您的办公效率，欢迎给我们一个 ⭐️ **Star**！

- 官方主页：[玄宇绘世设计工作室](https://www.xy-d.top/)
- 商业化系统定制、顶级 UI/UX 设计合作，请通过官网联系我们。

## ⚖️ 声明

本软件为办公效率辅助工具，非专业核心财务记账软件。提取结果需人工核对，因使用本工具造成的后续损失，开发者不承担任何责任。

# 音频自动降噪系统（AudioSmart）

## 项目简介

本项目为“音频自动降噪系统”，致力于为用户提供一站式的音频智能处理平台。平台集成了音频降噪、音频编辑、语音识别、图片去噪、格式转换、文件管理等多项功能，支持中英文界面切换，界面美观、操作便捷，适合内容创作者、教育、播客等多种场景。

---

## 技术架构

- **前端**：Vue3 + Vite
  - 音频上传、降噪、试听、波形可视化、音频编辑、语音识别、图片处理、格式转换、历史文件管理等
  - 支持中英文切换，响应式设计
- **后端**：Python Flask
  - 音频降噪（noisereduce）、语音识别（OpenAI Whisper）、图片去噪（OpenCV）、格式转换（pydub、Pillow、moviepy）、文件管理等
  - 提供 RESTful API，支持跨域

---

## 主要功能

### 1. 音频编辑
- 支持 MP3/WAV/MP4 等格式上传
- 一键 AI 降噪，前后试听对比
- 音频裁剪、变速、波形可视化分段、拼接
- 语音识别（Whisper），自动提取歌词/文本，支持下载
- 批量音频降噪处理

### 2. 图片编辑
- 图片上传、非局部均值去噪（NLM）、裁剪、标注
- 结果图片下载

### 3. 音视频分离
- 视频上传，自动提取音频

### 4. 格式转换
- 音频、图片、视频多格式互转

### 5. 文件管理
- 历史文件列表、下载、删除

### 6. 多语言支持
- 支持中文、英文界面切换（按钮、标签、下载等均有中英文）

---

## 快速启动

### 1. 后端环境准备

- Python 3.8+，推荐 Anaconda 环境
- 安装依赖：

```bash
pip install flask flask-cors pydub pillow moviepy opencv-python noisereduce librosa soundfile openai-whisper torch spleeter
```

- 配置 ffmpeg  
  下载 [ffmpeg](https://www.gyan.dev/ffmpeg/builds/)，解压后将 `bin` 目录路径写入 `backend.py` 的 `ensure_ffmpeg()` 函数。

- 启动后端：

```bash
python backend.py
```

### 2. 前端环境准备

- Node.js 16+
- 安装依赖：

```bash
npm install
```

- 启动前端：

```bash
npm run dev
```

- 默认访问地址：[http://localhost:5173](http://localhost:5173)

---

## 目录结构

```
AudioSmart/
├── backend/                # Flask后端
│   └── backend.py
├── src/                    # 前端源码
│   ├── App.vue
│   ├── components/
│   │   ├── AudioUploader.vue
│   │   ├── ImageDenoiser.vue
│   │   ├── AvSeparator.vue
│   │   ├── FormatConverter.vue
│   │   ├── FileManager.vue
│   │   └── Home.vue
│   └── ...
├── public/
├── package.json
└── README.md
```

---

## 主要界面与交互

- **首页**：品牌介绍、功能展示（中英文切换）
- **音频编辑**：上传、降噪、试听、编辑、语音识别（按钮、标签、下载均有中英文）
- **图片编辑**：上传、去噪、裁剪、标注、下载
- **音视频分离**：视频转音频
- **格式转换**：音频/图片/视频格式互转
- **历史记录**：文件列表、下载、删除

---

## 特色说明

- **AI能力**：集成 noisereduce（降噪）、OpenAI Whisper（语音识别）、OpenCV（图片去噪）
- **多语言**：所有主要按钮、标签、下载按钮等均支持中英文切换
- **现代UI**：卡片化、响应式、交互友好
- **批量处理**：支持批量音频降噪
- **文件管理**：支持历史文件的下载与删除

---

## 常见问题

- **ffmpeg未配置**：请确保 `ffmpeg.exe` 路径正确，并已加入环境变量或在 `backend.py` 中指定
- **语音识别慢**：Whisper模型较大，首次加载较慢，建议用 base 或 tiny 模型
- **依赖冲突**：建议在干净的虚拟环境中安装依赖

---

## 联系与支持

如有问题或建议，请通过wechat或邮件联系开发者：
wechat:Parker0309
email:2991982073@qq.com

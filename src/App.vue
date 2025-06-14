<script setup>
import { ref, provide } from 'vue'
import AudioUploader from './components/AudioUploader.vue'
import ImageDenoiser from './components/ImageDenoiser.vue'
import AvSeparator from './components/AvSeparator.vue'
import FormatConverter from './components/FormatConverter.vue'
import FileManager from './components/FileManager.vue'
import Home from './components/Home.vue'

// 语言切换
const lang = ref('zh')
const langMap = {
  zh: {
    platform: '音频智编平台',
    audio: '音频编辑',
    image: '图像编辑',
    av: '音视频分离',
    convert: '格式转换',
    file: '历史记录',
    copyright: '© 2025 音频自动降噪系统 | Powered by Vue3 & Flask',
    refresh: '刷新',
    folder: '文件夹：',
    filename: '文件名',
    size: '大小',
    mtime: '修改时间',
    action: '操作',
    download: '下载',
    delete: '删除',
    empty: '暂无文件',
    selectFile: '选择音频文件',
    denoise: '降噪',
    trim: '裁剪',
    speed: '变速',
    originalAudio: '原始音频试听',
    denoisedAudio: '降噪后试听',
    editedAudio: '编辑后试听',
    downloadDenoised: '下载降噪音频',
    downloadEdited: '下载编辑音频',
    batchSelectAudio: '批量选择音频文件',
    batchDenoise: '批量降噪',
    failed: '失败',
    upload: '上传',
    result: '结果',
    deleteConfirm: '确定要删除该文件吗？',
    extractAudio: '提取音频',
    videoPreview: '视频预览',
    audioPreview: '提取音频试听',
    cropTip: '拖动鼠标选择裁剪区域，点击“确定裁剪”',
    confirmCrop: '确定裁剪',
    cancel: '取消',
    audioClip: '音频剪辑',
    applyClip: '应用剪辑',
    reset: '重置',
    segment: '片段',
    playSegment: '播放片段',
    pauseSegment: '暂停',
    clipTip: '上传音频后可进行可视化剪辑，点击波形分割片段，点击片段可选中并删除。',
    downloadEdited: '下载剪辑音频'
  },
  en: {
    platform: 'AudioSmart',
    audio: 'Audio Edit',
    image: 'Image Edit',
    av: 'AV Separation',
    convert: 'Format Convert',
    file: 'History',
    copyright: '© 2025 Audio Denoise System | Powered by Vue3 & Flask',
    refresh: 'Refresh',
    folder: 'Folder:',
    filename: 'Filename',
    size: 'Size',
    mtime: 'Modified',
    action: 'Action',
    download: 'Download',
    delete: 'Delete',
    empty: 'No files',
    selectFile: 'Select Audio File',
    denoise: 'Denoise',
    trim: 'Trim',
    speed: 'Speed',
    originalAudio: 'Original Audio',
    denoisedAudio: 'Denoised Audio',
    editedAudio: 'Edited Audio',
    downloadDenoised: 'Download Denoised',
    downloadEdited: 'Download Edited',
    batchSelectAudio: 'Batch Select Audio',
    batchDenoise: 'Batch Denoise',
    downloadDenoised: 'Download Denoised',
    failed: 'Failed',
    upload: ' Upload',
    result: ' Result',
    deleteConfirm: 'Are you sure to delete this file?',
    extractAudio: 'Extract Audio',
    videoPreview: 'Video Preview',
    audioPreview: 'Audio Preview',
    cropTip: 'Drag to select crop area, then click "Crop"',
    confirmCrop: 'Crop',
    cancel: 'Cancel',
    audioClip: 'Audio Clip',
    applyClip: 'Apply Clip',
    reset: 'Reset',
    segment: 'Segment',
    playSegment: 'Play Segment',
    pauseSegment: 'Pause',
    clipTip: 'After uploading audio, you can visually clip it. Click the waveform to split segments, click a segment to select and delete.',
    downloadEdited: 'Download Clipped Audio'
  }
}
function toggleLang() {
  lang.value = lang.value === 'zh' ? 'en' : 'zh'
}
provide('lang', lang)
provide('langMap', langMap)

// 主题切换
const theme = ref('dark') // 'dark' or 'light'
function toggleTheme() {
  theme.value = theme.value === 'dark' ? 'light' : 'dark'
}
provide('theme', theme)

// 全局消息提示
const message = ref({ show: false, type: 'info', text: '' })
function showMessage(type, text, duration = 2000) {
  message.value = { show: true, type, text }
  setTimeout(() => { message.value.show = false }, duration)
}
provide('showMessage', showMessage)

// 这里补充selected变量
const selected = ref('audio')

// 帮助弹窗控制
const showHelp = ref(false)
function openHelp() {
  showHelp.value = true
}
function closeHelp() {
  showHelp.value = false
}
</script>

<template>
  <div class="main-bg">
    <div class="main-content">
      <!-- 左侧选择栏 -->
      <div class="side-bar">
        <div class="side-title">
          {{ langMap[lang].platform }}
        </div>
        <button
          :class="['side-btn', selected === 'home' ? 'active' : '', lang === 'en' ? 'en-font' : '']"
          @click="selected = 'home'"
        >🏠 首页</button>
        <button
          :class="['side-btn', selected === 'audio' ? 'active' : '', lang === 'en' ? 'en-font' : '']"
          @click="selected = 'audio'"
        >{{ langMap[lang].audio }}</button>
        <button
          :class="['side-btn', selected === 'image' ? 'active' : '', lang === 'en' ? 'en-font' : '']"
          @click="selected = 'image'"
        >{{ langMap[lang].image }}</button>
        <button
          :class="['side-btn', selected === 'av' ? 'active' : '', lang === 'en' ? 'en-font' : '']"
          @click="selected = 'av'"
        >{{ langMap[lang].av }}</button>
        <button
          :class="['side-btn', selected === 'convert' ? 'active' : '', lang === 'en' ? 'en-font' : '']"
          @click="selected = 'convert'"
        >{{ langMap[lang].convert }}</button>
        <button
          :class="['side-btn', selected === 'file' ? 'active' : '', lang === 'en' ? 'en-font' : '']"
          @click="selected = 'file'"
        >{{ langMap[lang].file }}</button>
        <button class="lang-btn" @click="toggleLang">
          {{ lang === 'zh' ? 'English' : '中文' }}
        </button>
        <button class="help-btn" @click="openHelp">
          {{ lang === 'zh' ? '帮助' : 'Help' }}
        </button>
      </div>
      <!-- 右侧内容区 -->
      <div :class="['main-panel', theme]">
        <Home v-if="selected === 'home'" />
        <div v-else-if="selected === 'audio'" style="width: 100%;"><AudioUploader /></div>
        <div v-else-if="selected === 'image'" style="width: 100%;"><ImageDenoiser /></div>
        <div v-else-if="selected === 'convert'" style="width: 100%;"><FormatConverter /></div>
        <div v-else-if="selected === 'file'" style="width: 100%;"><FileManager /></div>
        <div v-else style="width: 100%;"><AvSeparator /></div>
      </div>
    </div>
    <div class="footer-pro">
      <span>{{ langMap[lang].copyright }}</span>
    </div>
    <!-- 全局消息提示 -->
    <transition name="fade">
      <div v-if="message.show" :class="['global-message', message.type]">
        {{ message.text }}
      </div>
    </transition>
    <!-- 帮助弹窗 -->
    <div v-if="showHelp" class="help-modal-mask" @click.self="closeHelp">
      <div class="help-modal-box">
        <div class="help-modal-title">
          {{ lang === 'zh' ? '使用教程' : 'User Guide' }}
        </div>
        <div class="help-modal-content">
          <template v-if="lang === 'zh'">
            <ol>
              <li><b>音频编辑：</b>上传音频文件（支持MP3/WAV/MP4），点击“降噪”按钮自动处理，可试听降噪前后效果并导出降噪音频。</li>
              <li><b>图像编辑：</b>上传图片，支持非局部均值去噪与裁剪，处理后可下载结果。</li>
              <li><b>音视频分离：</b>上传视频文件，点击“提取音频”可分离出音频并下载。</li>
              <li><b>格式转换：</b>支持音频、图片、视频文件的格式互转，选择目标格式后点击转换。</li>
              <li><b>历史记录：</b>可查看、下载、删除已上传和处理的文件。</li>
              <li><b>批量处理：</b>支持批量选择音频文件进行降噪处理。</li>
              <li><b>多语言切换：</b>点击左侧“English/中文”按钮可切换界面语言。</li>
            </ol>
            <p style="margin-top:10px;">如遇问题请刷新页面或联系开发者。</p>
          </template>
          <template v-else>
            <ol>
              <li><b>Audio Edit:</b> Upload audio files (MP3/WAV/MP4 supported), click "Denoise" to process, preview before/after, and export denoised audio.</li>
              <li><b>Image Edit:</b> Upload images, support NLM denoising and cropping, download results after processing.</li>
              <li><b>AV Separation:</b> Upload video files, click "Extract Audio" to separate and download audio.</li>
              <li><b>Format Convert:</b> Convert audio, image, or video files to other formats, select target format and click convert.</li>
              <li><b>History:</b> View, download, or delete uploaded and processed files.</li>
              <li><b>Batch Processing:</b> Batch select audio files for denoising.</li>
              <li><b>Language Switch:</b> Click "English/中文" to switch interface language.</li>
            </ol>
            <p style="margin-top:10px;">If you encounter problems, please refresh the page or contact the developer.</p>
          </template>
        </div>
        <div class="help-modal-btns">
          <button class="action-btn-flat" @click="closeHelp">{{ lang === 'zh' ? '关闭' : 'Close' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
:root {
  --main-bg-dark: #232946;
  --main-fg-dark: #fff;
  --main-bg-light: #f7f7f7;
  --main-fg-light: #232946;
  --btn-bg: #fff;
  --btn-fg: #232946;
}
.main-bg.dark {
  background: var(--main-bg-dark);
}
.main-bg.light {
  background: var(--main-bg-light);
}
.main-content {
  min-height: 100vh;
  display: flex;
}
.side-bar {
  width: 200px;
  background: #232946;
  box-shadow: 2px 0 12px #e0e0e0;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 60px;
  z-index: 2;
  position: fixed;
  left: 0;
  top: 0;
  height: 100vh;
}
.side-title {
  font-weight: bold;
  font-size: 22px;
  color: #fff;
  margin-bottom: 40px;
  letter-spacing: 1px;
}
.side-btn {
  width: 140px;
  padding: 14px 0;
  margin-bottom: 18px;
  border: none;
  background: #232946;
  font-size: 17px;
  color: #fff;
  border-radius: 8px;
  text-align: center;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
  font-weight: 600;
  letter-spacing: 1px;
}

/* 英文模式下按钮字体稍小 */
:global(body) .side-bar .side-btn {
  font-size: 17px;
}
:global(body) .side-bar .side-btn.en-font {
  font-size: 15px;
}
.side-btn.active,
.side-btn:hover {
  background: #fff;
  color: #232946;
  font-weight: 700;
  box-shadow: 0 2px 12px #23294633;
}
.lang-btn {
  margin-top: 40px;
  background: none;
  border: 1px solid #fff;
  color: #fff;
  border-radius: 8px;
  padding: 8px 18px;
  font-size: 15px;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}
.lang-btn:hover {
  background: #fff;
  color: #232946;
}
.help-btn {
  margin-top: 18px;
  background: none;
  border: 1px solid #fff;
  color: #fff;
  border-radius: 8px;
  padding: 8px 18px;
  font-size: 15px;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}
.help-btn:hover {
  background: #fff;
  color: #232946;
}
.main-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  min-height: 100vh;
  padding-bottom: 40px;
  margin-left: 200px;
  width: calc(100vw - 200px);
  box-sizing: border-box;
  overflow-x: hidden;
}
.main-panel.dark {
  background: var(--main-bg-dark);
  color: var(--main-fg-dark);
}
.main-panel.light {
  background: var(--main-bg-light);
  color: var(--main-fg-light);
}
.main-panel.bg-dark, .main-panel.bg-dark *:not(button):not(.action-btn-flat):not(.download-btn-flat):not(.table-btn) {
  color: var(--main-fg-dark) !important;
}
.main-panel.bg-light, .main-panel.bg-light *:not(button):not(.action-btn-flat):not(.download-btn-flat):not(.table-btn) {
  color: var(--main-fg-light) !important;
}
.action-btn-flat,
.download-btn-flat,
.table-btn {
  background: var(--btn-bg) !important;
  color: var(--btn-fg) !important;
  border: none;
  border-radius: 18px;
  font-weight: 600;
  transition: background 0.2s, color 0.2s;
  height: 38px;           /* 固定高度 */
  line-height: 38px;      /* 垂直居中 */
  min-width: 120px;       /* 可选：设置最小宽度，防止英文太短 */
  font-size: 15px;
  white-space: nowrap;
}
.action-btn-flat:not(:disabled):hover,
.download-btn-flat:not(:disabled):hover,
.table-btn:not(:disabled):hover {
  background: var(--main-bg-dark) !important;
  color: var(--main-fg-dark) !important;
}
.global-message {
  position: fixed;
  left: 50%;
  top: 40px;
  transform: translateX(-50%);
  min-width: 180px;
  max-width: 60vw;
  padding: 14px 32px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  z-index: 9999;
  box-shadow: 0 4px 24px #23294633;
  background: #232946;
  color: #fff;
  text-align: center;
  opacity: 0.98;
  pointer-events: none;
}
.global-message.success {
  background: #43d675;
  color: #fff;
}
.global-message.error {
  background: #e74c3c;
  color: #fff;
}
.global-message.info {
  background: #232946;
  color: #fff;
}
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
.footer-pro {
  z-index: 1;
  width: 100vw;
  text-align: center;
  color: #232946;
  font-size: 15px;
  margin-bottom: 12px;
  margin-top: 8px;
  letter-spacing: 1px;
  user-select: none;
}
.help-modal-mask {
  position: fixed;
  left: 0; top: 0; width: 100vw; height: 100vh;
  background: rgba(30,40,60,0.35);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}
.help-modal-box {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 32px #b3c7e6;
  padding: 32px 32px 24px 32px;
  min-width: 340px;
  max-width: 90vw;
  max-height: 80vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}
.help-modal-title {
  font-size: 20px;
  font-weight: 700;
  color: #232946;
  margin-bottom: 18px;
}
.help-modal-content {
  color: #232946;
  font-size: 15px;
  line-height: 1.8;
}
.help-modal-btns {
  display: flex;
  gap: 18px;
  margin-top: 18px;
  width: 100%;
  justify-content: flex-end;
}
</style>

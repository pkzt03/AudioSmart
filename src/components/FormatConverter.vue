<template>
  <div class="format-converter-flat">
    <div class="header-bar">
      <span class="logo-emoji">🔄</span>
      <span class="title">{{ langMap[lang].convert }}</span>
    </div>
    <div class="divider"></div>
    <div class="btn-row">
      <select v-model="filetype" class="select-flat">
        <option value="audio">{{ langMap[lang].audio }}</option>
        <option value="image">{{ langMap[lang].image }}</option>
        <option value="video">{{ langMap[lang].av }}</option>
      </select>
      <label class="action-btn-flat">
        <input type="file" :accept="acceptType" @change="onFileChange" hidden />
        📁 {{ langMap[lang].selectFile || '选择文件' }}
      </label>
      <select v-model="targetFormat" class="select-flat">
        <option v-for="fmt in formatOptions" :key="fmt" :value="fmt">{{ fmt.toUpperCase() }}</option>
      </select>
      <button class="action-btn-flat" @click="convertFile" :disabled="!uploadedFilename">
        🔄 {{ langMap[lang].convert }}
      </button>
    </div>
    <!-- 文件名和预览 -->
    <div class="file-info-row" v-if="fileName">
      <span class="file-name">{{ langMap[lang].filename }}: {{ fileName }}</span>
      <img v-if="filetype === 'image'" :src="fileUrl" class="preview-img" />
      <video v-if="filetype === 'video'" :src="fileUrl" class="preview-video" controls />
    </div>
    <div class="result-row" v-if="resultUrl">
      <a :href="resultUrl" download class="download-btn-flat">
        📥 {{ langMap[lang].download || '下载' }}
      </a>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, inject } from 'vue'

const lang = inject('lang')
const langMap = inject('langMap')

const filetype = ref('audio')
const file = ref(null)
const uploadedFilename = ref('')
const targetFormat = ref('mp3')
const resultUrl = ref('')
const fileName = ref('')
const fileUrl = ref('')

const formatMap = {
  audio: ['mp3', 'wav', 'ogg'],
  image: ['jpg', 'png', 'bmp'],
  video: ['mp3'] // 仅支持视频转音频
}
const acceptMap = {
  audio: 'audio/*',
  image: 'image/*',
  video: 'video/*'
}
const formatOptions = computed(() => formatMap[filetype.value])
const acceptType = computed(() => acceptMap[filetype.value])

function onFileChange(e) {
  file.value = e.target.files[0]
  if (file.value) {
    fileName.value = file.value.name
    fileUrl.value = URL.createObjectURL(file.value)
    uploadFile()
  }
}

async function uploadFile() {
  if (!file.value) return
  const formData = new FormData()
  formData.append('file', file.value)
  // 音频/视频上传到 uploads，图片上传到 image_uploads
  const url = filetype.value === 'image'
    ? 'http://localhost:5000/api/image_upload'
    : 'http://localhost:5000/api/upload'
  const res = await fetch(url, {
    method: 'POST',
    body: formData
  })
  const data = await res.json()
  if (data.filename) {
    uploadedFilename.value = data.filename
    resultUrl.value = ''
  }
}

async function convertFile() {
  if (!uploadedFilename.value) return
  const res = await fetch('http://localhost:5000/api/convert', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      filename: uploadedFilename.value,
      target_format: targetFormat.value,
      filetype: filetype.value
    })
  })
  const data = await res.json()
  if (data.result_filename) {
    let base = filetype.value === 'image'
      ? 'http://localhost:5000/api/image_download/'
      : 'http://localhost:5000/api/download/'
    resultUrl.value = base + data.result_filename
  } else {
    alert(data.error || (langMap[lang].failed || '转换失败'))
  }
}
</script>

<style scoped>
.format-converter-flat {
  width: 100%;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 48px 0 0 0;
  color: #232946;
}
.header-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-left: 48px;
  margin-bottom: 10px;
}
.logo-emoji {
  font-size: 36px;
  margin-right: 8px;
  display: inline-block;
  vertical-align: middle;
}
.title {
  font-size: 22px;
  font-weight: 800;
  color: #232946;
  letter-spacing: 1.5px;
}
.divider {
  height: 2px;
  background: #f0f0f0;
  border-radius: 2px;
  margin: 8px 0 18px 0;
  width: 92%;
  align-self: center;
}
.btn-row {
  display: flex;
  gap: 18px;
  margin-left: 48px;
  margin-bottom: 24px;
}
.action-btn-flat {
  background: #ede9fe;
  color: #232946; /* 按钮字体为藏青色 */
  border: none;
  border-radius: 18px;
  padding: 7px 22px;
  font-size: 15px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 7px;
  box-shadow: 0 1px 6px #f3f0fa;
  transition: background 0.2s, color 0.2s;
}
.action-btn-flat:disabled {
  background: #f3f3f3;
  color: #bdbdbd;
  cursor: not-allowed;
}
.action-btn-flat:not(:disabled):hover {
  background: #d1c4e9;
  color: #232946;
}
.select-flat {
  border: 1px solid #d1c4e9;
  border-radius: 8px;
  padding: 6px 16px;
  font-size: 15px;
  color: #232946;
  background: #f8f8fc;
  font-weight: 600;
  outline: none;
}
.file-info-row {
  margin-left: 48px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 18px;
}
.file-name {
  color: #232946;
  font-size: 15px;
  font-weight: 600;
}
.preview-img {
  width: 80px;
  height: 80px;
  object-fit: contain;
  border-radius: 8px;
  background: #f4f8fc;
  box-shadow: 0 1px 8px #e3eaf7;
}
.preview-video {
  width: 120px;
  height: 80px;
  object-fit: contain;
  border-radius: 8px;
  background: #f4f8fc;
  box-shadow: 0 1px 8px #e3eaf7;
}
.result-row {
  margin-left: 48px;
  margin-top: 32px;
}
.download-btn-flat {
  background: #ffffff;
  color: #232946; /* 下载按钮字体为藏青色 */
  border: none;
  border-radius: 18px;
  padding: 7px 22px;
  font-size: 15px;
  cursor: pointer;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 7px;
  box-shadow: 0 1px 6px #e3eaf7;
  text-decoration: none;
  transition: background 0.2s, color 0.2s;
}
.download-btn-flat:hover {
  background: #f3f3f3;
  color: #232946;
}
@media (max-width: 700px) {
  .format-converter-flat {
    padding: 18px 0 0 0;
  }
  .header-bar, .btn-row, .result-row {
    margin-left: 12px;
  }
}
</style>
<template>
  <div class="av-separator-flat">
    <div class="header-bar">
      <span class="logo-emoji">🎬</span>
      <span class="title">{{ langMap[lang].videoEdit || langMap[lang].av }}</span>
    </div>
    <div class="divider"></div>
    <div class="btn-row">
      <label class="action-btn-flat">
        <input type="file" accept="video/*" @change="onFileChange" hidden />
        🎬 {{ langMap[lang].selectFile || '选择视频文件' }}
      </label>
      <button class="action-btn-flat" @click="extractAudio" :disabled="!uploadedFilename">
        🎵 {{ langMap[lang].extractAudio || '提取音频' }}
      </button>
    </div>
    <!-- 视频预览 -->
    <div class="video-area" v-if="videoUrl">
      <div class="video-block">
        <div class="video-title">{{ langMap[lang].videoPreview || '视频预览' }}</div>
        <video
          ref="videoRef"
          :src="videoUrl"
          controls
          class="video-player-flat"
          @loadedmetadata="onLoadedMetadata"
        />
      </div>
    </div>
    <!-- 音频试听 -->
    <div class="audio-area" v-if="audioUrl">
      <div class="audio-block">
        <div class="audio-title">{{ langMap[lang].audioPreview || '提取音频试听' }}</div>
        <audio :src="audioUrl" controls class="audio-player-flat" />
      </div>
    </div>
    <div class="download-row" v-if="audioUrl">
      <a :href="audioUrl" download class="download-btn-flat">
        📥 {{ langMap[lang].download || '下载音频（MP3）' }}
      </a>
    </div>
  </div>
</template>

<script setup>
import { ref, inject, nextTick } from 'vue'

const lang = inject('lang')
const langMap = inject('langMap')

const file = ref(null)
const uploadedFilename = ref('')
const audioUrl = ref('')
const videoUrl = ref('')
const videoRef = ref(null)

function onFileChange(e) {
  file.value = e.target.files[0]
  if (file.value) {
    videoUrl.value = URL.createObjectURL(file.value)
    audioUrl.value = ''
    uploadedFilename.value = ''
    nextTick(() => uploadFile())
  }
}

async function uploadFile() {
  if (!file.value) return
  const formData = new FormData()
  formData.append('file', file.value)
  const res = await fetch('http://localhost:5000/api/upload', {
    method: 'POST',
    body: formData
  })
  const data = await res.json()
  if (data.filename) {
    uploadedFilename.value = data.filename
  }
}

async function extractAudio() {
  if (!uploadedFilename.value) return
  const res = await fetch('http://localhost:5000/api/extract_audio', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ filename: uploadedFilename.value })
  })
  const data = await res.json()
  if (data.audio_filename) {
    audioUrl.value = `http://localhost:5000/api/download/${data.audio_filename}`
  } else {
    alert(langMap[lang].failed || '音频提取失败')
  }
}

function onLoadedMetadata(e) {
  // nothing needed here for main video
}
</script>

<style scoped>
.av-separator-flat {
  width: 100%;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 48px 0 0 0;
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
  color: #232946;
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
.video-area {
  display: flex;
  gap: 40px;
  margin: 32px 0 0 48px;
  width: calc(100% - 48px);
}
.video-block {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  min-width: 320px;
}
.video-title {
  font-size: 15px;
  color: #ffffff;
  font-weight: 700;
  margin-bottom: 8px;
  letter-spacing: 0.5px;
}
.video-player-flat {
  width: 480px;
  height: 270px;
  border-radius: 8px;
  background: #f4f8fc;
  box-shadow: 0 1px 8px #e3eaf7;
}
.video-editor-card {
  margin-left: 48px;
  margin-top: 32px;
  margin-bottom: 32px;
  background: #f8f8fc;
  border-radius: 14px;
  box-shadow: 0 2px 12px #b3c7e633;
  padding: 24px 28px 18px 28px;
  width: 92%;
  min-width: 340px;
  max-width: 900px;
}
.editor-title {
  font-size: 17px;
  font-weight: 700;
  color: #232946;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.timeline-bar {
  margin: 18px 0 0 0;
  width: 100%;
}
.timeline {
  position: relative;
  height: 32px;
  background: #e3eaf7;
  border-radius: 8px;
  margin-bottom: 12px;
  width: 100%;
  min-width: 320px;
  max-width: 800px;
}
.timeline-segment {
  position: absolute;
  top: 0;
  height: 100%;
  background: #43d67555;
  border-radius: 8px;
  border: 2px solid #43d675;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding-left: 8px;
  transition: border 0.2s, background 0.2s;
  font-size: 14px;
}
.timeline-segment.selected {
  border: 2px solid #232946;
  background: #43d67599;
}
.timeline-segment.deleted {
  opacity: 0.5;
  text-decoration: line-through;
  background: #ffeaea;
  border-color: #d32f2f;
}
.timeline-label {
  color: #232946;
  font-size: 13px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}
.delete-btn {
  background: none;
  border: none;
  color: #d32f2f;
  font-size: 16px;
  cursor: pointer;
  margin-left: 2px;
}
.clip-controls {
  margin-top: 10px;
  display: flex;
  gap: 18px;
}
.timeline-tip {
  color: #bbb;
  font-size: 15px;
  margin-top: 12px;
}
.audio-area {
  display: flex;
  gap: 40px;
  margin: 32px 0 0 48px;
  width: calc(100% - 48px);
}
.audio-block {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  min-width: 220px;
}
.audio-title {
  font-size: 15px;
  color: #fdfdfd;
  font-weight: 700;
  margin-bottom: 8px;
  letter-spacing: 0.5px;
}
.audio-player-flat {
  width: 220px;
  border-radius: 8px;
  background: #f4f8fc;
  box-shadow: 0 1px 8px #e3eaf7;
}
.download-row {
  margin-left: 48px;
  margin-top: 32px;
}
.download-btn-flat {
  background: #ffffff;
  color: #232946;
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
.modal-mask {
  position: fixed;
  left: 0; top: 0; width: 100vw; height: 100vh;
  background: rgba(30,40,60,0.35);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}
.modal-box {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 32px #b3c7e6;
  padding: 32px 32px 24px 32px;
  min-width: 320px;
  max-width: 90vw;
  max-height: 90vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}
.modal-title {
  font-size: 20px;
  font-weight: 700;
  color: #232946;
  margin-bottom: 18px;
}
.modal-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 18px;
}
.modal-btns {
  display: flex;
  gap: 18px;
  margin-top: 12px;
}
.action-btn-flat.danger {
  background: #ffeaea;
  color: #d32f2f;
}
@media (max-width: 700px) {
  .av-separator-flat {
    padding: 18px 0 0 0;
  }
  .header-bar, .btn-row, .audio-area, .video-area, .download-row {
    margin-left: 12px;
  }
  .audio-area, .video-area {
    flex-direction: column;
    gap: 18px;
  }
  .video-player-flat {
    width: 100vw;
    max-width: 98vw;
    height: auto;
    aspect-ratio: 16/9;
  }
}
</style>
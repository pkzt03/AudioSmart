<template>
  <div class="audio-uploader-flat">
    <div class="header-bar">
      <img src="https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/audiomack.svg" class="logo" />
      <span class="title">{{ langMap[lang].audio }}</span>
    </div>
    <div class="divider"></div>
    <div class="btn-row">
      <label class="action-btn-flat" :class="{ loading: loading.upload }">
        <input type="file" accept="audio/*,video/mp4" @change="onFileChange" hidden />
        <span v-if="loading.upload" class="loading-spinner"></span>
        🎵 {{ langMap[lang].selectFile || '选择音频文件' }}
      </label>
      <button class="action-btn-flat" @click="denoiseFile" :disabled="!uploadedFilename || loading.denoise" :class="{ loading: loading.denoise }">
        <span v-if="loading.denoise" class="loading-spinner"></span>
        ✨ {{ langMap[lang].denoise || '降噪' }}
      </button>
      <button class="action-btn-flat" @click="showTrim = true" :disabled="!uploadedFilename || loading.trim" :class="{ loading: loading.trim }">
        <span v-if="loading.trim" class="loading-spinner"></span>
        ✂️ {{ langMap[lang].trim || '裁剪' }}
      </button>
      <button class="action-btn-flat" @click="showSpeed = true" :disabled="!uploadedFilename || loading.speed" :class="{ loading: loading.speed }">
        <span v-if="loading.speed" class="loading-spinner"></span>
        ⏩ {{ langMap[lang].speed || '变速' }}
      </button>
      <!-- 在按钮区添加 -->
      <button class="action-btn-flat" @click="asrAudio" :disabled="!uploadedFilename || loading.asr" :class="{ loading: loading.asr }">
        <span v-if="loading.asr" class="loading-spinner"></span>
        📝 语音识别
      </button>
    </div>
    <div class="audio-area">
      <div class="audio-block" v-if="audioUrl">
        <div class="audio-title">原始音频试听</div>
        <audio :src="audioUrl" controls class="audio-player-flat" />
      </div>
      <div class="audio-block" v-if="denoisedUrl">
        <div class="audio-title">降噪后试听</div>
        <audio :src="denoisedUrl" controls class="audio-player-flat" />
      </div>
      <div class="audio-block" v-if="editedUrl">
        <div class="audio-title">编辑后试听</div>
        <audio :src="editedUrl" controls class="audio-player-flat" />
      </div>
    </div>
    <div class="download-row" v-if="denoisedUrl">
      <a :href="denoisedUrl" download class="download-btn-flat">
        <template v-if="lang === 'zh'">📥 下载降噪音频</template>
        <template v-else>📥 Download Denoised</template>
      </a>
    </div>
    <div class="download-row" v-if="editedUrl">
      <a :href="editedUrl" download class="download-btn-flat">
        <template v-if="lang === 'zh'">📥 下载编辑音频</template>
        <template v-else>📥 Download Edited</template>
      </a>
    </div>

    <!-- 裁剪弹窗 -->
    <div v-if="showTrim" class="modal-mask" @click.self="showTrim = false">
      <div class="modal-box">
        <div class="modal-title">裁剪音频</div>
        <div class="modal-row">
          <label>起始秒数：</label>
          <input type="number" v-model="trimStart" min="0" style="width:60px" />
          <label>结束秒数：</label>
          <input type="number" v-model="trimEnd" min="0" style="width:60px" />
        </div>
        <div class="modal-btns">
          <button class="action-btn-flat" @click="trimAudio">确定裁剪</button>
          <button class="action-btn-flat danger" @click="showTrim = false">取消</button>
        </div>
      </div>
    </div>
    <!-- 变速弹窗 -->
    <div v-if="showSpeed" class="modal-mask" @click.self="showSpeed = false">
      <div class="modal-box">
        <div class="modal-title">变速处理</div>
        <div class="modal-row">
          <label>速度倍数：</label>
          <input type="number" v-model="speedRate" min="0.5" max="3" step="0.1" style="width:60px" />
        </div>
        <div class="modal-btns">
          <button class="action-btn-flat" @click="changeSpeed">确定变速</button>
          <button class="action-btn-flat danger" @click="showSpeed = false">取消</button>
        </div>
      </div>
    </div>

    <!-- 批量处理区域 -->
    <div class="btn-row">
      <label class="action-btn-flat" :class="{ loading: loading.batchUpload }">
        <input type="file" accept="audio/*,video/mp4" @change="onFilesChange" multiple hidden />
        <span v-if="loading.batchUpload" class="loading-spinner"></span>
        🎵 {{ langMap[lang].batchSelectAudio || '批量选择音频文件' }}
      </label>
      <button class="action-btn-flat" @click="batchDenoise" :disabled="uploadedFiles.length === 0 || loading.batchDenoise" :class="{ loading: loading.batchDenoise }">
        <span v-if="loading.batchDenoise" class="loading-spinner"></span>
        ✨ {{ langMap[lang].batchDenoise || '批量降噪' }}
      </button>
    </div>

    <!-- 展示批量降噪结果 -->
    <div v-if="batchResults.length" class="batch-result-list">
      <div v-for="r in batchResults" :key="r.filename" class="batch-result-item">
        <span>{{ r.filename }}</span>
        <template v-if="r.success">
          <a :href="`http://localhost:5000/api/download/${r.result}`" download class="download-btn-flat">
            <template v-if="lang === 'zh'">{{ langMap[lang].downloadDenoised || '下载降噪' }}</template>
            <template v-else>Download Denoised</template>
          </a>
        </template>
        <template v-else>
          <span style="color:#f55;">
            <template v-if="lang === 'zh'">{{ langMap[lang].failed || '失败' }}</template>
            <template v-else>Failed</template>
            ：{{ r.error }}
          </span>
        </template>
      </div>
    </div>

    <!-- 音频剪辑区域 -->
    <div class="audio-editor-card">
      <div class="editor-title">
        <span>{{ langMap[lang].audioClip || '音频剪辑' }}</span>
        <button class="action-btn-flat" @click="resetSegments" style="margin-left:16px;">{{ langMap[lang].reset || '重置' }}</button>
        <button class="action-btn-flat" @click="applyClip" :disabled="segments.filter(s => !s.deleted).length === 0">{{ langMap[lang].applyClip || '应用剪辑' }}</button>
        <button class="action-btn-flat" v-if="clipBlobUrl" @click="downloadClip">
          {{ langMap[lang].downloadEdited || '下载剪辑音频' }}
        </button>
      </div>
      <div v-if="audioBuffer && waveformData.length" class="waveform-bar">
        <canvas ref="waveformCanvas" width="800" height="80"
          @click="onWaveformClick"
          @mousedown="onWaveformMouseDown"
          @mousemove="onWaveformMouseMove"
          @mouseup="onWaveformMouseUp"
          @mouseleave="onWaveformMouseUp"
        ></canvas>
        <div class="segment-list">
          <span v-for="(seg, idx) in segments" :key="idx"
            :class="['segment-chip', idx===selectedSegment ? 'selected' : '', seg.deleted ? 'deleted' : '']"
            @click="selectSegment(idx)">
            {{ langMap[lang].segment || '片段' }}{{ idx+1 }}
            <span style="margin-left:6px;font-size:13px;">
              ({{ formatTime(seg.start) }} - {{ formatTime(seg.end) }})
            </span>
            <button class="delete-btn" v-if="segments.length>1 && !seg.deleted" @click.stop="deleteSegment(idx)">×</button>
            <span v-if="seg.deleted" style="color:#d32f2f;margin-left:4px;">已删除</span>
          </span>
        </div>
        <div class="clip-controls">
          <button class="action-btn-flat" @click="playSegment" :disabled="selectedSegment===null || segments[selectedSegment]?.deleted || playing">
            ▶ {{ langMap[lang].playSegment || '播放片段' }}
          </button>
          <button class="action-btn-flat" @click="pauseSegment" :disabled="!playing">
            ⏸ {{ langMap[lang].pauseSegment || '暂停' }}
          </button>
        </div>
      </div>
      <div v-else class="waveform-tip">{{ langMap[lang].clipTip || '上传音频后可进行可视化剪辑，点击波形分割片段，点击片段可选中并删除。' }}</div>
    </div>

    <!-- 在试听区下方或合适位置添加 -->
    <div v-if="asrText" class="asr-result-block">
      <div class="asr-title">
        <template v-if="lang === 'zh'">识别文本</template>
        <template v-else>Recognized Text</template>
      </div>
      <pre class="asr-text">{{ asrText }}</pre>
      <a v-if="asrTxtUrl" :href="asrTxtUrl" download class="download-btn-flat">
        <template v-if="lang === 'zh'">📥 下载文本</template>
        <template v-else>📥 Download Text</template>
      </a>
    </div>
  </div>
</template>

<script setup>
import { ref, inject, onMounted, watch, nextTick } from 'vue'

const lang = inject('lang')
const langMap = inject('langMap')

const file = ref(null)
const fileName = ref('')
const audioUrl = ref('')
const uploadedFilename = ref('')
const denoisedUrl = ref('')
const editedUrl = ref('')
const uploadedFiles = ref([])
const batchResults = ref([])
const showTrim = ref(false)
const trimStart = ref(0)
const trimEnd = ref(10)
const showSpeed = ref(false)
const speedRate = ref(1.0)
const asrText = ref('')
const asrTxtUrl = ref('')

// loading 状态
const loading = ref({
  upload: false,
  denoise: false,
  trim: false,
  speed: false,
  batchUpload: false,
  batchDenoise: false,
  asr: false
})

// 不要再写 loading.value.asr = false 了！

// 剪辑相关
const audioBuffer = ref(null)
const waveformData = ref([])
const segments = ref([{ start: 0, end: 0, deleted: false }]) // end=0表示未加载
const selectedSegment = ref(null)
const waveformCanvas = ref(null)
let audioCtx = null
let audioSource = null
const playing = ref(false) // 替换 let playing = false
const clipBlobUrl = ref('')

function onFileChange(e) {
  file.value = e.target.files[0]
  if (file.value) {
    fileName.value = file.value.name
    audioUrl.value = URL.createObjectURL(file.value)
    denoisedUrl.value = ''
    editedUrl.value = ''
    uploadFile()
  }
}

function onFilesChange(e) {
  const files = Array.from(e.target.files)
  uploadedFiles.value = []
  batchResults.value = []
  loading.value.batchUpload = true
  Promise.all(files.map(async file => {
    const formData = new FormData()
    formData.append('file', file)
    const res = await fetch('http://localhost:5000/api/upload', {
      method: 'POST',
      body: formData
    })
    const data = await res.json()
    if (data.filename) {
      uploadedFiles.value.push({ name: file.name, serverName: data.filename })
    }
  })).finally(() => {
    loading.value.batchUpload = false
  })
}

async function uploadFile() {
  if (!file.value) return
  loading.value.upload = true
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
  loading.value.upload = false
}

async function denoiseFile() {
  if (!uploadedFilename.value) return
  loading.value.denoise = true
  const res = await fetch('http://localhost:5000/api/denoise', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ filename: uploadedFilename.value })
  })
  const data = await res.json()
  if (data.result_filename) {
    denoisedUrl.value = `http://localhost:5000/api/download/${data.result_filename}`
    editedUrl.value = ''
  } else {
    alert('降噪失败')
  }
  loading.value.denoise = false
}

async function trimAudio() {
  if (!uploadedFilename.value) return
  loading.value.trim = true
  const res = await fetch('http://localhost:5000/api/trim', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      filename: uploadedFilename.value,
      start: Number(trimStart.value),
      end: Number(trimEnd.value)
    })
  })
  const data = await res.json()
  if (data.result_filename) {
    editedUrl.value = `http://localhost:5000/api/download/${data.result_filename}`
    showTrim.value = false
  } else {
    alert(data.error || '裁剪失败')
  }
  loading.value.trim = false
}

async function changeSpeed() {
  if (!uploadedFilename.value) return
  loading.value.speed = true
  const res = await fetch('http://localhost:5000/api/speed', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      filename: uploadedFilename.value,
      rate: Number(speedRate.value)
    })
  })
  const data = await res.json()
  if (data.result_filename) {
    editedUrl.value = `http://localhost:5000/api/download/${data.result_filename}`
    showSpeed.value = false
  } else {
    alert(data.error || '变速失败')
  }
  loading.value.speed = false
}

async function batchDenoise() {
  if (!uploadedFiles.value.length) return
  loading.value.batchDenoise = true
  const filenames = uploadedFiles.value.map(f => f.serverName)
  const res = await fetch('http://localhost:5000/api/batch_denoise', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ filenames })
  })
  const data = await res.json()
  batchResults.value = data.results || []
  loading.value.batchDenoise = false
}

async function asrAudio() {
  if (!uploadedFilename.value) return
  loading.value.asr = true
  asrText.value = ''
  asrTxtUrl.value = ''
  try {
    const res = await fetch('http://localhost:5000/api/asr', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filename: uploadedFilename.value })
    })
    const data = await res.json()
    if (data.text) {
      asrText.value = data.text
      if (data.txt_filename) {
        asrTxtUrl.value = `http://localhost:5000/api/download/${data.txt_filename}`
      }
    } else {
      alert(data.error || '识别失败')
    }
  } catch (e) {
    alert('识别失败')
  }
  loading.value.asr = false
}

// 工具函数：格式化时间
function formatTime(sec) {
  sec = Math.max(0, sec || 0)
  const m = Math.floor(sec / 60)
  const s = Math.floor(sec % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

// 监听音频加载，生成波形和初始片段
watch(audioUrl, async (url) => {
  if (!url) {
    waveformData.value = []
    segments.value = [{ start: 0, end: 0, deleted: false }]
    audioBuffer.value = null
    return
  }
  await loadAudioBuffer(url)
  drawWaveform()
})

async function loadAudioBuffer(url) {
  if (!window.AudioContext) return
  audioCtx = audioCtx || new window.AudioContext()
  const resp = await fetch(url)
  const arrayBuffer = await resp.arrayBuffer()
  audioBuffer.value = await audioCtx.decodeAudioData(arrayBuffer)
  const duration = audioBuffer.value.duration
  segments.value = [{ start: 0, end: duration, deleted: false }]
  // 生成波形数据
  const raw = audioBuffer.value.getChannelData(0)
  const step = Math.floor(raw.length / 800)
  const data = []
  for (let i = 0; i < 800; i++) {
    let min = 1, max = -1
    for (let j = 0; j < step; j++) {
      const v = raw[i * step + j]
      if (v < min) min = v
      if (v > max) max = v
    }
    data.push({ min, max })
  }
  waveformData.value = data
  await nextTick()
  drawWaveform()
}

function drawWaveform() {
  const canvas = waveformCanvas.value
  if (!canvas || !waveformData.value.length) return
  const ctx = canvas.getContext('2d')
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  // 背景
  ctx.fillStyle = '#f7f9fa'
  ctx.fillRect(0, 0, canvas.width, canvas.height)
  // 波形
  ctx.strokeStyle = '#232946'
  ctx.beginPath()
  waveformData.value.forEach((d, i) => {
    const y1 = 40 - d.max * 36
    const y2 = 40 - d.min * 36
    ctx.moveTo(i, y1)
    ctx.lineTo(i, y2)
  })
  ctx.stroke()
  // 片段分割线
  ctx.strokeStyle = '#ffd600'
  ctx.lineWidth = 2
  segments.value.forEach(seg => {
    const x1 = Math.round(seg.start / audioBuffer.value.duration * 800)
    ctx.beginPath()
    ctx.moveTo(x1, 0)
    ctx.lineTo(x1, 80)
    ctx.stroke()
    const x2 = Math.round(seg.end / audioBuffer.value.duration * 800)
    ctx.beginPath()
    ctx.moveTo(x2, 0)
    ctx.lineTo(x2, 80)
    ctx.stroke()
  })
  // 选中片段高亮
  if (selectedSegment.value !== null) {
    const seg = segments.value[selectedSegment.value]
    const x1 = Math.round(seg.start / audioBuffer.value.duration * 800)
    const x2 = Math.round(seg.end / audioBuffer.value.duration * 800)
    ctx.fillStyle = 'rgba(67,214,117,0.18)'
    ctx.fillRect(x1, 0, x2 - x1, 80)
  }
}

function onWaveformClick(e) {
  if (!audioBuffer.value) return
  const rect = waveformCanvas.value.getBoundingClientRect()
  const x = e.clientX - rect.left
  const t = x / 800 * audioBuffer.value.duration
  let idx = segments.value.findIndex(seg => !seg.deleted && t > seg.start && t < seg.end)
  if (idx === -1) return
  const seg = segments.value[idx]
  if (seg.end - seg.start < 0.2) return
  // 插入新片段，继承deleted=false
  segments.value.splice(idx + 1, 0, { start: t, end: seg.end, deleted: false })
  seg.end = t
  selectedSegment.value = idx + 1
  drawWaveform()
}

let dragging = false
function onWaveformMouseDown(e) {
  dragging = true
}
function onWaveformMouseMove(e) {
  if (!dragging) return
}
function onWaveformMouseUp(e) {
  dragging = false
}

function selectSegment(idx) {
  selectedSegment.value = idx
  drawWaveform()
}

// 删除片段：直接标记deleted
function deleteSegment(idx) {
  if (segments.value.filter(s => !s.deleted).length <= 1) return
  segments.value[idx].deleted = true
  if (selectedSegment.value === idx) selectedSegment.value = null
  drawWaveform()
}

// 重置剪辑
function resetSegments() {
  if (!audioBuffer.value) return
  segments.value = [{ start: 0, end: audioBuffer.value.duration, deleted: false }]
  selectedSegment.value = null
  drawWaveform()
}

// 播放/暂停逻辑
function playSegment() {
  if (selectedSegment.value === null || !audioBuffer.value) return
  const seg = segments.value[selectedSegment.value]
  if (seg.deleted) return
  if (audioSource) {
    audioSource.stop()
    audioSource.disconnect()
    audioSource = null
  }
  audioSource = audioCtx.createBufferSource()
  audioSource.buffer = audioBuffer.value
  audioSource.connect(audioCtx.destination)
  audioSource.start(0, seg.start, seg.end - seg.start)
  playing.value = true // 这里改为 .value
  audioSource.onended = () => {
    playing.value = false // 这里改为 .value
  }
}
function pauseSegment() {
  if (audioSource) {
    audioSource.stop()
    audioSource.disconnect()
    audioSource = null
    playing.value = false // 这里改为 .value
  }
}

// 应用剪辑：拼接未被删除的片段
async function applyClip() {
  if (!audioBuffer.value || segments.value.length < 1) return
  const ch = audioBuffer.value.numberOfChannels
  const rate = audioBuffer.value.sampleRate
  const keptSegs = segments.value.filter(seg => !seg.deleted)
  if (keptSegs.length === 0) return
  let totalLen = 0
  const segSamples = keptSegs.map(seg => {
    const start = Math.floor(seg.start * rate)
    const end = Math.floor(seg.end * rate)
    totalLen += end - start
    return { start, end }
  })
  const newBuffer = audioCtx.createBuffer(ch, totalLen, rate)
  for (let c = 0; c < ch; c++) {
    let offset = 0
    const oldData = audioBuffer.value.getChannelData(c)
    const newData = newBuffer.getChannelData(c)
    segSamples.forEach(({ start, end }) => {
      newData.set(oldData.slice(start, end), offset)
      offset += end - start
    })
  }
  // 导出为wav并上传
  const wavBlob = bufferToWavBlob(newBuffer)
  const formData = new FormData()
  formData.append('file', wavBlob, 'clip.wav')
  loading.value.upload = true
  const res = await fetch('http://localhost:5000/api/upload', {
    method: 'POST',
    body: formData
  })
  const data = await res.json()
  if (data.filename) {
    uploadedFilename.value = data.filename
    audioUrl.value = URL.createObjectURL(wavBlob)
    denoisedUrl.value = ''
    editedUrl.value = ''
    await loadAudioBuffer(audioUrl.value)
    drawWaveform()
    if (clipBlobUrl.value) URL.revokeObjectURL(clipBlobUrl.value)
    clipBlobUrl.value = URL.createObjectURL(wavBlob)
  }
  loading.value.upload = false
}

// 下载剪辑后的音频
function downloadClip() {
  if (!clipBlobUrl.value) return
  const a = document.createElement('a')
  a.href = clipBlobUrl.value
  a.download = 'clip.wav'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}

// PCM AudioBuffer转wav Blob
function bufferToWavBlob(buffer) {
  const numOfChan = buffer.numberOfChannels
  const length = buffer.length * numOfChan * 2 + 44
  const bufferArray = new ArrayBuffer(length)
  const view = new DataView(bufferArray)
  // RIFF identifier
  writeString(view, 0, 'RIFF')
  view.setUint32(4, 36 + buffer.length * numOfChan * 2, true)
  writeString(view, 8, 'WAVE')
  writeString(view, 12, 'fmt ')
  view.setUint32(16, 16, true)
  view.setUint16(20, 1, true)
  view.setUint16(22, numOfChan, true)
  view.setUint32(24, buffer.sampleRate, true)
  view.setUint32(28, buffer.sampleRate * numOfChan * 2, true)
  view.setUint16(32, numOfChan * 2, true)
  view.setUint16(34, 16, true)
  writeString(view, 36, 'data')
  view.setUint32(40, buffer.length * numOfChan * 2, true)
  // PCM samples
  let offset = 44
  for (let i = 0; i < buffer.length; i++) {
    for (let ch = 0; ch < numOfChan; ch++) {
      let sample = buffer.getChannelData(ch)[i]
      sample = Math.max(-1, Math.min(1, sample))
      view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7FFF, true)
      offset += 2
    }
  }
  return new Blob([bufferArray], { type: 'audio/wav' })
}
function writeString(view, offset, string) {
  for (let i = 0; i < string.length; i++) {
    view.setUint8(offset + i, string.charCodeAt(i))
  }
}

onMounted(() => {
  // 监听窗口resize，重绘波形
  window.addEventListener('resize', drawWaveform)
})
</script>

<style scoped>
@import url('https://at.alicdn.com/t/c/font_4245482_2k8w7k0k8kq.css');

.audio-uploader-flat {
  width: 100%;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 48px 0 0 0;
  background: var(--card-bg);
  color: var(--main-fg);
}
.header-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-left: 48px;
  margin-bottom: 10px;
}
.logo {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: #f7f9fa;
  box-shadow: 0 2px 8px rgba(45,123,229,0.08);
}
.title {
  font-size: 22px;
  font-weight: 800;
  color: var(--card-title);
  letter-spacing: 1.5px;
}
.divider {
  height: 2px;
  background: var(--divider);
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
  background: var(--btn-bg);
  color: var(--btn-fg);
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
  background: var(--side-bg);
  color: var(--side-fg);
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
  color: #ffffff;
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
  background: var(--btn-bg);
  color: var(--btn-fg);
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
  background: var(--side-bg);
  color: var(--side-fg);
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
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}
.modal-title {
  font-size: 18px;
  font-weight: 700;
  color: #ffffff;
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
}
.action-btn-flat.danger {
  background: #ffeaea;
  color: #d32f2f;
}
.batch-result-list {
  margin-left: 48px;
  margin-top: 24px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.batch-result-item {
  display: flex;
  align-items: center;
  gap: 18px;
  font-size: 15px;
}
input, select {
  background: var(--input-bg);
  color: var(--input-fg);
}
.action-btn-flat.loading,
.download-btn-flat.loading,
.table-btn.loading {
  position: relative;
  pointer-events: none;
  opacity: 0.7;
}
.loading-spinner {
  display: inline-block;
  width: 18px;
  height: 18px;
  border: 2px solid #b3b3b3;
  border-top: 2px solid #232946;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-right: 6px;
  vertical-align: middle;
}
@keyframes spin {
  0% { transform: rotate(0deg);}
  100% { transform: rotate(360deg);}
}
.audio-editor-card {
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
.waveform-bar {
  margin-bottom: 12px;
  position: relative;
}
.waveform-tip {
  color: #bbb;
  font-size: 15px;
  margin-top: 12px;
}
.segment-list {
  margin: 10px 0 0 0;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
.segment-chip {
  background: #ede9fe;
  color: #232946;
  border-radius: 10px;
  padding: 3px 12px;
  font-size: 14px;
  cursor: pointer;
  margin-right: 4px;
  display: flex;
  align-items: center;
  gap: 4px;
  border: 2px solid transparent;
  transition: border 0.2s;
}
.segment-chip.selected {
  border: 2px solid #43d675;
  background: #e0ffe9;
}
.segment-chip.deleted {
  opacity: 0.5;
  text-decoration: line-through;
  background: #ffeaea;
  border-color: #d32f2f;
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
}
.asr-result-block {
  margin-left: 48px;
  margin-top: 32px;
  background: #fffbe6;
  border-radius: 10px;
  box-shadow: 0 1px 8px #e3eaf7;
  padding: 18px 22px;
  max-width: 600px;
}
.asr-title {
  font-size: 16px;
  font-weight: 700;
  color: #232946;
  margin-bottom: 8px;
}
.asr-text {
  font-size: 15px;
  color: #232946;
  white-space: pre-wrap;
  margin-bottom: 10px;
}
</style>
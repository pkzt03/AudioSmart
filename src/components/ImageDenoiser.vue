<template>
  <div class="image-denoiser-flat">
    <div class="header-bar">
      <img src="https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/opencv.svg" class="logo" />
      <span class="title">{{ langMap[lang].image }}</span>
    </div>
    <div class="divider"></div>
    <div class="btn-row">
      <label class="action-btn-flat">
        <input type="file" accept="image/*" @change="onFileChange" hidden />
        🖼️ {{ langMap[lang].selectFile || '选择图片文件' }}
      </label>
      <button class="action-btn-flat" @click="denoiseNLM" :disabled="!uploadedFilename">
        ✨ {{ langMap[lang].denoise || '非局部均值去噪（NLM）' }}
      </button>
      <button class="action-btn-flat" @click="showCrop = true" :disabled="!originUrl">
        ✂️ {{ langMap[lang].trim || '裁剪图片' }}
      </button>
    </div>
    <div class="img-area" v-if="originUrl">
      <div class="img-block" @click="showPreview(originUrl)">
        <div class="img-title">{{ langMap[lang].originalAudio || '原图' }}</div>
        <img :src="originUrl" class="img-preview" />
      </div>
      <div class="img-block" v-if="nlmUrl" @click="showPreview(nlmUrl)">
        <div class="img-title">{{ langMap[lang].denoise || '非局部均值去噪（NLM）' }}</div>
        <img :src="nlmUrl" class="img-preview" />
      </div>
      <div class="img-block" v-if="croppedUrl" @click="showPreview(croppedUrl)">
        <div class="img-title">{{ langMap[lang].trim || '裁剪结果' }}</div>
        <img :src="croppedUrl" class="img-preview" />
      </div>
    </div>
    <div v-if="previewUrl" class="preview-mask" @click="previewUrl = ''">
      <img :src="previewUrl" class="preview-img" @click.stop />
    </div>
    <div class="download-row" v-if="nlmUrl">
      <a :href="nlmUrl" download class="download-btn-flat">
        📥 {{ langMap[lang].downloadDenoised || '下载降噪图片' }}
      </a>
    </div>
    <div class="download-row" v-if="croppedUrl">
      <a :href="croppedUrl" download class="download-btn-flat">
        📥 {{ langMap[lang].downloadEdited || '下载裁剪图片' }}
      </a>
    </div>

    <!-- 裁剪弹窗 -->
    <div v-if="showCrop" class="modal-mask" @click.self="showCrop = false">
      <div class="modal-box">
        <div class="modal-title">{{ langMap[lang].trim || '裁剪图片' }}</div>
        <div class="cropper-area">
          <canvas
            ref="cropCanvas"
            :width="cropCanvasWidth"
            :height="cropCanvasHeight"
            class="crop-canvas"
            @mousedown="startCrop"
            @mousemove="moveCrop"
            @mouseup="endCrop"
            @mouseleave="endCrop"
          ></canvas>
        </div>
        <div class="modal-row" style="margin-top:12px;">
          <span style="font-size:14px;">
            {{ langMap[lang].cropTip || '拖动鼠标选择裁剪区域，点击“确定裁剪”' }}
          </span>
        </div>
        <div class="modal-btns">
          <button class="action-btn-flat" @click="doCrop">{{ langMap[lang].confirmCrop || '确定裁剪' }}</button>
          <button class="action-btn-flat danger" @click="showCrop = false">{{ langMap[lang].cancel || '取消' }}</button>
        </div>
      </div>
    </div>

    <!-- 标注按钮 -->
    <div class="btn-row" v-if="originUrl">
      <button class="action-btn-flat" @click="showAnnotate = true">
        🖊️ {{ langMap[lang].annotate || '图片标注' }}
      </button>
    </div>

    <!-- 标注弹窗 -->
    <div v-if="showAnnotate" class="modal-mask" @click.self="showAnnotate = false">
      <div class="modal-box" style="min-width:520px;">
        <div class="modal-title">{{ langMap[lang].annotate || '图片标注' }}</div>
        <div class="annotate-toolbar">
          <button class="action-btn-flat" :class="{active: tool==='pen'}" @click="tool='pen'">✏️ {{ langMap[lang].pen || '画笔' }}</button>
          <button class="action-btn-flat" :class="{active: tool==='arrow'}" @click="tool='arrow'">➡️ {{ langMap[lang].arrow || '箭头' }}</button>
          <button class="action-btn-flat" :class="{active: tool==='text'}" @click="tool='text'">🔤 {{ langMap[lang].text || '文字' }}</button>
          <input type="color" v-model="color" style="margin-left:12px;width:32px;height:32px;border:none;"/>
        </div>
        <div class="annotate-area">
          <canvas
            ref="annotateCanvas"
            :width="annotateCanvasWidth"
            :height="annotateCanvasHeight"
            class="annotate-canvas"
            @mousedown="onAnnotateMouseDown"
            @mousemove="onAnnotateMouseMove"
            @mouseup="onAnnotateMouseUp"
            @mouseleave="onAnnotateMouseUp"
            @dblclick="onAnnotateDblClick"
          ></canvas>
        </div>
        <div class="modal-btns">
          <button class="action-btn-flat" @click="downloadAnnotated">{{ langMap[lang].downloadEdited || '下载标注图片' }}</button>
          <button class="action-btn-flat danger" @click="showAnnotate = false">{{ langMap[lang].cancel || '取消' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, inject } from 'vue'

const lang = inject('lang')
const langMap = inject('langMap')

const file = ref(null)
const fileName = ref('')
const originUrl = ref('')
const uploadedFilename = ref('')
const nlmUrl = ref('')
const croppedUrl = ref('')
const previewUrl = ref('')

const showCrop = ref(false)
const cropCanvas = ref(null)
const cropCanvasWidth = 400
const cropCanvasHeight = 400
const cropRect = ref({ x: 50, y: 50, w: 200, h: 200 })
const cropping = ref(false)
const cropStart = ref({ x: 0, y: 0 })

const showAnnotate = ref(false)
const annotateCanvas = ref(null)
const annotateCanvasWidth = 400
const annotateCanvasHeight = 400
const tool = ref('pen') // pen, arrow, text
const color = ref('#ff0000')
const drawing = ref(false)
const lastPos = ref({ x: 0, y: 0 })
const arrowStart = ref({ x: 0, y: 0 })
const arrowEnd = ref({ x: 0, y: 0 })
const textPos = ref({ x: 0, y: 0 })
const textInput = ref('')
const annotations = ref([]) // {type, points, color, text}

function onFileChange(e) {
  file.value = e.target.files[0]
  if (file.value) {
    fileName.value = file.value.name
    originUrl.value = URL.createObjectURL(file.value)
    uploadedFilename.value = ''
    nlmUrl.value = ''
    croppedUrl.value = ''
    uploadFile()
  }
}

async function uploadFile() {
  const formData = new FormData()
  formData.append('file', file.value)
  const res = await fetch('http://localhost:5000/api/image_upload', {
    method: 'POST',
    body: formData
  })
  const data = await res.json()
  if (data.filename) {
    uploadedFilename.value = data.filename
  }
}

async function denoiseNLM() {
  const res = await fetch('http://localhost:5000/api/image_denoise', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      filename: uploadedFilename.value,
      noise_type: 'salt'
    })
  })
  const data = await res.json()
  if (data.result_filename) {
    nlmUrl.value = `http://localhost:5000/api/image_download/${data.result_filename}`
  }
}

function showPreview(url) {
  previewUrl.value = url
}

// 裁剪相关
watch(showCrop, async (val) => {
  if (val && originUrl.value) {
    await nextTick()
    drawCropper()
  }
})

function drawCropper() {
  const canvas = cropCanvas.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  const img = new window.Image()
  img.onload = () => {
    ctx.clearRect(0, 0, cropCanvasWidth, cropCanvasHeight)
    ctx.drawImage(img, 0, 0, cropCanvasWidth, cropCanvasHeight)
    const { x, y, w, h } = cropRect.value
    ctx.save()
    ctx.strokeStyle = '#ffd600'
    ctx.lineWidth = 2
    ctx.strokeRect(x, y, w, h)
    ctx.restore()
    ctx.save()
    ctx.globalAlpha = 0.3
    ctx.fillStyle = '#232946'
    ctx.fillRect(0, 0, cropCanvasWidth, y)
    ctx.fillRect(0, y + h, cropCanvasWidth, cropCanvasHeight - y - h)
    ctx.fillRect(0, y, x, h)
    ctx.fillRect(x + w, y, cropCanvasWidth - x - w, h)
    ctx.restore()
  }
  img.src = originUrl.value
}

function getMousePos(e) {
  const rect = cropCanvas.value.getBoundingClientRect()
  return {
    x: Math.max(0, Math.min(e.clientX - rect.left, cropCanvasWidth)),
    y: Math.max(0, Math.min(e.clientY - rect.top, cropCanvasHeight))
  }
}

function startCrop(e) {
  cropping.value = true
  cropStart.value = getMousePos(e)
}

function moveCrop(e) {
  if (!cropping.value) return
  const pos = getMousePos(e)
  cropRect.value = {
    x: Math.min(cropStart.value.x, pos.x),
    y: Math.min(cropStart.value.y, pos.y),
    w: Math.abs(pos.x - cropStart.value.x),
    h: Math.abs(pos.y - cropStart.value.y)
  }
  drawCropper()
}

function endCrop() {
  cropping.value = false
}

async function doCrop() {
  const img = new window.Image()
  img.onload = async () => {
    const scaleX = img.width / cropCanvasWidth
    const scaleY = img.height / cropCanvasHeight
    const { x, y, w, h } = cropRect.value
    const cropData = {
      filename: uploadedFilename.value,
      x: Math.round(x * scaleX),
      y: Math.round(y * scaleY),
      w: Math.round(w * scaleX),
      h: Math.round(h * scaleY)
    }
    const res = await fetch('http://localhost:5000/api/image_crop', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(cropData)
    })
    const data = await res.json()
    if (data.result_filename) {
      croppedUrl.value = `http://localhost:5000/api/image_download/${data.result_filename}`
      showCrop.value = false
    } else {
      alert(data.error || (langMap[lang].failed || '裁剪失败'))
    }
  }
  img.src = originUrl.value
}

// 标注相关
watch(showAnnotate, async (val) => {
  if (val && originUrl.value) {
    await nextTick()
    drawAnnotateCanvas()
  }
})

function drawAnnotateCanvas() {
  const canvas = annotateCanvas.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  const img = new window.Image()
  img.onload = () => {
    ctx.clearRect(0, 0, annotateCanvasWidth, annotateCanvasHeight)
    ctx.drawImage(img, 0, 0, annotateCanvasWidth, annotateCanvasHeight)
    // 绘制所有标注
    for (const ann of annotations.value) {
      ctx.save()
      ctx.strokeStyle = ann.color
      ctx.fillStyle = ann.color
      ctx.lineWidth = 2
      if (ann.type === 'pen') {
        ctx.beginPath()
        ctx.moveTo(ann.points[0].x, ann.points[0].y)
        for (let i = 1; i < ann.points.length; i++) {
          ctx.lineTo(ann.points[i].x, ann.points[i].y)
        }
        ctx.stroke()
      } else if (ann.type === 'arrow') {
        drawArrow(ctx, ann.points[0], ann.points[1], ann.color)
      } else if (ann.type === 'text') {
        ctx.font = '18px sans-serif'
        ctx.fillText(ann.text, ann.points[0].x, ann.points[0].y)
      }
      ctx.restore()
    }
  }
  img.src = originUrl.value
}

function onAnnotateMouseDown(e) {
  const pos = getAnnotateMousePos(e)
  if (tool.value === 'pen') {
    drawing.value = true
    annotations.value.push({ type: 'pen', points: [pos], color: color.value })
  } else if (tool.value === 'arrow') {
    drawing.value = true
    arrowStart.value = pos
    arrowEnd.value = pos
  } else if (tool.value === 'text') {
    textPos.value = pos
    textInput.value = prompt(langMap[lang].inputText || '请输入标注文字')
    if (textInput.value) {
      annotations.value.push({ type: 'text', points: [pos], color: color.value, text: textInput.value })
      drawAnnotateCanvas()
    }
  }
}
function onAnnotateMouseMove(e) {
  if (!drawing.value) return
  const pos = getAnnotateMousePos(e)
  if (tool.value === 'pen') {
    const ann = annotations.value[annotations.value.length - 1]
    ann.points.push(pos)
    drawAnnotateCanvas()
  } else if (tool.value === 'arrow') {
    arrowEnd.value = pos
    drawAnnotateCanvas()
    // 画动态箭头
    const ctx = annotateCanvas.value.getContext('2d')
    ctx.save()
    ctx.strokeStyle = color.value
    ctx.lineWidth = 2
    drawArrow(ctx, arrowStart.value, arrowEnd.value, color.value)
    ctx.restore()
  }
}
function onAnnotateMouseUp(e) {
  if (!drawing.value) return
  if (tool.value === 'arrow') {
    annotations.value.push({ type: 'arrow', points: [arrowStart.value, arrowEnd.value], color: color.value })
  }
  drawing.value = false
  drawAnnotateCanvas()
}
function onAnnotateDblClick(e) {
  // 预留：双击可撤销最后一次标注
  if (annotations.value.length > 0) {
    annotations.value.pop()
    drawAnnotateCanvas()
  }
}
function getAnnotateMousePos(e) {
  const rect = annotateCanvas.value.getBoundingClientRect()
  return {
    x: Math.max(0, Math.min(e.clientX - rect.left, annotateCanvasWidth)),
    y: Math.max(0, Math.min(e.clientY - rect.top, annotateCanvasHeight))
  }
}
function drawArrow(ctx, start, end, color) {
  const headlen = 12
  const dx = end.x - start.x
  const dy = end.y - start.y
  const angle = Math.atan2(dy, dx)
  ctx.beginPath()
  ctx.moveTo(start.x, start.y)
  ctx.lineTo(end.x, end.y)
  ctx.stroke()
  ctx.beginPath()
  ctx.moveTo(end.x, end.y)
  ctx.lineTo(end.x - headlen * Math.cos(angle - Math.PI / 6), end.y - headlen * Math.sin(angle - Math.PI / 6))
  ctx.lineTo(end.x - headlen * Math.cos(angle + Math.PI / 6), end.y - headlen * Math.sin(angle + Math.PI / 6))
  ctx.lineTo(end.x, end.y)
  ctx.lineTo(end.x - headlen * Math.cos(angle - Math.PI / 6), end.y - headlen * Math.sin(angle - Math.PI / 6))
  ctx.stroke()
  ctx.fill()
}
function downloadAnnotated() {
  drawAnnotateCanvas()
  const url = annotateCanvas.value.toDataURL('image/png')
  const a = document.createElement('a')
  a.href = url
  a.download = 'annotated.png'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}
</script>

<style scoped>
.image-denoiser-flat {
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
  color: #232946; /* 改为藏青色 */
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
.img-area {
  display: flex;
  gap: 40px;
  margin: 32px 0 0 48px;
  width: calc(100% - 48px);
}
.img-block {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  min-width: 220px;
  cursor: pointer;
}
.img-title {
  font-size: 15px;
  color: #ffffff;
  font-weight: 700;
  margin-bottom: 8px;
  letter-spacing: 0.5px;
}
.img-preview {
  width: 220px;
  height: 220px;
  object-fit: contain;
  border-radius: 8px;
  background: #f4f8fc;
  box-shadow: 0 1px 8px #e3eaf7;
  margin-bottom: 8px;
  transition: box-shadow 0.2s;
}
.img-block:hover .img-preview {
  box-shadow: 0 4px 24px #b3d8ff;
  transform: translateY(-4px) scale(1.04);
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
.preview-mask {
  position: fixed;
  left: 0; top: 0; width: 100vw; height: 100vh;
  background: rgba(30,40,60,0.75);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.2s;
}
.preview-img {
  max-width: 90vw;
  max-height: 90vh;
  border-radius: 16px;
  box-shadow: 0 8px 48px #feffff;
  background: #fff;
  animation: scaleIn 0.2s;
}
.cropper-area {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 18px 0;
  width: 100%;
}
.crop-canvas {
  border: 2px solid #ffd600;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 2px 16px #23294622;
  cursor: crosshair;
}
.footer-pro {
  z-index: 1;
  width: 100vw;
  text-align: center;
  color: #b3c7e6;
  font-size: 15px;
  margin-bottom: 12px;
  margin-top: 8px;
  letter-spacing: 1px;
  user-select: none;
}
.annotate-toolbar {
  display: flex;
  gap: 10px;
  margin-bottom: 12px;
  align-items: center;
}
.annotate-toolbar .action-btn-flat.active {
  background: #43d675;
  color: #fff;
}
.annotate-area {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 18px 0;
  width: 100%;
}
.annotate-canvas {
  border: 2px solid #ffd600;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 2px 16px #23294622;
  cursor: crosshair;
}
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
@keyanimations scaleIn {
  from { transform: scale(0.8);}
  to { transform: scale(1);}
}
@media (max-width: 700px) {
  .image-denoiser-flat {
    padding: 18px 0 0 0;
  }
  .header-bar, .btn-row, .img-area, .download-row {
    margin-left: 12px;
  }
  .img-area {
    flex-direction: column;
    gap: 18px;
  }
}
</style>
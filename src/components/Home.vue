<template>
  <div class="home-page">
    <div class="brand-bar">
      <img class="brand-logo" src="https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/audiomack.svg" />
      <div>
        <div class="brand-title">
          <template v-if="lang === 'zh'">音频智编平台</template>
          <template v-else>AudioSmart Platform</template>
        </div>
        <div class="brand-subtitle">
          <template v-if="lang === 'zh'">智能 · 高效 · 专业的音频处理工具</template>
          <template v-else>Intelligent · Efficient · Professional Audio Processing Tool</template>
        </div>
      </div>
    </div>
    <div class="carousel">
      <img :src="images[current].url" class="carousel-img" />
      <div class="carousel-mask"></div>
      <div class="carousel-caption">
        <template v-if="lang === 'zh'">{{ images[current].caption }}</template>
        <template v-else>{{ images[current].caption_en }}</template>
      </div>
      <div class="carousel-dots">
        <span
          v-for="(img, idx) in images"
          :key="idx"
          :class="{ active: idx === current }"
          @click="current = idx"
        ></span>
      </div>
    </div>
    <div class="feature-row">
      <div class="feature-card" v-for="f in features" :key="f.title">
        <div class="feature-icon" v-html="f.icon"></div>
        <div class="feature-title">
          <template v-if="lang === 'zh'">{{ f.title }}</template>
          <template v-else>{{ f.title_en }}</template>
        </div>
        <div class="feature-desc">
          <template v-if="lang === 'zh'">{{ f.desc }}</template>
          <template v-else>{{ f.desc_en }}</template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, inject } from 'vue'

const lang = inject('lang')

const images = [
  {
    url: 'https://images.unsplash.com/photo-1464983953574-0892a716854b?auto=format&fit=crop&w=600&q=80',
    caption: '多格式音频上传与降噪，轻松一步到位',
    caption_en: 'Multi-format audio upload and denoise, easy and fast'
  },
  {
    url: 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=600&q=80',
    caption: '波形可视化，编辑更直观',
    caption_en: 'Waveform visualization, more intuitive editing'
  },
  {
    url: 'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=600&q=80',
    caption: '批量处理，效率提升',
    caption_en: 'Batch processing, efficiency improvement'
  }
]
const current = ref(0)
let timer = null

onMounted(() => {
  timer = setInterval(() => {
    current.value = (current.value + 1) % images.length
  }, 3500)
})
onUnmounted(() => {
  clearInterval(timer)
})

const features = [
  {
    icon: '🎵',
    title: '音频降噪',
    title_en: 'Audio Denoise',
    desc: '支持MP3/WAV/MP4等格式，一键去除噪声，提升音质',
    desc_en: 'Support MP3/WAV/MP4, one-click noise reduction, improve audio quality'
  },
  {
    icon: '✂️',
    title: '音频编辑',
    title_en: 'Audio Editing',
    desc: '裁剪、变速、拼接等多种编辑功能，满足多样需求',
    desc_en: 'Trim, speed change, merge and more editing features'
  },
  {
    icon: '📊',
    title: '波形可视化',
    title_en: 'Waveform Visualization',
    desc: '音频波形实时显示，操作更直观',
    desc_en: 'Real-time waveform display, more intuitive operation'
  },
  {
    icon: '🖼️',
    title: '图片去噪',
    title_en: 'Image Denoise',
    desc: '支持图片降噪、裁剪、标注等多种图像处理',
    desc_en: 'Image denoise, crop, annotation and more'
  },
  {
    icon: '🚀',
    title: '批量处理',
    title_en: 'Batch Processing',
    desc: '支持音频/图片批量上传与处理，大幅提升效率',
    desc_en: 'Batch upload and process audio/images, greatly improve efficiency'
  }
]
</script>

<style scoped>
.home-page {
  width: 100%;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 48px;
  background: linear-gradient(120deg, #f7f7fa 60%, #e0e7ff 100%);
}
.brand-bar {
  display: flex;
  align-items: center;
  gap: 18px;
  margin-bottom: 18px;
}
.brand-logo {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 2px 12px #e0e0e0;
}
.brand-title {
  font-size: 30px;
  font-weight: 800;
  color: #232946;
  letter-spacing: 2px;
}
.brand-subtitle {
  font-size: 16px;
  color: #6b7280;
  margin-top: 2px;
  letter-spacing: 1px;
}
.carousel {
  position: relative;
  width: 420px;
  height: 220px;
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 4px 32px #b3c7e6;
  margin-bottom: 32px;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
}
.carousel-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: opacity 0.6s;
}
.carousel-mask {
  position: absolute;
  left: 0; top: 0; right: 0; bottom: 0;
  background: linear-gradient(180deg,rgba(0,0,0,0.08) 60%,rgba(0,0,0,0.32) 100%);
  pointer-events: none;
}
.carousel-caption {
  position: absolute;
  left: 0; right: 0; bottom: 18px;
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  text-align: center;
  text-shadow: 0 2px 8px #23294699;
  letter-spacing: 1px;
  z-index: 2;
}
.carousel-dots {
  position: absolute;
  bottom: 12px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 10px;
  z-index: 3;
}
.carousel-dots span {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #b3c7e6;
  cursor: pointer;
  transition: background 0.2s;
}
.carousel-dots span.active {
  background: #232946;
}
.feature-row {
  display: flex;
  flex-wrap: wrap;
  gap: 28px;
  justify-content: center;
  margin-top: 32px;
  margin-bottom: 32px;
  width: 100%;
  max-width: 900px;
}
.feature-card {
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 2px 16px #e0e0e0;
  padding: 28px 22px 18px 22px;
  width: 180px;
  min-height: 160px;
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: transform 0.18s, box-shadow 0.18s;
  cursor: pointer;
}
.feature-card:hover {
  transform: translateY(-6px) scale(1.04);
  box-shadow: 0 8px 32px #b3c7e6;
}
.feature-icon {
  font-size: 38px;
  margin-bottom: 12px;
}
.feature-title {
  font-size: 18px;
  font-weight: 700;
  color: #232946;
  margin-bottom: 6px;
}
.feature-desc {
  font-size: 14px;
  color: #6b7280;
  text-align: center;
  line-height: 1.6;
}
@media (max-width: 600px) {
  .carousel {
    width: 98vw;
    height: 160px;
  }
  .feature-row {
    gap: 14px;
    max-width: 100vw;
  }
  .feature-card {
    width: 44vw;
    min-width: 120px;
    padding: 16px 6px 10px 6px;
  }
  .brand-title {
    font-size: 22px;
  }
}
</style>
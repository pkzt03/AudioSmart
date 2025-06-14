<template>
  <div class="file-manager-flat">
    <div class="header-bar">
      <span class="logo-emoji">🗂️</span>
      <span class="title">{{ langMap[lang].file }}</span>
    </div>
    <div class="divider"></div>
    <div class="folder-row">
      <label>{{ langMap[lang].folder }}</label>
      <select v-model="folder" class="select-flat" @change="fetchFiles">
        <option value="uploads">{{ langMap[lang].audio }}{{ langMap[lang].upload || '上传' }}</option>
        <option value="results">{{ langMap[lang].audio }}{{ langMap[lang].result || '结果' }}</option>
        <option value="image_uploads">{{ langMap[lang].image }}{{ langMap[lang].upload || '上传' }}</option>
        <option value="image_results">{{ langMap[lang].image }}{{ langMap[lang].result || '结果' }}</option>
      </select>
      <button class="action-btn-flat" @click="fetchFiles">{{ langMap[lang].refresh }}</button>
    </div>
    <div class="file-table-wrap">
      <table class="file-table" v-if="files.length">
        <thead>
          <tr>
            <th>{{ langMap[lang].filename }}</th>
            <th>{{ langMap[lang].size }}</th>
            <th>{{ langMap[lang].mtime }}</th>
            <th>{{ langMap[lang].action }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="f in files" :key="f.filename">
            <td>{{ f.filename }}</td>
            <td>{{ formatSize(f.size) }}</td>
            <td>{{ f.mtime }}</td>
            <td>
              <a :href="downloadUrl(f.filename)" download class="table-btn">{{ langMap[lang].download }}</a>
              <button class="table-btn" @click="deleteFile(f.filename)">
                {{ langMap[lang].delete }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="empty-tip">{{ langMap[lang].empty }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, inject } from 'vue'

const lang = inject('lang')
const langMap = inject('langMap')

const folder = ref('uploads')
const files = ref([])

function fetchFiles() {
  fetch(`http://localhost:5000/api/list_files?folder=${folder.value}`)
    .then(res => res.json())
    .then(data => {
      files.value = data.files || []
    })
}

function formatSize(size) {
  if (size > 1024 * 1024)
    return (size / 1024 / 1024).toFixed(2) + ' MB'
  if (size > 1024)
    return (size / 1024).toFixed(2) + ' KB'
  return size + ' B'
}

function downloadUrl(filename) {
  if (folder.value === 'image_results')
    return `http://localhost:5000/api/image_download/${filename}`
  if (folder.value === 'image_uploads')
    return `http://localhost:5000/image_uploads/${filename}`
  return `http://localhost:5000/api/download/${filename}`
}

async function deleteFile(filename) {
  if (!confirm(langMap[lang].deleteConfirm || '确定要删除该文件吗？')) return
  const res = await fetch('http://localhost:5000/api/delete_file', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      folder: folder.value, // 修正为folder.value
      filename
    })
  })
  const data = await res.json()
  if (data.success) {
    showMessage && showMessage('success', langMap[lang].delete + '成功')
    fetchFiles() // 修正为fetchFiles()
  } else {
    showMessage && showMessage('error', data.error || '删除失败')
  }
}

onMounted(fetchFiles)
</script>

<style scoped>
.file-manager-flat {
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
.folder-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-left: 48px;
  margin-bottom: 18px;
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
.action-btn-flat:not(:disabled):hover {
  background: #d1c4e9;
  color: #232946;
}
.file-table-wrap {
  margin-left: 48px;
  width: 80%;
}
.file-table {
  width: 100%;
  border-collapse: collapse;
  background: #fff;
  margin-bottom: 24px;
}
.file-table th, .file-table td {
  border: 1px solid #f0f0f0;
  padding: 8px 12px;
  text-align: left;
  font-size: 15px;
  color: #232946;
}
.file-table th {
  background: #f8f8fc;
  color: #232946;
  font-weight: 700;
}
.table-btn {
  background: #ede9fe;
  color: #232946; /* 按钮字体为藏青色 */
  border: none;
  border-radius: 8px;
  padding: 4px 12px;
  font-size: 14px;
  cursor: pointer;
  margin-right: 8px;
  font-weight: 600;
  text-decoration: none;
  transition: background 0.2s, color 0.2s;
}
.table-btn.danger {
  background: #ffeaea;
  color: #d32f2f;
}
.table-btn:hover {
  background: #d1c4e9;
  color: #232946;
}
.empty-tip {
  color: #bbb;
  font-size: 15px;
  margin: 32px 0 0 48px;
}
@media (max-width: 700px) {
  .file-manager-flat {
    padding: 18px 0 0 0;
  }
  .header-bar, .folder-row, .file-table-wrap {
    margin-left: 12px;
  }
  .file-table-wrap {
    width: 98%;
  }
}
</style>
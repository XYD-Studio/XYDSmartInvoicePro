<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useInvoiceStore } from '../store/invoice'
import { exportDataToExcel } from '../utils/excelAndFile'
import axios from 'axios'
import ApiSetupModal from '../components/ApiSetupModal.vue'
import AboutModal from '../components/AboutModal.vue'

import { Splitpanes, Pane } from 'splitpanes'
import 'splitpanes/dist/splitpanes.css'

const store = useInvoiceStore()
const isDragging = ref(false)
const showSettings = ref(!store.config.provider)
const showAbout = ref(false)

interface InvoiceFile {
  id: string
  file: File
  url: string
  type: string
  status: 'pending' | 'processing' | 'success' | 'error' | 'warning'
  errorMsg?: string
  data: Record<string, any>
}

const fileList = ref<InvoiceFile[]>([])
const activeId = ref<string | null>(null)

const activeFile = computed(() => fileList.value.find(f => f.id === activeId.value))
const activeIndex = computed(() => fileList.value.findIndex(f => f.id === activeId.value))

const allFields = computed(() => {
  const fields = new Set<string>()
  fileList.value.forEach(f => {
    if (f.status === 'success' || f.status === 'warning') Object.keys(f.data).forEach(k => {
      if (!['源文件名', '是否重复'].includes(k)) fields.add(k)
    })
  })
  return Array.from(fields)
})

const displayCols = ref<string[]>([...(store.config.customColumnOrder || [])])
const draggingCol = ref<string | null>(null)

// 同步新增字段时，避开已经被用户删掉的隐藏列
watch(allFields, (newFields) => {
  let changed = false
  newFields.forEach(f => {
    const hiddenCols = store.config.hiddenCols || []
    if (!displayCols.value.includes(f) && !hiddenCols.includes(f)) {
      displayCols.value.push(f)
      changed = true
    }
  })
  if (changed) {
    store.saveConfig({ customColumnOrder: displayCols.value })
  }
}, { deep: true, immediate: true })

// 拖拽列功能
const onDragStartCol = (col: string) => { draggingCol.value = col }
const onDropCol = (targetCol: string) => {
  if (!draggingCol.value || draggingCol.value === targetCol) return
  const fromIdx = displayCols.value.indexOf(draggingCol.value)
  const toIdx = displayCols.value.indexOf(targetCol)
  displayCols.value.splice(fromIdx, 1)
  displayCols.value.splice(toIdx, 0, draggingCol.value)
  draggingCol.value = null
  store.saveConfig({ customColumnOrder: displayCols.value })
}

// >>> 新增：删除某一列 <<<
const removeCol = (colToRemove: string) => {
  displayCols.value = displayCols.value.filter(c => c !== colToRemove)
  const newHidden = [...(store.config.hiddenCols || []), colToRemove]
  store.saveConfig({ customColumnOrder: displayCols.value, hiddenCols: newHidden })
}

// >>> 新增：一键恢复被删除的列 <<<
const restoreCols = () => {
  store.saveConfig({ hiddenCols: [] }) // 清空黑名单
  allFields.value.forEach(f => {
     if (!displayCols.value.includes(f)) displayCols.value.push(f)
  })
  store.saveConfig({ customColumnOrder: displayCols.value })
}

const addFiles = (files: FileList | File[]) => {
  for (let i = 0; i < files.length; i++) {
    const id = Math.random().toString(36).substring(7)
    fileList.value.push({
      id, file: files[i], url: URL.createObjectURL(files[i]),
      type: files[i].type.includes('pdf') ? 'pdf' : 'image',
      status: 'pending', data: { '源文件名': files[i].name }
    })
    if (!activeId.value) activeId.value = id
  }
}

const handleDrop = (e: DragEvent) => {
  isDragging.value = false
  if (e.dataTransfer?.files) addFiles(e.dataTransfer.files)
}

const clearAllFiles = () => {
  if (fileList.value.length === 0) return
  if (confirm('确认要清空当前列表中的所有发票吗？这不会影响已导出的数据。')) {
    fileList.value = []
    activeId.value = null
  }
}

const startProcess = async () => {
  if (store.config.provider === 'aliyun-ocr') {
    if (!store.config.aliyunAk || !store.config.aliyunSk) {
       showSettings.value = true
       return alert("请先配置阿里云 OCR 的 AccessKey！")
    }
  } else {
    const providerKey = store.config.keys[store.config.provider as keyof typeof store.config.keys]
    if (!providerKey) {
       showSettings.value = true
       return alert("请先配置当前引擎的 API Key！")
    }
  }

  const pendingFiles = fileList.value.filter(f => f.status === 'pending' || f.status === 'error')
  if (pendingFiles.length === 0) return

  for (const item of pendingFiles) {
    item.status = 'processing'
    activeId.value = item.id

    const formData = new FormData()
    formData.append('file', item.file)
    formData.append('provider', store.config.provider)
    formData.append('aliyun_ak', store.config.aliyunAk || '')
    formData.append('aliyun_sk', store.config.aliyunSk || '')
    const llmKey = store.config.keys['aliyun'] || store.config.keys['zhipu'] || store.config.keys['openai'] || ''
    formData.append('ai_key', store.config.provider === 'aliyun-ocr' ? llmKey : (store.config.keys[store.config.provider as keyof typeof store.config.keys] || ''))
    formData.append('base_url', store.config.baseUrl || 'https://dashscope.aliyuncs.com/compatible-mode/v1')
    formData.append('model', store.config.model || 'qwen-vl-plus')

    try {
      const res = await axios.post('http://127.0.0.1:8000/api/v1/process-invoice', formData)
      item.data = { ...item.data, ...res.data.data }
      item.data['是否重复'] = store.checkDuplicate(item.data) ? '是' : '否'
      if (res.data.fallback_warning) {
        item.status = 'warning'
        item.errorMsg = res.data.fallback_warning
      } else {
        item.status = 'success'
      }
      store.invoiceFingerprints.add(item.data['发票号码'] || item.data['开票日期'])
    } catch (e: any) {
      item.status = 'error'
      item.errorMsg = e.response?.data?.detail || e.message
    }
  }
}

const handleKeydown = (e: KeyboardEvent) => {
  if (document.activeElement?.tagName === 'INPUT' || document.activeElement?.tagName === 'TEXTAREA') return
  if (fileList.value.length === 0) return

  if (e.altKey && e.key === 'ArrowDown') {
    e.preventDefault()
    if (activeIndex.value < fileList.value.length - 1) activeId.value = fileList.value[activeIndex.value + 1].id
  } else if (e.altKey && e.key === 'ArrowUp') {
    e.preventDefault()
    if (activeIndex.value > 0) activeId.value = fileList.value[activeIndex.value - 1].id
  }
}

onMounted(() => window.addEventListener('keydown', handleKeydown))
onUnmounted(() => window.removeEventListener('keydown', handleKeydown))

const handleExport = () => {
  const successData = fileList.value.filter(f => f.status === 'success' || f.status === 'warning').map(f => {
     const row: any = { '源文件名': f.data['源文件名'] }
     displayCols.value.forEach(col => { row[col] = f.data[col] || '-' })
     return row
  })
  if (successData.length === 0) return alert('没有成功的记录可导出')
  exportDataToExcel(successData, `发票台账_${new Date().getTime()}.xlsx`)
}
</script>

<template>
  <div class="flex flex-col h-screen bg-gray-50 text-gray-800 font-sans overflow-hidden">
    
    <div class="h-14 bg-white border-b flex justify-between items-center px-6 shadow-sm z-20 shrink-0">
      <h1 class="text-xl font-bold text-blue-600 flex items-center">
        <span class="mr-2">🧾</span> SmartInvoice 智能票据助手
      </h1>
      <div class="flex space-x-4">
        <button @click="showAbout = true" class="text-sm font-medium text-gray-500 hover:text-blue-600">ℹ️ 关于与帮助</button>
        <button @click="showSettings = true" class="text-sm font-medium text-gray-500 hover:text-blue-600">⚙️ 引擎设置</button>
        <button @click="startProcess" class="px-5 py-1.5 bg-blue-600 text-white text-sm font-bold rounded-md hover:bg-blue-700 shadow-sm transition-colors">
          ▶️ 开始识别全部
        </button>
      </div>
    </div>

    <splitpanes horizontal class="flex-1 default-theme">
      <pane size="65">
        <splitpanes>
          
          <pane size="20" min-size="15" class="bg-white flex flex-col relative z-10 border-r border-gray-200">
            <label 
              class="m-3 p-4 border-2 border-dashed border-gray-300 rounded-lg text-center cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition-colors"
              :class="{'border-blue-500 bg-blue-50': isDragging}"
              @dragover.prevent="isDragging = true" @dragleave.prevent="isDragging = false" @drop.prevent="handleDrop"
            >
              <div class="text-2xl mb-1">📂</div>
              <div class="text-xs text-gray-500 font-medium">拖拽上传票据</div>
              <input type="file" class="hidden" multiple accept=".pdf,.jpg,.png" @change="e => addFiles((e.target as HTMLInputElement).files!)" />
            </label>
            
            <div class="px-3 pb-2 flex justify-between items-center border-b border-gray-100">
               <span class="text-xs font-semibold text-gray-400">已导入 {{ fileList.length }} 份</span>
               <button @click="clearAllFiles" class="text-xs text-red-500 hover:text-red-700 hover:bg-red-50 px-2 py-1 rounded transition-colors" title="清空全部列表">
                 🗑️ 一键清空
               </button>
            </div>
            
            <div class="flex-1 overflow-y-auto px-3 pb-3 pt-2 space-y-1.5">
              <div 
                v-for="(item, idx) in fileList" :key="item.id"
                @click="activeId = item.id"
                class="p-2.5 rounded-md text-sm cursor-pointer border transition-all flex items-center justify-between"
                :class="activeId === item.id ? 'border-blue-500 bg-blue-50 shadow-sm' : 'border-transparent hover:bg-gray-100'"
              >
                <div class="truncate flex-1 pr-2">
                  <span class="text-gray-400 mr-1">{{ idx + 1 }}.</span>
                  <span class="font-medium text-gray-700" :title="item.file.name">{{ item.file.name }}</span>
                </div>
                <span v-if="item.status === 'success'" class="text-green-500 text-xs font-bold">●</span>
                <span v-else-if="item.status === 'warning'" class="text-yellow-500 text-xs font-bold" title="已降级为大模型识别">⚠️</span>
                <span v-else-if="item.status === 'processing'" class="text-blue-500 text-xs animate-spin">↻</span>
                <span v-else-if="item.status === 'error'" class="text-red-500 text-xs font-bold" :title="item.errorMsg">❗</span>
                <span v-else class="text-gray-300 text-xs">○</span>
              </div>
            </div>
          </pane>

          <pane size="55" min-size="30" class="bg-gray-200 p-4 flex flex-col relative">
            <div class="absolute top-6 left-6 text-xs text-gray-400 font-medium tracking-widest uppercase z-10">原件视图</div>
            <div class="flex-1 bg-white rounded-xl shadow border border-gray-300 overflow-hidden flex items-center justify-center relative">
              <template v-if="activeFile">
                <iframe v-if="activeFile.type === 'pdf'" :src="activeFile.url" class="w-full h-full border-0"></iframe>
                <img v-else :src="activeFile.url" class="max-w-full max-h-full object-contain p-2" />
              </template>
              <div v-else class="text-gray-400 text-sm">请选择左侧文件</div>
            </div>
            <div class="text-center mt-2 text-xs text-gray-500 font-medium">
              💡 提示：使用 <kbd class="bg-gray-300 text-white px-1 rounded">Alt</kbd> + <kbd class="bg-gray-300 text-white px-1 rounded">↑</kbd> <kbd class="bg-gray-300 text-white px-1 rounded">↓</kbd> 跨文件切换
            </div>
          </pane>

          <pane size="25" min-size="20" class="bg-white flex flex-col relative z-10 border-l border-gray-200">
            <div class="p-4 border-b bg-yellow-50/50 shrink-0">
              <h2 class="text-sm font-bold text-yellow-800 flex items-center"><span class="mr-1">✍️</span> 提取结果核对</h2>
              <p class="text-[10px] text-yellow-600 mt-1">提取有误请直接修改，系统自动保存。</p>
            </div>
            
            <div class="flex-1 overflow-y-auto p-4 space-y-4" v-if="activeFile && (activeFile.status === 'success' || activeFile.status === 'warning')">
              <div v-if="activeFile.status === 'warning'" class="bg-yellow-100 text-yellow-800 text-xs p-2 rounded border border-yellow-200">
                ⚠️ {{ activeFile.errorMsg }}
              </div>
              <div v-for="field in allFields" :key="field">
                <label class="block text-xs font-semibold text-gray-600 mb-1">{{ field }}</label>
                <textarea 
                  v-if="['购买项目名称', '销方名称', '购方名称'].includes(field)"
                  v-model="activeFile.data[field]" rows="2"
                  class="w-full border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500 shadow-sm p-2 bg-blue-50/30"
                ></textarea>
                <input 
                  v-else type="text" v-model="activeFile.data[field]" 
                  class="w-full border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500 shadow-sm p-2 bg-blue-50/30" 
                />
              </div>
            </div>
            <div v-else-if="activeFile && activeFile.status === 'processing'" class="flex-1 flex items-center justify-center text-blue-500 text-sm">AI 正在火速识别中...</div>
            <div v-else-if="activeFile && activeFile.status === 'error'" class="flex-1 p-4 text-red-500 text-sm break-words">{{ activeFile.errorMsg }}</div>
            <div v-else class="flex-1 flex items-center justify-center text-gray-400 text-sm">暂无识别数据</div>
          </pane>

        </splitpanes>
      </pane>

      <pane size="35" min-size="15" class="bg-white flex flex-col relative z-20 border-t border-gray-200">
        <div class="flex justify-between items-center p-3 border-b bg-gray-50 shrink-0">
          <div class="flex items-center space-x-4">
             <h3 class="text-sm font-bold text-gray-700">📊 最终台账总览 (支持拖拽表头排序)</h3>
             <!-- >>> 新增恢复列按钮 <<< -->
             <button v-if="(store.config.hiddenCols || []).length > 0" @click="restoreCols" class="text-xs text-blue-500 hover:text-blue-700 underline transition-colors">
               ↺ 恢复隐藏的列 ({{ store.config.hiddenCols?.length }})
             </button>
          </div>
          <button @click="handleExport" class="px-6 py-1.5 bg-emerald-500 text-white text-sm font-bold rounded-md hover:bg-emerald-600 shadow-sm transition-colors">
            📥 确认无误，导出 Excel
          </button>
        </div>
        <div class="flex-1 overflow-auto p-2">
          <table class="w-full text-left text-xs border-collapse">
            <thead class="bg-gray-100 sticky top-0 shadow-sm select-none z-10">
              <tr>
                <th class="p-2 border font-semibold text-gray-600 w-10 text-center">#</th>
                <th class="p-2 border font-semibold text-gray-600 min-w-[100px]">文件名</th>
                
                <th 
                  v-for="col in displayCols" :key="col" draggable="true"
                  @dragstart="onDragStartCol(col)" @dragover.prevent @drop="onDropCol(col)"
                  class="p-2 border font-semibold text-gray-600 whitespace-nowrap cursor-move hover:bg-gray-200 transition-colors group relative"
                  :class="{'opacity-50': draggingCol === col}" title="按住拖拽调整，点击右侧 X 隐藏"
                >
                  <div class="flex items-center justify-between">
                    <span>{{ col }} <span class="text-[10px] text-gray-400 ml-1">↕️</span></span>
                    <!-- >>> 新增隐藏列按钮 (X) <<< -->
                    <button @click.stop="removeCol(col)" class="text-red-400 hover:text-red-600 ml-2 opacity-0 group-hover:opacity-100 transition-opacity">×</button>
                  </div>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, idx) in fileList.filter(f => f.status === 'success' || f.status === 'warning')" :key="item.id" class="hover:bg-blue-50 transition-colors" :class="{'bg-blue-50/50': activeId === item.id}">
                <td class="p-2 border text-center text-gray-400">{{ idx + 1 }}</td>
                <td class="p-2 border text-gray-500 truncate max-w-[100px]" :title="item.data['源文件名']">{{ item.data['源文件名'] }}</td>
                <td v-for="col in displayCols" :key="col" class="p-2 border whitespace-normal break-words min-w-[120px]">
                  {{ item.data[col] || '-' }}
                </td>
              </tr>
              <tr v-if="fileList.filter(f => f.status === 'success' || f.status === 'warning').length === 0">
                 <td :colspan="displayCols.length + 2" class="p-8 text-center text-gray-400">暂无识别成功的发票数据</td>
              </tr>
            </tbody>
          </table>
        </div>
      </pane>

    </splitpanes>

    <ApiSetupModal v-if="showSettings" @close="showSettings = false" />
    <AboutModal v-if="showAbout" @close="showAbout = false" />
  </div>
</template>

<style>
/* @ts-ignore */
@import 'splitpanes/dist/splitpanes.css';

.splitpanes__splitter {
  background-color: #e5e7eb !important; 
  position: relative;
  transition: background-color 0.2s;
}
.splitpanes__splitter:hover {
  background-color: #3b82f6 !important; 
}
.splitpanes--vertical > .splitpanes__splitter {
  width: 4px !important;
  cursor: col-resize;
}
.splitpanes--horizontal > .splitpanes__splitter {
  height: 4px !important;
  cursor: row-resize;
}
</style>
<script setup lang="ts">
import { ref, computed } from 'vue'
import { useInvoiceStore } from '../store/invoice'
import axios from 'axios'

const store = useInvoiceStore()
const emit = defineEmits(['close'])

const provider = ref(store.config.provider || 'aliyun-ocr')
const showKey = ref(false)
const testStatus = ref<'idle'|'testing'|'success'|'error'>('idle')
const testMsg = ref('')

const keys = ref({
  aliyun: store.config.keys?.aliyun || '',
  zhipu: store.config.keys?.zhipu || '',
  openai: store.config.keys?.openai || '',
  custom: store.config.keys?.custom || ''
})

const customBaseUrl = ref(store.config.customBaseUrl || 'https://api.example.com/v1')
const customModel = ref(store.config.customModel || 'your-vision-model-name')

const aliyunAk = ref(store.config.aliyunAk || '')
const aliyunSk = ref(store.config.aliyunSk || '')

const providerConfigs: Record<string, { baseUrl: string, model: string }> = {
  'aliyun': { baseUrl: 'https://dashscope.aliyuncs.com/compatible-mode/v1', model: 'qwen-vl-plus' },
  'zhipu': { baseUrl: 'https://open.bigmodel.cn/api/paas/v4', model: 'glm-4v' },
  'openai': { baseUrl: 'https://api.openai.com/v1', model: 'gpt-4o' }
}

const currentKey = computed({
  get: () => keys.value[provider.value as keyof typeof keys.value] || '',
  set: (val) => { keys.value[provider.value as keyof typeof keys.value] = val }
})

const isKeyConfigured = computed(() => currentKey.value && currentKey.value.length > 5)
const isOcrConfigured = computed(() => aliyunAk.value.length > 5 && aliyunSk.value.length > 5)

const testApiConnection = async () => {
  testStatus.value = 'testing'
  testMsg.value = ''
  
  const formData = new FormData()

  try {
    if (provider.value === 'aliyun-ocr') {
      if (!aliyunAk.value.trim() || !aliyunSk.value.trim()) return alert('请先填写完整的 AK 和 SK')
      formData.append('provider', 'aliyun-ocr')
      formData.append('aliyun_ak', aliyunAk.value.trim())
      formData.append('aliyun_sk', aliyunSk.value.trim())
    } else {
      if (!currentKey.value.trim()) return alert('请先输入 Key')
      formData.append('provider', 'llm')
      formData.append('api_key', currentKey.value.trim())
      if (provider.value === 'custom') {
        if (!customBaseUrl.value.trim() || !customModel.value.trim()) return alert('请填写完整的自定义参数')
        formData.append('base_url', customBaseUrl.value.trim())
        formData.append('model', customModel.value.trim())
      } else {
        formData.append('base_url', providerConfigs[provider.value].baseUrl)
        formData.append('model', providerConfigs[provider.value].model)
      }
    }

    // >>> 端口改为 8888 <<<
    const res = await axios.post('http://127.0.0.1:8888/api/v1/test-api', formData)
    if (res.data.status === 'success') {
      testStatus.value = 'success'
      testMsg.value = res.data.message
    } else {
      testStatus.value = 'error'
      testMsg.value = res.data.message
    }
  } catch (e: any) {
    testStatus.value = 'error'
    testMsg.value = '后端服务未启动或网络异常'
  }
}

const saveConfig = () => {
  if (provider.value === 'aliyun-ocr') {
    if (!aliyunAk.value.trim() || !aliyunSk.value.trim()) return alert('⚠️ 选用 OCR 必须填写完整的 AK 和 SK！')
  } else if (provider.value === 'custom') {
    if (!currentKey.value.trim() || !customBaseUrl.value.trim() || !customModel.value.trim()) return alert('⚠️ 自定义模式必须填写完整！')
  } else {
    if (!currentKey.value.trim()) return alert('⚠️ 请输入当前大模型引擎的 API Key！')
  }

  const savePayload: any = {
    provider: provider.value,
    keys: keys.value,
    aliyunAk: aliyunAk.value.trim(),
    aliyunSk: aliyunSk.value.trim(),
    customBaseUrl: customBaseUrl.value.trim(),
    customModel: customModel.value.trim()
  }

  if (provider.value !== 'aliyun-ocr' && provider.value !== 'custom') {
    const currentConfig = providerConfigs[provider.value]
    savePayload.baseUrl = currentConfig.baseUrl
    savePayload.model = currentConfig.model
  } else if (provider.value === 'custom') {
    savePayload.baseUrl = customBaseUrl.value.trim()
    savePayload.model = customModel.value.trim()
  }

  store.saveConfig(savePayload)
  alert(`✅ 保存成功！已启用引擎: ${provider.value}`)
  emit('close')
}

const clearKey = () => {
  if (provider.value === 'aliyun-ocr') {
    aliyunAk.value = ''
    aliyunSk.value = ''
  } else {
    currentKey.value = ''
  }
}
</script>

<template>
  <div class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
    <div class="bg-white rounded-2xl w-[700px] shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
      
      <div class="px-6 py-4 border-b flex justify-between bg-gray-50 shrink-0">
        <h3 class="text-lg font-bold text-gray-800">⚙️ AI 识别引擎设置</h3>
        <button @click="$emit('close')" class="text-gray-400 hover:text-gray-700">✕</button>
      </div>
      
      <div class="p-6 overflow-y-auto space-y-6 flex-1">
        <div>
          <label class="block text-sm font-semibold mb-2">1. 选择核心识别引擎</label>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 mb-3">
             <label class="border rounded-xl p-3 cursor-pointer transition-colors" :class="provider === 'aliyun-ocr' ? 'border-purple-500 bg-purple-50 ring-1 ring-purple-500' : 'border-gray-200 hover:border-purple-300'">
              <input type="radio" v-model="provider" value="aliyun-ocr" class="hidden" @change="testStatus='idle'" />
              <div class="font-bold text-sm text-purple-800">✨ 阿里云增值税 OCR</div>
              <div class="text-[10px] text-gray-500 mt-1">商业级首选，100% 准确率</div>
            </label>
            <label class="border rounded-xl p-3 cursor-pointer transition-colors" :class="provider === 'aliyun' ? 'border-blue-500 bg-blue-50 ring-1 ring-blue-500' : 'border-gray-200 hover:border-blue-300'">
              <input type="radio" v-model="provider" value="aliyun" class="hidden" @change="testStatus='idle'" />
              <div class="font-bold text-sm text-blue-800">🤖 通义千问 (Qwen-VL)</div>
              <div class="text-[10px] text-gray-500 mt-1">国内最强免费额度大模型</div>
            </label>
            <label class="border rounded-xl p-3 cursor-pointer transition-colors" :class="provider === 'zhipu' ? 'border-indigo-500 bg-indigo-50 ring-1 ring-indigo-500' : 'border-gray-200 hover:border-indigo-300'">
              <input type="radio" v-model="provider" value="zhipu" class="hidden" @change="testStatus='idle'" />
              <div class="font-bold text-sm text-indigo-800">🤖 智谱清言 (GLM-4V)</div>
              <div class="text-[10px] text-gray-500 mt-1">高性价比视觉模型</div>
            </label>
            <label class="border rounded-xl p-3 cursor-pointer transition-colors" :class="provider === 'openai' ? 'border-emerald-500 bg-emerald-50 ring-1 ring-emerald-500' : 'border-gray-200 hover:border-emerald-300'">
              <input type="radio" v-model="provider" value="openai" class="hidden" @change="testStatus='idle'" />
              <div class="font-bold text-sm text-emerald-800">🤖 OpenAI GPT-4o</div>
              <div class="text-[10px] text-gray-500 mt-1">全球顶尖，支持外币发票</div>
            </label>
            <label class="border rounded-xl p-3 cursor-pointer transition-colors" :class="provider === 'custom' ? 'border-orange-500 bg-orange-50 ring-1 ring-orange-500' : 'border-gray-200 hover:border-orange-300'">
              <input type="radio" v-model="provider" value="custom" class="hidden" @change="testStatus='idle'" />
              <div class="font-bold text-sm text-orange-800">🛠️ 自定义第三方模型</div>
              <div class="text-[10px] text-gray-500 mt-1">兼容 OpenAI 格式的第三方接口</div>
            </label>
          </div>
        </div>

        <div class="space-y-4 border-t pt-4">
           <div class="bg-gray-50 p-3 rounded-lg text-sm text-gray-700 border border-gray-200 flex justify-between items-center">
             <span v-if="provider === 'aliyun-ocr'">前往 <a href="https://ram.console.aliyun.com/manage/ak" target="_blank" class="font-bold text-purple-600 hover:underline">阿里云 RAM</a> 获取 AK/SK。</span>
             <span v-if="provider === 'aliyun'">前往 <a href="https://dashscope.console.aliyun.com/api-key-management" target="_blank" class="font-bold text-blue-600 hover:underline">百炼控制台</a> 获取 API Key。</span>
             <span v-if="provider === 'zhipu'">前往 <a href="https://open.bigmodel.cn/usercenter/apikeys" target="_blank" class="font-bold text-indigo-600 hover:underline">智谱平台</a> 获取 API Key。</span>
             <span v-if="provider === 'openai'">前往 <a href="https://platform.openai.com/api-keys" target="_blank" class="font-bold text-emerald-600 hover:underline">OpenAI</a> 获取 API Key。</span>
             <span v-if="provider === 'custom'" class="text-orange-700 font-medium">⚠️ 自定义接口必须支持视觉(Vision)能力！</span>
             
             <button @click="testApiConnection" class="px-4 py-1.5 font-medium rounded shadow-sm text-white transition-colors" :class="provider === 'aliyun-ocr' ? 'bg-purple-600 hover:bg-purple-700' : (provider === 'custom' ? 'bg-orange-600 hover:bg-orange-700' : 'bg-blue-600 hover:bg-blue-700')">
               {{ testStatus === 'testing' ? '测试中...' : '🔌 测试连通性' }}
             </button>
           </div>
           
           <div v-if="testStatus !== 'idle'" class="p-2 rounded text-xs border" :class="testStatus === 'success' ? 'bg-green-50 text-green-700 border-green-200' : 'bg-red-50 text-red-700 border-red-200'">
             {{ testMsg }}
           </div>

           <!-- >>> 修复：强制增加 border, bg-gray-50，确保输入框清晰可见 <<< -->
           <div v-if="provider === 'aliyun-ocr'">
              <div class="flex justify-between items-end mb-2">
                 <label class="block text-xs font-semibold text-gray-700 mb-1">AccessKey ID</label>
                 <span v-if="isOcrConfigured" class="text-xs font-bold text-green-600">🟢 本地已存</span><span v-else class="text-xs font-bold text-red-500">🔴 未配置</span>
              </div>
              <input type="password" v-model="aliyunAk" class="w-full border border-gray-300 bg-gray-50 rounded-lg focus:bg-white focus:ring-2 focus:ring-purple-500 outline-none px-3 py-2 mb-3 transition-colors" />
              
              <label class="block text-xs font-semibold text-gray-700 mb-1">AccessKey Secret</label>
              <input type="password" v-model="aliyunSk" class="w-full border border-gray-300 bg-gray-50 rounded-lg focus:bg-white focus:ring-2 focus:ring-purple-500 outline-none px-3 py-2 transition-colors" />
           </div>

           <div v-else-if="provider === 'custom'" class="space-y-3 bg-orange-50/30 p-4 rounded-lg border border-orange-100">
              <div>
                <label class="block text-xs font-semibold text-gray-700 mb-1">接口地址 (Base URL)</label>
                <input type="text" v-model="customBaseUrl" class="w-full border border-gray-300 bg-gray-50 rounded-lg focus:bg-white focus:ring-2 focus:ring-orange-500 outline-none px-3 py-2 text-sm transition-colors" />
              </div>
              <div>
                <label class="block text-xs font-semibold text-gray-700 mb-1">模型名称 (Model Name)</label>
                <input type="text" v-model="customModel" class="w-full border border-gray-300 bg-gray-50 rounded-lg focus:bg-white focus:ring-2 focus:ring-orange-500 outline-none px-3 py-2 text-sm transition-colors" />
              </div>
              <div>
                <div class="flex justify-between items-end mb-1">
                   <label class="block text-xs font-semibold text-gray-700">API Key</label>
                   <span v-if="isKeyConfigured" class="text-xs font-bold text-green-600">🟢 本地已存</span><span v-else class="text-xs font-bold text-red-500">🔴 未配置</span>
                </div>
                <div class="relative">
                  <input :type="showKey ? 'text' : 'password'" v-model="currentKey" class="w-full border border-gray-300 bg-gray-50 rounded-lg focus:bg-white focus:ring-2 focus:ring-orange-500 outline-none px-3 py-2 pr-10 text-sm transition-colors" />
                  <button @click="showKey = !showKey" class="absolute right-3 top-2 text-gray-400">{{ showKey ? '👁️' : '🙈' }}</button>
                </div>
              </div>
           </div>

           <div v-else>
              <div class="flex justify-between items-end mb-1">
                 <label class="block text-xs font-semibold text-gray-700">API Key</label>
                 <span v-if="isKeyConfigured" class="text-xs font-bold text-green-600">🟢 本地已存</span><span v-else class="text-xs font-bold text-red-500">🔴 未配置</span>
              </div>
              <div class="flex space-x-2">
                <div class="relative flex-1">
                  <!-- >>> 修复：强制增加 border, bg-gray-50 <<< -->
                  <input :type="showKey ? 'text' : 'password'" v-model="currentKey" class="w-full border border-gray-300 bg-gray-50 rounded-lg focus:bg-white focus:ring-2 focus:ring-blue-500 outline-none px-3 py-2 pr-10 text-sm transition-colors" @keyup.enter="saveConfig"/>
                  <button @click="showKey = !showKey" class="absolute right-3 top-2 text-gray-400">{{ showKey ? '👁️' : '🙈' }}</button>
                </div>
                <button @click="clearKey" class="px-4 py-2 text-sm text-red-500 border border-red-200 rounded-lg hover:bg-red-50">清空</button>
              </div>
           </div>
        </div>
      </div>

      <div class="px-6 py-4 bg-gray-50 border-t flex justify-end space-x-3 shrink-0">
        <button @click="$emit('close')" class="px-5 py-2 text-sm text-gray-600 hover:bg-gray-200 rounded-lg">取消</button>
        <button @click="saveConfig" class="px-6 py-2 text-sm font-bold bg-blue-600 text-white rounded-lg hover:bg-blue-700">保存并启用</button>
      </div>
    </div>
  </div>
</template>
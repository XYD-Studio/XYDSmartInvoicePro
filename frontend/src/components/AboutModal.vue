<script setup lang="ts">
const emit = defineEmits(['close'])
</script>

<template>
  <div class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 transition-opacity">
    <div class="bg-white rounded-2xl w-[600px] shadow-2xl overflow-hidden transform transition-all flex flex-col max-h-[90vh]">
      
      <div class="px-6 py-6 bg-gradient-to-r from-gray-900 to-gray-800 flex justify-between items-center shrink-0">
        <a href="https://www.xy-d.top/" target="_blank" class="flex items-center space-x-3 group cursor-pointer transition-transform hover:scale-105">
          
          <div>
            <img src="../assets/logo.png" class=" h-10 rounded-lg shadow-lg" alt="Logo" />
          </div>
        </a>
        <button @click="$emit('close')" class="text-gray-400 hover:text-white transition-colors bg-gray-800 hover:bg-gray-700 w-8 h-8 rounded-full flex items-center justify-center">
          ✕
        </button>
      </div>
      
      <div class="p-6 overflow-y-auto space-y-6 bg-gray-50 flex-1">
        
        <div class="bg-white p-5 rounded-xl border shadow-sm">
          <h3 class="font-bold text-gray-800 mb-3 flex items-center">
            <span class="text-blue-500 mr-2">📘</span> 操作指南
          </h3>
          <ol class="list-decimal list-inside text-sm text-gray-600 space-y-2">
            <li><strong>配置引擎</strong>：首次使用，请点击【引擎设置】配置识别接口。</li>
            <li><strong>导入票据</strong>：将发票原件（PDF或照片）拖入左侧列表。</li>
            <li><strong>批量识别</strong>：点击【开始识别全部】，AI将自动提取关键信息。</li>
            <li><strong>快速核对</strong>：点击列表项，在右侧表单进行核对，支持键盘 <kbd class="bg-gray-100 border rounded px-1">↑</kbd> <kbd class="bg-gray-100 border rounded px-1">↓</kbd> 极速切换。</li>
            <li><strong>完美导出</strong>：核对后，点击底部按钮导出排版精美的 Excel 报销清单。</li>
          </ol>
        </div>

        <div class="bg-blue-50 p-5 rounded-xl border border-blue-100">
          <h3 class="font-bold text-blue-800 mb-2 flex items-center">
            <span class="mr-2">✨</span> 关于本项目
          </h3>
          <p class="text-sm text-blue-700 leading-relaxed">
            本项目由 <strong>玄宇绘世设计工作室</strong> 开源发布。专为企业员工报销清单整理、高新项目申报材料归档等场景打造的效率神器。欢迎访问官网了解我们的 UI/UX 设计及技术服务。
          </p>
        </div>

        <div class="bg-gray-100 p-5 rounded-xl border border-gray-200">
          <h3 class="font-bold text-gray-700 mb-2 flex items-center">
            <span class="mr-2">⚖️</span> 免责声明
          </h3>
          <div class="text-xs text-gray-500 space-y-2 leading-relaxed">
            <p>1. <strong>数据隐私</strong>：本软件为本地化运行，您的发票文件及密钥仅在您的本地及官方云端大模型间传输，工作室不会获取您的任何数据。</p>
            <p>2. <strong>使用边界</strong>：本软件仅作为提升普通办公效率的辅助工具，<strong>非专业核心财务记账软件</strong>。AI 提取可能存在误差，请务必进行人工复核。</p>
            <p>3. <strong>法律责任</strong>：对于因使用本辅助工具而导致的任何直接或间接损失，玄宇绘世设计工作室不承担任何法律责任。</p>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>
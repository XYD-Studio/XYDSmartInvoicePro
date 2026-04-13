import { defineStore } from 'pinia'

const getLocalConfig = () => {
  try {
    const saved = localStorage.getItem('invoice_config')
    if (saved) return JSON.parse(saved)
  } catch (e) {}
  return {}
}

const savedConfig = getLocalConfig()

export const useInvoiceStore = defineStore('invoice', {
  state: () => ({
    config: {
      provider: savedConfig.provider || 'aliyun-ocr',
      keys: savedConfig.keys || { aliyun: '', zhipu: '', openai: '', custom: '' },
      aliyunAk: savedConfig.aliyunAk || '',
      aliyunSk: savedConfig.aliyunSk || '',
      baseUrl: savedConfig.baseUrl || 'https://dashscope.aliyuncs.com/compatible-mode/v1',
      model: savedConfig.model || 'qwen-vl-plus',
      customBaseUrl: savedConfig.customBaseUrl || '',
      customModel: savedConfig.customModel || '',
      customColumnOrder: savedConfig.customColumnOrder || [],
      // >>> 新增：记忆用户删除了哪些列 <<<
      hiddenCols: savedConfig.hiddenCols || [] 
    },
    processedDataList: [] as Array<Record<string, any>>,
    invoiceFingerprints: new Set<string>()
  }),
  actions: {
    saveConfig(newConfig: any) {
      this.config = { ...this.config, ...newConfig }
      localStorage.setItem('invoice_config', JSON.stringify(this.config))
    },
    checkDuplicate(data: Record<string, any>): boolean {
      const number = data['发票号码'] || data['发票代码'] || '';
      const amount = data['价税合计'] || data['总金额'] || '';
      const date = data['开票日期'] || '';
      const fingerprint = number ? `NUM_${number}` : `COMP_${date}_${amount}`;
      return this.invoiceFingerprints.has(fingerprint) && fingerprint !== 'COMP__';
    },
    addProcessedData(data: Record<string, any>) {
      this.processedDataList.push(data)
      const number = data['发票号码'] || data['发票代码'] || '';
      const amount = data['价税合计'] || data['总金额'] || '';
      const date = data['开票日期'] || '';
      const fingerprint = number ? `NUM_${number}` : `COMP_${date}_${amount}`;
      if (fingerprint !== 'COMP__') this.invoiceFingerprints.add(fingerprint);
    }
  }
})
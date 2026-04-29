import * as ExcelJSModule from 'exceljs'

// 将二进制 buffer 转为 Base64 字符串的辅助函数
const arrayBufferToBase64 = (buffer: ArrayBuffer) => {
  let binary = '';
  const bytes = new Uint8Array(buffer);
  const len = bytes.byteLength;
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return window.btoa(binary);
}

export const exportDataToExcel = async (dataList: Array<Record<string, any>>, fileName: string = '票据整理台账.xlsx') => {
  try {
    if (dataList.length === 0) {
      alert('暂无数据可导出')
      return
    }

    const ExcelJS = (ExcelJSModule as any).default || ExcelJSModule
    const workbook = new ExcelJS.Workbook()
    const worksheet = workbook.addWorksheet('发票明细')
    
    const headers = Object.keys(dataList[0])
    const columns = headers.map((header: string) => {
      let maxLength = header.replace(/[\u0391-\uFFE5]/g, "aa").length
      dataList.forEach(row => {
        const cellValue = row[header] ? String(row[header]) : ''
        let cellLength = cellValue.replace(/[\u0391-\uFFE5]/g, "aa").length
        if (cellLength > 40) cellLength = 40 
        if (cellLength > maxLength) maxLength = cellLength
      })
      return { header: header, key: header, width: maxLength + 4 }
    })
    worksheet.columns = columns

    worksheet.getRow(1).eachCell((cell: any) => {
      cell.font = { bold: true, color: { argb: 'FF333333' } }
      cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFF3F4F6' } }
      cell.alignment = { vertical: 'middle', horizontal: 'center' }
      cell.border = {
        top: { style: 'thin' }, left: { style: 'thin' },
        bottom: { style: 'thin' }, right: { style: 'thin' }
      }
    })

    dataList.forEach((data) => {
      const rowData: any = {}
      Object.keys(data).forEach(key => {
        let val = data[key]
        const isMoneyField = ['总金额', '税额', '价税合计'].includes(key) || (key.includes('金额') && !key.includes('号码'))
        
        if (isMoneyField) {
          if (typeof val === 'string') {
            const cleanStr = val.replace(/[^\d.-]/g, '')
            if (cleanStr && !isNaN(Number(cleanStr))) val = Number(cleanStr) 
          }
        } else {
          if (val !== null && val !== undefined) val = String(val)
        }
        rowData[key] = val
      })

      const row = worksheet.addRow(rowData)
      row.eachCell((cell: any) => {
        cell.alignment = { wrapText: true, vertical: 'middle', horizontal: 'left' }
        cell.border = {
          top: { style: 'thin', color: { argb: 'FFEEEEEE' } },
          left: { style: 'thin', color: { argb: 'FFEEEEEE' } },
          bottom: { style: 'thin', color: { argb: 'FFEEEEEE' } },
          right: { style: 'thin', color: { argb: 'FFEEEEEE' } }
        }
        if (typeof cell.value === 'number') {
          cell.numFmt = '#,##0.00'
        } else if (typeof cell.value === 'string') {
          cell.numFmt = '@'
        }
      })
    })

    const buffer = await workbook.xlsx.writeBuffer()
    
    // >>> 核心改造：双端智能分发 <<<
    // 检查是否在桌面版 exe 环境中运行 (pywebview 会给 window 注入专属变量)
    if ((window as any).pywebview) {
        
        // 在桌面端：将 Excel 转为 base64 发给后端，唤起原生保存对话框
        const b64Data = arrayBufferToBase64(buffer)
        
        const res = await fetch('http://127.0.0.1:8888/api/v1/save-excel', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ filename: fileName, b64_data: b64Data })
        });
        
        const resData = await res.json();
        
        if (resData.status === 'success') {
            alert(`✅ 导出成功！\n文件已保存至：\n${resData.path}`);
        } else if (resData.status === 'error') {
            alert(`❌ 保存出错：${resData.message}`);
        }
        // 如果 status === 'cancelled' (用户点击了取消)，则静默关闭不提示
        
    } else {
        // 在纯 Web 浏览器中：保留原本的触发下载逻辑
        const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
        const link = document.createElement('a')
        link.href = URL.createObjectURL(blob)
        link.download = fileName
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        alert('✅ 导出成功！\n\n如果未弹出保存框，请去您电脑的【下载 (Downloads)】文件夹中查看。')
    }

  } catch (error: any) {
    console.error("导出Excel失败:", error)
    alert(`❌ 导出失败，请联系开发者：\n${error.message}`)
  }
}

export const generateSmartFileName = (data: Record<string, any>, originalExt: string): string => {
  const date = (data['开票日期'] || '未知日期').replace(/[:/\\]/g, '-')
  const type = data['发票类型'] || '票据'
  const amount = data['价税合计'] || data['总金额'] || '未知金额'
  return `${date}_${type}_${amount}.${originalExt}`
}
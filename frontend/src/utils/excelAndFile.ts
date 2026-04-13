import ExcelJS from 'exceljs'

export const exportDataToExcel = async (dataList: Array<Record<string, any>>, fileName: string = '票据整理台账.xlsx') => {
  if (dataList.length === 0) {
    alert('暂无数据可导出')
    return
  }

  const workbook = new ExcelJS.Workbook()
  const worksheet = workbook.addWorksheet('发票明细')
  const headers = Object.keys(dataList[0])
  
  const columns = headers.map(header => {
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

  worksheet.getRow(1).eachCell((cell) => {
    cell.font = { bold: true, color: { argb: 'FF333333' } }
    cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFF3F4F6' } }
    cell.alignment = { vertical: 'middle', horizontal: 'center' }
    cell.border = {
      top: { style: 'thin' }, left: { style: 'thin' },
      bottom: { style: 'thin' }, right: { style: 'thin' }
    }
  })

  // >>> 核心修复：在这里洗数据，把文本转为真实的数字型 <<<
  dataList.forEach((data) => {
    const rowData: any = {}
    Object.keys(data).forEach(key => {
      let val = data[key]
      // 只要表头带有'金额'、'税额'、'合计'，就尝试转数字
      if (['总金额', '税额', '价税合计'].includes(key) || key.includes('金额') || key.includes('税')) {
        if (typeof val === 'string') {
          // 用正则过滤掉货币符号、逗号等，只留数字和负号和小数点
          const cleanStr = val.replace(/[^\d.-]/g, '')
          if (cleanStr && !isNaN(Number(cleanStr))) {
            val = Number(cleanStr) // 强制转数值型
          }
        }
      }
      rowData[key] = val
    })

    const row = worksheet.addRow(rowData)
    row.eachCell((cell, colNumber) => {
      cell.alignment = { wrapText: true, vertical: 'middle', horizontal: 'left' }
      cell.border = {
        top: { style: 'thin', color: { argb: 'FFEEEEEE' } },
        left: { style: 'thin', color: { argb: 'FFEEEEEE' } },
        bottom: { style: 'thin', color: { argb: 'FFEEEEEE' } },
        right: { style: 'thin', color: { argb: 'FFEEEEEE' } }
      }
      // 如果单元格变成了数字型，自动加千位分隔符样式（方便查看）
      if (typeof cell.value === 'number') {
        cell.numFmt = '#,##0.00'
      }
    })
  })

  const buffer = await workbook.xlsx.writeBuffer()
  const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = fileName
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

export const generateSmartFileName = (data: Record<string, any>, originalExt: string): string => {
  const date = (data['开票日期'] || '未知日期').replace(/[:/\\]/g, '-')
  const type = data['发票类型'] || '票据'
  const amount = data['价税合计'] || data['总金额'] || '未知金额'
  return `${date}_${type}_${amount}.${originalExt}`
}
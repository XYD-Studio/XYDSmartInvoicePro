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

  dataList.forEach((data) => {
    const rowData: any = {}
    Object.keys(data).forEach(key => {
      let val = data[key]
      
      // >>> 核心修复：极度严格的白名单。只有明确是“钱”的字段才转数字 <<<
      // 坚决避开“发票号码”、“纳税人识别号”、“电话号码”等字段
      const isMoneyField = ['总金额', '税额', '价税合计'].includes(key) || (key.includes('金额') && !key.includes('号码'))
      
      if (isMoneyField) {
        if (typeof val === 'string') {
          const cleanStr = val.replace(/[^\d.-]/g, '')
          if (cleanStr && !isNaN(Number(cleanStr))) {
            val = Number(cleanStr) // 转换为真实的纯数字，支持后续 Excel 求和
          }
        }
      } else {
        // 其他所有字段（包含纳税人识别号、发票号码），全部强制转为字符串！
        // 这样即使数字再长，Excel 也不会将其转为科学计数法
        if (val !== null && val !== undefined) {
          val = String(val)
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
      // 如果单元格变成了真实的数字（钱），加上千位分隔符和两位小数
      if (typeof cell.value === 'number') {
        cell.numFmt = '#,##0.00'
      } else if (typeof cell.value === 'string') {
        // 强制告诉 Excel 这是一个文本，不要自作多情转格式
        cell.numFmt = '@'
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
declare module 'splitpanes';

// 新增下面这段，告诉 TypeScript 遇到所有以 .css 结尾的导入都不要报错
declare module '*.css' {
  const content: { [className: string]: string };
  export default content;
}
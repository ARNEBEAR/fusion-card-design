#!/usr/bin/env node
/**
 * 批量把 index.html 中的关键视觉单元截成高清 PNG。
 * 用法： node screenshot.js
 * 前提： python3 -m http.server 5181 --bind 127.0.0.1 已在跑
 *
 * 输出到 ./exports/
 */
const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const URL = 'http://127.0.0.1:5181/index.html';
const OUT = path.join(__dirname, 'exports');
if (!fs.existsSync(OUT)) fs.mkdirSync(OUT, { recursive: true });

// 截图任务清单
// element 表示通过 css 选择器选定一个 DOM 节点，截这个节点的范围
// region 表示用 viewport + scroll 截一个固定矩形（用于跨多个元素的整体画面）
const TASKS = [
  // ---------- 策略 1-4 phone（第 4 部分） ----------
  { name: 'stage-1-phone', element: '#stage-1 .phone', label: '策略 1 · 重交易一体卡（phone 原型）' },
  { name: 'stage-2-phone', element: '#stage-2 .phone', label: '策略 2 · 信息折叠一体卡（phone 原型）' },
  { name: 'stage-3-phone', element: '#stage-3 .phone', label: '策略 3 · 模块拆分排版（phone 原型）' },
  { name: 'stage-4-phone', element: '#stage-4 .phone', label: '策略 4 · 纯内容挂载（phone 原型）' },

  // ---------- 策略 1-4 完整一行（含右侧 phone + 左侧文字） ----------
  { name: 'stage-1-full', element: '#stage-1', label: '策略 1 · 完整介绍区（含文字）' },
  { name: 'stage-2-full', element: '#stage-2', label: '策略 2 · 完整介绍区' },
  { name: 'stage-3-full', element: '#stage-3', label: '策略 3 · 完整介绍区' },
  { name: 'stage-4-full', element: '#stage-4', label: '策略 4 · 完整介绍区' },

  // ---------- 第 1 部分：判断动线 ----------
  { name: 'sec01-flow', element: '#sec-framework', label: '第 1 部分 · 判断动线（识别→了解→转化）' },

  // ---------- 第 2 部分：原则三卡 ----------
  { name: 'sec02-principle', element: '#sec-principle', label: '第 2 部分 · 结构解耦原则' },

  // ---------- 第 3 部分：行业 + 推理 ----------
  { name: 'sec03-industry', element: '#sec-industry', label: '第 3 部分 · 行业观察 + TT 约束 + 4 方向' },

  // ---------- 第 4 部分概览 ----------
  { name: 'sec04-overview', element: '#sec-strategies > .stages', label: '第 4 部分 · 4 策略总览卡' },

  // ---------- 第 5 部分：光谱 + 4 列对比 + 矩阵 ----------
  { name: 'sec05-spectrum-bar', element: '#sec-spectrum > div:nth-of-type(2)', label: '第 5 部分 · 光谱条' },
  { name: 'sec05-cards', element: '#sec-spectrum > div:nth-of-type(3)', label: '第 5 部分 · 4 列纯文字对比卡' },
  { name: 'sec05-matrix', element: '#sec-spectrum > div:last-child', label: '第 5 部分 · 3 轴差异矩阵' },
  { name: 'sec05-full', element: '#sec-spectrum', label: '第 5 部分 · 整段（光谱 + 对比 + 矩阵）' },

  // ---------- 第 6 部分：可组合性 ----------
  { name: 'sec06-composability', element: '#sec-composability', label: '第 6 部分 · 可组合性' },

  // ---------- 顶部 Story Rail ----------
  { name: 'top-story-rail', element: '.story-rail', label: '顶部 · 推演主线 5 站' },
];

async function run() {
  console.log('[screenshot] launching browser...');
  const browser = await puppeteer.launch({
    headless: 'new',
    defaultViewport: { width: 1440, height: 900, deviceScaleFactor: 2 },
  });
  const page = await browser.newPage();

  console.log(`[screenshot] loading ${URL}`);
  await page.goto(URL, { waitUntil: 'networkidle0', timeout: 30000 });

  // 等动画/字体稳定
  await new Promise((r) => setTimeout(r, 800));

  for (const task of TASKS) {
    try {
      const handle = await page.$(task.element);
      if (!handle) {
        console.warn(`[skip] ${task.name}: element not found (${task.element})`);
        continue;
      }
      // 滚到可视区，避免懒加载/动画错位
      await handle.scrollIntoView();
      await new Promise((r) => setTimeout(r, 200));

      const out = path.join(OUT, `${task.name}.png`);
      await handle.screenshot({ path: out, omitBackground: false });
      console.log(`[ok] ${task.name} -> ${out}`);
    } catch (e) {
      console.error(`[err] ${task.name}:`, e.message);
    }
  }

  await browser.close();
  console.log('\n[done] all screenshots written to ./exports/');
}

run().catch((e) => {
  console.error(e);
  process.exit(1);
});

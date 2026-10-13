# AI教育与灵感周刊 · 第002期行业增补

内容截止：2026-10-12 09:00 Asia/Shanghai。本次为第002期行业增补发布；站点由 main 分支 docs/ 提供。

- 第002期：12条全球教育观察（7条本周发布、5条本周活动日程），6条深圳专题（1条本周、5条历史背景或旧项目追踪），10位公众人物具体动态。
- Dan Fitzpatrick为001期旧文补核全文，不是新发表。活动日程不代表实际完成或成效。
- 创意新增12项（1项本周进展、11项历史灵感），去重累计27项。
- 第002期7位人物有真实来源头像、3位明确缺图；12个新增创意中11个嵌入来源效果图，1个403保留原作链接。媒体为来源署名低清图，公开复用许可未确认。保留原期图片署名与权利状态，不宣称已获得全部转载授权。
- 001原始JSON、原深圳数据与历史人物档案不变。snapshots/001_original_20261007.html是原始整页快照。

## 构建与阅读

运行 python3 build_release.py；输出docs/index.html，也可直接打开它离线阅读。所有样式、图片和脚本内嵌，无登录、分析追踪或外部运行时依赖。

默认002，六页：本期预览、AI教育前沿、深圳专题、行业动态、公众人物言论、更新须知。期号下拉、上一期、下一期、回最新均保留。右上全部创意为独立累计库，回到历史期刊原页面。

## 文件

src/data/issues/001.json与002.json：各期快照；src/data/shenzhen/：每期深圳证据；src/data/ideas.json：累计库；people.json：按期人物档案；editorial.json：建议、追踪与修订。evidence/保留本轮研究资料。

## 检查

python3 src/validate.py
python3 tests/check_static.py
node tests/test_core.js
node tests/test_dom.js

生产数据验证与静态、核心逻辑、模拟DOM检查已通过。本次已准备桌面与手机宽度 Chromium 回归脚本，但环境 socket 权限阻止浏览器启动，视觉/触控及跨浏览器验收未完成，详见QA_SUMMARY.md。测试不等于对所有外部工具的实测。

## 发布限制

本次发布保留既有媒体署名与权利状态。公开可访问不等于获得第三方转载或再分发许可。技术部署步骤见 DEPLOYMENT.md。

## 002 行业栏目增补

增加13个国内外企业、机构与课程品牌代表样本，商业模式与财务口径分别说明。教育前沿保留12条原有内容，按三类分组。行业数据见 src/data/industry/002.json，完整研究依据见 evidence/industry_*.json。青禾致知课程原帖已核验，其法律主体、统一课时、价格及经营数据仍待确认。

保留 snapshots/002_published_20261012.html 与 .json，前者与 GitHub d3142761 已发布文档字节完全一致。001快照与全部既有媒体不变。保留已发布版本用于历史核对。

额外检查：python3 tests/check_industry.py；node tests/test_browser.js（需 Playwright 与 Chromium）。

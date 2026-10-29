# AI教育与灵感周刊 · 第004期

10月26日当周补刊，2026-10-29补发。观察窗口2026-10-19至2026-10-28，活动日程不等于完成情况；硬件文档核验不等于新品发布。

- 12条教育观察、10位人物的具名观点／署名说明／课例实践（同源报道不计作多次独立事件）。
- 3条深圳动态：龙华课例、深大采购、宝安公益培训。
- 行业保留18个历史观察对象，明确未重新核验；新增3个观察样本。
- 创意库累计41项，本期新增3项AI＋硬件方案：StackChan科学追问、AtomS3R语音实验记录、PaperS3电子墨水学习卡。课程改造未实测。
- 001—003期源数据与原始快照保留。

公开网页图片使用同站assets目录；构建时同时复制原始图片。

## 构建与检查

`python build_release.py` 生成 `docs/index.html`；GitHub Pages继续使用main分支docs目录。

`python src/validate.py`、`python tests/check_static.py`、`node tests/test_core.js`、`node tests/test_dom.js`。

详细核验见 `tests/QA_ISSUE004.md`。每个条目附来源与日期；旧条目的原核验日期不随新一期自动更新。

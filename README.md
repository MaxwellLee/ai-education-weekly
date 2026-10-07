# AI 教育与灵感周刊

静态候选源包，尚未部署。保留第001期（2026-10-06）的13条教育、13位人物、15个累计创意。保留13张人物肖像与14张原作效果图，全部附真实来源与署名。许可已确认与未确认的情况分别记录，详见 THIRD_PARTY_NOTICES.md。

## 构建

```sh
python3 build_release.py
```

构建仅需Python 3标准库；生成的docs/index.html包含正文、样式与脚本，阅读无外部运行时依赖。第三方来源只在点击时打开。无登录、分析追踪、外部字体或后端。

## 阅读结构

默认进入最新期的本期预览。五页为本期预览、AI教育前沿、公众人物言论、深圳专题、更新须知。期号选择、上一期、下一期、回到最新一期按钮保留，只有首期时相邻按钮禁用。右上角“全部创意”打开独立累计库，返回时恢复原期号与页面。筛选不删除底层条目。

## 维护与测试

- src/data/issues.json：真实期刊清单
- src/data/issues/001.json：独立期刊内容，历史摘要仍保留
- src/data/people.json：人物背景、成果与图片显示条件
- src/data/ideas.json：去重累计创意库
- src/data/editorial.json：尝试建议、变化基线、修订和事实更正
- src/data/schema.json：JSON数据约束
- src/build.py、src/render_helpers.py：构建和转义渲染
- src/core.js、src/interactions.js、src/styles.css：路由、筛选与响应式布局
- docs/：唯一Pages发布目录

追加真实期刊并更新latestIssueId；不伪造往期，不把教学建议写成已验证效果。媒体需保留可靠来源、作者或提供者、许可核验状态及实际处理说明；不能把公开可见或本站收录当作已获授权。

```sh
python3 src/validate.py
python3 src/build.py
python3 tests/check_static.py
node tests/test_core.js
node tests/test_dom.js
```

静态验证另需已有Pillow和lxml；完整Schema验证可使用jsonschema。浏览器实测另列，不能以DOM模拟代替。

## 发布

建议在独立ai-education-weekly仓库的main分支保存此包，Pages选择“Deploy from a branch → main → /docs”。docs/.nojekyll避免Jekyll处理。此包不包含自动发布工作流、凭据或自定义域名设置。发布步骤与限制见DEPLOYMENT.md。

此包没有为全部内容指定一个开放许可证；第三方素材的权利不因收录而转移，见逐图说明。

## 深圳专题（2026-10-07审阅增补）

在核对远端main全部文件后增补；基准提交cdba8992ab54c5234c63f69c63cb81406fe5b972。本次未提交、推送或部署。

- 每期专题：src/data/shenzhen/<期号>.json，渲染器src/shenzhen.py。
- current按该期观察窗口内原文发布日期判断，发生时间独立记录；baseline必须早于窗口。无新证据不冒充新进展。
- 每条必填区、机构、人物/企业、类型、阶段、发布日期、事件日期、摘要、参考价值、证据边界与原始来源。源数据验证由src/validate.py执行。
- 新期建新文件，不覆盖旧期；缺失数据时栏目显示未核验提示，不搬用旧闻。全球栏目、人物栏目与累计创意库继续独立更新。
- 兼容说明：本可维护源包使用与当前GitHub仓库一致的src/、docs/、tests/结构；构建入口为python3 build_release.py。

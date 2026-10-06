# 发布准备与验收

核对日期：2026-10-06。当前仅准备本地候选源包，没有创建仓库、提交、推送或部署。

## 推荐方式

使用独立仓库ai-education-weekly，源代码和已构建docs/index.html均放main分支。Settings → Pages → Source选择Deploy from a branch，再选择main与/docs。docs/.nojekyll禁用默认Jekyll处理。没有必要为当前纯静态构建增加自定义GitHub Actions文件。

官方依据：[配置Pages发布源](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)。该方式允许任意现有分支的根目录或/docs，保存后该目录的更新会触发发布，需要仓库管理员或维护者权限。

## 尚需完成

1. 核实仓库所属账户、仓库名称和可见性，以及实际写入权限。
2. 核对27张图像的出处、署名和许可核验状态与实际展示一致；图片许可未确认状态不会因收录而变为已授权。
3. 取得可用的真实浏览器预览并验收桌面和手机布局；当前静态/DOM验证不等于浏览器验收。
4. 确认提交实际存在于目标远端，Pages的部署对应这个提交，随后打开GitHub返回的真实站点地址复核，不猜测上线URL。

## 平台条件

GitHub Free可用于公开仓库的Pages；私有仓库需要支持的付费计划。Pages网站通常公开，即使源仓库私有，也不能将私有仓库等同于私有网站。入口index.html需在发布目录顶层。更新发布可能需约10分钟，完成以实际部署与站点验证为准。

官方依据：[创建GitHub Pages站点](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site)。

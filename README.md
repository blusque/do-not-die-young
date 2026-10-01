# 高性价比人生指南 · 阅读页与 PDF

把开源书《高性价比人生指南》渲染成一个**自包含的单文件网页**，并每天自动产出
**PDF 电子书**。网页不依赖任何外部资源、可离线阅读；PDF 可从 Release 下载。

本仓库：<https://github.com/blusque/do-not-die-young>

## 内容来源

原书由 [eternity4719/HowToLiveBetter](https://github.com/eternity4719/HowToLiveBetter)
维护（Unlicense，公有领域），按「性价比」排序，每条写清花掉什么、换回什么、证据多硬，
只引期刊论文和官方文件。

本仓库不是原书的 fork，也不改动原书内容，只做两件事：

1. 把原书 32 节正文渲染成单文件网页 `index.html`；
2. 把该网页转成 PDF 电子书。

## 生成物

| 文件 | 说明 |
| --- | --- |
| `index.html` | 自包含阅读页，零外部依赖，可离线打开 |
| `dist/how-to-live-better-full.pdf` | PDF，展开每条建议的「来源」文献（约 610 页） |
| `dist/how-to-live-better-simple.pdf` | PDF，来源只留「来源（N 条文献）」一行（约 490 页） |

PDF 由本机无头 Chrome 生成，不提交进仓库（已写入 `.gitignore`）。

## 页面特性

- **零外部资源**：没有 CDN、没有字体外链、不 fetch 任何数据，断网也能读
- 逐条卡片：建议标题、证据等级（A/B/C）、性价比档、成本标签
- **「说人话」高亮块**——原书专把统计量翻成日常说法的栏目，页面上做得最显眼
- 全站关键词搜索（结果高亮）、只看 A 级、只看说人话
- 左侧目录带性价比色点，滚动联动
- 手机端：搜索框独占一行、顶栏向下滚动后自动收成一行、回到顶部按钮
- 明暗主题切换，支持直接打印

## 本地使用

不用构建，双击 `index.html` 即可。

## 重新生成网页

```bash
# 先有一份上游仓库的本地克隆
git clone --depth 1 https://github.com/eternity4719/HowToLiveBetter.git /tmp/upstream

# 全部 32 节
python build.py all -o index.html --repo /tmp/upstream

# 只做某几节
python build.py 1 2 16 --repo /tmp/upstream
```

源目录也可用环境变量 `HLTB_REPO` 指定。

统计口径（条目数、A/B/C 分级、性价比三档）与上游 `tools/sync-stats.ps1`
和 `index.html` 保持一致，生成结果可与上游徽章逐项对照。

## 生成 PDF

`make_pdf.py` 用无头 Chrome（Chrome / Edge 均可）把 `index.html` 渲染成两个版本：

```bash
python make_pdf.py index.html -o dist
# 产物：dist/how-to-live-better-full.pdf
#       dist/how-to-live-better-simple.pdf
```

| 参数 | 说明 |
| --- | --- |
| `-o, --out` | 输出目录（默认 `dist`） |
| `--paper` | 纸张尺寸，默认 `A4`，也可传 `Letter` 或 `default` |
| `--chrome` | 指定浏览器可执行文件；也可用环境变量 `CHROME_PATH` |
| `--prefix` | 输出文件名前缀（默认 `how-to-live-better`） |

- **full**：把每个「来源」折叠块展开，文献完整。
- **simple**：来源保持收起，只留「来源（N 条文献）」一行，更精简。

## 自动更新

仓库有两个定时工作流，都可以到 Actions 页面手动触发：

| 工作流 | 时间（北京时间） | 做什么 |
| --- | --- | --- |
| `.github/workflows/rebuild.yml` | 每天 06:00 | 拉上游重新生成 `index.html`，有变化才提交 |
| `.github/workflows/pdf.yml` | 每天 07:00 | 拉上游 → 生成 simple / full 两版 PDF → 发布到 Release |

PDF 发布到滚动 Release，tag 固定为 `pdf-latest`，每天覆盖更新，链接长期不变：

**下载：** <https://github.com/blusque/do-not-die-young/releases/tag/pdf-latest>

> 定时任务在云端运行，产物发到 Release 和 Actions artifact，**不会写到你本地磁盘**。
> 想在本地拿到 PDF，请按上面的「生成 PDF」手动跑一次。

## 授权

原书内容为 Unlicense（公有领域）。本仓库的构建脚本同样不作任何权利保留。

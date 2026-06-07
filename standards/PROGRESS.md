# PROGRESS · bank-marketing-predictor 〔本项目活记忆 · 状态机〕

> **作用**：这是项目的"存档点"。任意 AI、任意重启会话，读它即可知道当前做到哪、下一步做什么、踩过什么坑。
> **更新时机**：每完成一个有意义步骤、每次会话结束前。
> **格式要求**：时间倒序，最新在上；短、准、可接力。

---

## 当前状态 (最后更新: 2026-06-07 · by AI)

- **阶段**：`初始化 / 第①步完成，等待 Secrets 配置`
- **对应六步流程**：第①步（建仓 done，Secrets 待配置）
- **上一步完成**：`gh repo create` 创建仓库 `huan-w123/bank-marketing-predictor`，main 分支已推送初始提交。
- **下一步 (TODO 第一条)**：人类配置 GitHub Secrets（SSH_PRIVATE_KEY / SSH_HOST / SSH_USER）。
- **阻塞项**：✋ 确认门 1 — 等待人类确认「Secrets 已配置」。

---

## 待办清单 (TODO，按优先级)

- [x] **确认门 ✋1-a**：人类确认 `00-project-context.md` 与 `01-requirements.md`
- [x] ① 建仓：`gh repo create` 创建 `bank-marketing-predictor`，初始化 `.gitignore`、`README.md`
- [ ] **✋ 确认门 1-b**：人类配置 Secrets（SSH_PRIVATE_KEY / SSH_HOST / SSH_USER）→ `gh secret list` 验证
- [ ] ② 开 feature 分支 `feature/1-project-init` 从 main
- [ ] ③ 模块 1 — 项目骨架：创建目录结构、`requirements.txt`、`requirements-dev.txt`、`Dockerfile`、CI/CD workflows
- [ ] ③ 模块 2 — 数据加载与校验：`src/analysis.py` 核心函数 + `tests/test_analysis.py`
- [ ] ③ 模块 3 — 数据分析页面（US-2）：Streamlit 可视化页面 + 测试
- [ ] ③ 模块 4 — 离线模型训练（US-3）：`src/train.py` + `tests/test_train.py`
- [ ] ③ 模块 5 — 在线预测页面（US-4）：`src/predict.py` + Streamlit 预测 UI + 测试
- [ ] ④ 本地 CI 自检：ruff + pytest --cov + 覆盖率 >= 80%
- [ ] ⑤ 推送分支 + 创建 PR + 盯 CI（含 docker build）
- [ ] ⑥ 人工审核合并 → CD 自动部署 → 健康检查验证端口 8004

---

## 关键决策记录 (ADR)

| 日期 | 决策 | 理由 |
|---|---|---|
| 2026-06-07 | 采用 Streamlit 而非 Flask/FastAPI | 两个功能均为数据看板 + ML 推理交互，Streamlit 无需前后端分离，满足需求且开发效率高 |
| 2026-06-07 | 模型基线选 LogisticRegression | 银行营销数据特征以结构化表格为主，线性模型可解释性好，AUC 0.80 合理可达成；后续可升级 RF/XGB |
| 2026-06-07 | 数据与模型产物不进 Git | 数据可能含敏感客户信息；模型文件体积大且可复现（代码 + 数据即可重建） |
| 2026-06-07 | 本地不强制 Docker | 遵循 `05-cicd-standards.md` 标准：本地只跑代码质量门禁，Docker 构建交给 CI runner |

---

## 已知坑 (GOTCHAS)

- 暂无（项目尚未开始开发）。

---

## 里程碑 (DONE)

- [x] 2026-06-07 · 需求文档完成：`00-project-context.md`、`01-requirements.md`（4 条用户故事）、`PROGRESS.md` 初始化
- [x] 2026-06-07 · 建仓完成：`huan-w123/bank-marketing-predictor`，main 分支含 15 个文件（standards + .gitignore + README）

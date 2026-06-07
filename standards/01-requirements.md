# 01 · 需求 / 活 PRD 〔本项目活记忆 · AI 维护〕

> **作用**：这是本项目唯一的需求文档。所有新功能、缺陷、技术债都追加到这里，不要另起多个 PRD 文件。
> **更新时机**：每次有新需求、需求变更、验收标准变化时更新。

---

## 1. 需求来源

| 类型 | 来源 | 进入方式 |
|---|---|---|
| 功能需求 Feature | 用户 / 老师 / 产品 / 客户 | 写成用户故事 |
| 缺陷 Bug | 测试 / 线上日志 / 用户反馈 | 写复现步骤和期望结果 |
| 技术债 Tech Debt | 开发 / Review / CI/CD 故障 | 写影响和修复目标 |

---

## 2. Issue 生命周期

| 阶段 | 状态 | 动作 |
|---|---|---|
| 提出 | Open | 写清场景、目标、验收标准 |
| 排期 | Backlog / Todo | 决定优先级和负责人 |
| 开发 | In Progress | 从 main 开 feature 分支 |
| 评审 | In Review | 提 PR，等待 CI 和 Review |
| 合并 | Done | PR 合并 main，自动关闭 Issue |
| 验收 | Verified | 按验收标准确认 |

**追踪规则**：分支名带 Issue 号，PR 描述写 `closes #<编号>`。

---

## 3. 用户故事模板

```text
### US-<编号> <一句话标题> · 状态: Backlog
作为 <角色>,
我想要 <能力>,
以便 <价值>。

验收标准:
- AC1: Given <前提>,When <动作>,Then <可验证结果>。
- AC2: <补充标准>

技术备注:
- <可选:约束、边界、风险>
```

---

## 4. 需求清单

### US-1 初始化项目工程化与 CI/CD · 状态: Todo

作为 **项目开发者**，
我想要 项目具备基础工程结构、测试、CI 与 CD，
以便 后续每次开发都能自动检查并自动部署。

验收标准:
- AC1: 从 `main` 开 feature 分支完成初始化，不直接 push main。
- AC2: PR 触发 CI，至少包含 ruff format、ruff check、pytest + 覆盖率 >= 80%、docker build。
- AC3: CI 全绿后合并 main。
- AC4: 合并 main 自动触发 CD，部署后健康检查通过（`curl http://localhost:8004/_stcore/health` 返回 200）。
- AC5: `streamlit run app.py --server.port 8004` 可本地启动，页面可访问。
- AC6: 完成后更新 `standards/PROGRESS.md`。

技术备注:
- 本地不强制 Docker；`docker build` 交给 CI 执行。
- 端口容器内固定 8004，主机端口回退区间 8004–8010。
- Secrets（SSH_PRIVATE_KEY / SSH_HOST / SSH_USER）需在建仓后由人类配置。

---

### US-2 数据分析交互页面 · 状态: Todo

作为 **银行营销分析师**，
我想要 在 Web 页面上对营销数据进行多维度可视化探索，
以便 快速了解客户分布特征、历史营销效果，为策略制定提供数据支撑。

验收标准:
- AC1: Given 已加载的银行营销数据集，When 打开数据分析页面，Then 页面展示数据总览（行数、列数、关键字段统计摘要）。
- AC2: Given 数据分析页面，When 用户选择不同维度（如年龄、职业、教育程度）进行筛选和分组，Then 图表自动更新并展示对应的分布情况。
- AC3: Given 数据分析页面，When 用户查看目标变量 y（是否认购）的分布，Then 展示认购/未认购比例饼图或柱状图。
- AC4: Given 数据分析页面，When 用户选择两个特征进行交叉分析（如年龄 × 认购结果），Then 展示交叉维度的可视化图表。
- AC5: Given 数据有缺失值或异常值时，When 页面加载，Then 以非阻断方式提示数据质量信息（如缺失率），但页面仍可正常展示。
- AC6: Given 数据分析页面，When 用户操作图表（筛选/缩放/悬停），Then 图表响应流畅（< 2 秒），无明显卡顿。

技术备注:
- 使用 Streamlit 原生图表组件（`st.plotly_chart` 或 `st.bar_chart` 等）。
- 数据加载抽象为独立函数，方便测试和复用。
- 页面布局需适配 1920px 宽屏，左侧筛选 + 右侧图表区域。

---

### US-3 离线模型训练 · 状态: Todo

作为 **数据科学家**，
我想要 基于历史营销数据离线训练一个二分类预测模型，
以便 该模型可用于在线预测客户是否会认购定期存款。

验收标准:
- AC1: Given 银行营销数据集（含标签列 y），When 运行训练脚本，Then 完成数据预处理（编码、标准化、训练/测试集拆分）并输出预处理器的配置信息。
- AC2: Given 训练数据，When 模型训练完成，Then 在测试集上 AUC >= 0.80。
- AC3: Given 训练完成的模型，When 保存模型产物，Then 模型文件（pkl 或 joblib）保存到 `models/` 目录，包含预处理器 + 模型 pipeline。
- AC4: Given 测试集，When 运行评估，Then 输出分类报告（precision、recall、f1-score）到控制台，供人工确认模型质量。
- AC5: Given 训练数据和目标变量 y，When y 分布不均衡（认购比例 < 20%），Then 训练过程使用分层抽样（stratify）并记录类别权重策略。

技术备注:
- 模型选型：优先 LogisticRegression 做基线，后续可升级为 RandomForest / XGBoost。
- 训练脚本 `src/train.py` 可独立运行（不依赖 Streamlit）。
- 特征工程需处理：数值特征标准化、类别特征 OneHot 编码、缺失值填充。
- 暂不包含超参数搜索（后续可扩展）。

---

### US-4 在线预测系统 · 状态: Todo

作为 **银行营销业务人员**，
我想要 在 Web 页面上输入客户特征信息，点击预测按钮后立即看到该客户是否会认购，
以便 在实际营销活动中优先联系高意向客户，提升转化率。

验收标准:
- AC1: Given 已加载离线训练的模型（存在于 `models/`），When 打开预测页面，Then 页面展示所有必要特征输入字段。
- AC2: Given 用户正确填写所有必填字段，When 点击「预测」按钮，Then 页面显示预测结果（"会认购" / "不会认购"）及置信度概率。
- AC3: Given 用户未填写必填字段或填写了非法值（如年龄为负数），When 点击「预测」，Then 页面拒绝预测并给出明确的字段级错误提示，不会崩溃。
- AC4: Given 正常输入，When 点击预测按钮到显示结果，Then 推理耗时 < 500ms（不含模型首次加载时间）。
- AC5: Given 模型文件不存在或损坏，When 进入预测页面，Then 页面显示清晰的错误提示"模型未训练，请先运行离线训练"，而非白屏或堆栈错误。
- AC6: Given 用户多次连续预测不同输入，When 每轮输入后点击预测，Then 每次预测结果互不干扰，页面状态正确重置。

技术备注:
- 预测页面与数据分析页面在同一个 Streamlit 应用中通过侧边栏导航切换。
- 模型在 Streamlit 应用启动时通过 `@st.cache_resource` 加载一次，避免重复 I/O。
- 输入字段对照银行营销数据集的原始特征：age、job、marital、education、default、balance、housing、loan、contact、day、month、duration、campaign、pdays、previous、poutcome。

---

## 5. 非功能需求

- **安全**：密钥只进 Secrets，不进 Git。
- **可维护**：一需求一小 PR（PR 尽量 < 400 行），避免大爆炸式提交。
- **可测试**：核心逻辑必须有单元测试，覆盖率 >= 80%。
- **可部署**：部署后必须有健康检查（Streamlit `/_stcore/health`）。
- **可用性**：页面在 1920px 宽屏下布局合理，操作流畅。
- **数据隐私**：原始数据不进入 Docker 镜像；模型产物通过 CI pipeline 或手动上传至服务器。

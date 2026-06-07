# 00 · 项目上下文 〔本项目活记忆 · AI 维护〕

> **作用**：这是项目的"身份档案"。AI 接管项目时先读这里，了解项目目标、技术栈、目录、部署取值。
> **更新时机**：架构、技术栈、目录结构、端口、部署目录、重要约束变化时更新。

---

## 1. 项目是什么

- **项目名称**：`bank-marketing-predictor`
- **一句话目标**：基于银行电话营销历史数据，提供交互式数据分析看板与客户认购意向在线预测。
- **使用者/受益者**：银行营销分析师、业务决策者；辅助制定精准营销策略。
- **核心功能**：
  - **数据分析交互页面**：对营销数据进行多维度可视化探索，支持筛选、图表交互。
  - **在线预测系统**：基于离线训练的模型，用户输入客户特征后实时预测是否会认购定期存款。
- **输入/数据**：银行营销数据集（UCI Bank Marketing 风格），含客户属性、营销接触信息、历史行为等字段；数据文件不进 Git（`.gitignore` 排除），通过 `.gitkeep` 占位 `data/` 目录。

## 2. 技术栈

| 层 | 选型 | 理由 |
|---|---|---|
| 语言/运行时 | Python 3.11 | 课程统一版本，ML 生态成熟 |
| Web/应用框架 | Streamlit | 纯 Python 快速构建数据应用，无需前后端分离 |
| 数据处理 | pandas、scikit-learn | 数据分析与机器学习标准库 |
| 测试 | pytest + pytest-cov | 课程统一测试框架 |
| 格式/静态检查 | ruff（format + check） | 单工具替代 flake8/isort/black，速度快 |
| 打包/运行 | Docker | 统一部署环境，云端 CI 构建镜像 |
| CI/CD | GitHub Actions | 通用、可视化、适合教学与团队协作 |

## 3. 目录地图

```text
bank-marketing-predictor/
├── standards/                 # AI 项目记忆与通用规范
│   ├── README.md
│   ├── 00-project-context.md
│   ├── 01-requirements.md
│   ├── PROGRESS.md
│   ├── 02-coding-standards.md
│   ├── 03-testing-standards.md
│   ├── 04-git-workflow.md
│   ├── 05-cicd-standards.md
│   ├── 06-ai-collab-protocol.md
│   └── templates/
├── data/                      # 原始数据（不进 Git，本地放置）
│   └── .gitkeep
├── models/                    # 离线训练的模型产物（不进 Git）
│   └── .gitkeep
├── app.py                     # Streamlit 应用入口
├── src/                       # 业务逻辑
│   ├── __init__.py
│   ├── analysis.py            # 数据分析模块
│   ├── train.py               # 离线训练模块
│   └── predict.py             # 在线预测模块
├── tests/                     # 测试
│   ├── __init__.py
│   ├── test_analysis.py
│   ├── test_train.py
│   └── test_predict.py
├── requirements.txt           # 生产运行依赖
├── requirements-dev.txt       # 本地/CI 检查依赖（pytest, ruff, pytest-cov）
├── Dockerfile                 # 容器构建
├── .github/workflows/
│   ├── ci.yml                 # PR 触发：ruff + pytest + docker build
│   └── cd.yml                 # 合并 main 触发：SSH 部署 + 健康检查
├── .gitignore
└── README.md
```

> 新增目录前先更新本节，避免项目越做越散。

## 4. 质量门槛

| 类型 | 本项目标准 |
|---|---|
| 格式检查 | `ruff format --check .` |
| 静态检查 | `ruff check .` |
| 单元测试 | `pytest` |
| 覆盖率 | `>=80%（核心模块）` |
| 构建 | `docker build` 成功 |
| 业务/模型指标 | AUC >= 0.80，模型推理延迟 < 500ms（单条） |
| 数据校验 | 预测输入字段类型/范围校验，缺失必填字段时拒绝推理并给出提示 |

## 5. 不变约束

- 密钥、密码、私钥、Token **绝不写进代码或文档**，只进 GitHub Secrets / 环境变量。
- 数据文件（`data/`）、模型产物（`models/`）不进 Git。
- `main` 分支受保护，日常开发必须走 feature 分支 + PR。
- CI 红灯不合并。
- 端口：容器内固定 `8004`，主机端口回退区间 `8004-8010`。

## 6. 部署/CI 占位符取值

> `guides/` 和 workflow 里的通用占位符，在本项目里的真实值只写这里。

| 占位符 | 本项目取值 | 说明 |
|---|---|---|
| `<APP>` | `bank-marketing-predictor` | 应用名/镜像名/容器名 |
| `<DEPLOY_DIR>` | `/opt/bank-marketing-predictor` | 服务器部署目录 |
| `<PORT>` | `8004` | 容器内服务端口 |
| `<PORT_MAX>` | `8010` | 主机端口回退上限 |
| `<PYVER>` | `3.11` | Python 版本 |
| `<HEALTHCHECK>` | `/_stcore/health` | Streamlit 内置健康检查端点 |
| `<SSH_USER>` | `<部署用户>` | 如 `root` 或 `deploy` |
| `<SSH_HOST>` | `<服务器公网 IP 或域名>` | 不写敏感信息以外的密钥 |

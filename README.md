# EduFlow

EduFlow 是一个基于 Python 构建的在线教育学习平台智能客服系统，能够在多轮对话中理解学生诉求、检索课程与售后知识，并自主完成意图识别、Agent 路由、工具调用与回复聚合。它通过 GeneralAgent、TechnicalAgent 和 BillingAgent 协同处理课程咨询与答疑、平台技术故障、订单支付及课程售后等场景，并内置 RAG 知识问答、分层会话记忆、Skills 动态注入、工具治理、可观测指标与自动化评测，旨在把复杂的客服协作任务转化为可观测、可评测、可扩展的自动化工作流。

![Python](https://img.shields.io/badge/Python-3.12-3776ab.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)
![Redis](https://img.shields.io/badge/Redis-7-dc382d.svg)
![ChromaDB](https://img.shields.io/badge/ChromaDB-0.5.23-f5a623.svg)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ed.svg)

## 功能概览

- 多 Agent 协作：GeneralAgent、TechnicalAgent、BillingAgent 按职责处理不同类型的学生诉求
- 意图识别与路由：融合 LLM、语义匹配和关键词规则，支持细粒度意图识别与复合问题拆分
- RAG 知识问答：基于 ChromaDB 完成知识入库、语义检索和 Cross-Encoder 重排
- 分层会话记忆：Redis 保存工作记忆，ChromaDB 保存情景记忆和用户画像
- Skills 动态注入：按 Agent 和业务场景加载独立规则与处理流程
- 工具治理：提供超时、熔断、降级、TTL 缓存、并行召回和调用链追踪
- 可观测与评测：暴露 Prometheus 指标，并支持意图指标和 LLM-as-Judge 质量评测
- 工程化部署：提供 Dockerfile、Docker Compose、Nginx 反向代理和健康检查

## Agent 分工

| Agent | 主要职责 | 典型问题 |
| --- | --- | --- |
| GeneralAgent | 课程信息、课程内容、学习路径及平台使用指引 | “零基础应该先学哪门课？” |
| TechnicalAgent | 登录、视频、直播、作业上传及设备兼容故障 | “课程视频一直加载失败怎么办？” |
| BillingAgent | 课程价格、支付、退款、发票及换课延期 | “课程退款进度在哪里查看？” |

当一个问题同时包含多种诉求时，调度器会拆分子任务并行调用相应 Agent，再由聚合节点生成统一回复；需要人工介入的投诉或高风险请求会进入升级处理流程。

## 技术栈

- 语言与 Web 服务：Python 3.12、FastAPI 0.115、Uvicorn、Pydantic
- 模型接入：Anthropic SDK，支持兼容 Anthropic 协议的模型服务
- RAG 检索：ChromaDB 0.5.23、Sentence Transformers、Cross-Encoder Reranker
- 缓存与记忆：Redis 7、进程内 TTL Cache
- 监控与评测：Prometheus Client、Webhook 告警、LLM-as-Judge
- 网关与部署：Nginx、Docker、Docker Compose
- 测试：pytest

## 仓库结构

```text
.
├── api/                         # FastAPI 接口和应用入口
├── agents/                      # Agent 实现、编排与工具定义
├── core/                        # 意图识别、LLM 工具函数和 Skills 加载
├── memory/                      # Redis + ChromaDB 分层记忆
├── mcp/                         # 知识检索、工具管理、缓存与重排
├── monitor/                     # 在线指标与异常监控
├── evaluation/                  # 意图评测和 LLM-as-Judge
├── skills/                      # Agent 专属业务规则
├── tests/                       # 自动化测试
├── config/                      # Prometheus、Nginx 与 Grafana 配置
├── data/                        # 示例知识文档与评测基线
├── docker-compose.yml           # 完整服务编排
├── Dockerfile                   # 多阶段镜像构建
└── requirements.txt             # Python 依赖
```

`data/demo_docs/` 提供可直接导入的示例知识文档，`data/eval/baseline.json` 是评测回归基线；`data/chroma/` 为本地生成的向量库，克隆后首次运行会自动重建。

## 启动前准备

最低要求：

- Docker Desktop 或 Docker Engine
- Docker Compose
- 可用的大模型 API Key

本地开发还需要：

- Python 3.12
- Redis 7

确认 Docker 可用：

```bash
docker --version
docker compose version
```

## 配置模型

### 1. 创建环境变量文件

macOS / Linux：

```bash
cp .env.example .env
```

Windows PowerShell：

```powershell
Copy-Item .env.example .env
```

### 2. 填写模型服务

编辑 `.env`，至少填写：

```env
ANTHROPIC_API_KEY=your_api_key
```

如果使用兼容 Anthropic 协议的第三方服务，还需要调整：

```env
ANTHROPIC_BASE_URL=https://your-provider.example.com/anthropic
ANTHROPIC_MODEL=your-model-id
```

### 3. 调整存储与监控（可选）

```env
REDIS_PASSWORD=change_me
REDIS_URL=redis://:change_me@localhost:6379/0
CHROMA_PERSIST_DIRECTORY=./data/chroma
PROMETHEUS_PORT=9091
MONITOR_INTERVAL=10
```

`.env` 包含敏感凭据，已被 `.gitignore` 忽略，请勿提交到公开仓库。

## 方式一：Docker Compose 启动

这是最完整、最省事的启动方式。

### 1. 克隆仓库

```bash
git clone https://github.com/Ultramarvel/EduFlow.git
cd EduFlow
```

### 2. 构建并启动

```bash
docker compose up -d --build
```

该命令会启动：

- EduFlow FastAPI 服务
- Redis
- ChromaDB
- Prometheus
- Nginx

### 3. 查看状态与日志

```bash
docker compose ps
docker compose logs -f eduflow
```

### 4. 访问服务

- Nginx 统一入口：[http://localhost](http://localhost)
- API：[http://localhost:8000](http://localhost:8000)
- Swagger：[http://localhost:8000/docs](http://localhost:8000/docs)
- 健康检查：[http://localhost:8000/health](http://localhost:8000/health)
- Prometheus：[http://localhost:9090](http://localhost:9090)

停止服务：

```bash
docker compose down
```

## 方式二：本地启动

### 1. 创建虚拟环境并安装依赖

```bash
python -m venv .venv
```

macOS / Linux：

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell：

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. 启动依赖

```bash
docker compose up -d redis chromadb
```

### 3. 启动 API

```bash
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

## 命令行对话模式

不需要经过 HTTP 层时，可以直接进入命令行对话：

```bash
python api/main.py --cli
```

## 核心处理链路

```text
学生请求
  -> 读取会话记忆
  -> LLM + Embedding + 关键词规则融合意图识别
  -> 按意图决定是否执行知识检索
  -> General / Technical / Billing Agent 路由或并行协作
  -> Skills 与工具调用
  -> 回答聚合和可信度检查
  -> 写回记忆并记录监控指标
```

## 主要接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/health` | 健康检查 |
| POST | `/chat` | 智能客服主对话接口 |
| POST | `/search` | 知识库检索 |
| POST | `/knowledge/add` | 批量添加知识文档 |
| POST | `/knowledge/upload` | 上传 `.txt`、`.md` 或 `.json` 文档 |
| GET | `/knowledge/stats` | 查看知识库统计 |
| GET | `/skills` | 查看已加载 Skills |
| POST | `/skills/reload` | 重新加载 Skills |
| GET | `/monitor` | 查看运行监控摘要 |
| GET | `/metrics` | Prometheus 指标 |
| GET | `/trace/tools` | 查看近期工具调用链路 |
| GET | `/trace/tool/{request_id}` | 查看单次请求的工具调用链路 |
| POST | `/eval/run` | 执行端到端评测 |

完整参数和响应结构请以 Swagger 页面为准。首次验证建议依次检查 `GET /health`、`POST /chat`、`POST /knowledge/upload`、`POST /search`，最后确认 `/metrics` 能够被 Prometheus 采集。

对话请求示例：

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "课程视频无法播放，同时我想了解退款规则",
    "user_id": "student-1001"
  }'
```

## 端口说明

| 组件 | 默认端口 |
| --- | ---: |
| Nginx | `80` |
| EduFlow API | `8000` |
| ChromaDB | `8001` |
| Redis | `6379` |
| Prometheus | `9090` |

## 关键配置

主要配置文件是 `.env`。

### 模型服务

```env
ANTHROPIC_API_KEY=your_api_key
ANTHROPIC_BASE_URL=https://api.anthropic.com
ANTHROPIC_MODEL=your-model-id
```

### Redis 与 ChromaDB

```env
REDIS_PASSWORD=change_me
REDIS_URL=redis://:change_me@localhost:6379/0
CHROMA_HOST=localhost
CHROMA_PORT=8001
CHROMA_PERSIST_DIRECTORY=./data/chroma
```

### RAG 重排

```env
RERANKER_MODEL=BAAI/bge-reranker-base
RERANKER_DEVICE=cpu
RERANKER_BATCH_SIZE=16
RERANKER_MAX_CHARS=4000
```

`RERANKER_DEVICE` 留空时由 Sentence Transformers 自动选择设备；模型会在首次重排时懒加载。

## 二次开发入口

第一次接手代码，建议按这个顺序阅读：

1. [main.py](api/main.py)
2. [intent_recognizer.py](core/intent_recognizer.py)
3. [agent_orchestrator.py](agents/agent_orchestrator.py)
4. [knowledge_base.py](mcp/knowledge_base.py)
5. [tool_manager.py](mcp/tool_manager.py)
6. [conversation_memory.py](memory/conversation_memory.py)
7. [performance_monitor.py](monitor/performance_monitor.py)
8. [evaluator.py](evaluation/evaluator.py)

模块分工：

- `api`：接口定义、依赖初始化和主调用链路
- `core`：三路融合意图识别、LLM 响应工具函数和 Skills 加载
- `agents`：Agent 配置、路由、并行执行、结果聚合和工具定义
- `mcp`：知识入库与语义检索、工具治理、缓存、熔断和 Cross-Encoder 重排
- `memory`：工作记忆、情景记忆和用户画像
- `monitor` / `evaluation`：运行指标、告警与评测回归检测
- `skills`：按 Agent 和业务场景维护的独立规则与处理流程

## 测试

运行全部测试：

```bash
pytest -q
```

运行 Agent 编排和重排测试：

```bash
pytest -q tests/test_agent_orchestrator.py
pytest -q tests/test_cross_encoder_reranker.py
```

## 常见问题

### 1. 服务启动后调用模型失败

确认 `.env` 中的 `ANTHROPIC_API_KEY`、`ANTHROPIC_BASE_URL` 和 `ANTHROPIC_MODEL` 与实际服务商配置一致，再查看日志：

```bash
docker compose logs -f eduflow
```

### 2. Docker Compose 提示找不到 .env

`docker-compose.yml` 通过 `env_file` 读取 `.env`，该文件不会随仓库分发。请先执行 `cp .env.example .env` 并填写模型配置。

### 3. 首次检索或重排较慢

ChromaDB Embedding 模型和 Cross-Encoder 重排模型首次使用时需要加载，首次请求通常比后续请求慢；生产部署可在启动阶段增加预热。

### 4. Redis 连接失败

检查 `REDIS_PASSWORD` 与 `REDIS_URL` 是否一致，并确认 Redis 容器健康：

```bash
docker compose ps redis
docker compose logs redis
```

### 5. 知识库检索结果不理想

优先检查文档切分质量、召回数量和重排模型配置，再通过 `/trace/tools` 查看实际工具调用及检索链路。

# 智扫通机器人智能客服 · Agent Service

基于 **LangChain 1.x / LangGraph** 的扫地机器人智能客服：RAG 知识库问答 + 多工具 Agent 编排 + 中间件动态提示词 + 流式对话界面。

![Python](https://img.shields.io/badge/Python-3.13-blue) ![LangChain](https://img.shields.io/badge/LangChain-1.x-1c9c9c) ![LangGraph](https://img.shields.io/badge/LangGraph-Agent-ff6b6b) ![Streamlit](https://img.shields.io/badge/Streamlit-UI-ff4b4b)

---

## 功能特性

- **知识库问答（RAG）**：txt/pdf 文档增量入库（MD5 查重去重）、递归字符切片（200 字/20 重叠）、Chroma 向量检索、生成结果严格基于参考资料，抑制幻觉
- **多工具 Agent**：7 个工具（知识库检索 / 天气 / 位置 / 用户ID / 月份 / 外部使用记录 / 报告钩子），模型自主规划并串联调用——例：先取"位置+天气"，再组合成更精确的检索词查询知识库
- **中间件 + 动态提示词**：`wrap_tool_call` 拦截每次工具调用（监控 + 写旗标），`dynamic_prompt` 依据旗标在"普通客服 / 报告生成"两种系统提示词间**运行时切换**
- **流式输出**：LangGraph `stream` → 生成器逐段产出 → Streamlit 打字机效果
- **工程化**：yml 配置驱动、双通道日志（控制台 INFO + 文件 DEBUG）、四道门异常容错、失败文件自动重试

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置模型密钥（网关与模型名见 config/rag.yml）
export DASHSCOPE_API_KEY="你的API Key"

# 3. 知识库入库（幂等，可重复执行）
python -m rag.vector_store

# 4. 启动客服界面
streamlit run app.py

# 5.（可选）单测全部工具
python -m agent.tools.agent_tools
```

## 系统架构

```
用户提问
   │
   ▼
┌─ Streamlit 界面（app.py）：session_state 会话单例 + write_stream 流式上屏
   │
   ▼
┌─ Agent 循环（LangGraph create_agent）─────────────────────┐
   思考 → 选工具 → 执行 → 观察 → 思考 → … → 最终回答        │
           │                    ▲                            │
           ▼ 中间件拦截          │ 工具结果回流为"观察"        │
   wrap_tool_call：工具日志 + 旗标写入                        │
   dynamic_prompt：按旗标贴系统提示词（普通/报告）            │
   before_model：调模型前记状态流水                           │
   │                                                         │
   ▼                                                         │
┌─ 工具层（7 个 @tool）───────────────────────────────────────┤
   rag_summarize ──► RAG 总结链（prompt | model | parser）   │
                 └──► 向量检索（Chroma / MD5 增量入库）      │
   fetch_external_data ──► 外部 CSV 使用记录（懒加载缓存）    │
   fill_context_for_report ──► 钩子（只"按铃"，中间件干活）   │
   get_weather / get_user_location / get_user_id /            │
   get_current_month ──► 场景数据                             │
└─────────────────────────────────────────────────────────────┘

旗标流转：fill_context_for_report 被调用 → monitor_tool 置 report=True
        → 下一轮 dynamic_prompt 读到 True → 系统提示词切换为"报告模式"
```

## 项目结构

```
agent/
├── tools/
│   ├── agent_tools.py      # 7 个工具（@tool 装饰器，函数签名即模型参数 schema）
│   └── middleware.py       # 3 个中间件（工具拦截 / 模型日志 / 动态提示词）
└── react_agent.py          # create_agent 总装 + execute_stream 生成器
app.py                      # Streamlit 网页（会话单例 + 打字机流式）
config/                     # yml 配置（模型 / 向量库 / 提示词 / Agent）
data/                       # 知识库文档 + 外部使用记录 CSV
model/factory.py            # 模型工厂（工厂模式，Chat/Embedding 双实现）
prompts/                    # 提示词模板（系统 / RAG 总结 / 报告）
rag/
├── vector_store.py         # 向量库服务（MD5 查重、四道门、检索门面）
└── rag_service.py          # RAG 总结链
utils/                      # 五件套（path / logger / config / file / prompt）
```

## 设计亮点

### 1. 四道门容错 + "先干活再记账" → 失败自愈
入库主流程每步设防：MD5 查重跳过、空文档跳过、空切片跳过、异常捕获跳过（每道门都先记日志再放行）。MD5 账本**只在入库成功后追加**——失败文件不记账，下一轮自动重试。批量任务"吞掉继续"的前提，是任务之间互不依赖。

### 2. 钩子模式：工具只"按铃"，中间件干活
`fill_context_for_report` 函数体只返回一个字符串，不注入任何内容；真正的工作由中间件完成：拦截该工具调用 → 写入 context 旗标 → 下一轮动态切换系统提示词。**工具、状态、提示词三方职责分离**——新增业务场景只需加一个旗标分支，不改动任何现有工具。

### 3. 静默失效排查："不报错 ≠ 没问题"
实际排查过一类问题：检索参数名拼写错误，被 pydantic **静默吞掉**（多余 kwargs 被忽略、不抛任何异常），导致检索条数配置永远不生效、且无任何报错。由此形成习惯：对 kwargs / 配置键级别的"看起来正常"保持怀疑，用最小复现逐参数验证是否真正落地。

### 4. 生成器三级流水线
`agent.stream`（状态块）→ `execute_stream` 逐段 yield（文本中继）→ `capture` 逐字符 yield（打字机节流）→ `write_stream` 上屏。每级只做一件事，消费端拿到统一字符流。

### 5. 异常边界：批量"吞"，循环"抛"
批量入库：捕获后 continue，跳过互不依赖的个体；Agent 循环：捕获记录后**必须 raise**，把真相交还循环——决策者是模型，吞掉异常等于让模型拿着假情报继续推理（幻觉源头）。

## 技术栈

| 类别 | 选型 |
| --- | --- |
| 语言 | Python 3.13 |
| LLM 编排 | LangChain 1.x · LangGraph（create_agent + middleware）|
| 向量库 | Chroma（langchain-chroma）|
| 模型 | Qwen（DashScope / OpenAI 兼容网关）|
| 界面 | Streamlit |
| 工程化 | PyYAML 配置 · logging 双通道 · MD5 增量去重 |

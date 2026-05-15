# 🌍 GeoAgent Copilot：AI 空间智能分析工作台

Created time: 2026年5月9日 12:49

[![Status](https://img.shields.io/badge/Status-Live-success?style=for-the-badge&logo=streamlit)]([这里填你的在线体验网址])
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![Model](https://img.shields.io/badge/AI_Model-GLM--4-orange?style=for-the-badge&logo=openai)


---

## ① 项目简介

**GeoAgent Copilot** 是一个基于 `LLM + GIS Tool Calling` 架构的空间智能分析 Agent。

针对非专业测绘人员使用传统 GIS 软件门槛高的痛点，本项目通过大模型意图识别与底层工具链调度，让用户可以直接以**自然语言对话**的方式完成复杂的空间数据挖掘。目前已支持：

- 🔍 **POI 精准检索与过滤**
- ⭕ **空间缓冲区分析 (Buffer Analysis)**
- 🔥 **热点区域密度分析 (Heatmap)**
- 🧠 **空间商业聚类分析 (DBSCAN)**
- 🗺️ **交互式地图动态可视化**

> **🚀 立即体验：[点击这里访问 GeoAgent 网页版](https://geoagent-copilot.streamlit.app/)**
> 

---

## ② 项目截图与演示视频

### 1. 沉浸式左右分栏主界面 (Dashboard)

![主界面](ui.png)

### 2. Multi-Step Agent 意图拆解与规划 (JSON Planning)

![Agent计划](json.png)

### 3. 空间密度热力图渲染 (Heatmap Visualization)

![热力图](heatmap.png)

### 4. 商业空间聚类分析 (DBSCAN Clustering)

![聚类图](cluster.png)
---
### 5. 项目完整演示视频

Demo 视频（Bilibili）：
https://www.bilibili.com/video/BV1M75v6SEbG/?share_source=copy_web&vd_source=6ac55e276e464565c6c1a7df7da0806c
⚠️ 如果无法播放，请复制链接到浏览器地址栏打开。

## ③ 技术架构

系统采用了标准的 **Agentic Workflow（智能体工作流）** 单向数据流设计：

```mermaid
flowchart TB
    %% 样式定义
    classDef user fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#01579b,font-weight:bold;
    classDef frontend fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#e65100;
    classDef memory fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#4a148c;
    classDef prompt fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px,color:#1b5e20;
    classDef llm fill:#ffebee,stroke:#b71c1c,stroke-width:2px,color:#b71c1c;
    classDef guard fill:#fff9c4,stroke:#f57f17,stroke-width:2px,color:#f57f17;
    classDef sandbox fill:#e0f2f1,stroke:#004d40,stroke-width:2px,color:#004d40;
    classDef gis fill:#e3f2fd,stroke:#0d47a1,stroke-width:2px,color:#0d47a1;
    classDef viz fill:#fce4ec,stroke:#880e4f,stroke-width:2px,color:#880e4f;
    classDef output fill:#ede7f6,stroke:#311b92,stroke-width:2px,color:#311b92;

    subgraph Frontend["🖥️ 前端层"]
        UI["Streamlit UI<br/>控制面板 + 地图区"]
    end

    subgraph Core["🧠 Agent 核心"]
        SS["Session State<br/>记忆与状态管理"]
        PROMPT["约束提示词构建"]
    end

    subgraph LLM["🤖 模型层"]
        GLM["GLM-4-flash<br/>自然语言 → 工具调用代码"]
    end

    subgraph Safety["🛡️ 安全层"]
        GUARD["Regex Guardrails<br/>代码清洗/校验"]
    end

    subgraph Execution["⚙️ 执行层"]
        SANDBOX["Python Eval 沙盒<br/>安全执行空间代码"]
    end

    subgraph GIS_Lib["🗺️ GIS 算子库"]
        BUFFER["Haversine 缓冲区"]
        FILTER["类型筛选"]
        HEAT["热力图数据"]
        CLUSTER["DBSCAN 聚类"]
    end

    subgraph Visual["📊 可视化层"]
        FOLIUM["Folium 地图引擎"]
        RENDER["streamlit-folium 渲染"]
    end

    USER["👤 用户"]:::user -->|上传 CSV + 自然语言| UI:::frontend
    UI --> SS:::memory
    SS --> PROMPT:::prompt
    PROMPT --> GLM:::llm
    GLM -->|生成分析代码| GUARD:::guard
    GUARD --> SANDBOX:::sandbox
    SANDBOX <-->|动态调用| BUFFER:::gis
    SANDBOX <-->|动态调用| FILTER:::gis
    SANDBOX <-->|动态调用| HEAT:::gis
    SANDBOX <-->|动态调用| CLUSTER:::gis
    BUFFER & FILTER & HEAT & CLUSTER -.->|返回 DataFrame| SANDBOX
    SANDBOX -->|处理结果| FOLIUM:::viz
    FOLIUM --> RENDER:::viz
    RENDER -->|HTML 地图| UI
    UI -->|最终可视化结果| USER

    %% 样式微调
    style Frontend fill:#fff8e1,stroke:#f9a825,stroke-width:2px,rx:10,ry:10
    style Core fill:#f1f8e9,stroke:#7cb342,stroke-width:2px,rx:10,ry:10
    style LLM fill:#ffebee,stroke:#ef5350,stroke-width:2px,rx:10,ry:10
    style Safety fill:#fff9c4,stroke:#ffca28,stroke-width:2px,rx:10,ry:10
    style Execution fill:#e0f2f1,stroke:#4db6ac,stroke-width:2px,rx:10,ry:10
    style GIS_Lib fill:#e3f2fd,stroke:#64b5f6,stroke-width:2px,rx:10,ry:10
    style Visual fill:#fce4ec,stroke:#f06292,stroke-width:2px,rx:10,ry:10
```

---

## ④ 技术栈

- **前端交互与状态管理**：`Streamlit` (结合 Session State 解决组件重载问题)
- **大模型引擎**：`ZhipuAI (GLM-4 Flash)`
- **地图渲染引擎**：`Folium`, `streamlit-folium`
- **空间数据处理**：`Pandas`, `Numpy`
- **空间机器学习算法**：`scikit-learn` (DBSCAN)
- **核心 AI 范式**：`Multi-Step Tool Calling`, `Agentic Workflow`

---

## ⑤ 核心亮点 (Core Highlights)

作为一款 AI Native 的空间数据产品，本项目的核心壁垒不在于简单的 API 调用，而在于**系统级的产品架构设计与工程容错能力**：

1. **从“代码生成”进化为“多步工具调用” (Multi-Step Tool Calling)**
摒弃了危险且不可控的 `eval()` 直接执行代码模式。将 GIS 能力原子化封装为 `Tool Registry`，强制大模型输出结构化的 JSON 步骤计划，实现了“意图解析”与“系统执行”的彻底解耦，极大提升了系统的安全性与可扩展性。
2. **硬核空间算法的平民化赋能**
将需要专业背景才能操作的机器学习算法（如 DBSCAN 空间聚类参数调优、Haversine 球面距离计算）封装在产品底层，用户只需输入“分析商业聚集区”，系统即可自动完成从特征提取到高精度渲染的全闭环。
3. **极其克制的前端状态管理 (Stateful UI)**
针对数据可视化中高频的“地图拖拽导致页面重载闪退”痛点，深入前端框架底层，引入单向渲染锁 (`returned_objects=[]`) 与全局 `Session State` 记忆机制，保障了流畅的商业级 SaaS 交互体验。
4. **双重护栏兜底机制 (Dual Guardrails)**
深知大模型存在“格式幻觉”，在 Prompt 强约束的基础上，在工程执行层引入 Regex 暴力清洗机制，确保 Agent 输出的 JSON Schema 100% 可被后台安全解析。

---

---

## 👤 关于作者

**张林果**

- 🎓 武汉大学 测绘工程专业
- 💻 专注方向：AI 产品经理 / 空间数据分析 (GIS)
- 📧 邮箱：3123309125@qq.com
- 💡 *"永远相信，优秀的产品是在极度克制与解决真实痛点中诞生的。"*

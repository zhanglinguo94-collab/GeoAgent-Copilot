import json
import time

import streamlit as st
import pandas as pd
import numpy as np
import folium

from folium.plugins import HeatMap
from sklearn.cluster import DBSCAN
from streamlit_folium import st_folium
from zhipuai import ZhipuAI


# ==================================================
# 1. 页面配置
# ==================================================

st.set_page_config(
    page_title="GeoAgent Copilot",
    layout="wide"
)

st.markdown("""
# 🌍 GeoAgent Copilot
### AI Spatial Intelligence Platform
""")

st.markdown("---")


# ==================================================
# 2. 初始化大模型
# ==================================================

try:
    # 尝试从 Streamlit 云端的隐藏配置中读取密码
    my_api_key = st.secrets["ZHIPUAI_API_KEY"]
except:
    # 如果没找到，给一个假密码防止程序直接崩溃
    my_api_key = "please_configure_api_key_in_secrets"

client = ZhipuAI(api_key=my_api_key)

# ==================================================
# 3. Session State（记忆系统）
# ==================================================

if "agent_plan" not in st.session_state:
    st.session_state.agent_plan = None

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ==================================================
# 4. GIS 工具函数
# ==================================================

# 4.1 缓冲区分析
def buffer_analysis(df, center_lat, center_lon, radius_km):

    lat1, lon1 = np.radians(center_lat), np.radians(center_lon)

    lat2, lon2 = np.radians(df['纬度']), np.radians(df['经度'])

    dlat, dlon = lat2 - lat1, lon2 - lon1

    a = (
        np.sin(dlat / 2) ** 2
        + np.cos(lat1)
        * np.cos(lat2)
        * np.sin(dlon / 2) ** 2
    )

    c = 2 * np.arctan2(
        np.sqrt(a),
        np.sqrt(1 - a)
    )

    distance = 6371.0 * c

    return df[distance <= radius_km]


# 4.2 类型过滤
def category_filter(df, category):

    return df[
        df["类型"].str.lower() == category.lower()
    ]


# 4.3 热力图
def heatmap_analysis(df):

    return df[
        ["纬度", "经度"]
    ].values.tolist()


# 4.4 聚类分析
def cluster_analysis(df):

    coords = df[
        ["纬度", "经度"]
    ].values

    db = DBSCAN(
        eps=0.01,
        min_samples=5
    )

    clusters = db.fit_predict(coords)

    df = df.copy()

    df["cluster"] = clusters

    return df


# ==================================================
# 5. Tool Registry
# ==================================================

TOOLS = {

    "buffer_analysis": buffer_analysis,

    "category_filter": category_filter,

    "heatmap_analysis": heatmap_analysis,

    "cluster_analysis": cluster_analysis
}


# ==================================================
# 6. 左右布局
# ==================================================

left_col, right_col = st.columns([1, 2])


# ==================================================
# 7. 左侧控制台
# ==================================================

with left_col:

    st.markdown("## ⚙️ Control Panel")

    uploaded_file = st.file_uploader(
        "上传空间数据 CSV 文件",
        type="csv"
    )

    user_query = st.text_area(
        "请输入空间分析需求",
        height=120,
        placeholder="例如：分析 cafe 的热点区域"
    )

    run_button = st.button(
        "🚀 开始分析",
        use_container_width=True
    )

    st.markdown("---")

    st.markdown("### 💡 Example Queries")

    examples = [

        "找出所有 cafe",

        "restaurant有多少",

        "找出纬度30.53 经度114.36 周边2公里内的餐厅",

        "分析 cafe 热点区域",

        "分析商业聚集区"
    ]

    for q in examples:

        st.code(q)

    st.markdown("---")

    st.markdown("### 🧠 Agent Memory")

    if st.session_state.chat_history:

        for item in st.session_state.chat_history[-5:]:

            st.info(item)

    else:

        st.caption("暂无历史分析记录")


# ==================================================
# 8. 数据读取
# ==================================================

df = None

if uploaded_file is not None:

    try:

        df = pd.read_csv(
            uploaded_file,
            encoding="utf-8"
        )

    except:

        uploaded_file.seek(0)

        df = pd.read_csv(
            uploaded_file,
            encoding="gbk"
        )


# ==================================================
# 9. 右侧地图区域
# ==================================================

with right_col:

    st.markdown("## 🗺️ Spatial Visualization")

    if df is not None:

        # ==========================================
        # 数据指标卡片
        # ==========================================

        metric1, metric2, metric3 = st.columns(3)

        with metric1:

            st.metric(
                "POI数量",
                len(df)
            )

        with metric2:

            st.metric(
                "字段数量",
                len(df.columns)
            )

        with metric3:

            st.metric(
                "空间点数量",
                len(df)
            )

        st.markdown("---")

        st.success(
            f"✅ 数据加载成功，共 {len(df)} 条记录"
        )

        st.dataframe(
            df.head(5),
            use_container_width=True
        )

        # ==========================================
        # 点击分析
        # ==========================================

        if run_button and user_query:

            progress = st.progress(0)

            with st.status(
                "🤖 GeoAgent Working...",
                expanded=True
            ) as status:

                st.write("🧠 Intent Understanding...")
                progress.progress(20)
                time.sleep(0.5)

                st.write("🛠️ Tool Routing...")
                progress.progress(50)
                time.sleep(0.5)

                st.write("🌍 Spatial Reasoning...")
                progress.progress(80)
                time.sleep(0.5)

                # ======================================
                # Multi-Step Prompt
                # ======================================

                prompt = f"""
                你是 GIS 空间分析 Agent。

                你可以使用以下工具：

                ------------------------------------------------

                1. category_filter

                用途：
                普通类型筛选。

                适用于：
                - 找出 cafe
                - 找出 restaurant

                参数：
                - category

                ------------------------------------------------

                2. buffer_analysis

                用途：
                空间范围分析。

                适用于：
                - 周边3公里
                - 附近5公里
                - 缓冲区分析

                参数：
                - lat
                - lon
                - radius

                ------------------------------------------------

                3. heatmap_analysis

                用途：
                空间热点分析。

                适用于：
                - 热点区域
                - 热力图
                - 热区分析
                - 密集区域

                参数：
                无

                ------------------------------------------------

                4. cluster_analysis

                用途：
                空间聚类分析。

                适用于：
                - 聚集区
                - 商业聚类
                - 空间聚类

                参数：
                无

                ------------------------------------------------

                用户请求：
                {user_query}

                ------------------------------------------------

                你必须返回多步骤 JSON。

                不允许 markdown。
                不允许解释。

                示例：

                {{
                    "steps":[
                        {{
                            "tool":"category_filter",
                            "args": {{
                                "category":"cafe"
                            }}
                        }},
                        {{
                            "tool":"heatmap_analysis",
                            "args": {{}}
                        }}
                    ]
                }}
                """

                try:

                    response = client.chat.completions.create(

                        model="glm-4-flash",

                        messages=[
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],

                        temperature=0.1
                    )

                    raw_output = (
                        response
                        .choices[0]
                        .message
                        .content
                        .strip()
                    )

                    raw_output = raw_output.replace(
                        "```json",
                        ""
                    )

                    raw_output = raw_output.replace(
                        "```",
                        ""
                    )

                    raw_output = raw_output.strip()

                    st.session_state.agent_plan = raw_output

                    progress.progress(100)

                    status.update(
                        label="✅ Agent Analysis Complete",
                        state="complete",
                        expanded=False
                    )

                except Exception as e:

                    status.update(
                        label="❌ Agent Failed",
                        state="error",
                        expanded=True
                    )

                    st.error(f"大模型调用失败：{e}")

        # ==========================================
        # Agent Planning 展示
        # ==========================================

        if st.session_state.agent_plan is not None:

            st.markdown("---")

            st.markdown("## 🤖 Agent Planning")

            st.code(
                st.session_state.agent_plan,
                language="json"
            )

            try:

                plan = json.loads(
                    st.session_state.agent_plan
                )

                steps = plan.get("steps", [])

                current_df = df.copy()

                m = None

                # ======================================
                # Multi-Step Tool Calling
                # ======================================

                for step in steps:

                    tool_name = step["tool"]

                    args = step.get("args", {})

                    st.info(
                        f"⚡ 执行工具：{tool_name}"
                    )

                    # ==============================
                    # category_filter
                    # ==============================

                    if tool_name == "category_filter":

                        current_df = category_filter(

                            current_df,

                            args["category"]
                        )

                        st.success(
                            f"筛选后剩余 {len(current_df)} 条数据"
                        )

                    # ==============================
                    # buffer_analysis
                    # ==============================

                    elif tool_name == "buffer_analysis":

                        current_df = buffer_analysis(

                            current_df,

                            args["lat"],

                            args["lon"],

                            args["radius"]
                        )

                        st.success(
                            f"缓冲区内找到 {len(current_df)} 条数据"
                        )

                    # ==============================
                    # heatmap_analysis
                    # ==============================

                    elif tool_name == "heatmap_analysis":

                        heat_data = heatmap_analysis(
                            current_df
                        )

                        if len(heat_data) > 0:

                            m = folium.Map(

                                location=[
                                    current_df.iloc[0]["纬度"],
                                    current_df.iloc[0]["经度"]
                                ],

                                zoom_start=12
                            )

                            HeatMap(
                                heat_data
                            ).add_to(m)

                            st.success(
                                "🔥 热点区域分析完成"
                            )

                    # ==============================
                    # cluster_analysis
                    # ==============================

                    elif tool_name == "cluster_analysis":

                        current_df = cluster_analysis(
                            current_df
                        )

                        m = folium.Map(

                            location=[
                                current_df.iloc[0]["纬度"],
                                current_df.iloc[0]["经度"]
                            ],

                            zoom_start=12
                        )

                        colors = [

                            'red',
                            'blue',
                            'green',
                            'purple',
                            'orange',
                            'darkred',
                            'cadetblue'
                        ]

                        for idx, row in current_df.iterrows():

                            cluster_id = row["cluster"]

                            color = colors[
                                cluster_id % len(colors)
                            ] if cluster_id != -1 else "black"

                            folium.CircleMarker(

                                location=[
                                    row["纬度"],
                                    row["经度"]
                                ],

                                radius=6,

                                color=color,

                                fill=True,

                                fill_color=color,

                                popup=f"Cluster {cluster_id}"

                            ).add_to(m)

                        st.success(
                            "🧠 聚类分析完成"
                        )

                # ======================================
                # 最终结果
                # ======================================

                st.markdown("---")

                st.markdown("## 📊 Final Result")

                st.dataframe(
                    current_df,
                    use_container_width=True
                )

                st.session_state.last_result = current_df

                st.session_state.chat_history.append(
                    f"用户：{user_query}"
                )

                # ======================================
                # 渲染地图
                # ======================================

                if m is not None:

                    st_folium(
                        m,
                        width="100%",
                        height=600,
                        returned_objects=[]
                    )

                else:

                    if not current_df.empty:

                        m = folium.Map(

                            location=[
                                current_df.iloc[0]["纬度"],
                                current_df.iloc[0]["经度"]
                            ],

                            zoom_start=12
                        )

                        for idx, row in current_df.iterrows():

                            folium.Marker(

                                [
                                    row["纬度"],
                                    row["经度"]
                                ],

                                popup=row.get(
                                    "类型",
                                    "未知"
                                )

                            ).add_to(m)

                        st_folium(
                            m,
                            width="100%",
                            height=600,
                            returned_objects=[]
                        )

            except Exception as e:

                st.error(f"❌ 渲染失败：{e}")

    else:

        st.info("⬅️ 请先上传 CSV 文件")
"""硅智 SiliconMind UI v0.3：Streamlit 美化版。"""
import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "rag"))
sys.path.insert(0, str(ROOT / "kg"))

import streamlit as st
from query import answer as rag_answer
from simulate import simulate as circuit_sim
from multimodal import analyze as vl_analyze

# ============== 页面配置 ==============
st.set_page_config(
    page_title="硅智 SiliconMind",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============== 自定义 CSS ==============
st.markdown("""
<style>
    /* 主标题 */
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(120deg, #1f77b4, #2ca02c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    /* 副标题 */
    .sub-title {
        text-align: center;
        color: #666;
        font-size: 0.9rem;
        margin-bottom: 2rem;
    }
    /* Tab 标签 */
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 1.05rem;
        font-weight: 600;
    }
    /* 主按钮 */
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: 600;
        border-radius: 6px;
        border: none;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: #2ca02c;
    }
    /* 示例问题按钮 */
    .example-btn {
        background-color: #f0f2f6;
        color: #333;
        padding: 0.4rem 0.8rem;
        border-radius: 6px;
        border: 1px solid #d0d0d0;
        margin: 0.2rem 0;
        cursor: pointer;
        font-size: 0.85rem;
        text-align: left;
    }
    .example-btn:hover {
        background-color: #1f77b4;
        color: white;
    }
    /* 答案框 */
    .answer-box {
        background: #fafafa;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        max-height: 600px;
        overflow-y: auto;
    }
    /* 仿真框 */
    .sim-box {
        background: #1e1e1e;
        color: #d4d4d4;
        border-radius: 8px;
        padding: 1rem;
        max-height: 500px;
        overflow-y: auto;
        font-family: 'Consolas', monospace;
        font-size: 0.85rem;
    }
    /* 信息卡片 */
    .info-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    /* 统计 */
    .stat-card {
        background: #f0f2f6;
        padding: 0.8rem;
        border-radius: 6px;
        text-align: center;
    }
    .stat-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1f77b4;
    }
    .stat-label {
        font-size: 0.75rem;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

# ============== 侧边栏 ==============
with st.sidebar:
    st.markdown("### 🔬 硅智 SiliconMind")
    st.caption("v0.3 · 2026 大赛参赛作品")
    st.markdown("---")
    st.markdown("**📊 当前模型**")
    st.markdown("- LLM: `qwen-plus`")
    st.markdown("- Embedding: `bge-small-zh`")
    st.markdown("- VectorDB: `ChromaDB`")
    st.markdown("---")
    st.markdown("**🎯 核心功能**")
    st.markdown("- 💬 多模态问答")
    st.markdown("- 🧮 自动公式推导")
    st.markdown("- 🖼️ 电路图识别")
    st.markdown("- 🕸️ 知识图谱")
    st.markdown("---")
    st.markdown("**📈 评测数据**")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="stat-card"><div class="stat-value">95%</div><div class="stat-label">命中率</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="stat-card"><div class="stat-value">100%</div><div class="stat-label">引用率</div></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.caption(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# ============== 主标题 ==============
st.markdown('<div class="main-title">🔬 硅智 SiliconMind</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">AI × 模电教学 · 多模态智能解答 · 学科知识图谱</div>', unsafe_allow_html=True)

# ============== 示例问题库 ==============
EXAMPLE_QA = [
    "为什么 MOS 管的 G 极几乎不取电流？",
    "PN 结的死区电压是怎么形成的？硅和锗分别是多少？",
    "理想运放的两条核心假设是什么？",
    "为什么三极管共射放大电路的输出信号与输入信号反相？",
    "LM358 作为比较器时输出为什么需要上拉？",
]

EXAMPLE_SIM = [
    "RC 时间常数 τ=R*C, R=10kΩ, C=100nF, 推导并计算",
    "RC 低通截止频率 f_c = 1/(2πRC), R=10kΩ, C=100nF, 计算",
    "NE555 单稳态脉宽 T = 1.1RC, R=10kΩ, C=10nF, 推导并计算",
    "三极管共射放大 Ic=βIb, β=100, Ib=0.1mA, 求 Ic",
    "7805 输入 12V, 输出 5V, 压差功率 P=ΔU*I, 负载 0.5A, 计算",
]

# ============== 4 个 Tab ==============
tab1, tab2, tab3, tab4 = st.tabs(["💬 问答", "🧮 仿真", "🖼️ 看图", "🕸️ 知识图谱"])

# ========== Tab 1: 问答 ==========
with tab1:
    st.markdown("#### 📖 原理问答 · 含教材引用")
    
    col_input, col_btn = st.columns([5, 1])
    with col_input:
        q = st.text_input("输入问题：", placeholder="如：为什么 MOS 管的 G 极几乎不取电流？", label_visibility="collapsed")
    with col_btn:
        ask_btn = st.button("🚀 提问", use_container_width=True)
    
    st.markdown("**💡 一键试问：**")
    cols = st.columns(2)
    for i, eq in enumerate(EXAMPLE_QA):
        with cols[i % 2]:
            if st.button(f"📌 {eq}", key=f"qa_ex_{i}", use_container_width=True):
                q = eq
                ask_btn = True
    
    if ask_btn and q:
        with st.spinner("🧠 硅智思考中..."):
            ans = rag_answer(q)
        st.markdown("**📝 回答：**")
        st.markdown(f'<div class="answer-box">{ans}</div>', unsafe_allow_html=True)
    elif ask_btn:
        st.warning("请先输入问题")

# ========== Tab 2: 仿真 ==========
with tab2:
    st.markdown("#### 🧮 自动公式推导 · SymPy 计算")
    
    col_input, col_btn = st.columns([5, 1])
    with col_input:
        sq = st.text_input("输入问题：", placeholder="如：RC 时间常数...", key="sim_input", label_visibility="collapsed")
    with col_btn:
        sim_btn = st.button("⚡ 仿真", key="sim_btn", use_container_width=True)
    
    st.markdown("**💡 一键试问：**")
    cols = st.columns(2)
    for i, es in enumerate(EXAMPLE_SIM):
        with cols[i % 2]:
            if st.button(f"⚡ {es}", key=f"sim_ex_{i}", use_container_width=True):
                sq = es
                sim_btn = True
    
    if sim_btn and sq:
        with st.spinner("🧮 硅智计算中..."):
            sim = circuit_sim(sq)
        st.markdown("**🔬 仿真结果：**")
        st.markdown(f'<div class="sim-box"><pre style="margin:0;color:#d4d4d4;">{sim}</pre></div>', unsafe_allow_html=True)
    elif sim_btn:
        st.warning("请先输入问题")

# ========== Tab 3: 看图 ==========
with tab3:
    st.markdown("#### 🖼️ 电路图识别 · Qwen-VL 多模态")
    
    up = st.file_uploader("上传电路图（PNG / JPG / JPEG）", type=["png", "jpg", "jpeg"])
    qimg = st.text_input("追问（可选）：", placeholder="如：增益怎么算？", key="img_input")
    
    if up:
        # 显示上传的图
        st.image(up, caption="已上传电路图", use_container_width=True)
        if st.button("🔍 识别", use_container_width=True):
            tmp = Path("assets/_uploaded.png")
            tmp.parent.mkdir(exist_ok=True)
            tmp.write_bytes(up.read())
            with st.spinner("🖼️ 硅智识别中..."):
                desc = vl_analyze(str(tmp), qimg)
            st.markdown("**📋 识别结果：**")
            st.markdown(f'<div class="answer-box">{desc}</div>', unsafe_allow_html=True)
    else:
        st.info("👆 上传一张电路图开始体验")

# ========== Tab 4: 知识图谱 ==========
with tab4:
    st.markdown("#### 🕸️ 学科知识图谱 · 元件-原理-应用 三层关系")
    
    kg_html = Path("assets/kg.html")
    if kg_html.exists():
       kg_size = kg_html.stat().st_size / 1024
       st.success(f"✅ 知识图谱已生成（{kg_size:.0f} KB）· 451 节点 / 634 关系")
       col1, col2 = st.columns(2)
       with col1:
           if st.button("🚀 启动本地服务器", use_container_width=True):
               # 用 socket 判断端口是否已被占用（比查进程稳得多）
               import socket
               def is_port_in_use(port):
                   with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                       return s.connect_ex(('localhost', port)) == 0

               if is_port_in_use(8765):
                   st.info("服务器已在运行")
               else:
                   subprocess.Popen(
                       ["python", "-m", "http.server", "8765"],
                       cwd="assets",
                       creationflags=subprocess.CREATE_NO_WINDOW
                   )
                   time.sleep(1)
                   st.success("✅ 服务器已启动")
           else:
             st.info("服务器已在运行")
       with col2:
            st.link_button("🕸️ 打开知识图谱", "http://localhost:8765/kg.html", use_container_width=True)      
            st.info("💡 启动本地服务器，再打开图谱鼠标拖动节点、滚轮缩放、点击边看关系标签")
    else:
      st.warning("⚠️ 知识图谱还没生成")
      st.code("python src/kg/kg_build.py\npython src/kg/kg_viz.py", language="bash")
# ============== 页脚 ==============
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; font-size: 0.85rem;">
🔬 硅智 SiliconMind · 2026 人工智能算法精英大赛 · AI+学科交叉参赛作品
</div>
""", unsafe_allow_html=True)















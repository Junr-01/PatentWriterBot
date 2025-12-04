import streamlit as st
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent.agent import run_patentbot_async_stream, init_patentbot
from agent.agent import shoud_stop

def _get_status_icon(status: str) -> str:
    """根据状态返回对应的图标"""
    status_map = {
        "pending": "⏳",
        "in_progress": "🔄",
        "completed": "✅",
        "cancelled": "❌",
    }
    return status_map.get(status.lower(), "📋")

def _get_status_color(status: str) -> str:
    """根据状态返回对应的颜色"""
    status_map = {
        "pending": "gray",
        "in_progress": "blue",
        "completed": "green",
        "cancelled": "red",
    }
    return status_map.get(status.lower(), "gray")

# 页面配置
st.set_page_config(
    page_title="专利写作Bot",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="expanded"
)

# 标题
st.title("📝 专利写作机器人")

# 初始化 session state
if 'uploaded_file_name' not in st.session_state:
    st.session_state.uploaded_file_name = None
if 'generation_status' not in st.session_state:
    st.session_state.generation_status = None
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'is_generating' not in st.session_state:
    st.session_state.is_generating = False

# 组件1：模型选择下拉框
st.header("模型选择")
model_options = ['deepseek-chat', 'gpt-5', 'gpt-5-mini']
selected_model = st.selectbox(
    "请选择模型",
    options=model_options,
    index=0,  # 默认选择 'deepseek-chat'
    help="选择用于生成专利的 AI 模型"
)

# API Key 输入（根据模型选择显示不同的输入框）
st.header("API 配置")

# 根据选择的模型显示相应的 API key 输入框
if selected_model == 'deepseek-chat':
    api_key_label = "DeepSeek API Key"
    api_key_help = "请输入您的 DeepSeek API Key。如果没有，请访问 https://platform.deepseek.com/ 获取。"
    env_key_name = "DEEPSEEK_API_KEY"
elif selected_model in ['gpt-5', 'gpt-5-mini']:
    api_key_label = "OpenAI API Key"
    api_key_help = "请输入您的 OpenAI API Key。如果没有，请访问 https://platform.openai.com/ 获取。"
    env_key_name = "OPENAI_API_KEY"
else:
    api_key_label = "API Key"
    api_key_help = "请输入 API Key"
    env_key_name = "API_KEY"

# 从环境变量读取默认值（如果存在）
default_api_key = os.getenv(env_key_name, "")

# API Key 输入框
api_key = st.text_input(
    api_key_label,
    value=st.session_state.get(f'api_key_{selected_model}', default_api_key),
    type="password",
    help=api_key_help,
    placeholder="请输入API Key，按回车输入！！！"
)

if st.session_state.is_generating:
    shoud_stop()
    st.session_state.is_generating = False

# 保存到 session state
st.session_state[f'api_key_{selected_model}'] = api_key

# 显示 API Key 状态
if api_key:
    # 设置环境变量
    if api_key != default_api_key:
        os.environ[env_key_name] = api_key
    #初始化模型及代理
    init_patentbot(model_name=selected_model)

    st.success(f"✅ {api_key_label} 已配置")
    # 显示部分 API Key（前4位和后4位）
    masked_key = api_key[:4] + "..." + api_key[-4:] if len(api_key) > 8 else "****"
    st.caption(f"当前配置: {masked_key}")
else:
    st.warning(f"⚠️ 请配置 {api_key_label}")

# 组件2：文件上传
st.header("文件上传")
uploaded_file = st.file_uploader(
    "选择技术交底书文件",
    type=['docx', 'doc', 'txt', 'md'],
    help="上传技术交底书文件，支持word, pdf等"
)

if uploaded_file is None:
    st.session_state.uploaded_file_name = None
    if st.session_state.is_generating:
        shoud_stop()
        st.session_state.is_generating = False
else:
    # 确保目标目录存在
    upload_dir = project_root / "workspace" / "data"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存文件
    file_path = upload_dir / uploaded_file.name
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # 如果上传了新文件，清除之前的生成状态
    if st.session_state.uploaded_file_name != uploaded_file.name:
        st.session_state.generation_status = None
        if st.session_state.is_generating:
            shoud_stop()
            st.session_state.is_generating = False
    
    st.session_state.uploaded_file_name = uploaded_file.name
    st.success(f"✅ 文件已上传: {uploaded_file.name}")
    
    # 显示文件信息
    st.info(f"📄 文件名: {uploaded_file.name}\n📊 文件大小: {uploaded_file.size / 1024:.2f} KB")

# 组件3：生成专利按钮
st.header("生成专利")
if st.session_state.uploaded_file_name:
    # 检查 API Key 是否已配置
    if not st.session_state[f'api_key_{selected_model}']:
        st.error(f"❌ 请先配置api key!!!")
    else:
        # 按钮区域
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button(
                "🚀 开始生成专利",
                type="primary",
                use_container_width=True,
                disabled=st.session_state.get('is_generating', False)
            ):
                st.session_state.generation_status = None
                st.session_state.is_generating = True
                

        with col2:
            if st.button(
                "⏹️ 停止生成专利",
                type="secondary",
                use_container_width=True,
                disabled=not st.session_state.get('is_generating', False)
            ):
                #让后端线程结束运行
                shoud_stop()
                st.session_state.generation_status = None
                st.session_state.is_generating = False
                
        
        # 如果正在生成，执行生成逻辑
        if st.session_state.is_generating:
            # 创建用于显示任务列表的容器
            progress_container = st.container()
            result_container = st.empty()
            error_container = st.empty()
            
            try:
                with progress_container:
                    st.subheader("📋 任务进展")
                    todo_placeholder = st.empty()
                    messages = []
                    current_todos = {}
                    
                    for chunk in run_patentbot_async_stream(st.session_state.uploaded_file_name):
                        todo_list = []
                        for step, data in chunk.items():
                            if step == "tools" and data.get("todos"):
                                todo_list = [(item["content"], item["status"]) for item in data.get("todos")]
                            if step == "model" and data.get("messages"):
                                messages += data.get("messages")
                        
                        # 更新任务列表（使用最新的 todo_list 覆盖）
                        if todo_list:
                            current_todos.clear()
                            for content, status in todo_list:
                                current_todos[content] = status
                        
                        # 实时更新显示当前任务列表
                        with todo_placeholder.container():
                            # 计算进度
                            total = len(current_todos)
                            completed = sum(1 for s in current_todos.values() if s.lower() == "completed")
                            in_progress = sum(1 for s in current_todos.values() if s.lower() == "in_progress")
                            pending = sum(1 for s in current_todos.values() if s.lower() == "pending")
                            
                            # 显示进度条
                            progress = completed / total if total > 0 else 0
                            st.progress(progress, text=f"进度: {completed}/{total} 已完成 | {in_progress} 进行中 | {pending} 待处理")
                            
                            # 显示任务列表（按照原始顺序显示）
                            st.markdown("#### 任务列表")
                            for content, status in todo_list:
                                icon = _get_status_icon(status)
                                color = _get_status_color(status)
                                status_text = {
                                    "pending": "待处理",
                                    "in_progress": "进行中",
                                    "completed": "已完成",
                                    "cancelled": "已取消",
                                }.get(status.lower(), status)
                                
                                # 使用更清晰的显示方式
                                if status.lower() == "in_progress":
                                    st.markdown(f"{icon} **{content}** - <span style='color: {color}; font-weight: bold'>{status_text}</span>", 
                                                unsafe_allow_html=True)
                                else:
                                    st.markdown(f"{icon} {content} - <span style='color: {color}'>{status_text}</span>", 
                                                unsafe_allow_html=True)
                # 生成完成后显示结果
                # 检查所有任务是否全部完成
                all_completed = True
                if current_todos:
                    for status in current_todos.values():
                        if status.lower() != "completed":
                            all_completed = False
                            break
                else:
                    all_completed = False
                
                # 根据任务完成情况显示相应消息和结果
                with result_container.container():
                    if all_completed:
                        st.session_state.generation_status = "success"
                        st.success("✅ 专利生成完成！")
                    else:
                        st.session_state.generation_status = "error"
                        st.error("❌ 专利生成失败！")
                    
                    # 显示最后一条消息的内容
                    if messages:
                        st.markdown("---")
                        st.markdown("### 📄 生成结果")
                        # 获取最后一条消息的内容
                        last_message = messages[-1]
                        content = last_message.content
                        # 显示内容
                        st.markdown(content)
                # 重置生成状态
                st.session_state.is_generating = False
                            
            except Exception as e:
                st.session_state.generation_status = "error"
                st.session_state.is_generating = False
                result_container.error(f"❌ 生成专利时出错: {str(e)}")
                with error_container:
                    st.exception(e)
else:
    st.warning("⚠️ 请先上传技术交底书文件")

# 侧边栏信息
with st.sidebar:
    st.header("📋 使用说明")
    st.markdown("""
    1. **选择模型**: 从下拉框中选择要使用的 AI 模型
    2. **配置 API Key**: 根据选择的模型输入相应的 API Key
    3. **上传文件**: 上传技术交底书文件（支持word, pdf等）
    4. **生成专利**: 点击"开始生成专利"按钮开始处理
    
    ### 支持的模型
    - **deepseek-chat**（默认）
    - **gpt-5**、**gpt-5-mini**
    """)


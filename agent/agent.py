import asyncio
import queue
import threading

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain.agents.middleware.todo import TodoListMiddleware
from langchain.agents.middleware import ToolRetryMiddleware

from agent.prompts import leader_agent_prompt
from agent.prompts import todo_prompt

from agent.utils.subagent_tools import call_input_parser_subagent, call_patent_searcher_subagent
from agent.utils.subagent_tools import call_outline_generator_subagent, call_abstract_writer_subagent, call_claims_writer_subagent
from agent.utils.subagent_tools import call_description_writer_part1_subagent, call_description_writer_part2_subagent, call_diagram_generator_subagent
from agent.utils.subagent_tools import call_markdown_merger_subagent
from agent.utils.subagent_tools import init_subagents

from agent.utils.tools import get_filesystem_tools

from agent.utils import llm_model
from agent.utils.llm_model import update_llm_model

import time

leader_agent = None

finished = threading.Event()
stopped = threading.Event()

def shoud_stop():
    stopped.set()

def init_leader_agent():
    global leader_agent
    _filesystem_tools = get_filesystem_tools()
    _subagents_tool = [
    call_input_parser_subagent,
    call_patent_searcher_subagent,
    call_outline_generator_subagent,
    call_abstract_writer_subagent,
    call_claims_writer_subagent,
    call_description_writer_part1_subagent,
    call_description_writer_part2_subagent,
    call_diagram_generator_subagent,
    call_markdown_merger_subagent,
    ]

    leader_agent = create_agent(
        model=llm_model.llm_temp_high,
        tools=_filesystem_tools + _subagents_tool,
        middleware=[
            TodoListMiddleware(
                system_prompt=todo_prompt.sys_prompt,
                tool_description=todo_prompt.tool_prompt
            ),
            ToolRetryMiddleware(
                max_retries=0,
            )
        ],
    )

async def _astream_call_patentbot(file_name: str):
    timestamp = int(time.time())
    query = f"将技术交底书 '{file_name}' 生成专利，项目的uuid为{str(timestamp)}"
    messages = [HumanMessage(content=query), HumanMessage(content=leader_agent_prompt.prompt)]
    async for chunk in leader_agent.astream({"messages": messages}, stream_mode="updates"):
        yield chunk#[(item["content"], item["status"]) for item in data.get("todos")]

def run_patentbot_async_stream(file_name: str):
    """
    运行异步流式生成器，实时转换为同步生成器
    
    Args:
        file_name: 文件名
        should_stop_func: 停止检查函数，返回 True 时停止生成
    """
    # 使用队列来在线程间传递数据
    chunk_queue = queue.Queue()
    exception_queue = queue.Queue()
    finished.clear()
    stopped.clear()

    async def _stream():
        """异步流式处理函数"""
        try:
            async for chunk in _astream_call_patentbot(file_name):
                chunk_queue.put(chunk)
            finished.set()
        except Exception as e:
            exception_queue.put(e)
    
    async def _run_async():
        task = asyncio.create_task(_stream())
        while not finished.is_set() and not stopped.is_set():
            await asyncio.sleep(0)
        if stopped.is_set():
            task.cancel()
        
    
    def _main_async():
        asyncio.run(_run_async())
    
    # 在后台线程中运行异步函数
    thread = threading.Thread(target=_main_async, daemon=True)
    thread.start()
    
    # 实时 yield 队列中的数据
    while not finished.is_set() or not chunk_queue.empty():
        try:
            # 非阻塞获取数据，超时时间 0.1 秒
            chunk = chunk_queue.get(timeout=0.1)
            yield chunk
        except queue.Empty:
            # 如果队列为空，检查是否有异常
            if not exception_queue.empty():
                raise exception_queue.get()
            # 如果已停止，退出循环
            if stopped.is_set():
                break
            # 继续等待
            time.sleep(0.05)

def init_patentbot(model_name: str = "deepseek-chat"):
    update_llm_model(model_name)
    init_leader_agent()
    init_subagents()


if __name__ == "__main__":
    ...
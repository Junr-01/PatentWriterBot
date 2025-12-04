from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from langchain.agents.middleware.todo import TodoListMiddleware
from langchain.agents.middleware import ToolRetryMiddleware

from agent.prompts import input_parser_prompt, patent_searcher_prompt, outline_generator_prompt, abstract_writer_prompt
from agent.prompts import todo_prompt, claims_writer_prompt, description_writer_prompt, diagram_generator_prompt, markdown_merger_prompt

from agent.utils.tools import get_filesystem_tools, get_markitdown_tools, get_google_patent_search_tools, get_learn_skills_tools

from agent.utils import llm_model

input_parser_subagent = None
patent_searcher_subagent = None
outline_generator_subagent = None
abstract_writer_subagent = None
claims_writer_subagent = None
description_writer_part1_subagent = None
description_writer_part2_subagent = None
diagram_generator_subagent = None
markdown_merger_subagent = None

def init_subagents():
    global input_parser_subagent, patent_searcher_subagent, outline_generator_subagent
    global abstract_writer_subagent, claims_writer_subagent, description_writer_part1_subagent
    global description_writer_part2_subagent, diagram_generator_subagent, markdown_merger_subagent

    filesystem_tools = get_filesystem_tools()
    markitdown_tools = get_markitdown_tools()
    google_patent_search_tools = get_google_patent_search_tools()
    learn_skills_tools = get_learn_skills_tools()

    input_parser_subagent = create_agent(
        model=llm_model.llm_temp_high,
        tools=filesystem_tools+markitdown_tools,
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
    patent_searcher_subagent = create_agent(
        model=llm_model.llm_temp_high,
        tools=filesystem_tools+markitdown_tools+google_patent_search_tools,
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
    outline_generator_subagent = create_agent(
        model=llm_model.llm_temp_high,
        tools=filesystem_tools + learn_skills_tools,
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
    abstract_writer_subagent = create_agent(
        model=llm_model.llm_temp_high,
        tools=filesystem_tools + learn_skills_tools,
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
    claims_writer_subagent = create_agent(
        model=llm_model.llm_temp_high,
        tools=filesystem_tools + learn_skills_tools,
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
    description_writer_part1_subagent = create_agent(
        model=llm_model.llm_temp_high,
        tools=filesystem_tools + learn_skills_tools,
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
    description_writer_part2_subagent = create_agent(
        model=llm_model.llm_temp_high,
        tools=filesystem_tools + learn_skills_tools,
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
    diagram_generator_subagent = create_agent(
        model=llm_model.llm_temp_low,
        tools=filesystem_tools + learn_skills_tools,
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
    markdown_merger_subagent = create_agent(
        model=llm_model.llm_temp_high,
        tools=filesystem_tools + learn_skills_tools,
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

@tool(
    "input_parser",
    parse_docstring=True
)
async def call_input_parser_subagent(job_content: str) -> str:
    """解析输入文档，提取结构化信息.

    Args:
        job_content: 委托的任务内容
    """
    messages = [HumanMessage(content=job_content), HumanMessage(content=input_parser_prompt.prompt)]
    result = await input_parser_subagent.ainvoke({
        "messages": messages
    })
    return result["messages"][-1].content


@tool(
    "patent_searcher",
    parse_docstring=True
)
async def call_patent_searcher_subagent(job_content: str):
    """搜索相似专利，并进行分析总结.

    Args:
        job_content: 委托的任务内容
    """
    messages = [HumanMessage(content=job_content), HumanMessage(content=patent_searcher_prompt.prompt)]
    result = await patent_searcher_subagent.ainvoke({
        "messages": messages
    })
    return result["messages"][-1].content


@tool(
    "outline_generator",
    parse_docstring=True
)
async def call_outline_generator_subagent(job_content: str) -> str:
    """生成专利的大纲.

    Args:
        job_content: 委托的任务内容
    """
    messages = [HumanMessage(content=job_content), HumanMessage(content=outline_generator_prompt.prompt)]
    result = await outline_generator_subagent.ainvoke({
        "messages": messages
    })
    return result["messages"][-1].content



@tool(
    "abstract_writer",
    parse_docstring=True
)
async def call_abstract_writer_subagent(job_content: str) -> str:
    """撰写专利的摘要.

    Args:
        job_content: 委托的任务内容
    """
    messages = [HumanMessage(content=job_content), HumanMessage(content=abstract_writer_prompt.prompt)]
    result = await abstract_writer_subagent.ainvoke({
        "messages": messages
    })
    return result["messages"][-1].content




@tool(
    "claims_writer",
    parse_docstring=True
)
async def call_claims_writer_subagent(job_content: str) -> str:
    """撰写专利的权利要求书.

    Args:
        job_content: 委托的任务内容
    """
    messages = [HumanMessage(content=job_content), HumanMessage(content=claims_writer_prompt.prompt)]
    result = await claims_writer_subagent.ainvoke({
        "messages": messages
    })
    return result["messages"][-1].content


@tool(
    "description_writer_part1",
    parse_docstring=True
)
async def call_description_writer_part1_subagent(job_content: str) -> str:
    """撰写专利的说明书 part1：技术领域、背景技术、发明内容、附图说明.

    Args:
        job_content: 委托的任务内容
    """
    messages = [HumanMessage(content=job_content), HumanMessage(content=description_writer_prompt.prompt_part1)]
    result = await description_writer_part1_subagent.ainvoke({
        "messages": messages
    })
    return result["messages"][-1].content



@tool(
    "description_writer_part2",
    parse_docstring=True
)
async def call_description_writer_part2_subagent(job_content: str) -> str:
    """撰写专利的说明书 part2：具体实施方式.

    Args:
        job_content: 委托的任务内容
    """
    messages = [HumanMessage(content=job_content), HumanMessage(content=description_writer_prompt.prompt_part2)]
    result = await description_writer_part2_subagent.ainvoke({
        "messages": messages
    })
    return result["messages"][-1].content


@tool(
    "diagram_generator",
    parse_docstring=True
)
async def call_diagram_generator_subagent(job_content: str) -> str:
    """撰写专利的说明书附图.

    Args:
        job_content: 委托的任务内容
    """
    messages = [HumanMessage(content=job_content), HumanMessage(content=diagram_generator_prompt.prompt)]
    result = await diagram_generator_subagent.ainvoke({
        "messages": messages
    })
    return result["messages"][-1].content


@tool(
    "markdown_merger",
    parse_docstring=True
)
async def call_markdown_merger_subagent(job_content: str) -> str:
    """生成完整专利，撰写专利分析报告.

    Args:
        job_content: 委托的任务内容
    """
    messages = [HumanMessage(content=job_content), HumanMessage(content=markdown_merger_prompt.prompt)]
    result = await markdown_merger_subagent.ainvoke({
        "messages": messages
    })
    return result["messages"][-1].content
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("learn_skills")

@mcp.tool()
def learn_skills_mermaid() -> str:
    """mermaid画图技能"""
    # 获取当前文件所在目录
    current_dir = Path(__file__).parent
    skills_dir = current_dir / "skills"
    
    # 读取两个文件
    flowchart_file = skills_dir / "mermaid_flowchart.md"
    sequence_file = skills_dir / "mermaid_sequence_diagram.md"
    
    try:
        flowchart_content = flowchart_file.read_text(encoding='utf-8')
        sequence_content = sequence_file.read_text(encoding='utf-8')
        
        # 合并内容并返回
        return f"# Mermaid Flowchart 语法\n\n{flowchart_content}\n\n# Mermaid Sequence Diagram 语法\n\n{sequence_content}"
    except FileNotFoundError as e:
        return f"文件未找到: {e}"
    except Exception as e:
        return f"读取失败: {e}"

@mcp.tool()
def learn_skills_patent_writing() -> str:
    """专利写作技能"""
    # 获取当前文件所在目录
    current_dir = Path(__file__).parent
    skills_dir = current_dir / "skills"
    
    # 读取两个文件
    patent_writing_file = skills_dir / "patent_guide.md"
    
    try:
        patent_writing_content = patent_writing_file.read_text(encoding='utf-8')
        return patent_writing_content
    except FileNotFoundError as e:
        return f"文件未找到: {e}"
    except Exception as e:
        return f"读取失败: {e}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
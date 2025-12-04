# filesystem.py
import json
import shutil
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("filesystem")

def _return_work_path():
    project_root = Path(__file__).parent.parent
    output_dir = project_root / "workspace"
    output_dir.mkdir(parents=True, exist_ok=True)
    return str(output_dir)

def _check_path_permission(path: Path) -> tuple[bool, str]:
    """检查路径是否在工作目录下
    
    Returns:
        (是否通过, 错误信息)
    """
    work_path = Path(_return_work_path()).resolve()
    target_path = path.resolve()
    
    try:
        # 检查目标路径是否是工作目录的子路径
        target_path.relative_to(work_path)
        return True, ""
    except ValueError:
        return False, f"没有权限，不在工作目录{work_path}下"

@mcp.tool()
def return_work_path():
    """返回工作目录的绝对路径"""
    return "当前工作目录的绝对路径: " + _return_work_path()

@mcp.tool()
def list_directory(path: str) -> str:
    """列举指定目录的文件

    Args:
        path: 绝对路径
    """
    target = Path(path).expanduser().resolve()
    has_permission, error_msg = _check_path_permission(target)
    if not has_permission:
        return error_msg
    if not target.exists():
        return f"路径不存在: {target}"
    if not target.is_dir():
        return f"不是一个目录: {target}"

    def describe(entry: Path) -> str:
        if entry.is_dir():
            kind = "目录"
        elif entry.is_file():
            kind = "文件"
        elif entry.is_symlink():
            kind = "符号链接"
        else:
            kind = "其他"
        return f"{entry.name}\t{kind}"

    entries = [describe(item) for item in target.iterdir()]
    return "\n".join(entries)

@mcp.tool()
def create_directory(path: str, dire_name: str) -> str:
    """指定路径创建目录
    
    Args:
        path: 绝对路径
        dire_name: 目录名称
    """
    base = Path(path).expanduser().resolve()
    has_permission, error_msg = _check_path_permission(base)
    if not has_permission:
        return error_msg
    if not base.exists():
        return f"路径不存在: {base}"
    if not base.is_dir():
        return f"路径不存在: {base}"

    target = base / dire_name
    if target.exists():
        return f"创建失败，目录以存在: {target}"

    try:
        target.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        return f"创建失败，目录以存在: {target}"
    except OSError as exc:
        return f"创建失败: {target} {exc}"

    return f"目录创建成功: {target}"

@mcp.tool()
def delete_directory(path: str, dire_name: str) -> str:
    """指定路径删除目录
    
    Args:
        path: 绝对路径
        dire_name: 目录名称
    """
    base = Path(path).expanduser().resolve()
    has_permission, error_msg = _check_path_permission(base)
    if not has_permission:
        return error_msg
    if not base.exists():
        return f"路径不存在: {base}"
    if not base.is_dir():
        return f"路径不存在: {base}"
    
    target = base / dire_name
    if not target.exists():
        return f"删除失败，目录不存在: {target}"
    if not target.is_dir():
        return f"删除失败，目录不存在: {target}"
    
    try:
        shutil.rmtree(target)
    except OSError as exc:
        return f"删除失败: {target} {exc}"
    
    return f"目录删除成功: {target}"

@mcp.tool()
def write_file_json(path_to_file: str, content: dict) -> str:
    """将内容写入指定路径（json格式）
    
    Args:
        path_to_file: 写入文件的路径（json格式）
        content: 内容
    """
    target = Path(path_to_file).expanduser().resolve()
    has_permission, error_msg = _check_path_permission(target)
    if not has_permission:
        return error_msg
    
    # 检查文件后缀是否为json
    if target.suffix.lower() != '.json':
        return f"文件类型非.json: {target}"
    
    # 确保父目录存在
    target.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(target, 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
        return f"文件写入成功: {target}"
    except Exception as exc:
        return f"写入失败: {target} {exc}"


@mcp.tool()
def read_file_json(path_to_file: str) -> str:
    """读取指定路径的.json文件
    
    Args:
        path_to_file: 文件路径（绝对路径）
    """
    base = Path(path_to_file).expanduser().resolve()
    has_permission, error_msg = _check_path_permission(base)
    if not has_permission:
        return error_msg
    if not base.exists():
        return f"路径不存在: {base}"
    if not base.is_file():
        return f"文件不存在: {base}"

    try:
        with open(base, 'r', encoding='utf-8') as f:
            return str(json.load(f))
    except Exception as exc:
        return f"读取失败: {base} {exc}"

@mcp.tool()
def read_file(path_to_file: str) -> str:
    """读取指定路径的文件

    Args:
        path_to_file: 文件路径（绝对路径）
    """
    target = Path(path_to_file).expanduser().resolve()
    has_permission, error_msg = _check_path_permission(target)
    if not has_permission:
        return error_msg
    if not target.exists():
        return f"路径不存在: {target}"
    if not target.is_file():
        return f"文件不存在: {target}"

    try:
        return target.read_text(encoding="utf-8")
    except Exception as exc:
        return f"读取失败: {target} {exc}"

@mcp.tool()
def write_file(path_to_file: str, content: str) -> str:
    """将内容写入指定文件
    
    Args:
        path_to_file: 写入文件的路径（绝对路径）
        content: 内容
    """
    target = Path(path_to_file).expanduser().resolve()
    has_permission, error_msg = _check_path_permission(target)
    if not has_permission:
        return error_msg
    
    # 确保父目录存在
    target.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        target.write_text(content, encoding='utf-8')
        return f"文件写入成功: {target}"
    except Exception as exc:
        return f"写入失败: {target} {exc}"

@mcp.tool()
def delete_file(path_to_file: str) -> str:
    """删除指定文件
    
    Args:
        path_to_file: 文件路径（绝对路径）
    """
    target = Path(path_to_file).expanduser().resolve()
    has_permission, error_msg = _check_path_permission(target)
    if not has_permission:
        return error_msg
    if not target.exists():
        return f"文件不存在: {target}"
    if not target.is_file():
        return f"不是文件: {target}"
    
    try:
        target.unlink()
        return f"文件删除成功: {target}"
    except Exception as exc:
        return f"删除失败: {target} {exc}"

@mcp.tool()
def append_file(path_to_file: str, content: str) -> str:
    """将内容追加到指定文件（文件不存在时创建）
    
    Args:
        path_to_file: 写入文件的路径（绝对路径）
        content: 内容
    """
    target = Path(path_to_file).expanduser().resolve()
    has_permission, error_msg = _check_path_permission(target)
    if not has_permission:
        return error_msg
    
    # 确保父目录存在
    target.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(target, 'a', encoding='utf-8') as f:
            f.write(content)
        return f"文件追加成功: {target}"
    except Exception as exc:
        return f"追加失败: {target} {exc}"

@mcp.tool()
def join_files(path_to_files: list[str], output_file: str) -> str:
    """
    将多个文件合并为一个文件，并保存到指定路径。合并顺序为path_to_files列表中的顺序。
    
    Args:
        path_to_files: 文件路径列表（绝对路径）
        output_file: 输出文件路径（绝对路径）
    """
    contents = []
    for file_path in path_to_files:
        target = Path(file_path).expanduser().resolve()
        has_permission, error_msg = _check_path_permission(target)
        if not has_permission:
            return error_msg
        if not target.exists():
            return f"文件不存在: {target}"
        if not target.is_file():
            return f"不是文件: {target}"
        try:
            contents.append(target.read_text(encoding='utf-8'))
        except Exception as exc:
            return f"读取失败: {target} {exc}"
    
    output = Path(output_file).expanduser().resolve()
    has_permission, error_msg = _check_path_permission(output)
    if not has_permission:
        return error_msg
    output.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        output.write_text('\n'.join(contents), encoding='utf-8')
        return f"文件合并成功: {output}"
    except Exception as exc:
        return f"写入失败: {output} {exc}"

@mcp.tool()
def copy_file(from_file_path: str, to_file_path: str) -> str:
    """将源文件拷贝至目标文件
    
    Args:
        from_file_path: 源文件路径（绝对路径）
        to_file_path: 目标文件路径（绝对路径）
    """
    source = Path(from_file_path).expanduser().resolve()
    has_permission, error_msg = _check_path_permission(source)
    if not has_permission:
        return error_msg
    if not source.exists():
        return f"源文件不存在: {source}"
    if not source.is_file():
        return f"源文件不存在: {source}"
    
    target = Path(to_file_path).expanduser().resolve()
    has_permission, error_msg = _check_path_permission(target)
    if not has_permission:
        return error_msg
    
    try:
        # 确保目标目录存在
        target.parent.mkdir(parents=True, exist_ok=True)
        # 拷贝文件
        shutil.copy2(source, target)
        return f"文件拷贝成功: {source} -> {target}"
    except Exception as exc:
        return f"拷贝失败: {exc}"

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
    
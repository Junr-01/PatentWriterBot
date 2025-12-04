from serpapi import GoogleSearch
from mcp.server.fastmcp import FastMCP
import os
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
mcp = FastMCP("google_patent_search")

@mcp.tool()
def search_patents(query: str, country: str, status: str,  sort: str, num: str) -> str:
    """google 专利搜索

    Args:
        query: 搜索关键词：请求格式为 (关键词1 OR 关键词2 OR ...)
        country: CN-中国、US-美国
        status: 专利状态：GRANT-授权状态，APPLICATION-申请状态
        sort: 排序方式：relevance-相关性, new-最新, old-最久
        num: 返回的结果数量，最小10，最大100
    Returns:
        搜索结果
    """
    
    if(SERPAPI_API_KEY == None):
        return "工具不可用，没有配置SERPAPI_API_KEY"
    
    if sort == 'relevance':
        sort = None
    
    params = {
        "api_key": SERPAPI_API_KEY,
        "engine": "google_patents",
        "q": query,
        "country": country,
        "status": status,
        "sort": sort,
        "num": num,
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    return str(results)
    

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
using System.Text;

namespace KoalaWiki.KoalaWarehouse;

/// <summary>
/// 文件树节点，用于构建节省tokens的树形结构
/// </summary>
public class FileTreeNode
{
    /// <summary>
    /// 节点名称
    /// </summary>
    public string Name { get; set; } = string.Empty;
    
    /// <summary>
    /// 节点类型：F=文件，D=目录
    /// </summary>
    public string Type { get; set; } = string.Empty;
    
    /// <summary>
    /// 子节点
    /// </summary>
    public Dictionary<string, FileTreeNode> Children { get; set; } = new();
    
    /// <summary>
    /// 是否为叶子节点（文件）
    /// </summary>
    public bool IsFile => Type == "F";
    
    /// <summary>
    /// 是否为目录节点
    /// </summary>
    public bool IsDirectory => Type == "D";
}

/// <summary>
/// 文件树构建器
/// </summary>
public static class FileTreeBuilder
{
    /// <summary>
    /// 从路径信息列表构建文件树，确保完整的目录结构
    /// </summary>
    /// <param name="pathInfos">路径信息列表</param>
    /// <param name="basePath">基础路径，用于计算相对路径</param>
    /// <returns>文件树根节点</returns>
    public static FileTreeNode BuildTree(List<PathInfo> pathInfos, string basePath)
    {
        var root = new FileTreeNode { Name = "/", Type = "D" };
        
        foreach (var pathInfo in pathInfos)
        {
            // 计算相对路径
            var relativePath = pathInfo.Path.Replace(basePath, "").TrimStart('\\', '/');
            
            // 过滤.开头的文件
            if (relativePath.StartsWith("."))
                continue;
                
            // 分割路径，确保处理空字符串
            var parts = relativePath.Split(['\\', '/'], StringSplitOptions.RemoveEmptyEntries);
            
            // 如果路径为空，跳过
            if (parts.Length == 0)
                continue;
            
            // 从根节点开始构建完整路径
            BuildPathInTree(root, parts, pathInfo.Type);
        }
        
        return root;
    }
    
    /// <summary>
    /// 在文件树中构建指定路径，确保所有中间目录都被创建
    /// </summary>
    /// <param name="root">根节点</param>
    /// <param name="pathParts">路径片段数组</param>
    /// <param name="finalType">最终节点类型（File 或 Directory）</param>
    private static void BuildPathInTree(FileTreeNode root, string[] pathParts, string finalType)
    {
        var currentNode = root;
        
        for (int i = 0; i < pathParts.Length; i++)
        {
            var part = pathParts[i];
            var isLastPart = i == pathParts.Length - 1;
            
            // 确定当前节点的类型
            string nodeType;
            if (isLastPart)
            {
                // 最后一个部分：根据传入的类型决定
                nodeType = finalType == "File" ? "F" : "D";
            }
            else
            {
                // 中间部分：肯定是目录
                nodeType = "D";
            }
            
            // 如果节点不存在，创建新节点
            if (!currentNode.Children.ContainsKey(part))
            {
                currentNode.Children[part] = new FileTreeNode
                {
                    Name = part,
                    Type = nodeType
                };
            }
            else
            {
                // 如果节点已存在，但类型可能需要更新
                // 例如：先遇到 "src/main.js"，后遇到 "src/" 目录
                var existingNode = currentNode.Children[part];
                
                // 如果现有节点是文件，但当前路径表明它应该是目录，则更新类型
                if (existingNode.IsFile && (!isLastPart || finalType != "File"))
                {
                    existingNode.Type = "D";
                }
                // 如果现有节点是目录，但当前是最后一个部分且应该是文件，保持目录类型
                // （因为目录的优先级高于文件）
            }
            
            currentNode = currentNode.Children[part];
        }
    }
    
    /// <summary>
    /// 将文件树转换为紧凑的字符串表示，确保完整构建所有目录层次
    /// 格式示例：
    /// /
    ///   server/D
    ///     src/D
    ///       Main/F
    ///   web/D
    ///     components/D
    ///       Header.tsx/F
    ///       Footer.tsx/F
    ///     pages/D
    ///       index.tsx/F
    /// </summary>
    /// <param name="node">文件树节点</param>
    /// <param name="indent">缩进级别</param>
    /// <returns>紧凑的字符串表示</returns>
    public static string ToCompactString(FileTreeNode node, int indent = 0)
    {
        var sb = new StringBuilder();
        var indentStr = new string(' ', indent * 2);
        
        // 根节点特殊处理
        if (indent == 0)
        {
            sb.AppendLine("/");
        }
        
        // 按照目录优先，然后按名称排序的方式遍历子节点
        var sortedChildren = node.Children
            .OrderBy(x => x.Value.IsFile)  // 目录在前，文件在后
            .ThenBy(x => x.Key)            // 按名称排序
            .ToList();
        
        foreach (var child in sortedChildren)
        {
            // 输出当前节点信息
            sb.AppendLine($"{indentStr}{child.Key}/{child.Value.Type}");
            
            // 如果是目录，无论是否有子节点都要递归处理，确保完整的目录结构
            if (child.Value.IsDirectory)
            {
                // 递归处理子目录，即使子目录为空也要保持结构
                var childContent = ToCompactString(child.Value, indent + 1);
                if (!string.IsNullOrEmpty(childContent.Trim()))
                {
                    sb.Append(childContent);
                }
            }
        }
        
        return sb.ToString();
    }
    
    /// <summary>
    /// 获取文件树的所有完整路径，用于验证结构完整性
    /// </summary>
    /// <param name="node">文件树节点</param>
    /// <param name="currentPath">当前路径</param>
    /// <returns>所有完整路径的列表</returns>
    public static List<string> GetAllPaths(FileTreeNode node, string currentPath = "")
    {
        var allPaths = new List<string>();
        
        foreach (var child in node.Children)
        {
            var childPath = string.IsNullOrEmpty(currentPath) 
                ? child.Key 
                : $"{currentPath}/{child.Key}";
                
            // 添加当前路径（目录也要记录）
            allPaths.Add($"{childPath}({child.Value.Type})");
            
            // 如果是目录，递归获取子路径
            if (child.Value.IsDirectory && child.Value.Children.Count > 0)
            {
                allPaths.AddRange(GetAllPaths(child.Value, childPath));
            }
        }
        
        return allPaths;
    }
    
    /// <summary>
    /// 将文件树转换为极度紧凑的JSON格式
    /// 使用单字符键名来最大化节省tokens
    /// </summary>
    /// <param name="node">文件树节点</param>
    /// <returns>JSON字符串</returns>
    public static string ToCompactJson(FileTreeNode node)
    {
        return System.Text.Json.JsonSerializer.Serialize(SerializeNodeCompact(node), new System.Text.Json.JsonSerializerOptions
        {
            WriteIndented = false,
            Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping,
        });
    }
    
    private static object SerializeNodeCompact(FileTreeNode node)
    {
        if (node.IsFile)
        {
            return "F"; // 文件只需要一个标识符
        }
        
        var result = new Dictionary<string, object>();
        
        foreach (var child in node.Children)
        {
            result[child.Key] = SerializeNodeCompact(child.Value);
        }
        
        return result;
    }
    
    /// <summary>
    /// 将文件树转换为路径列表格式（但去重了公共前缀）
    /// 适用于需要路径列表但希望减少冗余的场景
    /// </summary>
    /// <param name="node">文件树节点</param>
    /// <param name="currentPath">当前路径</param>
    /// <returns>路径列表</returns>
    public static List<string> ToPathList(FileTreeNode node, string currentPath = "")
    {
        var paths = new List<string>();
        
        foreach (var child in node.Children)
        {
            var childPath = string.IsNullOrEmpty(currentPath) 
                ? child.Key 
                : $"{currentPath}/{child.Key}";
                
            if (child.Value.IsFile)
            {
                paths.Add(childPath);
            }
            else
            {
                // 如果目录只有一个子节点，可以压缩路径
                if (child.Value.Children.Count == 1)
                {
                    var subPaths = ToPathList(child.Value, childPath);
                    paths.AddRange(subPaths);
                }
                else
                {
                    paths.Add($"{childPath}/");
                    var subPaths = ToPathList(child.Value, childPath);
                    paths.AddRange(subPaths);
                }
            }
        }
        
        return paths;
    }
    
    /// <summary>
    /// 将文件树转换为Unix风格的树形结构
    /// 类似于 Unix tree 命令的输出效果
    /// 使用 ├── 和 └── 等字符来构建可视化的树形结构
    /// </summary>
    /// <param name="node">文件树节点</param>
    /// <param name="prefix">当前行的前缀</param>
    /// <param name="isLast">是否为父节点的最后一个子节点</param>
    /// <returns>Unix风格的树形字符串</returns>
    public static string ToUnixTree(FileTreeNode node, string prefix = "", bool isLast = true)
    {
        var sb = new StringBuilder();
        
        // 根节点特殊处理
        if (string.IsNullOrEmpty(prefix))
        {
            sb.AppendLine(".");
            foreach (var child in node.Children.OrderBy(x => x.Value.IsFile).ThenBy(x => x.Key))
            {
                var isLastChild = child.Equals(node.Children.OrderBy(x => x.Value.IsFile).ThenBy(x => x.Key).Last());
                sb.Append(ToUnixTree(child.Value, "", isLastChild, child.Key));
            }
        }
        
        return sb.ToString();
    }
    
    /// <summary>
    /// Unix风格树形结构的递归实现
    /// </summary>
    private static string ToUnixTree(FileTreeNode node, string prefix, bool isLast, string nodeName)
    {
        var sb = new StringBuilder();
        
        // 当前节点的连接符
        var connector = isLast ? "└── " : "├── ";
        
        // 输出当前节点
        sb.AppendLine($"{prefix}{connector}{nodeName}{(node.IsDirectory ? "/" : "")}");
        
        // 如果是目录且有子节点，递归处理子节点
        if (node.IsDirectory && node.Children.Count > 0)
        {
            var childPrefix = prefix + (isLast ? "    " : "│   ");
            var sortedChildren = node.Children.OrderBy(x => x.Value.IsFile).ThenBy(x => x.Key).ToList();
            
            for (int i = 0; i < sortedChildren.Count; i++)
            {
                var child = sortedChildren[i];
                var isLastChild = i == sortedChildren.Count - 1;
                sb.Append(ToUnixTree(child.Value, childPrefix, isLastChild, child.Key));
            }
        }
        
        return sb.ToString();
    }
}
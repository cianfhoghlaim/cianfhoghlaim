using System.ComponentModel;
using System.Runtime.CompilerServices;
using System.Text.Json.Serialization;
using Microsoft.Extensions.AI;

namespace KoalaWiki.Tools;

public class FileTool(string gitPath, List<string>? files)
{
    private int _readTokens = 0;

    public async Task<string> ReadFileAsync(
        [Description("File Path")] string filePath)
    {
        try
        {
            // 检查是否已达到文件读取限制
            if (DocumentOptions.ReadMaxTokens > 0 &&
                _readTokens >= DocumentOptions.ReadMaxTokens)
            {
                return "FILE READ LIMIT EXCEEDED STOP reading files immediately and complete analysis ";
            }

            files?.Add(filePath);
            filePath = Path.Combine(gitPath, filePath.TrimStart('/'));
            Console.WriteLine($"Reading file: {filePath}");

            var info = new FileInfo(filePath);
            // 判断文件是否存在
            if (!info.Exists)
            {
                return $"File not found: {filePath}";
            }

            // 判断文件大小
            if (info.Length > 1024 * 100)
            {
                return $"File too large: {filePath} ({info.Length / 1024 / 100}KB)";
            }

            // 读取整个文件内容
            string content = await File.ReadAllTextAsync(filePath);

            _readTokens += TokenHelper.GetTokens(content);

            return content;
        }
        catch (Exception ex)
        {
            // 处理异常
            Console.WriteLine($"Error reading file: {ex.Message}");
            return $"Error reading file: {ex.Message}";
        }
    }


    public AITool Create()
    {
        return AIFunctionFactory.Create(ReadFileFromLineAsync, new AIFunctionFactoryOptions()
        {
            Name = "ReadFile"
        });
    }

    /// <summary>
    /// 从指定行数开始读取文件内容
    /// </summary>
    /// <returns></returns>
    [KernelFunction(name: "Read"),
     Description(
         """
         To read the code files under the repository, note that the current method can only read text files and the path format provided by the user is relative rather than absolute.
         Usage:
         - The filePath must be a relative directory provided by the user
         - By default, it reads up to 200 lines from the beginning of the file
         - You can choose to specify the line offset and limit (particularly useful for long files), but it is recommended not to provide these parameters to read the entire file
         - Any lines exceeding 200 characters will be truncated
         - You can call multiple tools in a single response. It is best to batch read multiple potentially useful files. It is best to batch read multiple potentially useful files.
         - If the file you read exists but is empty, you will receive a system alert warning instead of the file content.
         - Reading an non-existent file is also fine, and it will return an error.
         """)]
    public async Task<string> ReadFileFromLineAsync(
        [Description(
            "The Read File")]
        ReadFileItemInput? item)
    {
        // 检查是否已达到文件读取限制
        if (DocumentOptions.ReadMaxTokens > 0 &&
            _readTokens >= DocumentOptions.ReadMaxTokens)
        {
            return "\n\n<system-reminder>\n" +
                   "CRITICAL: FILE READ LIMIT EXCEEDED \n" +
                   "IMMEDIATE ACTION REQUIRED:\n" +
                   "• STOP reading files NOW\n" +
                   "• Use ONLY the information you have already gathered\n" +
                   "• Complete your analysis with existing data\n" +
                   "• Focus on generating final documentation\n" +
                   "Continued file reading will impact system performance and may violate usage policies.\n" +
                   "</system-reminder>";
        }

        return await ReadItem(item.FilePath, item.Offset, item.Limit);
    }


    public async Task<string> ReadItem(
        string filePath,
        int offset = 0,
        int limit = 200)
    {
        try
        {
            files?.Add(filePath);

            filePath = Path.Combine(gitPath, filePath.TrimStart('/'));
            Console.WriteLine(
                $"Reading file from line {offset}: {filePath} offset={offset}, limit={limit}");

            // 如果<0则读取全部
            if (offset < 0 && limit < 0)
            {
                limit = 2000;
            }

            if (limit > 2000)
            {
                limit = 2000;
            }

            // 如果endLine<0则读取到最后一行
            if (limit < 0)
            {
                limit = int.MaxValue;
            }

            // 先读取整个文件内容
            string fileContent = await File.ReadAllTextAsync(filePath);

            if (string.IsNullOrEmpty(fileContent))
            {
                // 返回警告
                return """
                       <system-warning>
                       The current file contains empty text content.
                       </system-warning>
                       """;
            }

            // 将压缩后的内容按行分割
            var lines = fileContent.Split('\n');

            // 如果offset大于文件总行数，则返回空
            if (offset >= lines.Length)
            {
                return $"No content to read from line {offset} in file: {filePath}";
            }

            // 计算实际读取的行数
            int actualLimit = Math.Min(limit, lines.Length - offset);
            // 读取指定行数的内容
            var resultLines = new List<string>();
            for (int i = offset; i < offset + actualLimit && i < lines.Length; i++)
            {
                // 如果行内容超过2000字符，则截断
                if (lines[i].Length > 2000)
                {
                    resultLines.Add(lines[i][..2000]);
                }
                else
                {
                    resultLines.Add(lines[i]);
                }
            }

            // 将结果行号从1开始
            var numberedLines = resultLines.Select((line, index) => $"{index + 1}: {line}").ToList();

            var content = string.Join("\n", numberedLines);
            _readTokens += TokenHelper.GetTokens(content);
            return content;
        }
        catch (Exception ex)
        {
            // 处理异常
            Console.WriteLine($"Error reading file: {ex.Message}");
            return $"Error reading file: {ex.Message}";
        }
    }
}

public class ReadFileItemInput
{
    [Description(
        "The relative address to be read")]
    [JsonPropertyName("filePath")]
    public string FilePath { get; set; }

    [Description(
        "The line number to start reading from. Only provide if the file is too large to read at once")]
    [JsonPropertyName("offset")]
    public int Offset { get; set; } = 0;

    [Description(
        "The number of lines to read. Only provide if the file is too large to read at once.")]
    [JsonPropertyName("limit")]
    public int Limit { get; set; } = 200;
}
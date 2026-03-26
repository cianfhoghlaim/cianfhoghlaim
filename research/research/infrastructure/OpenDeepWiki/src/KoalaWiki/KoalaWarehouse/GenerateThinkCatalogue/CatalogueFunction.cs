using System.ComponentModel;
using System.Text.Json.Serialization;
using Microsoft.Extensions.AI;
using Newtonsoft.Json.Linq;

namespace KoalaWiki.KoalaWarehouse.GenerateThinkCatalogue;

public class CatalogueFunction
{
    public List<AITool> Create()
    {
        return
        [
            AIFunctionFactory.Create(Write, new AIFunctionFactoryOptions()
            {
                Name = "Write"
            }),

            AIFunctionFactory.Create(Read, new AIFunctionFactoryOptions()
            {
                Name = "Read"
            }),

            AIFunctionFactory.Create(MultiEdit, new AIFunctionFactoryOptions()
            {
                Name = "MultiEdit"
            })
        ];
    }


    [KernelFunction("Write"), Description("""
                                          Generate and store the complete documentation structure JSON.
                                          Usage:
                                          - This tool overwrites the existing catalogue JSON.
                                          - Output MUST be valid JSON following the items/children schema.
                                          - Do NOT wrap JSON in code fences or tags.
                                          - Call this only when the JSON is complete and validated.
                                          - Use emojis only when explicitly requested by the user.
                                          """)]
    public string Write(
        [Description("The complete documentation structure JSON")]
        string json)
    {
        Content = json;
        if (string.IsNullOrWhiteSpace(Content))
        {
            return "<system-reminder>Content cannot be empty.</system-reminder>";
        }

        Content = Content.Trim();


        // Validate JSON integrity after edit
        try
        {
            JToken.Parse(Content);
        }
        catch (Exception exception)
        {
            return
                $"<system-reminder>Write rejected: resulting content is not valid JSON. Provide a more precise edit. Error Message:{exception.Message}</system-reminder>";
        }


        return "<system-reminder>Write successful</system-reminder>";
    }

    [KernelFunction("Read"), Description("""
                                         Read the currently stored catalogue JSON for verification.
                                         Usage:
                                         - Returns the entire stored JSON string.
                                         - If empty, a system reminder is returned.
                                         """)]
    public string Read()
    {
        if (string.IsNullOrWhiteSpace(Content))
        {
            return "<system-reminder>Catalogue is empty. Use Write to store JSON first.</system-reminder>";
        }

        return Content;
    }

    [KernelFunction("MultiEdit"), Description(
         """
         This is a tool that enables multiple revisions to be made to the content at once.It is based on the "Edit" tool and can help you efficiently perform multiple search and replace operations. When you need to edit the content multiple times, it is recommended to use this tool instead of the "Edit" tool.

         Before using this tool:

         Use the "Read" tool to understand the content and its background information.

         To make multiple file edits, provide the following:
         An array of edit operations to perform, where each edit contains:
            - old_string: The text to replace (must match the file contents exactly, including all whitespace and indentation)
            - new_string: The edited text to replace the old_string
            - replace_all: Replace all occurences of old_string. This parameter is optional and defaults to false.

         IMPORTANT:
         - All edits are applied in sequence, in the order they are provided
         - Each edit operates on the result of the previous edit
         - All edits must be valid for the operation to succeed - if any edit fails, none will be applied
         - This tool is ideal when you need to make several changes to different parts of the same file

         CRITICAL REQUIREMENTS:
         1. All edits follow the same requirements as the single Edit tool
         2. The edits are atomic - either all succeed or none are applied
         3. Plan your edits carefully to avoid conflicts between sequential operations

         WARNING:
         - The tool will fail if edits.old_string doesn't match the file contents exactly (including whitespace)
         - The tool will fail if edits.old_string and edits.new_string are the same
         - Since edits are applied in sequence, ensure that earlier edits don't affect the text that later edits are trying to find

         When making edits:
         - Ensure all edits result in idiomatic, correct code
         - Only use emojis if the user explicitly requests it. Avoid adding emojis to files unless asked.
         - Use replace_all for replacing and renaming strings across the file. This parameter is useful if you want to rename a variable for instance.
         """)]
    public string MultiEdit(
        [Description("Array of edit operations to perform sequentially on")]
        MultiEditInput[] edits)
    {
        if (string.IsNullOrWhiteSpace(Content))
        {
            return "<system-reminder>Catalogue is empty. Write content first.</system-reminder>";
        }

        if (edits == null || edits.Length == 0)
        {
            return "<system-reminder>No edits provided.</system-reminder>";
        }

        // Validate all edits before applying any
        for (int i = 0; i < edits.Length; i++)
        {
            var edit = edits[i];

            if (string.IsNullOrEmpty(edit.OldString))
            {
                return $"<system-reminder>Edit {i + 1}: Old string cannot be empty.</system-reminder>";
            }

            if (edit.OldString == edit.NewString)
            {
                return
                    $"<system-reminder>Edit {i + 1}: New string must be different from old string.</system-reminder>";
            }
        }

        // Apply edits sequentially
        string currentContent = Content;

        for (int i = 0; i < edits.Length; i++)
        {
            var edit = edits[i];

            if (!currentContent.Contains(edit.OldString))
            {
                return $"<system-reminder>Edit {i + 1}: Old string not found in catalogue.</system-reminder>";
            }

            if (!edit.ReplaceAll && currentContent.Split(new[] { edit.OldString }, StringSplitOptions.None).Length > 2)
            {
                return
                    $"<system-reminder>Edit {i + 1}: Old string is not unique. Use replaceAll=true or provide a longer unique string.</system-reminder>";
            }

            // Apply the edit
            if (edit.ReplaceAll)
            {
                currentContent = currentContent.Replace(edit.OldString, edit.NewString);
            }
            else
            {
                var index = currentContent.IndexOf(edit.OldString, StringComparison.Ordinal);
                currentContent = currentContent.Substring(0, index) + edit.NewString +
                                 currentContent.Substring(index + edit.OldString.Length);
            }
        }

        // Validate JSON integrity after all edits
        try
        {
            JToken.Parse(currentContent);
        }
        catch (Exception exception)
        {
            return
                $"<system-reminder>MultiEdit rejected: resulting content is not valid JSON. Provide more precise edits. Error Message:{exception.Message}</system-reminder>";
        }

        Content = currentContent;
        return "<system-reminder>MultiEdit successful</system-reminder>";
    }

    public string? Content { get; private set; }
}

public class MultiEditInput
{
    [JsonPropertyName("old_string"), Description("The text to replace")]
    public string OldString { get; set; }

    [JsonPropertyName("new_string"), Description("The text to replace it with")]
    public string NewString { get; set; }

    [JsonPropertyName("replace_all"), Description("Replace all occurences of old_string (default false).")]
    public bool ReplaceAll { get; set; } = false;
}
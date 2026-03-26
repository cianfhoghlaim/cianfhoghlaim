using KoalaWiki.Core.Extensions;

namespace KoalaWiki.KoalaWarehouse;

public static class Prompt
{
    private static readonly string _language = "简体中文";

    static Prompt()
    {
        // 获取环境变量
        var language = Environment.GetEnvironmentVariable("LANGUAGE").GetTrimmedValueOrEmpty();
        if (!string.IsNullOrEmpty(language))
        {
            _language = language;
        }
        
        Console.WriteLine("当前语言环境：" + _language);
    }

    public static string Language => $"\nNote: You must reply in {_language}.\n";

    public static readonly string AnalyzeNewCatalogue =
        """
        You are an expert AI assistant specialized in incremental document structure analysis for code repositories. Your task is to perform precise, conservative updates to existing documentation based on code changes while preserving valuable content.

        ## Input Data Analysis

        Analyze the following information systematically:

        1. **Repository Structure**:
        <repository_structure>
        {{catalogue}}
        </repository_structure>

        2. **Repository Information**:
        <repository_info>
        {{git_repository}}
        </repository_info>

        3. **Git Changes**:
        <git_update>
        {{git_commit}}
        </git_update>

        4. **Current Document Structure**:
        <existing_document_structure>
        {{document_catalogue}}
        </existing_document_structure>

        ## Analysis Framework

        Perform your analysis using this systematic approach:

        <repository_change_analysis>

        ### 1. Change Classification
        For each file change, categorize by:
        - **Scope**: Core functionality, configuration, tests, documentation, dependencies
        - **Impact Level**: Critical (API changes, architecture), Moderate (new features, refactoring), Minor (bug fixes, formatting)
        - **Documentation Relevance**: High (user-facing changes), Medium (internal changes affecting understanding), Low (implementation details)

        ### 2. File Change Impact Assessment
        For each modified file:
        - **File**: [path/filename]
        - **Change Type**: Added/Modified/Deleted/Renamed
        - **Scope**: [Core/Config/Test/Docs/Dependencies]
        - **Impact Level**: [Critical/Moderate/Minor]
        - **Documentation Relevance**: [High/Medium/Low]
        - **Existing Section Mapping**: [List affected document sections by ID]
        - **Change Justification**: [Specific reason why documentation needs updating]
        - **Content Delta**: [What specific information needs to be added/modified]

        ### 3. Documentation Impact Analysis
        - **New Sections Required**: Only for significant new functionality or architectural changes
        - **Updates Required**: For existing sections with changed functionality
        - **Content Preservation**: Identify valuable existing content that should be retained
        - **Cross-Section Dependencies**: Analyze how changes affect related documentation sections

        ### 4. Deletion Safety Assessment
        Apply these strict criteria before marking any section for deletion:
        - **Obsolescence Verification**: Confirm the documented functionality no longer exists in codebase
        - **Reference Analysis**: Check for references to this section from other documentation
        - **User Impact**: Assess potential impact on documentation users
        - **Recovery Difficulty**: Consider if the information would be difficult to recreate
        
        **CRITICAL**: Only recommend deletion if ALL criteria are met:
        1. Corresponding code/functionality completely removed
        2. No references from other documentation sections
        3. No ongoing user value
        4. Information is trivially recoverable if needed

        </repository_change_analysis>

        ## Output Requirements

        Generate a JSON structure following these strict guidelines:

        ### Deletion Policy
        - **Conservative Approach**: Prefer marking sections as needing updates over deletion
        - **Evidence Required**: Include specific evidence for why deletion is necessary
        - **Empty by Default**: `delete_id` should be empty unless absolutely certain

        ### Update Policy
        - **Granular Updates**: Update only affected sections, preserve unchanged content
        - **Version-Safe**: Ensure updates don't break existing documentation structure
        - **Context Preservation**: Maintain relationships between documentation sections

        ### Addition Policy
        - **Threshold-Based**: Only add new sections for substantial new functionality
        - **Integration-Focused**: Ensure new sections integrate well with existing structure
        - **Future-Proof**: Design sections to accommodate future related changes

        <document_structure>
        {
          "delete_id": [],
          "items": [
            {
              "title": "component-specific-identifier",
              "name": "Descriptive Section Name",
              "type": "add",
              "prompt": "Generate comprehensive documentation for [SPECIFIC COMPONENT/FEATURE] based on recent codebase changes. Focus on practical implementation details, configuration options, and integration patterns. Structure content to be immediately actionable for developers. Include code examples from the actual implementation. Document public APIs, configuration parameters, and common usage scenarios. Maintain consistency with existing documentation style and terminology. Address any breaking changes or migration requirements explicitly.",
              "children": [
                {
                  "title": "specific-subsection-identifier", 
                  "name": "Focused Subsection Name",
                  "type": "update",
                  "id": "existing-section-id-from-input",
                  "prompt": "Update existing documentation for [SPECIFIC FUNCTIONALITY] to reflect recent changes in commit {{git_commit}}. Preserve existing valuable content while incorporating new implementation details. Focus on changed APIs, updated configuration options, or modified behavior patterns. Maintain backward compatibility information where relevant. Ensure all code examples and references are current with the latest implementation."
                }
              ]
            }
          ]
        }
        </document_structure>

        Proceed with systematic analysis and conservative documentation updates.
        """;
}
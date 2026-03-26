using KoalaWiki.Prompts;

namespace KoalaWiki.KoalaWarehouse.GenerateThinkCatalogue;

public partial class GenerateThinkCatalogueService
{
    public static async Task<string> GenerateThinkCataloguePromptAsync(ClassifyType? classifyType,
        string catalogue)
    {
        var projectType = GetProjectTypeDescription(classifyType);
        var basePrompt = await PromptContext.Warehouse(nameof(PromptConstant.Warehouse.AnalyzeCatalogue),
            new KernelArguments()
            {
                ["code_files"] = catalogue,
                ["projectType"] = projectType
            }, OpenAIOptions.AnalysisModel);

        return basePrompt;
    }


    private static string GetProjectTypeDescription(ClassifyType? classifyType)
    {
        if (classifyType == ClassifyType.Applications)
        {
            return """
                   ## Application System
                   Focus on comprehensive application system analysis:
                   - **Getting Started**: 
                     1. Project overview with clear business problem statement and target market analysis, 
                     2. User personas definition with specific use case scenarios and success metrics, 
                     3. Technology stack breakdown with version requirements and compatibility matrix, 
                     4. Local environment setup with detailed prerequisite installation guides, 
                     5. Database initialization with sample data and seed scripts, 
                     6. Basic user workflow walkthrough with screenshot guides and expected outcomes, 
                     7. Configuration file explanation with security considerations and environment-specific settings
                   - **Deep Dive**: 
                     System architecture with service layers and data flow, user management and authentication/authorization systems, business logic implementation and domain models, API endpoints and integration patterns, database schema and data models, security implementations and access control, performance optimization and scalability patterns, deployment strategies and environment management, monitoring and observability setup, error handling and recovery mechanisms
                   Emphasize multi-tier architecture analysis, user experience flows, business rule implementation, and operational considerations for production deployment.
                   """;
        }

        if (classifyType == ClassifyType.Frameworks)
        {
            return """
                   ## Development Framework
                   Focus on comprehensive framework ecosystem analysis:
                   - **Getting Started**: 
                     1. Framework philosophy with core design principles and architectural decisions rationale, 
                     2. Mental model establishment with key concepts mapping and terminology glossary, 
                     3. Development environment setup with IDE configuration and required tooling installation, 
                     4. Project scaffolding with step-by-step template creation and initial structure explanation, 
                     5. Hello World implementation with code walkthrough and build process verification,
                     6. Essential CLI commands with usage examples and common workflow patterns, 
                     7. Configuration system overview with environment-specific settings and customization options, 
                     8. First feature implementation with guided tutorial and best practice examples
                   - **Deep Dive**: 
                     Complete framework architecture with core components breakdown, extension points and plugin system design, lifecycle management and hooks system, configuration system and conventions over configuration, middleware/interceptor patterns and request/response pipeline, dependency injection and service container, routing and navigation systems, state management and data binding, template/view engine and rendering pipeline, build system and development toolchain, testing framework integration and best practices, performance optimization techniques, ecosystem packages and community modules, migration guides and version compatibility, advanced customization and framework extension patterns
                   Emphasize framework internals, extensibility mechanisms, developer experience optimization, and ecosystem integration patterns.
                   """;
        }

        if (classifyType == ClassifyType.Libraries)
        {
            return """
                   ## Reusable Code Library
                   Focus on comprehensive library component analysis:
                   - **Getting Started**: 
                     1. Library purpose with specific problem domain and use case scenarios, 
                     2. Installation guide with package manager commands and dependency resolution, 
                     3. Basic import/require statements with module system compatibility, 
                     4. Minimal working example with expected output and common variations, 
                     5. Core API overview with essential classes/functions and their relationships, 
                     6. Configuration options with default values and customization examples, 
                     7. Integration examples with popular frameworks and development environments, 
                     8. Troubleshooting guide for common installation and setup issues
                   - **Deep Dive**: 
                     Complete API reference with all classes, methods, and interfaces, detailed analysis of every component and module, usage examples for all major features and edge cases, design patterns and architectural decisions, performance characteristics and benchmarks, error handling and exception management, extensibility points and customization options, configuration options and behavioral controls, dependency requirements and compatibility matrix, version migration guides and breaking changes, best practices and common pitfalls, integration patterns with popular frameworks, TypeScript definitions or language bindings, testing strategies and validation approaches, security considerations and safe usage patterns
                   For component libraries: analyze every single component, its props/parameters, styling options, accessibility features, and usage scenarios.
                   """;
        }

        if (classifyType == ClassifyType.DevelopmentTools)
        {
            return """
                   ## Development Tool
                   Focus on comprehensive development tooling analysis:
                   - **Getting Started**: 
                     1. Tool purpose with development workflow integration points and productivity benefits, 
                     2. System requirements with platform compatibility and dependency checks, 
                     3. Installation process with multiple installation methods and verification steps, 
                     4. Initial configuration with workspace setup and essential preferences, 
                     5. First project creation with template selection and basic structure, 
                     6. Essential feature walkthrough with practical examples and expected outcomes, 
                     7. IDE/editor integration with plugin installation and configuration, 
                     8. Basic automation workflow with time-saving tips and common patterns
                   - **Deep Dive**: 
                     Complete feature set with detailed command/option reference, advanced configuration and customization options, plugin system and extension mechanisms, integration with build systems and CI/CD pipelines, automation capabilities and scripting interfaces, performance optimization and efficiency features, workspace and project management, collaboration features and team workflows, debugging and troubleshooting capabilities, export/import features and data migration, integration with version control systems, template and scaffold systems, code generation and automation features, monitoring and analytics capabilities
                   Emphasize workflow optimization, team collaboration features, and development productivity enhancements.
                   """;
        }

        if (classifyType == ClassifyType.CLITools)
        {
            return """
                   ## Command-Line Interface Tool
                   Focus on comprehensive CLI tool analysis:
                   - **Getting Started**: 
                     1. Tool purpose with specific problem solving scenarios and target use cases, 
                     2. Multi-platform installation with package managers, binary downloads, and source compilation, 
                     3. Command structure overview with syntax patterns and common conventions, 
                     4. Basic command examples with input/output demonstrations and error handling, 
                     5. Configuration file creation with template examples and validation methods, 
                     6. Environment variables setup with security considerations and precedence rules, 
                     7. Shell integration with auto-completion setup and alias recommendations, 
                     8. First automation script with practical workflow examples and best practices
                   - **Deep Dive**: 
                     Complete command reference with all options and flags, subcommand hierarchy and command composition, parameter validation and input handling, configuration system and precedence rules, plugin architecture and extension mechanisms, scripting and automation integration, pipeline and chaining capabilities, output formatting and parsing options, logging and debugging features, error handling and recovery mechanisms, performance optimization for large datasets, batch processing and parallel execution, integration with shell environments and completion systems, credential management and security features, update mechanisms and version management
                   Emphasize command-line interface design, automation integration, and power user workflows.
                   """;
        }

        if (classifyType == ClassifyType.DevOpsConfiguration)
        {
            return """
                   ## DevOps & Infrastructure Configuration
                   Focus on comprehensive infrastructure and deployment analysis:
                   - **Getting Started**: 
                     1. Infrastructure purpose with architectural decisions and deployment strategy overview, 
                     2. Prerequisites checklist with cloud provider setup and access permissions, 
                     3. Environment preparation with tool installation and credential configuration, 
                     4. Initial deployment with step-by-step execution and validation checkpoints, 
                     5. Basic monitoring setup with health checks and alerting configuration, 
                     6. Security baseline with essential hardening steps and compliance checks, 
                     7. Rollback procedures with emergency response protocols and data protection, 
                     8. Cost monitoring with resource optimization recommendations and budget alerts
                   - **Deep Dive**: 
                     Complete infrastructure-as-code implementation with resource definitions, deployment pipeline architecture and stage configurations, container orchestration and service management, networking and load balancing configurations, security hardening and compliance requirements, monitoring and observability stack setup, logging aggregation and analysis systems, backup and disaster recovery procedures, scaling strategies and auto-scaling configurations, environment promotion and release management, secrets management and credential handling, cost optimization and resource management, compliance auditing and security scanning, incident response and troubleshooting procedures, performance monitoring and optimization
                   Emphasize deployment automation, operational procedures, security best practices, and production readiness considerations.
                   """;
        }

        if (classifyType == ClassifyType.Documentation)
        {
            return """
                   ## Documentation & Testing Project
                   Focus on comprehensive documentation system analysis:
                   - **Getting Started**: 
                     1. Documentation purpose with audience analysis and content strategy definition, 
                     2. Content structure with information architecture and navigation design, 
                     3. Authoring environment setup with tools installation and workspace configuration, 
                     4. Style guide overview with writing standards and formatting conventions, 
                     5. Content creation workflow with templates, review process, and publication pipeline, 
                     6. Collaboration guidelines with contributor onboarding and role definitions, 
                     7. Quality assurance with validation tools and testing procedures, 
                     8. Maintenance schedule with update cycles and content lifecycle management
                   - **Deep Dive**: 
                     Complete content architecture and information hierarchy, documentation toolchain and build system, content management and version control strategies, template systems and content reuse patterns, multi-format publishing and output generation, search and navigation optimization, accessibility and internationalization support, content validation and quality assurance processes, automated testing for documentation accuracy, contributor onboarding and collaboration workflows, content lifecycle management and maintenance procedures, analytics and usage tracking, feedback collection and improvement processes, integration with development workflows and CI/CD
                   Emphasize content quality assurance, contributor experience, and documentation maintenance strategies.
                   """;
        }

        return """
               ## General Project Analysis
               Focus on comprehensive project understanding and documentation:
               - **Getting Started**: 
                 1. Project purpose with clear problem statement and solution approach, 
                 2. Target audience with user personas and specific use case scenarios, 
                 3. Technology stack with version requirements and architectural rationale, 
                 4. Environment setup with detailed prerequisites and installation verification, 
                 5. Project structure with directory layout and key file explanations, 
                 6. Basic usage with working examples and expected outcomes, 
                 7. Configuration options with default settings and customization guidelines, 
                 8. Common workflows with step-by-step tutorials and troubleshooting tips
               - **Deep Dive**: 
                 Complete system architecture with component relationships, detailed feature analysis and implementation patterns, technical design decisions and trade-offs, performance characteristics and optimization opportunities, security considerations and best practices, integration points and external dependencies, testing strategies and quality assurance, deployment and operational considerations, maintenance and evolution strategies, contribution guidelines and development workflows
               Provide thorough analysis that serves both newcomers seeking understanding and experienced developers requiring implementation details.
               """;
    }
}
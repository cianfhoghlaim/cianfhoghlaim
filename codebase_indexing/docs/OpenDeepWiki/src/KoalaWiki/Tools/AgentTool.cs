using System.ComponentModel;

namespace KoalaWiki.Tools;

public class AgentTool
{
    [KernelFunction("think"), Description(
         """
         You have been given a thinking prompt or complex problem that requires internal reasoning and reflection. This is your opportunity to work through difficult concepts, organize your thoughts, engage in multi-step reasoning, or critically evaluate information without taking any external actions.
         
         Use this internal thinking tool when you need to:
         - Break down complex problems into smaller components
         - Organize and structure your thoughts before proceeding
         - Engage in multi-step reasoning or logical analysis
         - Evaluate the quality, reliability, or relevance of different sources or results
         - Reflect critically on next steps after receiving information
         - Consider multiple perspectives or approaches to a problem
         - Work through uncertainties or ambiguities
         
         Approach your thinking systematically:
         1. First, clearly identify what the core question or problem is
         2. Break down complex issues into manageable parts
         3. Consider what you know, what you don't know, and what assumptions you might be making
         4. Think through different approaches or perspectives
         5. Evaluate the strengths and weaknesses of different options
         6. Synthesize your analysis into clear next steps or conclusions
         
         Remember, this is purely for internal reflection and reasoning. You are not expected to take any external actions or provide definitive answers to others - this is your space to think through the problem thoroughly.
         """)]
    public string DeepThinking(
        [Description("A thought to think about")]
        string thought)
    {
        var originalColor = System.Console.ForegroundColor;
        System.Console.ForegroundColor = ConsoleColor.Yellow;
        System.Console.WriteLine("深入思考>"+thought);
        System.Console.ForegroundColor = originalColor;
        return thought;
    }
}
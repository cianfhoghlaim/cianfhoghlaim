using System;

namespace Nationalist
{
    internal static class Interactions
    {
        internal static string GetTargetLocale()
        {
            Console.WriteLine("Enter target locale:");
            return Console.ReadLine();
        }
    }
}
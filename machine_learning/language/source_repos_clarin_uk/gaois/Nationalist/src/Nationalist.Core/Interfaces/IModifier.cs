using System.Collections.Generic;

namespace Nationalist.Core
{
    public interface IModifier
    {
        List<Country> ModifyList(List<Country> countries, string locale);
    }
}
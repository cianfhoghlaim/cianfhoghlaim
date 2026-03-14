using System.Collections.Generic;

namespace Nationalist.Core
{
    public interface IReducer
    {
        List<Country> GenerateList(string locale);
    }
}
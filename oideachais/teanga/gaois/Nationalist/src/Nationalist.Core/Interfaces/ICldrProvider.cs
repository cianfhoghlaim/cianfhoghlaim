using System.Collections.Generic;

namespace Nationalist.Core
{
    public interface ICldrProvider
    {
        List<Country> ListCountries(string locale);
    }
}
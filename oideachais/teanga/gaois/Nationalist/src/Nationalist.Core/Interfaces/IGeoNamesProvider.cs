using System.Collections.Generic;

namespace Nationalist.Core
{
    public interface IGeoNamesProvider
    {
        List<Country> PopulateGeoNameIDs(List<Country> countries);
    }
}
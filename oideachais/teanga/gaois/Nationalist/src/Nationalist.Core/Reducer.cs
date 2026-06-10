using System.Collections.Generic;
using System.Linq;

namespace Nationalist.Core
{
    public class Reducer : IReducer
    {
        private readonly ICldrProvider _cldrProvider;
        private readonly IGeoNamesProvider _geoNamesProvider;

        public Reducer(
            ICldrProvider cldrProvider,
            IGeoNamesProvider geoNamesProvider)
        {
            _cldrProvider = cldrProvider;
            _geoNamesProvider = geoNamesProvider;
        }

        public List<Country> GenerateList(string locale)
        {
            var cldrCountries = _cldrProvider.ListCountries(locale);
            var reducedCountries = _geoNamesProvider.PopulateGeoNameIDs(cldrCountries);
            return reducedCountries;
        }
    }
}
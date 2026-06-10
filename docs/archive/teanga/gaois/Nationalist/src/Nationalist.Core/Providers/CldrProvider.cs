using System;
using System.Collections.Generic;
using System.Linq;
using Ansa.Extensions;
using Sepia.Globalization;

namespace Nationalist.Core
{
    public class CldrProvider : ICldrProvider
    {
        public List<Country> ListCountries(string locale)
        {
            Console.WriteLine("Verifying CLDR data…");

            var version = Cldr.Instance.DownloadLatestAsync().Result;

            Console.WriteLine($"Using CLDR {version}");

            var countries = new List<Country>();

            Console.WriteLine($"Obtaining countries data for locale '{locale}'…");

            try
            {
                var document = Cldr.Instance.GetDocuments($"common/main/{locale}.xml").FirstOrDefault();
                var documentNavigator = document.CreateNavigator();
                var territories = documentNavigator.Select("/ldml/localeDisplayNames/territories/territory");

                while (territories.MoveNext())  
                {
                    var type = territories.Current.GetAttribute("type", string.Empty);

                    // only countries have alphabetical type codes; other territories are represented numerically
                    if (type.IsNullOrWhiteSpace() || int.TryParse(type, out int number))
                        continue;

                    var name = territories.Current.Value;
                    var alternate = territories.Current.GetAttribute("alt", string.Empty);

                    var country = new Country(type, null, name, alternate);
                    countries.Add(country);
                }
            }
            catch
            {
                Console.WriteLine("No CLDR data found for the provided locale");
            }

            return countries;
        }
    }
}
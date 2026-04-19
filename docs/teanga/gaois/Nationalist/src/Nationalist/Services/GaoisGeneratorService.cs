using Microsoft.Extensions.Options;
using Nationalist.Core;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace Nationalist
{
    public class GaoisGeneratorService
    {
        private readonly string _outputPath;

        public GaoisGeneratorService(IOptionsMonitor<NationalistSettings> settings)
        {
            _outputPath = settings.CurrentValue.OutputPath;
        }

        public void WriteCountries(List<Country> countriesEN, List<Country> countriesGA)
        {
            Console.WriteLine("Writing Gaois C# file…");

            var outputFile = Path.Combine(_outputPath, $"Countries.cs");

            using (var fileStream = File.CreateText(outputFile))
            {
                fileStream.WriteLine("using System.Collections.Generic;");
                fileStream.WriteLine();
                fileStream.WriteLine("namespace Nationalist");
                fileStream.WriteLine("{");
                fileStream.WriteLine("\tpublic static class Toponymic");
                fileStream.WriteLine("\t{");
                fileStream.WriteLine("\t\tpublic static List<Country> Countries = new List<Country>");
                fileStream.WriteLine("\t\t{");

                foreach (var country in countriesEN)
                {
                    var countryGA = countriesGA.Where(c => c.Code == country.Code).FirstOrDefault();
                    fileStream.WriteLine($"\t\t\tnew Country {{ IsoCode = \"{country.Code}\", GeoNameID = {country.GeoNameID}, NameEN = \"{country.Name}\", NameGA = \"{countryGA.Name}\" }},");
                }

                fileStream.WriteLine("\t\t};");
                fileStream.WriteLine("\t}");
                fileStream.WriteLine("}");
            }

            Console.WriteLine("Gaois C# file written!");
        }
    }
}
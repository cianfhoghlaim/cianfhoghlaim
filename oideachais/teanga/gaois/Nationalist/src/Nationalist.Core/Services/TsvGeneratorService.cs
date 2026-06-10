using System;
using System.Collections.Generic;
using System.IO;
using CsvHelper;
using Microsoft.Extensions.Options;

namespace Nationalist.Core
{
    public class TsvGeneratorService
    {
        private readonly string _outputPath;

        public TsvGeneratorService(IOptionsMonitor<NationalistSettings> settings)
        {
            _outputPath = settings.CurrentValue.OutputPath;
        }

        public void WriteTsv(List<Country> countries, string locale)
        {
            Console.WriteLine("Writing TSV file…");

            var outputFile = Path.Combine(_outputPath, $"{locale}/countries.{locale}.tsv");

            using (var writer = new StreamWriter(outputFile))
            using (var csv = new CsvWriter(writer))
            {
                csv.Configuration.Delimiter = "\t";
                csv.WriteRecords(countries);
            }

            Console.WriteLine("TSV file written!");
        }
    }
}
using System;
using System.Collections.Generic;
using System.IO;
using Microsoft.Extensions.Options;
using Newtonsoft.Json;
using Newtonsoft.Json.Serialization;

namespace Nationalist.Core
{
    public class JsonGeneratorService
    {
        private readonly string _outputPath;

        public JsonGeneratorService(IOptionsMonitor<NationalistSettings> settings)
        {
            _outputPath = settings.CurrentValue.OutputPath;
        }

        public void WriteJson(List<Country> countries, string locale)
        {
            Console.WriteLine("Writing JSON file…");

            var outputFile = Path.Combine(_outputPath, $"{locale}/countries.{locale}.json");

            using (var fileStream = File.CreateText(outputFile))
            {
                var serializer = new JsonSerializer();
                var serializerSettings = new JsonSerializerSettings();
                serializerSettings.ContractResolver = new CamelCasePropertyNamesContractResolver();
                var json = JsonConvert.SerializeObject(countries, serializerSettings);
                fileStream.Write(json);
            }
            
            Console.WriteLine("JSON file written!");
        }
    }
}
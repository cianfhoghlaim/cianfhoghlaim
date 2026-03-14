using System.Linq;
using Nationalist.Core;

namespace Nationalist
{
    public class Generator
    {
        private readonly IReducer _reducer;
        private readonly CSharpGeneratorService _cSharpGeneratorService;
        private readonly CsvGeneratorService _csvGeneratorService;
        private readonly JsonGeneratorService _jsonGeneratorService;
        private readonly TsvGeneratorService _tsvGeneratorService;
        private readonly GaoisGeneratorService _gaoisGeneratorService;

        public Generator(
            IReducer reducer,
            CSharpGeneratorService cSharpGeneratorService,
            CsvGeneratorService csvGeneratorService,
            JsonGeneratorService jsonGeneratorService,
            TsvGeneratorService tsvGeneratorService,
            GaoisGeneratorService gaoisGeneratorService)
        {
            _reducer = reducer;
            _cSharpGeneratorService = cSharpGeneratorService;
            _csvGeneratorService = csvGeneratorService;
            _jsonGeneratorService = jsonGeneratorService;
            _tsvGeneratorService = tsvGeneratorService;
            _gaoisGeneratorService = gaoisGeneratorService;
        }

        public void GenerateList(IModifier modifier = default(IModifier))
        {
            var countriesEN = _reducer.GenerateList("en");
            var countriesGA = _reducer.GenerateList("ga");

            if (modifier != default(IModifier))
            {
                countriesEN = modifier.ModifyList(countriesEN, "en");
                countriesGA = modifier.ModifyList(countriesGA, "ga");
            }

            countriesEN = countriesEN.OrderBy(c => c.Code).ToList();
            countriesGA = countriesGA.OrderBy(c => c.Code).ToList();

            _cSharpGeneratorService.WriteCSharp(countriesEN, "en");
            _cSharpGeneratorService.WriteCSharp(countriesGA, "ga");
            _csvGeneratorService.WriteCsv(countriesEN, "en");
            _csvGeneratorService.WriteCsv(countriesGA, "ga");
            _jsonGeneratorService.WriteJson(countriesEN, "en");
            _jsonGeneratorService.WriteJson(countriesGA, "ga");
            _tsvGeneratorService.WriteTsv(countriesEN, "en");
            _tsvGeneratorService.WriteTsv(countriesGA, "ga");
            _gaoisGeneratorService.WriteCountries(countriesEN, countriesGA);
        }
    }
}
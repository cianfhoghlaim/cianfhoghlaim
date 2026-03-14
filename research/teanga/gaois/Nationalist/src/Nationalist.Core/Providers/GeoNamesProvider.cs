using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Microsoft.Extensions.Options;
using NGeoNames;

namespace Nationalist.Core
{
    public class GeoNamesProvider : IGeoNamesProvider
    {
        private readonly string _fileName;
        private readonly string _dataPath;
        private readonly string _countryInfoPath;

        public GeoNamesProvider(IOptionsMonitor<NationalistSettings> settings)
        {
            _fileName = "countryInfo.txt";
            _dataPath = settings.CurrentValue.DataPath;
            _countryInfoPath = Path.Combine(_dataPath, _fileName);
        }

        public List<Country> PopulateGeoNameIDs(List<Country> countries)
        {
            if (!File.Exists(_countryInfoPath))
            {
                Console.WriteLine("Downloading country info data…");
                
                var downloader = GeoFileDownloader.CreateGeoFileDownloader();
                downloader.DownloadFile(_fileName, _dataPath);

                Console.WriteLine("Country info downloaded…");
            }

            var nonCountries = new List<Country>();

            foreach (var country in countries)
            {
                var geoNameID = GeoFileReader.ReadCountryInfo(_countryInfoPath)
                    .Where(c => c.ISO_Alpha2 == country.Code)
                    .FirstOrDefault()?
                    .GeoNameId;

                if (geoNameID is int id)
                {
                    country.GeoNameID = id;
                }
                else
                {
                    nonCountries.Add(country);
                }
            }

            foreach (var nonCountry in nonCountries)
            {
                countries.Remove(nonCountry);
            }

            return countries;
        }
    }
}
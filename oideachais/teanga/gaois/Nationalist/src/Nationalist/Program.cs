using System;
using System.IO;
using Ansa.Extensions;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Nationalist.Core;

namespace Nationalist
{
    class Program
    {
        static void Main(string[] args)
        {
            var environment = Environment.GetEnvironmentVariable("ASPNETCORE_ENVIRONMENT");
            environment = (environment.IsNullOrWhiteSpace()) ? "Development" : environment;

            var configuration = new ConfigurationBuilder()
                .SetBasePath(Directory.GetCurrentDirectory())
                .AddJsonFile($"appsettings.json", true, true)
                .AddJsonFile($"appsettings.{environment}.json", true, true)
                .Build();

            var serviceProvider = ConfigureServiceProvider(configuration);
            var modifier = serviceProvider.GetService<IModifier>();
            var generator = serviceProvider.GetService<Generator>();

            Console.WriteLine("This is a custom version of the Nationalist curated country list generator.");
            Console.WriteLine("This program will generate files in English and Irish.");
            Console.WriteLine("To generate files in other languages please clone the standard Nationalist repo.");
            Console.WriteLine("Press any key to proceed...");
            Console.ReadLine();

            generator.GenerateList(modifier);
        }

        static IServiceProvider ConfigureServiceProvider(IConfiguration configuration)
        {
            var services = new ServiceCollection();

            services.AddOptions();
            services.Configure<NationalistSettings>(configuration.GetSection("Nationalist"));

            services.AddSingleton<NationalistSettings>();
            services.AddSingleton<ICldrProvider, CldrProvider>();
            services.AddSingleton<IGeoNamesProvider, GeoNamesProvider>();
            services.AddSingleton<IReducer, Reducer>();
            services.AddSingleton<IModifier, Modifier>();
            services.AddSingleton<CSharpGeneratorService>();
            services.AddSingleton<CsvGeneratorService>();
            services.AddSingleton<JsonGeneratorService>();
            services.AddSingleton<TsvGeneratorService>();
            services.AddSingleton<GaoisGeneratorService>();
            services.AddSingleton<Generator>();

            return services.BuildServiceProvider();
        }
    }
}
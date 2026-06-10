using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using Ansa.Extensions;
using Nationalist.Core;

namespace Nationalist
{
    public class Modifier : IModifier
    {
        public List<Country> ModifyList(List<Country> countries, string locale)
        {
            // Choose between alternate forms
            if (locale == "en")
            {
                var bosnia = countries.SingleOrDefault(c => c.Code == "BA" && c.AlternateForm == "short");
                countries.Remove(bosnia);
                var congoDRC = countries.SingleOrDefault(c => c.Code == "CD" && c.AlternateForm.IsNullOrWhiteSpace());
                countries.Remove(congoDRC);
                var congoRepublic = countries.SingleOrDefault(c => c.Code == "CG" && c.AlternateForm.IsNullOrWhiteSpace());
                countries.Remove(congoRepublic);
                var ivoryCoast = countries.SingleOrDefault(c => c.Code == "CI" && c.AlternateForm.IsNullOrWhiteSpace());
                countries.Remove(ivoryCoast);
                var czechia = countries.SingleOrDefault(c => c.Code == "CZ" && c.AlternateForm == "variant");
                countries.Remove(czechia);
                var falkland = countries.SingleOrDefault(c => c.Code == "FK" && c.AlternateForm == "variant");
                countries.Remove(falkland);
                var uk = countries.SingleOrDefault(c => c.Code == "GB" && c.AlternateForm == "short");
                countries.Remove(uk);
                var hongcong = countries.SingleOrDefault(c => c.Code == "HK" && c.AlternateForm.IsNullOrWhiteSpace());
                countries.Remove(hongcong);
                var macedonia = countries.SingleOrDefault(c => c.Code == "MK" && c.AlternateForm == "variant");
                countries.Remove(macedonia);
                var myanmar = countries.SingleOrDefault(c => c.Code == "MM" && c.AlternateForm.IsNullOrWhiteSpace());
                countries.Remove(myanmar);
                var macau = countries.SingleOrDefault(c => c.Code == "MO" && c.AlternateForm.IsNullOrWhiteSpace());
                countries.Remove(macau);
                var palestine = countries.SingleOrDefault(c => c.Code == "PS" && c.AlternateForm == "short");
                countries.Remove(palestine);
                var eastTimor = countries.SingleOrDefault(c => c.Code == "TL" && c.AlternateForm == "variant");
                countries.Remove(eastTimor);
                var us = countries.SingleOrDefault(c => c.Code == "US" && c.AlternateForm == "short");
                countries.Remove(us);
            }
            
            if (locale == "ga")
            {
                var congoDRC = countries.SingleOrDefault(c => c.Code == "CD" && c.AlternateForm.IsNullOrWhiteSpace());
                countries.Remove(congoDRC);
                var congoRepublic = countries.SingleOrDefault(c => c.Code == "CG" && c.AlternateForm.IsNullOrWhiteSpace());
                countries.Remove(congoRepublic);
                var ivoryCoast = countries.SingleOrDefault(c => c.Code == "CI" && c.AlternateForm == "variant");
                countries.Remove(ivoryCoast);
                var czechia = countries.SingleOrDefault(c => c.Code == "CZ" && c.AlternateForm.IsNullOrWhiteSpace());
                countries.Remove(czechia);
                var falkland = countries.SingleOrDefault(c => c.Code == "FK" && c.AlternateForm == "variant");
                countries.Remove(falkland);
                var uk = countries.SingleOrDefault(c => c.Code == "GB" && c.AlternateForm == "short");
                countries.Remove(uk);
                var hongcong = countries.SingleOrDefault(c => c.Code == "HK" && c.AlternateForm.IsNullOrWhiteSpace());
                countries.Remove(hongcong);
                var macedonia = countries.SingleOrDefault(c => c.Code == "MK" && c.AlternateForm == "variant");
                countries.Remove(macedonia);
                var macau = countries.SingleOrDefault(c => c.Code == "MO" && c.AlternateForm.IsNullOrWhiteSpace());
                countries.Remove(macau);
                var palestine = countries.SingleOrDefault(c => c.Code == "PS" && c.AlternateForm == "short");
                countries.Remove(palestine);
                var timor = countries.SingleOrDefault(c => c.Code == "TL" && c.AlternateForm == "variant");
                countries.Remove(timor);
                var us = countries.SingleOrDefault(c => c.Code == "US" && c.AlternateForm == "short");
                countries.Remove(us);
            }

            // Add subdivisions
            if (locale == "en")
            {
                countries.Add(new Country("GB-ENG", 6269131, "England"));
                countries.Add(new Country("GB-NIR", 2641364, "Northern Ireland"));
                countries.Add(new Country("GB-SCT", 2638360, "Scotland"));
                countries.Add(new Country("GB-WLS", 2634895, "Wales"));
            }

            if (locale == "ga")
            {
                countries.Add(new Country("GB-ENG", 6269131, "Sasana"));
                countries.Add(new Country("GB-NIR", 2641364, "Tuaisceart Éireann"));
                countries.Add(new Country("GB-SCT", 2638360, "Albain"));
                countries.Add(new Country("GB-WLS", 2634895, "an Bhreatain Bheag"));
            }

            // Standardize GA capitalization
            if (locale == "ga")
            {
                foreach (var country in countries)
                {
                    country.Name = Regex.Replace(country.Name, "^an", "An");
                }
            }

            return countries;
        }
    }
}
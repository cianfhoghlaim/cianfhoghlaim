namespace Nationalist.Core
{
    public class Country
    {
        public Country(string code, int? geoNameID, string name, string alternateForm = default(string))
        {
            Code = code;
            GeoNameID = geoNameID;
            Name = name;
            AlternateForm = alternateForm;
        }

        public string Code { get; set; }

        public int? GeoNameID { get; set; }

        public string Name { get; set; }

        public string AlternateForm { get; set; }
    }
}
using System.ComponentModel;

namespace KoalaWiki.KoalaWarehouse;

public class DocumentResultCatalogue
{
    public List<DocumentResultCatalogueItem> items { get; set; } = new();
}

public class DocumentResultCatalogueItem
{
    public string name { get; set; }

    public string title { get; set; }

    public string prompt { get; set; }

    public List<DocumentResultCatalogueItem>? children { get; set; }
}
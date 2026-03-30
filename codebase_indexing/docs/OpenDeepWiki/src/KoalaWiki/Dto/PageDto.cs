namespace KoalaWiki.Dto;

public class PageDto<T>
{
    public int Total { get; set; }

    public IList<T> Items { get; set; } = new List<T>();

    public PageDto(int total, IList<T> items)
    {
        Total = total;
        Items = items;
    }
}
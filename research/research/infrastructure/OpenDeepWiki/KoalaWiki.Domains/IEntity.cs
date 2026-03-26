namespace KoalaWiki.Domains;

public interface IEntity<TKey>
{
    public TKey Id { get; set; }
}
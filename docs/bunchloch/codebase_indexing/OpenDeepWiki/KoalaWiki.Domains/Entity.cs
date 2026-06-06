using System;
using KoalaWiki.Entities;

namespace KoalaWiki.Domains;

public class Entity<TKey> : IEntity<TKey>, ICreateEntity
{
    public TKey Id { get; set; }

    public DateTime CreatedAt { get; set; }
}
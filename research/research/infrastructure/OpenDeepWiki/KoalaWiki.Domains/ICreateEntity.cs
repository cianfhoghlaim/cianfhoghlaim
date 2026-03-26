using System;

namespace KoalaWiki.Entities;

public interface ICreateEntity
{
    public DateTime CreatedAt { get; set; }
}
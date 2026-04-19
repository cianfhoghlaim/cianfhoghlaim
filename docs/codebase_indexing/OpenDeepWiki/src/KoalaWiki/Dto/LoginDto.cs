using KoalaWiki.Domains.Users;

namespace KoalaWiki.Dto;

public record LoginDto(bool Success, string Token, string? RefreshToken, UserInfoDto? User, string? ErrorMessage);
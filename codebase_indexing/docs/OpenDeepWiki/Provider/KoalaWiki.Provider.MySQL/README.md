# MySQL Database Configuration Test

## Test appsettings.json for MySQL

Create a test configuration file to verify MySQL support:

```json
{
  "ConnectionStrings": {
    "Type": "mysql",
    "Default": "Server=localhost;Database=KoalaWiki;Uid=root;Pwd=password;"
  }
}
```

## Environment Variables Test

Test with environment variables:

```bash
DB_TYPE=mysql
DB_CONNECTION_STRING=Server=localhost;Database=KoalaWiki;Uid=root;Pwd=password;
```

## Expected Behavior

When configured with MySQL:
1. The application should load the KoalaWiki.Provider.MySQL project
2. MySQLApplicationExtensions.AddMySQLDbContext should be called
3. Entity Framework should configure MySQLContext with the MySQL provider
4. Database migrations should work with MySQL syntax

## Testing MySQL Support

To test MySQL support:

1. Set up a MySQL database instance
2. Configure the connection string in appsettings.json or environment variables
3. Run the application
4. The application should connect to MySQL and create the required tables
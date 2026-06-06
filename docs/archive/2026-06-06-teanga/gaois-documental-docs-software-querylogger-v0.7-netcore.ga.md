---
title: Gaois.QueryLogger (ASP.NET Core)
shortTitle: .NET Core
description: Logálaí simplí iarratais is féidir a chumrú le haghaidh fheidhmchláir ASP.NET agus ASP.NET Core
keywords: logálaí iarratais, cuardaigh, staitisticí cuardaigh, foinse oscailte, C#, .NET Core, dotnet, SQL Server, Fiontar & Scoil na Gaeilge, DCU
github: https://github.com/gaois/Gaois.QueryLogger
nuget: https://www.nuget.org/packages/Gaois.QueryLogger.AspNetCore/
order: 3
public: true
---

Logálaí simplí iarratais is féidir a chumrú le haghaidh fheidhmchláir ASP.NET Core 2.1+. Tá réamhrá ginearálta don leabharlann ar fáil [anseo](../intro).

## Suiteáil agus cumrú

### Bunachar sonraí

1. Tabhair cead rochtana ar bhunachar sonraí don fheidhmchláir.
2. Rith an [ script SQL chun tábla `QueryLogs` a chruthú](https://github.com/gaois/Gaois.QueryLogger/tree/master/scripts) sa bhunachar sonraí céanna.

### Feidhmchlár

Cuir an pacáiste NuGet [Gaois.QueryLogger.AspNetCore](https://www.nuget.org/packages/Gaois.QueryLogger.AspNetCore/) le tionscadal ar bith de chuid ASP.NET Core 2.1+.

```cmd
dotnet add package Gaois.QueryLogger.AspNetCore
```

Ansin, in **Startup.cs**, cumraigh an modh *ConfigureServices* ach glaoch a chur ar `services.AddQueryLogger()`. Beidh ort ainm feidhmchláir agus teaghrán ceangail don stóras sonraí de chuid SQL Server a roghnaíonn tú a chur leis:

```csharp
services.AddQueryLogger(settings =>
{
    settings.ApplicationName = "RecordsApp"
    settings.Store.ConnectionString = configuration.GetConnectionString("query_logger");
});
```

De rogha air sin, lódáil an chumraíocht ó do chomhad `appsettings.json`:

```csharp
services.AddQueryLogger(configuration.GetSection("QueryLogger"));
```

Nó is féidir leat an dá chur chuige a mheascadh:

```csharp
services.AddQueryLogger(configuration.GetSection("QueryLogger"), settings =>
{
    settings.IsEnabled = !environment.IsDevelopment();
});
```

Is féidir leat an treoir `using Gaois.QueryLogger` a chur le comhad C# ar bith anois chun rochtain a fháil ar mhodhanna agus ar sheirbhísí na leabharlainne.

## Úsáid

Cuirtear Gaois.QueryLogger i bhfeidhm in ASP.NET Core ach gnásanna molta na creatlaí maidir le [hinteilgean spléachas](https://docs.microsoft.com/en-us/aspnet/core/fundamentals/dependency-injection) a úsáid. Cuir inteilgean an logálaí iarratais chuig cruthaitheoir aicme tríd an gcomhéadan `IQueryLogger`:

```csharp
private readonly IQueryLogger _queryLogger;

public RecordsController(IQueryLogger queryLogger)
{
    _queryLogger = queryLogger;
}

var query = new Query { QueryCategory = "birth_records", QueryTerms = "test", QueryText = Request.Url.Query };
_queryLogger.Log(query);
```

### Iarratas a logáil

Glacann an modh `Log()` le go leor oibiachtaí `Query` mar pharaiméadair.

Úsáid shamplach:

```csharp
var query = new Query()
{
    QueryCategory = "birth_records",
    QueryTerms = "John Doe Jr.",
    QueryText = Request.Url.Query,
    ResultCount = 27
};

_queryLogger.Log(query);
```

Faigheann an leabharlann airíonna `Host` an tsuímh gréasáin agus `IPAddress` an chliaint ón gcomhthéacs HTTP go huathoibríoch. Mar an gcéanna, mura sonraíonn tú airí `QueryID` (i bhfoirm GUID), cruthófar ceann duit. Is féidir leat aon cheann de na luachanna seo a pobalaíodh go huathoibríoch a fhorscríobh ach an t-airí ábhartha a shonrú san oibiacht `Query`, áfach. Féach an liosta iomlán de shonraí iarratais is féidir a shonrú [anseo](../data). 

Baineann cur chuige *fire-and-forget* leis an modh `Log()`, cuirtear iarratais go sioncronach le ciú logálaí atá snáithe-oiriúnach agus déantar próiseáil go haisioncronach orthu i snáithe eile agus an patrún Táirgeora-Tomhaltóra á chur i bhfeidhm. Ciallaíonn sé sin nach gcuireann logáil aon taca le haga freagartha an fhreastalaí i ndáiríre. Ag an am céanna, cruthaíodh Gaois.QueryLogger agus lamháltas lochtanna agus láimhseáil earráide ar intinn againn. Tuilleadh faisnéise [anseo](../faulttolerance). 

### Iarratais ghaolmhara a chomhcheangal

Más mian leat iarratais ghaolmhara a chur i ngrúpa le chéile — mar shampla, iarratais dhifriúla chuardaigh a ritheadh ar leathanach amháin — sann an t-airí `QueryID` céanna do gach ceann de na hiarratais ghaolmhara:

```csharp
var queryID = Guid.NewGuid();
var searchText = "John Doe Jr.";

var births = new Query()
{
    QueryID = queryID,
    QueryCategory = "birth_records",
    QueryTerms = searchText
};

var deaths = new Query()
{
    QueryID = queryID,
    QueryCategory = "death_records",
    QueryTerms = searchText
};

_queryLogger.Log(births, deaths);
```

## Cumrú

Mar a dhéantar cur síos air thuas, is féidir leat an modh `services.AddQueryLogger()` a chumrú in **Startup.cs** chun socruithe an logálaí iarratais a chumrú: 

```csharp
services.AddQueryLogger(settings =>
{
    settings.IsEnabled = !environment.IsDevelopment();
    settings.StoreClientIPAddress = false;
    settings.Store.ConnectionString = Configuration.GetConnectionString("query_logger");
});
```

Is féidir leat an chumraíocht a lódáil ó do chomhad cumraíochta JSON freisin:

```json
{
  "QueryLogger": {
    "ApplicationName": "RecordsApp",
    "IsEnabled": true,
    "Store": {
      "ConnectionString": "Server=localhost;Database=recordsappdb;Trusted_Connection=True;"
    },
    "Email": {
      "ToAddress": "me@test.ie",
      "FromAddress": "test@test.ie",
      "FromDisplayName": "RecordsApp — QueryLogger",
      "SMTPHost": "smtp.myhost.net",
      "SMTPPort": 587,
      "SMTPUserName": "MY_USERNAME",
      "SMTPPassword": "MY_PASSWORD",
      "SMTPEnableSSL": true
    },
    "ExcludedIPAddresses": [
      { "name": "Bingbot", "ipAddress": "40.77.167.0" },
      { "name": "Bingbot", "ipAddress": "207.46.13.0" }
    ]
}
```

Féach an liosta iomlán de shocruithe is féidir a chumrú [anseo](../configuration). Déantar cur síos sa chuid eile den mhír seo ar bhealaí úsáideacha chun leas a bhaint as na socruithe cumraíochta.

### An logálaí iarratais a chumasú/a dhíchumasú go huilíoch

Cumasaítear an logálaí iarratais de réir réamhshocraithe. D’fhéadfadh ócáidí nó timpeallachtaí áirithe a bheith ann, le haghaidh tástáil nó cuspóirí eile, áfach, inar mhaith leat an logálaí iarratais a dhíchumasú gan gach ordú iarratais a thimfhilleadh ina loighic choinníollach féin. Chun freastal air seo, díchumasaigh an logálaí iarratais go huilíoch laistigh de d’fheidhmchláir ach `IsEnabled` a shocrú ag `false`.

```csharp
services.AddQueryLogger(settings =>
{
    settings.IsEnabled = false;
    settings.Store.ConnectionString = Configuration.GetConnectionString("query_logger");
});
```

### Ainm an fheidhmchláir a chumrú

Cumraigh ainm an fheidhmchláir go huilíoch le nach mbeidh ort é a shonrú le haghaidh gach oibiacht `Query` a chruthaíonn tú.  

```csharp
services.AddQueryLogger(settings =>
{
    settings.ApplicationName = "My Application";
    settings.Store.ConnectionString = Configuration.GetConnectionString("query_logger");
});
```

### Anaithnidiú IP a chumrú

Úsáid oibiacht na socruithe chun anaithnidiú sheoladh IP an úsáideora a chumrú.  

```csharp
services.AddQueryLogger(settings =>
{
    settings.Store.ConnectionString = Configuration.GetConnectionString("query_logger");
    settings.AnonymizeIPAddress = IPAddressAnonymizationLevel.None;
});
```

Faoi láthair, is ionann na leibhéil anaithnidithe atá ar fáil agus `None` (níor cuireadh anaithnidiú i bhfeidhm) agus `Partial` (baintear an t-ochtréad deireanach de sheoladh IPv4 an chliaint nó an 80 giotán deireanach de sheoladh IPv6).

Is féidir leat cosc a chur leis an logálaí seoltaí IP a bhailiú ar an gcéad dul síos ach an socrú `StoreClientIPAddress` a chumrú:

```csharp
services.AddQueryLogger(settings =>
{
    settings.Store.ConnectionString = Configuration.GetConnectionString("query_logger");
    settings.StoreClientIPAddress = false;
});
```
Nuair a shocraítear `StoreClientIPAddress` ag `false`, taifeadfar an luach `PRIVATE` sa cholún `IPAddress` de thábla an logálaí iarratais a bhaineann le do bhunachar sonraí. Má shocraítear `StoreClientIPAddress` ag `true`, ach mura féidir seoladh IP an chliaint a fháil ón gcomhthéacs HTTP ar chúis éigin, taifeadfar luach `UNKNOWN`.

## Logaí comhiomlánaithe iarratais agus anailís ar logaí

In [Gaois](https://www.gaois.ie), Fiontar & Scoil na Gaeilge, DCU comhiomlánaímid sonraí achoimre ó thábla na logaí iarratais go míosúil agus stórálaimid i dtábla bunachair sonraí eile iad. Chuireamar struchtúr an tábla agus na gnásanna stóráilte a bhainistíonn an próiseas ar fáil i bhfillteán na [scripteanna](https://github.com/gaois/Gaois.QueryLogger/tree/master/scripts) i stórlann GitHub Gaois.QueryLogger sa chás go mbeidh aon duine eile ag iarraidh úsáid a bhaint astu. Tá eintiteas `AggregratedQueryLog` ag Gaois.QueryLogger chomh maith a chomhfhreagraíonn d’iontrálacha i dtábla na logaí comhiomlánaithe. Faightear cuid de na hiarratais níos ginearálta SQL a úsáidimid chun sonraí logaí a achoimriú agus a anailísiú i bhfillteán na scripteanna.

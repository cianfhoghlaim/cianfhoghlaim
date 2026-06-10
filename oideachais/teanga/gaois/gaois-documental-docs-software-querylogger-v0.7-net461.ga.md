---
title: Gaois.QueryLogger (ASP.NET Framework)
shortTitle: .NET Framework
description: Logálaí simplí iarratais is féidir a chumrú le haghaidh fheidhmchláir ASP.NET agus ASP.NET Core 
keywords: logálaí iarratais, cuardaigh, staitisticí cuardaigh, foinse oscailte, C#, .NET Core, dotnet, SQL Server, Fiontar & Scoil na Gaeilge, DCU
github: https://github.com/gaois/Gaois.QueryLogger
nuget: https://www.nuget.org/packages/Gaois.QueryLogger/
order: 2
public: true
---

Logálaí simplí iarratais is féidir a chumrú le haghaidh fheidhmchláir ASP.NET Framework 4.6.1+. Tá réamhrá ginearálta don leabharlann ar fáil [anseo](../intro).

## Suiteáil agus cumrú

### Bunachar sonraí

1. Tabhair cead rochtana ar bhunachar sonraí don fheidhmchláir.
2. Rith an [script SQL chun tábla `QueryLogs` a chruthú](https://github.com/gaois/Gaois.QueryLogger/tree/master/scripts) sa bhunachar sonraí céanna.

### Feidhmchlár

Cuir an pacáiste NuGet [Gaois.QueryLogger](https://www.nuget.org/packages/Gaois.QueryLogger/) le tionscadal ar bith de chuid ASP.NET Framework 4.6.1+.

```cmd
Install-Package Gaois.QueryLogger
```

Ansin, cumraigh an logálaí iarratais i do chomhad **Web.config**. Beidh ort rannóg cumraíochta a chur leis mar aon le hainm feidhmchláir agus teaghrán ceangail a shonrú don stóras sonraí de chuid SQL Server a roghnaíonn tú:

```xml
<configSections>
  <section name="QueryLogger" type="Gaois.QueryLogger.ConfigurationSettings, Gaois.QueryLogger" />
</configSections>
```

```xml
<QueryLogger applicationName="RecordsApp" isEnabled="true">
  <Store connectionString="Server=localhost;Database=recordsappdb;Trusted_Connection=True;" />
  <Email toAddress="me@test.ie" />
</QueryLogger>
```

Is féidir leat an treoir `using Gaois.QueryLogger` a chur le comhad C# ar bith anois chun rochtain a fháil ar mhodhanna agus ar sheirbhísí na leabharlainne. 

## Úsáid

### Iarratas a logáil

Glacann an modh `QueryLogger.Log()` le go leor oibiachtaí `Query` mar pharaiméadair.  

Úsáid shamplach:

```csharp
var query = new Query()
{
    QueryCategory = "birth_records",
    QueryTerms = "John Doe Jr.",
    QueryText = Request.Url.Query,
    ResultCount = 27
};

QueryLogger.Log(query);
```

Faigheann an leabharlann airíonna `Host` an tsuímh gréasáin agus `IPAddress` an chliaint ón gcomhthéacs HTTP go huathoibríoch. Mar an gcéanna, mura sonraíonn tú `QueryID` (i bhfoirm GUID) san oibiacht `Query`, cruthófar ceann duit. Is féidir leat aon cheann de na luachanna seo a cruthaíodh go huathoibríoch a fhorscríobh ach an t-airí ábhartha a shonrú san oibiacht `Query`, áfach. Féach an liosta iomlán de shonraí iarratais is féidir a shonrú [anseo](../data).  

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

QueryLogger.Log(births, deaths);
```

## Cumrú

Mar a dhéantar cur síos air thuas, is féidir leat socruithe an logálaí iarratais a chumrú i do chomhad **Web.config**:

```xml
<QueryLogger applicationName="RecordsApp" isEnabled="true">
  <Store connectionString="Server=localhost;Database=recordsappdb;Trusted_Connection=True;" />
  <Email toAddress="me@test.ie"
         fromAddress="test@test.ie"
         fromDisplayName="RecordsApp — QueryLogger"
         smtpHost="smtp.myhost.net"
         smtpPort="587"
         smtpUserName="MY_USERNAME"
         smtpPassword="MY_PASSWORD"
         smtpEnableSSL="true" />
  <ExcludedIPAddresses>
    <add name="Bingbot" ipAddress="40.77.167.0" />
    <add name="Bingbot" ipAddress="207.46.13.0" />
  </ExcludedIPAddresses>
</QueryLogger>
```

Féach an liosta iomlán de shocruithe is féidir a chumrú [anseo](../configuration). Déantar cur síos sa chuid eile den mhír seo ar bhealaí úsáideacha chun leas a bhaint as na socruithe cumraíochta. 

### An logálaí iarratais a chumasú/a dhíchumasú go huilíoch

Cumasaítear an logálaí iarratais de réir réamhshocraithe. D’fhéadfadh ócáidí nó timpeallachtaí áirithe a bheith ann, le haghaidh tástáil nó cuspóirí eile, áfach, inar mhaith leat an logálaí iarratais a dhíchumasú gan gach ordú iarratais a thimfhilleadh ina loighic choinníollach féin. Chun freastal air seo, díchumasaigh an logálaí iarratais go huilíoch laistigh de d’fheidhmchlár ach `IsEnabled` a shocrú ag `false`.

```xml
<QueryLogger applicationName="RecordsApp" isEnabled="false">
  <Store connectionString="Server=localhost;Database=recordsappdb;Trusted_Connection=True;" />
  <Email toAddress="me@test.ie" />
</QueryLogger>
```

### Ainm an fheidhmchláir a chumrú

Cumraigh ainm an fheidhmchláir go huilíoch le nach mbeidh ort é a shonrú le haghaidh gach oibiacht `Query` a chruthaíonn tú. 

```xml
<QueryLogger applicationName="RecordsApp">
  <Store connectionString="Server=localhost;Database=recordsappdb;Trusted_Connection=True;" />
  <Email toAddress="me@test.ie" />
</QueryLogger>
```

### Anaithnidiú IP a chumrú

Cumraigh socruithe maidir le hanaithnidiú sheoladh IP an úsáideora.  

```xml
<QueryLogger applicationName="RecordsApp" anonymizeIPAddress="None">
  <Store connectionString="Server=localhost;Database=recordsappdb;Trusted_Connection=True;" />
  <Email toAddress="me@test.ie" />
</QueryLogger>
```

Faoi láthair, is ionann na leibhéil anaithnidithe atá ar fáil agus `None` (níor cuireadh anaithnidiú i bhfeidhm) agus `Partial` (baintear an t-ochtréad deireanach de sheoladh IPv4 an chliaint nó an 80 giotán deireanach de sheoladh IPv6). 

Is féidir leat cosc a chur leis an logálaí seoltaí IP a bhailiú ar an gcéad dul síos ach an socrú `StoreClientIPAddress` a chumrú:

```xml
<QueryLogger applicationName="RecordsApp" storeClientIPAddress="false">
  <Store connectionString="Server=localhost;Database=recordsappdb;Trusted_Connection=True;" />
  <Email toAddress="me@test.ie" />
</QueryLogger>
```

Nuair a shocraítear `StoreClientIPAddress` ag `false`, taifeadfar an luach `PRIVATE` sa cholún `IPAddress` de thábla an logálaí iarratais a bhaineann le do bhunachar sonraí. Má shocraítear `StoreClientIPAddress` ag `true`, ach mura féidir seoladh IP an chliaint a fháil ón gcomhthéacs HTTP ar chúis éigin, taifeadfar luach `UNKNOWN`.

## Logaí comhiomlánaithe iarratais agus anailís ar logaí

In [Gaois](https://www.gaois.ie), Fiontar & Scoil na Gaeilge, DCU comhiomlánaímid sonraí achoimre ó thábla na logaí iarratais go míosúil agus stórálaimid i dtábla bunachair sonraí eile iad. Chuireamar struchtúr an tábla agus na gnásanna stóráilte a bhainistíonn an próiseas ar fáil i bhfillteán na [scripteanna](https://github.com/gaois/Gaois.QueryLogger/tree/master/scripts) i stórlann GitHub Gaois.QueryLogger sa chás go mbeidh aon duine eile ag iarraidh úsáid a bhaint astu. Tá eintiteas `AggregratedQueryLog` ag Gaois.QueryLogger chomh maith a chomhfhreagraíonn d’iontrálacha i dtábla na logaí comhiomlánaithe. Faightear cuid de na hiarratais níos ginearálta SQL a úsáidimid chun sonraí logaí a achoimriú agus a anailísiú i bhfillteán na scripteanna.

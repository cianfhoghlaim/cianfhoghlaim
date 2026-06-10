---
title: GeoNames2Sql
description: Bunachar sonraí SQL a thógáil agus a chothú ach GeoNames Gazetteer a úsáid
keywords: GeoNames, gasaitéar, logainmneacha, logainmníocht, SQL, SQL Server, C#, .NET Core
github: https://github.com/gaois/GeoNames2Sql
public: true
---

Is uirlis é GeoNames2Sql a chuir [grúpa taighde Gaois](https://www.gaois.ie) in Fiontar & Scoil na Gaeilge, DCU le chéile chun sonraí Gasaitéir a iompórtáil ó [bhunachar sonraí geografach GeoNames](http://www.geonames.org/) agus a stóráil in ásc SQL Server. Is éard atá ann, go bunúsach, ná asbhaint thar leabharlann [NGeoNames](https://github.com/RobThree/NGeoNames), lena gcuirtear Comhéadan Líne na nOrduithe agus na huirlisí chun bunachar sonraí SQL a ghiniúint. Cuirtear GeoNames2Sql i bhfeidhm in C# mar Fheidhmchlár Consóil .NET Core 2.1. Ciallaíonn sé seo gur feidhmchlár trasardáin é. Glacann an cur i bhfeidhm stóras sonraí SQL Server ach ba chóir go mbeadh sé sách simplí soláthraithe a chur i bhfeidhm le haghaidh PostgreSQL nó cineálacha eile bunachar sonraí coibhneasta. 

## Stádas

Téann an feidhmchlár seo i ngleic le riachtanais ghrúpa taighde Gaois. Níl sé cuimsitheach do gach cás úsáide eile go fóill. Cuimsíonn an tacar sonraí aschuir táblaí a bhaineann le GeoNames, ainmneacha malartacha agus eolas ar an tír. Níl aon soláthar ann faoi láthair do ghnéchóid, cóid riaracháin, amchriosanna nó liostaí tagartha eile atá i dtacar sonraí GeoNames mar nach gcuimsítear i scóip ár gcuid riachtanas iad. D’fhéadfaí na míreanna seo a chur san áireamh amach anseo, más gá, agus cuirimid fáilte freisin roimh iarratais ar tharraingt ó úsáideoirí eile.

## Suiteáil agus cumraíocht

### Bunachar sonraí

1. Tabhair cead don fheidhmchlár rochtain a fháil ar bhunachar sonraí. 
2. Rith [script SQL](https://github.com/gaois/GeoNames2Sql/blob/master/scripts/CreateTables.sql) chun táblaí an bhunachair sonraí a chruthú.
3. Más mian leat, cruthaigh innéacsanna do do chuid táblaí. Cuirtear roinnt samplaí d’innéacsanna ar fáil [anseo](https://github.com/gaois/GeoNames2Sql/blob/master/scripts/CreateIndexes.sql).

Léiríonn scéimre an bhunachair sonraí struchtúr sonraí Ghasaitéar GeoNames ar a ndéantar cur síos [anseo](http://download.geonames.org/export/dump/).

### Feidhmchlár

Clónáil an stórlann ar do mheaisín:

```cmd
git clone https://github.com/gaois/GeoNames2Sql
```

Ansin, foilsigh tionscadal .NET Core in `src/GeoNames2Sql`, agus sonraigh an timpeallacht am rite atá mar sprioc agat, e.g.:

```cmd
dotnet publish -r win10-x64
```

**Leid:** Féach liosta na sprioc-aitheantóirí am rite [anseo](https://docs.microsoft.com/en-us/dotnet/core/rid-catalog?irgwc=1&OCID=AID681541_aff_7593_1243925&tduid=(ir_6d4f9ce9N213458eb7517c20a2b9db916)(7593)(1243925)(je6NUbpObpQ-wDYfcuMFmHDb6Ja3HC_Ryw)()&irclickid=6d4f9ce9N213458eb7517c20a2b9db916#using-rids?ranMID=24542&ranEAID=je6NUbpObpQ&ranSiteID=je6NUbpObpQ-wDYfcuMFmHDb6Ja3HC_Ryw&epi=je6NUbpObpQ-wDYfcuMFmHDb6Ja3HC_Ryw).

Aschuirfidh sé seo bailiúchán de leabharlanna nasctha dinimiciúla (comhaid .dll) agus comhad appsettings.json. Cóipeáil na comhaid seo sa chomhadlann ina rithfear an ríomhchlár, más gá. De rogha air sin, is féidir leat an feidhmchlár a rith laistigh de Visual Studio.

## Úsáid

Ligeann GeoNames2Sql duit ábhar do bhunachair sonraí aschuir a chumadh. Mar shampla, seans nach dteastóidh clúdach domhain ar thíortha an domhain uait nó b’fhéidir nach mbeidh uait ach fothacar sonraí i dteangacha áirithe. Is féidir leagan amach beacht an spriocbhunachair sonraí a shonrú laistigh den chomhad cumraíochta.

### Cumraíocht

Úsáid an comhad **appsettings.json** chun do spriocbhunachar sonraí a chumrú, e.g.:

```json
{
  "ConnectionString": "Server=localhost;Database=geonames;Trusted_Connection=True;",
  "DataDirectory": "C:/PATH/TO/DIRECTORY",
  "GeoNames": {
    "AllCountries": false,
    "AlternateNamesLanguages": [ "en", "ga" ],
    "CitiesMinimumPopulation": 15000,
    "Countries": ["AT", "BE", "CA", "CH", "CZ", "DE", "DK", "EE", "ES", "FI", "FR", "GB", "GR", "IE", "IM", "IT", "LU", "MT", "NL", "NO", "PL", "PT", "US", "SE", "no-country" ],
    "CountryInfo": true
  }
}
```

Tugtar achoimre sa tábla thíos ar na hairíonna cumraíochta.

| Eochair | Cur síos |
| ------- | -------- |
| **ConnectionString** | Teaghrán ceangail bhunachar sonraí SQL Server. | Tabhair faoi deara go gcaithfidh réimír `Data Source=` a bheith le teaghrán ceangail bhunachar Sqlite. |
| **DataDirectory** | An áit a bhfuil sé i gceist agat comhaid dumpála na sonraí loma a stóráil. Íoslódálfar na comhaid seo ó stóras sonraí GeoNames sula gcuirfear isteach sa bhunachar sonraí iad. |
| **GeoNames:AllCountries** | Má tá sé fíor, aisghabhfar sonraí GeoNames do gach tír i nGasaitéar GeoNames. Má tá sé fíor, ní chaithfear na luachanna `CitiesMinimumPopulation` nó `Countries` a shonrú. |
| **GeoNames:AlternateNamesLanguages** | Sonraigh na teangacha ina mbeidh logainmneacha malartacha agat. Tabhair eagar camógdheighilte de chóid teanga dhá-litir ISO. Má tá sé folamh, ní íoslódálfar sonraí teangacha malartacha. |
| **GeoNames:CitiesMinimumPopulation** | Má tá sé socraithe, aisghabhfar sonraí GeoNames do gach cathair ina bhfuil an t-íosdaonra sonraithe ar a laghad. Is iad **500**, **1,000**, **5,000** nó **15,000** na luachanna féideartha. |
| **GeoNames:Countries** | Má tá sé socraithe, aisghabhfar sonraí GeoNames a bhaineann leis na tíortha sonraithe. Tabhair eagar camógdheighilte de chóid tíortha ISO Alpha-2. |
| **GeoNames:CountryInfo** | Má tá sé fíor, pobalófar an tábla CountryInfo. |

Tabhair faoi deara go ndéantar cur síos sa chumraíocht ar shamhail shuimitheach. Mar shampla, aischuirfidh an chumraíocht shamplach thuas bunachar sonraí lena mbaineann na hairíonna seo a leanas:

- Beidh na sonraí GeoNames ar fad a bhaineann le liosta sonraithe tíortha ann.
- Beidh sonraí GeoNames a bhaineann le gach cathair ar fud an domhain ina bhfuil daonra de níos mó ná 15,000 sa bhunachar.
- Pobalóidh sé an tábla AlternateNames le sonraí sa dá theanga.
- Pobalóidh sé an tábla CountryInfo leis na sonraí ábhartha ar fad.

Pointí eile le lua:

- Ní bheidh ort comhaid dumpála na sonraí loma de chuid GeoNames a aisghabháil tú féin. Déanfaidh an feidhmchlár é seo duit. Sonraíonn tú an `DataDirectory` ina stórálfar na comhaid seo dá bharr sin.
- Bíonn cuid de théacschomhaid loma GeoNames idir 0.5-2.5GB dízipeáilte, ag brath ar an gcumraíocht a roghnaíonn tú. Cinntigh go bhfuil dóthain spás diosca ar an tiomántán ina bhfuil do `DataDirectory`.
- Athraíonn an t-am a thógann sé an bunachar sonraí a phobalú de réir na cumraíochta, e.g. an bhfuil gach tír nó fothacar tíortha sonraithe nó nach bhfuil, cá mhéad teangacha malartacha atá sonraithe, etc.

### An bunachar sonraí a phobalú

Ach an chumraíocht a shonrú, is féidir leat an ríomhchlár a rith. Cuir an chomhadlann san áit a bhfuil ríomhchlár foilsithe GeoName2Sql agus rith an t-ordú seo a leanas:

```
dotnet ./GeoNames2Sql.dll
```

Cuirfear tús leis an ríomhchlár agus iarrfar ort do chumraíocht a dheimhnú agus cur síos a dhéanamh ar leagan amach an bhunachair sonraí aschuir. Lean na treoracha ar an scáileán le dul ar aghaidh.

![Comhéadan Líne na nOrduithe GeoNames2Sql](/images/geonames2sql.jpg)

### An bunachar sonraí a nuashonrú

Déantar nuashonrú ar Ghasaitéar GeoNames ar bhonn leanúnach agus seans go mbeidh tú ag iarraidh na sonraí sa bhunachar sonraí SQL a thabhairt suas chun dáta leis na hathruithe is déanaí go tréimhsiúil. D’fhonn seo a dhéanamh, athrith an ríomhchlár. Cumascfaidh GeoNames2Sql sonraí nuashonraithe sa bhunachar sonraí reatha ar bhealach feidhmiúil: ní chaitear sonraí bailí atá ann cheana amach agus níor chóir go gcuirfeadh an próiseas ualach iomarcach ar an spriocbhunachar sonraí, fiú i dtimpeallachtaí táirgthe. Más mian leat leagan amach do spriocbhunachair sonraí a athrú, mar shampla, chun sonraí ó thíortha breise nó teangacha breise malartacha a chur san áireamh, ní chaithfidh tú ach an comhad cumraíochta a nuashonrú dá réir sin.

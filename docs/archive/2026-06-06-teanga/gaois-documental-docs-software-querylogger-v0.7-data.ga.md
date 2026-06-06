---
title: Sonraí iarratais a chur leis
description: Logálaí simplí iarratais is féidir a chumrú le haghaidh fheidhmchláir ASP.NET agus ASP.NET Core
keywords: logálaí iarratais, cuardaigh, staitisticí cuardaigh, foinse oscailte, C#, .NET Core, dotnet, SQL Server, Fiontar & Scoil na Gaeilge, DCU
order: 5
public: true
---

Tá an oibiacht `Query` i gcroílár Gaois.QueryLogger. Iompraíonn oibiachtaí `Query` sonraí an iarratais a logálfar i do stóras sonraí. Pobalóidh Gaois.QueryLogger sonraí áirithe iarratais go huathoibríoch, amhail óstach an fheidhmchláir nó IP an chliaint, roimh logáil ach caithfidh d’fheidhmchlár sonraí eile a shonrú. Is féidir gach iompraíocht réamhshocraithe a shárú. Déantar cur síos sa chuid eile den doiciméad seo ar na hairíonna éagsúla atá ar fáil chun sonraí d’iarratais a stóráil agus ar mhodhanna a d’fhéadfaí a ghlaoch ar an oibiacht `Query`. 

## Sonraí

**QueryID** (`Guid`): ID uathúil a léiríonn iarratas ar leith nó grúpa iarratas. Cruthófar ID iarratais go huathoibríoch mura sonraíonn d’fheidhmchlár é.

**ApplicationName** (`string`): Ainm an fheidhmchláir a ritheann an t-iarratas. Aisghabhfar ainm an fheidhmchláir ó do shocruithe cumraíochta mura sonraítear i gcód é. 

**QueryCategory** (`string`): Ceanglaíonn sé an t-iarratas le catagóir a shonraigh an feidhmchlár. Tá sé úsáideach, mar shampla, má tá cineálacha éagsúla cuardaigh agat laistigh d’fheidhmchlár amháin (roghnach).

**QueryTerms** (`string`): Téarma(í) an iarratais nó comhthéacs théacs an iarratais (roghnach). 

**QueryText** (`string`): Téacs lom an iarratais, amhail teaghrán iarratais nó réimse foirme POST-ed (roghnach).

**Host** (`string`): Fearann óstach an fheidhmchláir, e.g. www.example.com. Gheofar go huathoibríoch ón gcomhthéacs reatha HTTP é mura sonrófar a mhalairt.

**IPAddress** (`string`): Seoladh IP an chliaint. Gheofar go huathoibríoch ón gcomhthéacs reatha HTTP é mura sonrófar a mhalairt.

**ExecutedSuccessfully** (`bool`, réamhshocrú: `true`): Taifeadann sé cé acu a d'éirigh leis an iarratas rith nó nár éirigh.

**ExecutionTime** (`int?`): Aga rite an iarratais i milleasoicindí (roghnach). 

**ResultCount** (`int?`): Comhaireamh na dtorthaí a chuir an t-iarratas ar ais (roghnach).

**LogDate** (`DateTime`): Dáta agus am logáil an iarratais. Ginfear luach go huathoibríoch don airí seo nuair a logálfar é mura sonrófar a mhalairt. 

**JsonData** (`string`): Sonraí breise a thaifeadadh i bhformáid JSON. Tá sé úsáideach chun sonraí sainiúla feidhmchláir nó iarratais a stóráil i dtimpeallacht ilfheidhmchláir, mar shampla.

## Modhanna

**ToJson()** (`string`): Cuireann sé léiriú JSON ar oibiacht `Query` ar ais.

**FromJson()** (`Query`): Díshrathaíonn sé an JSON a cuireadh ar fáil ina oibiacht `Query`.

---
title: Gaois.QueryLogger
description: Logálaí simplí iarratais is féidir a chumrú le haghaidh fheidhmchláir ASP.NET agus ASP.NET Core
keywords: logálaí iarratais, cuardaigh, staitisticí cuardaigh, foinse oscailte, C#, .NET Core, dotnet, SQL Server, Fiontar & Scoil na Gaeilge, DCU
github: https://github.com/gaois/Gaois.QueryLogger
order: 1
public: true
---

Logálaí simplí iarratais is féidir a chumrú le haghaidh fheidhmchláir ASP.NET agus ASP.NET Core. Is é an logálaí iarratais a úsáideann [Gaois](https://www.gaois.ie), Fiontar & Scoil na Gaeilge, DCU chun staitisticí cuardaigh maidir le SQL Server a logáil é. Is leabharlann [.NET Standard 2.0](https://docs.microsoft.com/en-us/dotnet/standard/net-standard) é Gaois.QueryLogger agus tacaíonn sé le feidhmchláir a tógadh le ASP.NET Framework 4.6.1 agus le ASP.NET Core 2.1 nó níos airde.

## Stádas an phacáiste

| Pacáiste | NuGet (Cobhsaí) | NuGet (Réamheisiúint) | Íoslódálacha |
| -------- | ------------- | ------------------- | --------- |
| Gaois.QueryLogger | N/A | [![NuGet Pre Release](https://img.shields.io/nuget/vpre/Gaois.QueryLogger.svg)](https://www.nuget.org/packages/Gaois.QueryLogger/) | [![NuGet](https://img.shields.io/nuget/dt/Gaois.QueryLogger.svg)](https://www.nuget.org/packages/Gaois.QueryLogger/) |
| Gaois.QueryLogger.AspNetCore | N/A | [![NuGet Pre Release](https://img.shields.io/nuget/vpre/Gaois.QueryLogger.AspNetCore.svg)](https://www.nuget.org/packages/Gaois.QueryLogger.AspNetCore/) | [![NuGet](https://img.shields.io/nuget/dt/Gaois.QueryLogger.AspNetCore.svg)](https://www.nuget.org/packages/Gaois.QueryLogger.AspNetCore/) |

## Gnéithe

- Téarmaí iarratais agus meiteashonraí gaolmhara a logáil le SQL Server.
- Áirítear leis na meiteashonraí ID uathúil iarratais, ainm an iarratais, catagóir an iarratais, óstfhreastalaí, seoladh IP an chliaint, rath rith an iarratais, comhaireamh torthaí agus faisnéis am-dháta.  
- Is féidir le hiarratais GUID a roinnt, agus ciallaíonn sé sin gur féidir leat iarratais éagsúla ghaolmhara a chur i ngrúpaí.
- Meiteashonraí saincheaptha a chur le do chuid logálaithe. Úsáidimid é sin chun sonraí a bhaineann le feidhchlár faoi leith a stóráil i loga ilfheidhmchláir.
- De réir réamhshocraithe, déanann an leabharlann seoltaí IP an úsaideora a anaithnidiú ach an t-ochtréad deireanach de sheoltaí IPv4 an chliaint, nó an 80 giotán deireanach de sheoladh IPv6, a bhaint. Is féidir an socrú seo a mhúchadh.  
- Feidhmíocht: ní chuireann logáil aon taca breise le hagaí freagartha an fhreastalaí.
- Tá seirbhís fógraí ríomhphoist ag an logálaí a thabharfaidh foláireamh duit má tá aon earráid logála ann.

## Doiciméadacht

Athraíonn suiteáil agus úsáid beagáinín de réir na sprioc-chreatlaí. Lean na naisc thíos chun an doiciméadacht ábhartha a fheiceáil. 

- Léigh an doiciméadacht a bhaineann le ASP.NET Framework 4.6.1+ [anseo](../net461).
- Léigh an doiciméadacht a bhaineann le ASP.NET Core 2.1+ [anseo](../netcore).

Tá tuilleadh doiciméadachta ar fáil freisin maidir le [roghanna cumraíochta](../configuration) agus [sonraí saincheaptha logálaí](../data).  

## Cé atá á úsáid?

Tá úsáid táirgeachta á baint as Gaois.QueryLogger ag [www.tearma.ie](https://www.tearma.ie), [www.duchas.ie](https://www.duchas.ie), [www.gaois.ie](https://www.gaois.ie), [www.ainm.ie](https://www.ainm.ie), [www.logainm.ie](https://www.logainm.ie) agus [meitheal.logainm.ie](https://meitheal.logainm.ie).

## Creidiúintí breise

Is í leabharlann [StackExchange.Exceptional](https://github.com/NickCraver/StackExchange.Exceptional) a spreag cuid mhór d'ailtireacht Gaois.QueryLogger. Baineann Gaois.QueryLogger úsáid as dhá leabharlann tríú páirtí foinse oscailte eile: [Dapper](https://github.com/StackExchange/Dapper/) agus [AutoMapper](https://automapper.org/). 

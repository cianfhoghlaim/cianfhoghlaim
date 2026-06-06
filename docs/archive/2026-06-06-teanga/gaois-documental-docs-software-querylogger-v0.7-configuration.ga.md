---
title: Cumraíocht
description: Logálaí simplí iarratais is féidir a chumrú le haghaidh fheidhmchláir ASP.NET agus ASP.NET Core
keywords: logálaí iarratais, cuardaigh, staitisticí cuardaigh, foinse oscailte, C#, .NET Core, dotnet, SQL Server, Fiontar & Scoil na Gaeilge, DCU
order: 4
public: true
---

Is féidir na socruithe thíos a chumrú le bheith in oiriúint do do chuid riachtanais féin. Is féidir leat an logálaí iarratais a chumrú i gcód (ASP.NET Core amháin) nó i gcomhad cumraíochta d’fheidhmchláir. Féach an doiciméadacht a bhaineann le [ASP.NET Framework](../net461) agus le [ASP.NET Core](../netcore) chun teacht ar eolas ar chur i bhfeidhm an logálaí i do sprioc-chreatlach.

## Barrleibhéal

**ApplicationName** (`string`): Sonraíonn sé ainm uilíoch ar d’fheidhmchlár a d’fhéadfaí a úsáid i ngach iarratas a logáiltear. Ciallaíonn sé seo gur féidir le feidhmchláir dhifriúla an bunachar sonraí céanna SQL a roinnt maidir le logáil iarratais.

**MaxQueryTermsLength** (`int?`): Má tá sé socraithe, theascfaí téarmaí iarratais atá níos faide ná an t—uasfhad sonraithe.

**MaxQueryTextLength** (`int?`): Má tá sé socraithe, theascfaí téacs iarratais atá níos faide ná an t—uasfhad sonraithe.

**IsEnabled** (`bool`, réamhshocrú: `true`): Sonraíonn sé ar cumraíodh an feidhmchlár chun iarratais a logáil nó nár cumraíodh. Seans go mbeidh sé úsáideach más gá duit logáil a dhíchumasú go sealadach ar chúis éigin nó más mian leat logáil a chumasú nó a dhíchumasú bunaithe ar athróga timpeallachta.

**StoreClientIPAddress** (`bool`, réamhshocrú: `true`): Sonraíonn sé ar cheart seoladh IP an chliaint a logáil nó nár cheart. Seans go mbeidh cuid den seoladh IP logáilte anaithnidithe, nó seans nach mbeidh sé, de réir an tsocraithe `AnonymizeIPAddress` a roghnaíodh. 

**AnonymizeIPAddress** (`IPAddressAnonymizationLevel` enum, réamhshocrú: `IPAddressAnonymizationLevel.Partial`): Socraíonn sé leibhéal anaithnidithe sheoladh IP an chliaint. Is iad `None` (níor cuireadh anaithnidiú i bhfeidhm) nó `Partial` (baintear an t-ochtréad deireanach de sheoltaí IPv4 nó an 80 giotán deireanach de sheoladh IPv6) na luachanna féideartha. Thángamar ar an tuairim nach féidir anaithnidiú ‘iomlán’ — trí haiseáil nó ar bhealach ar bith eile — a chinntiú agus molaimid an socrú `StoreClientIPAddress` a athrú go `false` le cinntiú nach logálfar sonraí IP ar bith.

**AlertInterval** (`integer`, réamhshocrú: `300000`): An t-eatramh ama (i milleasoicindí) a fhanfaidh an logálaí iarratais sula seolfar foláirimh maidir le ceist faoin tseirbhís logálaí. Seolfar foláirimh má sháraíonn an ciú logálaí an uasacmhainn nó má tá ceist ann i dtaca le scríobh chuig an stóras sonraí — tá súil againn nach dtarlóidh sé sin ach nílimid ag iarraidh do bhosca isteach a bhriseadh má tharlaíonn sé.

## Stóras

**ConnectionString** (`string`): An teaghrán ceangail do do stóras sonraí de chuid SQL Server.

**ConnectionStringName** (`string`, **ASP.NET Framework only**): Ainm an teaghráin ceangail a úsáidtear ó chumraíocht an fheidhmchláir, e.g. an eochair a bhaineann le hiontráil ar leith sa chuid `ConnectionStrings` den chomhad Web.config de chuid feidhmchláir. 

**MaxQueueSize** (`integer`, réamhshocrú: `1000`): Uasmhéid fhéideartha chiú an logálaí iarratais. Nuair a bhaintear uasmhéid an chiú amach, cuileálfar iontrálacha sa chiú ar bhonn 'is túisce isteach is túisce amach'. Ba cheart duit méid an chiú a shocrú i bhfianaise na n-acmhainní atá ar fáil ar do chóras. Ach logaí a stóráil i gciú sula maireann sonraí, laghdaítear an seans go gcaillfidh tú sonraí mar gheall ar cheist seachadta faoi IOPS an bhunachair sonraí, mar shampla.

**MaxQueueRetryInterval** (`integer`, réamhshocrú: `300000`): An méid ama (i milleasoicindí) is gá duit fanacht idir iarrachtaí ar scríobh chuig an stóras logálaí sa chás nach féidir ceangal leis an stóras a chruthú. D’fhéadfadh suas le `MaxQueueSize` iarratas a bheith i gciú an logálaí atá le scríobh.

**TableName** (`string`, réamhshocrú: `QueryLogs`): Ainm an tábla (lena n-áirítear scéimre, más mian leat), e.g. 'dbo.QueryLogs' a úsáidtear nuair atá iarratais á logáil. Cumraigh é seo más mian leat ainm níos andúchasaí a thabhairt ar do thábla logálaí seachas 'QueryLogs'.

## Ríomhphost

Úsáidfear na socruithe seo, má cumraíodh iad, chun ríomhphoist foláirimh a sheoladh chugat nuair is gá. Maidir le feidhmchláir ASP.NET Framework, gheofar socruithe ríomhphoist go huathoibríoch ó do chumraíocht `mailSettings`, má tá siad ann, ach ní mór duit `ToAddress` a shonrú anseo fós.

**ToAddress** (`string`): An seoladh a seolfar teachtaireachtaí ríomhphoist chuige (ag teastáil le haghaidh seirbhís foláireamh).

**FromAddress** (`string`): An seoladh óna seolfar teachtaireachtaí ríomhphoist.

**FromDisplayName** (`string`): An t-ainm taispeána lena seolfar teachtaireachtaí ríomhphoist.

**SMTPHost** (`string`): An freastalaí SMTP trína seolfar ríomhphost.

**SMTPPort** (`int?`): An port trína seolfar ríomhphost (má shonraítear freastalaí SMTP trí `SMTPHost` thuas.)

**SMTPUserName** (`string`): Ainm úsáideora an SMTP a úsáidfear, má tá fíordheimhniú á dhéanamh agat.

**SMTPPassword** (`string`): Pasfhocal an SMTP a úsáidfear, má tá fíordheimhniú á dhéanamh agat.

**SMTPEnableSSL** (`bool`, réamhshocrú: `false`): SSL a úsáid agus rud á sheoladh trí SMTP agat, nó gan é a úsáid.

## ExcludedIPAddresses

Ní logálfar iarratais a bhaineann leis na seoltaí IP sa liosta seo. Tá sé úsáideach, mar shampla, le cinntiú nach logálfar iarratais ó ransaitheoir ionsaitheach gréasáin.

**IPAddress** (`string`): An seoladh IP a fhágfar ar lár (caithfidh luach uathúil a bheith air).

**Name** (`string`): Cuireann sé lipéad ar an seoladh IP a fhágfar ar lár. Is é an seoladh IP an eochair iontrála agus mar sin de, is féidir leat an t-ainm céanna a shocrú le haghaidh iontrálacha éagsúla más mian leat go leor foinsí IP a chur i ngrúpa le chéile.

---
title: Gaois.Localizer
description: Foireann uirlisí i dtaca le feidhmchláir ghréasáin ilteangacha a thógáil ar ASP.NET Core
keywords: logánú, idirnáisiúnú, bogearraí, foinse oscailte, C#, .NET Core, dotnet, Fiontar & Scoil na Gaeilge, DCU
github: https://github.com/gaois/Gaois.Localizer
nuget: https://www.nuget.org/packages/Gaois.Localizer/
public: true
---

**Tabhair faoi deara:** Is **leagan réamheisiúna** é seo ar mhaithe le tástáil. Bí ag súil le roinnt athruithe briste agus le modhanna athainmnithe API sula mbeidh eisiúint 1.0 againn. 

Foireann uirlisí i dtaca le feidhmchláir ghréasáin ilteangacha a thógáil ar ASP.NET Core atá anseo. Cuireann sé meánearraí logánaithe is féidir a chumrú ar fáil, lena n-áirítear bailíochtóirí chultúr an iarratais, bainistíocht fianán, láimhseálaithe eisceachtaí agus rialacha maidir le URL a athscríobh. Timfhilleann agus breisíonn siad feidhmeanna dúchasacha [domhandaithe agus logánaithe](https://docs.microsoft.com/en-us/aspnet/core/fundamentals/localization?view=aspnetcore-2.1) na creatlaí chun an dua a bhaint de shuíomhanna gréasáin logánaithe a thógáil.

D'fhorbair [Gaois](https://www.gaois.ie), Fiontar & Scoil na Gaeilge, DCU an leabharlann agus tá sí in úsáid againn chun feidhmchláir ghréasáin ilteangacha dár gcuid féin a thógáil.

## Gnéithe

Cuireann an leabharlann feidhmiúlacht ar an bpointe boise ar fáil a cheadaíonn duit:

- Cultúr an iarratais a fháil ó pharaiméadair chosán URL amhail `www.mymultilingualapp.com/en-GB/about/` agus `www.mymultilingualapp.com/ga/about/`.
- Fianáin agus ceanntásca HTTP `Accept-Language` a úsáid chun tátal a bhaint as an gcultúr atá ón úsáideoir nuair a thugann siad cuairt ar leathanach baile an tsuímh gréasáin, e.g. `www.mymultilingualapp.com`, áit nach bhfaightear aon pharaiméadar cosáin.
- Iarratais ar chultúir gan tacaíocht a láimhseáil, ach leathanach earráide 404 a chur ar ais nó an t-úsáideoir a atreorú chuig leathanach sa teanga réamhshocraithe.
- Gan róid áirithe a chur faoi thionchar na meánearraí logánaithe.
- Socruithe a bhaineann le fianáin logánaithe a bhainistiú agus a chumrú ionas go bhféadfaí roghanna teanga an úsáideora a choinneáil le linn na seisiún brabhsála.
- Cinneadh ar chóir go n-atreorófaí na húsáideoirí chuig URL logánaithe nuair a dhéanann siad iarratas ar leathanach baile an tsuímh gréasáin don chéad uair.
- Cásanna a láimhseáil ina dteastaíonn uait cód teanga ISO sa URL ina bhfuil dhá nó trí litir a mhapáil go hinmheánach le réigiún nó le fochlib breisithe teanga.

Is féidir an chuid is mó de na gnéithe seo a chumrú: cuirtear réamhshocruithe ciallmhara ar fáil, ach is féidir leat na cineálacha atreoruithe a úsáidtear, tréimhse bhailí fianán logánaithe, etc., a shonrú. Smaoiníodh ar SEO agus an leabharlann á dearadh, agus tugann an tsuiteáil réamhshocraithe réiteach optamach logánaithe dúinn maidir leis an innéacsú a dhéanann na príomhinnill chuardaigh. Oibríonn na meánearraí logánaithe go maith, fiú nuair a ritear i gcomhadlann fhíorúil iad. 

## Suiteáil agus cumraigh

Cuir an pacáiste [Gaois.Localizer](https://www.nuget.org/packages/Gaois.Localizer/) le tionscadal ASP.NET Core 2.1+ ar bith.

```cmd
dotnet add package Gaois.Localizer
```

In **Startup.cs**, cuir an treoir `using Gaois.Localizer` ag barr an chomhaid. Déantar an chumraíocht ar fad ar an bpacáiste sa chomhad seo. Braitheann an chumraíocht a bhaineann le d’iarratas ar do chuid riachtanas féin.  

### Cumraíocht bhunúsach

1. Cuir na meánearraí `app.UseLocalizer()` leis an modh *Configure* áit ar bith tar éis `app.UseStaticFiles()` (más ann dó) agus roimh `app.UseMvc()`, mar seo a leanas:  

```csharp
public void Configure(IApplicationBuilder app, IHostingEnvironment env)
{
    if (env.IsDevelopment())
    {
        app.UseDeveloperExceptionPage();
    }
    else
    {
        app.UseExceptionHandler("/Error");
        app.UseStatusCodePagesWithReExecute("/Error/{0}");
    }

    app.UseStaticFiles();

    app.UseLocalizer();

    app.UseMvc(routes =>
    {
        routes.MapRoute(
            name: "default",
            template: "{controller=Home}/{action=Index}/{id?}");
    });
}
```

2. Mionathraigh an modh *ConfigureServices*:

```csharp
public void ConfigureServices(IServiceCollection services)
{
    services.AddLocalization(options =>
    {
        options.ResourcesPath = "Resources";
    });

    services.AddMvc()
        .SetCompatibilityVersion(CompatibilityVersion.Version_2_1)
        .AddRazorPagesOptions(options =>
        {
            options.RootDirectory = "/Pages";
            options.Conventions.AddPageRoute("/Index", route: "{culture?}");
            options.Conventions.AddPageRoute("/About", route: "{culture}/about/{id?}");
            options.Conventions.AddPageRoute("/Error", route: "/Error/{0}");
        })
        .AddViewLocalization(LanguageViewLocationExpanderFormat.Suffix, options =>
        {
            options.ResourcesPath = "Resources";
        })
        .AddDataAnnotationsLocalization();

    services.AddLocalizer(options =>
    {
        var supportedCultures = new[]
        {
            new CultureInfo("en-GB"),
            new CultureInfo("ga-IE")
        };
        options.SupportedCultures = supportedCultures;
        options.SupportedUICultures = supportedCultures;
        options.DefaultRequestCulture = new RequestCulture(culture: "en-GB", uiCulture: "en-GB");
    });
}
```

Tá na roghanna `SupportedCultures`, `SupportedUICultures` agus `DefaultRequestCulture` riachtanach.

## Cultúr an iarratais a fháil 

Is é príomhsprioc an phacáiste seo ná éascaíocht a dhéanamh maidir le tuiscint a fháil ar an teanga a úsáidfidh an t-úsáideoir agus é ag dul isteach i do shuíomh gréasáin ionas gur féidir leis an bhfeidhmchlár an cultúr ceart a shocrú agus na hábhair a logánú ón úsáideoir. Gheobhaidh tú a bhfuil uait chun cultúr an iarratais a léirmhíniú ó URL sa chumraíocht íosta a pléadh roimhe seo. 

```csharp
public void ConfigureServices(IServiceCollection services)
{
    ...

    services.AddLocalizer(options =>
    {
        var supportedCultures = new[]
        {
            new CultureInfo("en-GB"),
            new CultureInfo("ga-IE")
        };
        options.SupportedCultures = supportedCultures;
        options.SupportedUICultures = supportedCultures;
        options.DefaultRequestCulture = new RequestCulture(culture: "en-GB", uiCulture: "en-GB");
    });
}
```

Liostaítear sna hathróga `supportedCultures` na teangacha agus na cineálacha cultúr ar mhaith linn tacú leo san fheidhmchlár. Cuireann an `DefaultRequestCulture` an tacachumas deiridh ar fáil mura féidir tátal a bhaint as an gcultúr atá ag teastáil ón iarratas HTTP.

Parsálann na meánearraí logánaithe an t-iarratas HTTP agus cuireann siad sprioc-chultúr ar ais de réir na gcritéar seo a leanas:

1. Paraiméadar chosán an chultúir, i.e. [clib teanga IETF](https://en.wikipedia.org/wiki/IETF_language_tag), in URL an iarratais (e.g. an paraiméadar 'ga-IE' in `www.mymultilingualapp.com/ga-IE/`).
2. Bíonn fianán cultúir san iarratas a fuarthas ón suíomh gréasáin roimhe seo (féach [thíos](#fianain-loganaithe)).
3. Shonraigh an t-úsáideoir an teanga atá uaidh sa bhrabhsálaí (a fuarthas tríd an gceanntásc HTTP `Accept-Language`) a mheaitseálann ceann de chultúir an fheidhmchláir a dtacaítear leo.
4. An teanga réamhshocraithe a sonraíodh sa tseirbhís `RequestLocalizationOptions`.

Úsáidfear an chéad chritéar a chuireann toradh neamhnialasach ar ais. Mar sin de, taispeánfar leathanach sa Rúisis d’úsáideoir a théann isteach in `www.mymultilingualapp.com/ru-RU/`, is cuma na socruithe brabhsálaí atá aige. Taispeánfar leathanach sa Bhéarla d’úsáideoir a roghnaíonn `en` mar a theanga roghnaithe agus a thugann cuairt ar `www.mymultilingualapp.com`.

Déanfar na seiceálacha seo nuair a bhaintear an modh `app.UseLocalizer()` amach i rith an iarratais. Is féidir leis na meánearraí agus loighic an fheidhmchláir a ghlaoitear ina dhiaidh seo rochtain a fháil ar chultúr an iarratais tríd an oibiacht `CultureInfo.CurrentCulture`.

### Paraiméadar chosán an chultúir a chumrú

De réir réamhshocraithe, glacann Gaois.Localizer leis go gcumsaítear sa chéad pharaiméadar de chuid chosán an iarratais, i.e. paraiméadar `ga-IE` in URL `www.mymultilingualapp.com/ga-IE/about/our-story/`, faisnéis an sprioc-chultúir, mar a dhéantar de ghnáth. Is féidir leat an feidhmchlár a chumrú chun innéacs difriúil paraiméadair a úsáid, áfach: 

```csharp
services.AddLocalizer(options =>
{
    ...
    options.RouteCulture.CultureParameterIndex = 2;
});
```

Déanfaidh an feidhmchlár iarracht anois an dara paraiméadar cosáin san iarratas a úsáid nuair atá cultúr an iarratais á mheas aige. Ciallaíonn sé seo go n-oibreoidh URL ar nós `www.mymultilingualapp.com/shop/fr-FR/products/` mar a bheifeá ag súil leis.

### Focal faoi SEO

Is dócha gurb é seo an ghné is teanntásaí den leabharlann seo, agus tugtar tús áite i gcónaí do chultúr a fhaightear ó pharaiméadar cosáin URL i bhfianán cliaint nó i socruithe ceanntáisc HTTP. Má thugann úsáideoir cuairt ar `www.mymultilingualapp.com/en-GB/` agus más é Béarla na Stát Aontaithe (en-US) a theanga roghnaithe don bhrabhsálaí, gheobhaidh sé an leathanach i mBéarla na Ríochta Aontaithe (en-GB) fós, ar choinníoll go dtacaítear leis an gcultúr seo laistigh den fheidhmchlár. Ciallaíonn sé seo (i) go bhfaigheann úsáideoirí an leathanach lena raibh siad ag súil nuair a chliceáil siad ar an URL, agus (ii) gur féidir le ransaitheoirí cuardaigh URL a cheangal le hábhar logánaithe go hiontaofa. Creidimid go bhfuil sé seo barrmhaith do SEO agus d’eispéireas an úsáideora. Ach an leathanach a oscailt, ba chóir go mbeadh úsáideoirí in ann teangacha a athrú dá ndeoin féin trí mhalartóir tiomnaithe teanga sa UI. 

## Cultúir gan tacaíocht

Cad a tharlaíonn nuair a ionchuireann úsáideoir URL ina bhfuil cultúr gan tacaíocht? Mar shampla, má thacaíonn do shuíomh le hábhar sa Spáinnis agus sa Phortaingéilis, ach tugann an t-úsáideoir fochlib don réigiún `fr-FR` sa URL. Go hinmheánach, caithfidh na meánearraí logánaithe `CultureNotFoundException` sa chás seo. Cuireann Gaois.Localizer dhá bhealach ar fáil chun an earráid seo a láimhseáil.

### Cód stádais '*404 Not Found*' a chur ar ais

De réir réamhshocraithe, cuirfear cód stádais HTTP '*404 Not Found*' ar ais mar fhreagrairt ar iarratas ar chultúr gan tacaíocht agus taispeánfar teachtaireacht oiriúnach don úsáideoir, ar choinníoll gur cumraíodh ród don leathanach earráide. Seans gurb é seo an cur chuige is fearr maidir le SEO. Ní bheidh amhras ar bith ar innill chuardaigh nach bhfuil ábhar ar fáil ag an URL a iarradh.  

### An t-úsáideoir a atreorú chuig leathanach sa chultúr réamhshocraithe

I gcásanna áirithe, b’fhéidir gurb é seo an rogha is fearr d’eispéireas an úsáideora. Nuair a théitear isteach in URL ina bhfuil cultúr gan tacaíocht, atreorófar an cliant chuig leathanach coibhéiseach i gcultúr réamhshocraithe an fheidhmchláir. Chun é seo a chur i bhfeidhm, cumraigh `RequestCultureRerouter` sa modh *ConfigureServices* in **Startup.cs**. De réir réamhshocraithe, cuirfidh an fhreagairt atreorú 302 chuig an gcosán céanna le paraiméadar nuashonraithe cultúir ar ais.

```csharp
services.AddLocalizer(options =>
{
    ...
    options.RequestCultureRerouter.RerouteRequestCultureExceptions = true;
});
```

#### An t-athródaire a chumrú

Is féidir leat tuilleadh cumraíochta a dhéanamh ar an ródaire le gur féidir leis cód stádais difriúil HTTP a sheoladh sa fhreagairt nó atreoruithe a ródú ar chosán ar leith. 

```csharp
services.AddLocalizer(options =>
{
    ...
    options.RequestCultureRerouter.RerouteRequestCultureExceptions = true;
    options.RequestCultureRerouter.StatusCode = 301;
    options.RequestCultureRerouter.ResponsePath = "/en-GB/lost/";
});
```

## Róid a fhágáil ar lár

B’fhéidir go n-úsáidfeá an chéad pharaiméadar de do chosán iarratais chun an sprioc-chultúr a léiriú an chuid is mó den am, ach b’fhéidir gur mhaith leat róid áirithe a fhágáil ar lár sa phíblíne logánaithe, mar shampla `www.mymultilingualapp.com/api/v1.2`.  Ach an chumraíocht ar an bpointe boise a úsáid, caithfidh URL dá leithéid `CultureNotFoundException`. Is féidir leat é seo a chosc, áfach, ach róid áirithe a fhágáil ar lár laistigh de chumraíocht do sheirbhíse:

```csharp
services.AddLocalizer(options =>
{
    ...
    options.RouteCulture.ExcludedRoutes.Add(@"^/api");
    options.RouteCulture.ExcludedRoutes.Add(@"^/content");
});
```

Úsáidtear teaghráin shloinn rialta chun sainmhíniú a thabhairt ar chosáin. Cuirtear róid a thosaíonn le `/error`, e.g. `/Error` nó `/error/{0}/`,  leis an liosta eisiaimh de réir réamhshocraithe chun fadhbanna i dtaca le ródú ciorclach a sheachaint nuair a chaitear  `CultureNotFoundException`. 

## Fianáin logánaithe

Nuair a thugann úsáideoir cuairt ar do shuíomh gréasáin, seans go socróidh siad teanga eile a roghnú trí mhalartóir teanga nó trí shaoráid UI den chineál céanna. D’fhéadfadh sé a bheith úsáideach rogha an úsáideora a stóráil i bhfianán ionas go gcuimhneoidh an feidhmchlár ar an rogha agus gur féidir leis an úsáideoir tosú arís san áit ar stop sé an chéad uair eile. Ar an dea-uair, tá [soláthraí](https://docs.microsoft.com/en-us/aspnet/core/fundamentals/localization?view=aspnetcore-2.1#set-the-culture-programmatically) ionsuite in ASP.NET Core a iarcheanglaíonn fianáin chultúir leis an bhfreagairt HTTP. Timfhilleann Gaois.Localizer an soláthraí seo i loighic úsáideach a fhaightear i bpíblíne rite an iarratais: níl ar iarratais POST nó ar rialaitheoirí breise roghanna teanga an úsáideora a shocrú nó a nuashonrú, mar sin de. Níl ort ach an modh *AddLocalizer* a chumrú in **Startup.cs**: 

```csharp
services.AddLocalizer(options =>
{
    ...
    options.LocalizationCookies.UseLocalizationCookies = true;
});
```

Cinnteoidh meánearraí na bhfianán logánaithe go dtaispeántar do shuíomh i gcultúr roghnaithe an úsáideora gach uair a thugann sé cuairt ar an leathanach baile. Ná déan dearmad, áfach, go dtugann na huirlisí logánaithe [tús áite don chultúr i bparaiméadair chosáin URL ar aon socrú eile](#focal-faoi-seo), mar sin de, má leanann an t-úsáideoir nasc chuig leathanach i gcultúr ar leith, ní chuirfear fianáin logánaithe san áireamh. 

### Na fianáin logánaithe a chumrú

Más mian leat, is féidir tuilleadh cumraíochta a dhéanamh ar shocruithe na bhfianán logánaithe, rud a cheadóidh duit dáta éaga an fhianáin agus an bhfuil an fianán riachtanach d’fheidhmiú an fheidhmchláir, nó nach bhfuil, a shonrú. Is iad `1 year` agus `false` na luachanna réamhshocraithe, faoi seach. Ba chóir an t-airí `IsEssential` a chumrú maidir le do pholasaithe príobháideachais agus cosanta sonraí. Má tá sé fíor, d’fhéadfaí seiceálacha ar an bpolasaí toilithe a sheachaint.

```csharp
services.AddLocalizer(options =>
{
    ...
    options.LocalizationCookies.UseLocalizationCookies = true;
    options.LocalizationCookies.Expires = DateTime.UtcNow.AddDays(5);
    options.LocalizationCookies.IsEssential = true;
});
```

## Atreorú an leathanaigh lamairne

Nuair a thugann úsáideoir cuairt ar leathanach baile suímh gréasáin, e.g. `www.mymultilingualapp.com`, d’fhéadfadh sé a bheith inmhianaithe uaireanta an t-úsáideoir a atreorú chuig URL a bhaineann le leagan logánaithe den leathanach go huathoibríoch, e.g. `www.mymultilingualapp.com/es`. Ní hionann é seo agus an iompraíocht réamhshocraithe a bhaineann le Gaois.Localizer a úsáid ar chúiseanna SEO (féach thíos) ach aithnímid gur cás coiteann úsáide é. Chun atreorú an leathanaigh lamairne a chur ar siúl, cumraigh an modh *AddLocalizer* in **Startup.cs**:

```csharp
services.AddLocalizer(options =>
{
    ...
    options.RequireCulturePathParameter.RequireCulturePathParameter = true;
});
```

Aithníonn URL an atreoraithe na socruithe a cumraíodh sa tseirbhís [`Microsoft.AspNetCore.Routing.RouteOptions`](https://docs.microsoft.com/en-us/dotnet/api/microsoft.aspnetcore.routing.routeoptions?view=aspnetcore-2.1) go huathoibríoch, i dtaca le slais chun deiridh a iarcheangal leis an URL ginte nó gan í a iarcheangal.

### Focal eile faoi SEO

Is féidir glacadh le cuir chuige éagsula agus leathanach baile an tsuímh gréasáin á logánú agat. Measfaidh roinnt suíomhanna gréasáin teanga roghnaithe an úsáideora agus atreoróidh siad chuig URL nua é, amhail aistriú idir `example.com` agus `example.com/es`. D’fhéadfadh sé seo deacrachtaí a chruthú, áfach, mar gheall ar nádúr na n-atreoruithe HTTP agus an chaoi a n-idirghníomhaíonn siad leis an mbrabhsálaí:

- Scrúdaíonn roinnt suíomhanna gréasáin (mar shampla, [mozilla.org](https://www.mozilla.org/)) roghanna teanga an bhrabhsálaí agus cuireann siad atreorú (buan) 301 i bhfeidhm. Tá sé seo go breá má tá tú sách cinnte go rachaidh an chuid is mó d’úsáideoirí isteach san fheidhmchlár i dteanga amháin. Taiscfidh go leor brabhsálaithe atreoruithe 301 go deo, áfach. Má nuashonraíonn an t-úsáideoir socruithe an bhrabhsálaí – nó má dhéanann sé rochtain ar an ríomhaire in áit phoiblí, amhail scoil nó leabharlann – tabharfaidh an brabhsálaí chuig an gcéad leagan logánaithe den suíomh a osclaíodh sa bhrabhsálaí sin i gcónaí é. 
- Cuireann go leor suíomhanna gréasáin eile atreoruithe 302 i bhfeidhm ar na cúiseanna thuas, is dócha. Níl sé soiléir, áfach, an dtugann príomhransaitheoirí gréasáin aird ar leathanaigh ar a bhfuil atreoruithe 302 nó nach dtugann, agus seans nach n-oirfidh sé seo do SEO.

Is é an cur chuige réamhshocraithe a bhaineann le leabharlann Gaois.Localizer a úsáid dá bharr seo ná nach n-atreoraítear an t-úsáideoir (i.e. fanann an t-úsáideoir ar `example.com`), cé go logánófar an t-eolas ar an gcultúr de réir na gcritéar [thuas](#cultur-an-iarratais-a-fhail). Sílimid go mbaineann na torthaí is fearr leis seo ó thaobh SEO agus eispéireas an úsáideora de.

## Rogha na clibe teanga

Tá an leabharlann il-oiriúnach maidir le [clib theanga IETF](https://en.wikipedia.org/wiki/IETF_language_tag) a úsáideann tú sa URL chun an sprioc-chultúr a léiriú. Úsáideann na samplaí sa doiciméad seo fochlibeanna réigiúin amhail `ga-IE`, `en-GB`, `pt-BR`, etc. Is fearr le go leor feidhmchlár cóid teanga ISO ina bhfuil dhá litir amhail `ga`, `en`, `fr`. In athróg na gcultúr a dtacaítear leo, a bhaineann le `RequestLocalizationOptions` in **Startup.cs**, is féidir ceachtar de na cineálacha clibe seo a shonrú. 

Má roghnaíonn tú cóid teanga dhá litir, d’fhéadfadh sé a bheith úsáideach fochlibeanna réigiúin nó fochlibeanna breisithe teanga a stóráil a mhapálann le do chóid teanga – mar shampla, nuair a chuireann tú sonraí logchaighdeáin ar fáil i meitichlibeanna [Open Graph](http://ogp.me/). Éascaíonn Gaois.Localizer é seo ach cead a thabhairt duit roghanna chultúr an róid a chumrú sa mhodh *Configure* de **Startup.cs**:

```csharp
services.AddLocalizer(options =>
{
    ...
    options.RouteCulture.LanguageLocaleMap.Add("en", "en-GB");
    options.RouteCulture.LanguageLocaleMap.Add("ga", "ga-IE");
});
```

Is féidir rochtain a fháil ar na clibeanna mapáilte áit éigin eile san fheidhmchlár ansin, agus cuirtear feidhm éascaíochta `InferLocaleFromLanguage()` ar fáil chun an chlib cheart logchaighdeáin nó réigiúin a aschur nuair a fhaightear cód comhfhreagrach teanga.

Úsáid shamplach (amharc Razor):

```csharp
@using Gaois.Localizer
@inject IOptions<RequestLocalizationOptions> LocalizationOptions
@inject IOptions<RouteCultureOptions> CultureOptions

...

@foreach (var culture in LocalizationOptions.Value.SupportedUICultures)
{
    if (culture.Name != CultureInfo.CurrentCulture.Name)
    {
        string lang = @culture.TwoLetterISOLanguageName;
        string locale = CultureOptions.Value.InferLocaleFromLanguage(@lang);
        <link rel="alternate" hreflang="@lang" href="https://www.mymultilingualapp.com/(@lang)">
        <meta property="og:locale:alternate" content="@locale">
    }
}
```

## Aistriú idir clibeanna teanga i scéim URL

Más mian leat aistriú ó scéim URL a d’úsáid clibeanna teanga dhá litir (amhail `example.com/es`) chuig scéim a úsáideann logchaighdeáin réigiúnacha (amhail `example.com/es-ES`), tá prótacal úsáideach atreoraithe ar fáil in Gaois.Localizer a bhaineann leas as meánearraí athscríofa dúchasacha an URL de chuid ASP.NET Core chun an obair chrua a dhéanamh duit.

Ar dtús, cumraigh an modh *AddLocalizer* mar a dhéantar cur síos air sa [mhír roimhe seo](#rogha-na-clibe-teanga):

```csharp
public void ConfigureServices(IServiceCollection services)
{
    ...

    services.AddLocalizer(options =>
    {
        ...
        options.RouteCulture.LanguageLocaleMap.Add("en", "en-GB");
        options.RouteCulture.LanguageLocaleMap.Add("ga", "ga-IE");
    });

    ...
}
```

Is féidir leat an `LanguageLocaleMap` a chur chuig oibiacht `RedirectLanguageToLocale` ansin i meánearraí athscríofa an URL:

```csharp
public void Configure(IApplicationBuilder app, IHostingEnvironment env)
{
    ...

    var routeCultureOptions = app.ApplicationServices
        .GetService<IOptions<RouteCultureOptions>>().Value;

    var rewriteOptions = new RewriteOptions()
        .Add(new RedirectLanguageToLocale(routeCultureOptions.LanguageLocaleMap));

    app.UseRewriter(rewriteOptions);

    ...

    app.UseMvc();
}
```

Atreorófar gach iarratas ar `www.mymultilingualapp.com/ga/about/` go huathoibríoch chuig `www.mymultilingualapp.com/ga-IE/about/` anois. Cuireann an oibiacht `RedirectLanguageToLocale` atreorú 302 i bhfeidhm de réir réamhshocraithe, ach is féidir leat 301 nó cineál eile atreoraithe a shonrú in argóint roghnach.

## Modhanna cabhracha

Aimsítear modhanna breisithe in Gaois.Localizer chomh maith, a chuidíonn le tascanna a bhaineann le logánú.

### GetDisplayUrl()

Breisíonn an modh seo an modh [*GetDisplayUrl()*](https://docs.microsoft.com/en-us/dotnet/api/microsoft.aspnetcore.http.extensions.urihelper.getdisplayurl?view=aspnetcore-2.2) agus ligeann sé seo duit paraiméadar cosáin URL (má tá sé ann) a athchur de réir innéacs.

### GetEncodedUrl()

Is ionann é seo agus an modh roimhe seo, ach aschuireann sé seo teaghrán atá ionchódaithe go hiomlán mar URL. I gcomhthéacs logánú an fheidhmchláir gréasáin, tá an modh seo an-úsáideach nuair atá naisc mhalartacha le paraiméadair mhalartacha cultúr á nginiúint agat:

```c#
<link rel="alternate" hreflang="@lang" href="@Context.Request.GetEncodedUrl(1, "fr-FR")">
```

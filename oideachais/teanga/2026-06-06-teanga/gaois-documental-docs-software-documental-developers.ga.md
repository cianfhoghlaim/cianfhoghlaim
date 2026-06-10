---
title: Doiciméadacht Forbróirí
shortTitle: D'fhorbróirí
description: Conas Documental a bhreisiú agus a mhionathrú
keywords: doiciméadacht, logánú, idirnáisiúnú, Sapper, Svelte, Gaois, Fiontar & Scoil na Gaeilge, DCU
resource: Documental
order: 3
public: true
---

Is feidhmchlár [Node.js](https://nodejs.org/) é Documental scríofa i Javascript. Is féidir leis rith ar fhreastalaí, ag soláthar inneachair go dinimiciúil, nó is féidir é a úsáid mar [ghineadóir suímh stataigh](https://www.staticgen.com/about). Mínítear é seo a thuilleadh sa chuid den suíomh a bhaineann le [himlonnú](/ga/software/documental/deployment). Stóráiltear inneachar suímh gréasáin ar dhiosca i bhformáid chomhad Markdown agus níl aon bhunachar sonraí ná aon saghas sonraíochta eile stóráilte. 

Oibríonn an bogearra ar gach córas oibriúcháin coitianta: an t-aon réamhriachtanas ná Node.js a shuiteáil ar do ríomhaire. Aimseoidh agus suiteálfaidh Node.js Package Manager (NPM) gach spleáchais eile as féin i rith na cumraíochta. Tógtar Documental trí úsáid a bhaint as [Svelte](https://svelte.dev/), creatlach comhpháirteanna cosúil le [React](https://reactjs.org/), agus [Sapper](https://sapper.svelte.dev/), creatlach feidhmchláir á chumhachtú ag Svelte. Féach an doiciméadacht le haghaidh na gcreatlach seo má bhíonn aon cheist agat ó thaobh an fheidhmchláir de, mar tá eolas den saghas sin lasmuigh de scóip an ailt seo. 

## Ag tosú

### Suiteáil agus cumraíocht

Déan an stór Documental a chlónáil ar do mheaisín: 

```cmd
git clone https://github.com/gaois/documental
```

Athraigh an chomhadlann go dtí do stór logánta agus déan spleáchais an tionscadail a shuiteáil: 

```cmd
npm install
```

### An feidhmchlár a thosú

Déan an t-ordú seo a leanas a rith chun Documental a thosú i mód forbróra: 

```cmd
npm run dev
```



Nuair a bhíonn an feidhmchlár á rith i mód forbróra, bíonn beo-athlódáil modúl ar fáil (i.e. déantar na hathruithe a dhéanann tú san eagarthóir a thaispeáint sa bhrabhsálaí láithreach bonn nuair a shábháiltear é), chomh maith le teachtaireachtaí mionsonraithe sa chonsól i dtaobh faisnéise agus earráidí. Sula ndéanann tú an feidhmchlár a imlonnú go timpeallacht freastalaí, beidh ort an feidhmchlár a thógáil sa mhód táirgeachta. Pléitear é seo sa chuid a bhaineann le [himlonnú](../deployment). 

## Struchtúr an tionscadail

Caithimis súil ar struchtúr an fhillteáin laistigh de do stór Documental. Sna fillteáin bharrleibhéil seo a leanas is dóichí a dhéanfaidh tú athruithe: 

- **`docs`**: Beidh an doiciméadacht Markdown a fhoilseofar ar do shuíomh gréasáin istigh anseo.
- **`messages`**: Na teaghráin aistrithe a thaispeánfar sa chomhéadan úsáideora (UI), tá siad istigh anseo. Féach [Logánú](#loganu) thíos. 
- **`src`**: Cód foinseach an fheidhmchláir, loighic ródaithe agus gnólachta san áireamh. 
- **`static`**: Comhaid statacha a sholáthróidh d'fheidhmchlár, ar nós íomhánna, deilbhíní suímh nó comhaid sheachtracha CSS. 

## Cur chuige comhpháirt-bhunaithe

Bíonn cur chuige comhpháirt-bhunaithe ag creatlacha nua-aimseartha Javascript agus iad ag tógáil feidhmchláir. Má tá taithí agat ar HTML a tháirgeadh le creatlacha ar thaobh an fhreastalaí in C#, PHP, etc. , b'fhéidir nach dtiocfaidh sé seo go réidh leat i dtosach.  Ó thaobh Documental de, comhaid shingile le hiarmhír is éard atá i gceist le comhpháirteanna. De ghnáth, cuirtear sa fillteán `src/node_modules/components` iad.* Déanann na comhaid chomhpháirte an mharcáil, an stíl, an stad agus an loighic le haghaidh cuid áirithe den fheidhmchlár a imchochlú. D'fhéadaidís comhpháirteanna eile a iompórtáil agus iad a úsáid laistigh dá marcáil. Mar shampla, déanann **Resource.svelte** mac-chomhpháirt darb ainm **Article.svelte** a iompórtáil  agus úsáideann sé an chlib chomhpháirte `<Article/>` laistigh dá marcáil. Cé go bhfuil cuma (X)HTML ar an gclib `<Article/>`, ní mar sin a léireofar sa bhrabhsálaí é. Is amhlaidh go dtiomsófar comhpháirt an ailt, mar aon lena mac-chomhpháirteanna go léir, go HTML caighdeánach bailí roimh sheoladh go dtí an cliant. Is éasca an cur chuige comhpháirt-bhunaithe a fhoghlaim nuair a chuireann tú tús le heagarthóireacht ar chomhaid .svelte. Tá tuilleadh eolais ar fáil sa doiciméadacht Sapper agus Svelte thuasluaite. 

\* Tabhair do d'aire gur comhpháirteanna chomh maith iad na comhaid .svelte san fhillteán `src/routes`, ach gur fusa féachaint orthu mar leathanaigh chomhfhreagracha gréasáin. 

## Coincheapa

Tá Documental bunaithe ar roinnt eochairchoincheapa:

1. **Logchaighdeáin**: Léiríonn sé seo sainroghanna logánaithe/idirnáisiúnaithe an úsáideora, mar shampla, Gaeilge nó Béarla.
2. **Catagóir Doiciméadachta**: Tá dhá chatagóir in Documental — sonraí oscailte agus bogearraí — is féidir tuilleadh a chur leis, áfach. 
3. **Acmhainní**: Is éard is acmhainní ann ná bailiúcháin scoite de dhoiciméad amháin, nó níos mó, a bhaineann le píosa bogearraí, le seirbhís nó le déantán sonraí. 
4. **Leaganacha acmhainne**: Is féidir leaganú a dhéanamh ar dhoiciméadacht le haghaidh acmhainní faoi leith. Is iondúil go ndéantar é seo trí thagairt a dhéanamh d'uimhir leagain na hacmhainne. 
5.**Doiciméid**: Leathanach singil doiciméadachta a bhaineann go sonrach le catagóir, logchaighdeán, acmhainn agus, más mian leat, leagan acmhainne.

Léirítear na coincheapa seo sna URLanna a úsáideann an suíomh gréasáin docs.gaois.ie: 

> `https://docs.gaois.ie/en/data/logainm/v0.9/licence`

- **`en`**: Is ionann an logchaighdeán agus Béarla. 
- **`data`**: Is ionann an chatagóir agus Sonraí Oscailte.
- **`logainm`**: Is ionann an fhoinse agus Logainm API.
- **`v0.9`**: Is ionann uimhir leagain na hacmhainne agus 0.9. 
- **`licence`**: Baineann an slug `licence` le hainm doiciméid shingil (i.e. comhad singil sa chomhadlann `docs`). 

Mar atá ráite thuas, ní dhéantar leaganú ar gach acmhainn: 

> `https://docs.gaois.ie/ga/software/geonames2sql`

- **`ga`**: Is ionann an logchaighdeán agus Gaeilge.
- **`software`**: Is ionann an chatagóir agus Bogearraí 
- **`geonames2sql`**: Is ionann an acmhainn agus GeoNames2Sql. 

Mura bhfuil ach aon doiciméad amháin a bhaineann leis an acmhainn, níl an slug doiciméid riachtanach, faoi mar atá sa sampla roimhe seo.  

Léirítear na coincheapa seo in ainmniú na gcomhad svelte sa chomhadlann `src/routes` chomh maith. Féach an doiciméadacht a bhaineann le Sapper chun faisnéis i dtaobh ródú a fháil.

```
- routes
  - [locale]
    - [category]
      - index
      - [version]
        - [slug]
      - [slug]
  - index
```

Ina theannta sin, mar a fheiceann tú sa doiciméadacht le haghaidh [eagarthóirí](/ga/software/documental/editors), bíonn na comhaid doiciméadachta Markdown bunaithe ar na coincheapa seo den chuid is mó. 

## Logánú

Déileálann Documental le logánú UI tríd an leabharlann [svelte-i18n](https://github.com/kaisermann/svelte-i18n). Úsáideann sé seo an [fhormáid teachtaireacht ICU](http://userguide.icu-project.org/formatparse/messages) chun na teaghráin atá sofheicthe ag an úsáideoir a aistriú. 

Stóráiltear na haistriúcháin ar chomhaid JSON san fhillteán barrleibhéil `messages`. Ainmnítear na comhaid seo san fhormáid `[locale].json`. De réir an réamhshocraithe, is mar seo a leanas a bhíonn struchtúr an fhillteáin `messages`: 

```
- messages
  - en.json
  - ga.json
```

Is féidir aistriúcháin a neadú sna comhaid JSON seo de réir aon struchtúir a mheasann tú a bheith oiriúnach, mar shampla: 

```json
{
  "navigation": {
    "api": "API",
    "changelog": "Changelog",
    "dataDictionary": "Data dictionary",
    "gettingStarted": "Getting started",
    "licence": "Licence",
    "openData": "Open Data",
    "software": "Software",
    "surnames": "Surnames Index"
  },
  ...
}
```

Níl aon srian leis an oiread neaduithe is féidir a dhéanamh ar oibiachtaí sa chomhad aistriúcháin.

Glaoimid ar theaghrán logánaithe sa UI ag úsáid poncnodaireacht ar nós `$_('navigation.openData')`, nuair a thugann `navigation.openData` `Open Data` do logchaighdeán Béarla nó `Open Data` do logchaighdeán Gaeilge, etc.

I gcomhair blocanna níos mó téacs, is féidir linn ábhar logánaithe a chur i gcomhaid Markdown ar leith, mar a dhéantar i gcás phríomhábhar doiciméadachta an tsuímh gréasáin a stóráiltear san fhillteán barrleibhéil `docs`. 

## Acmhainn nua a chur leis

Cé gur féidir le baill foirne eagarthóireachta [doiciméid a chruthú agus a chur in eagar](/ga/software/documental/editors) laistigh d'acmhainn ar leith, bíonn ionchur ón bhforbróir ag teastáil de ghnáth chun acmhainn nua a chur leis, nó chun athrú a dhéanamh ar léiriú na hacmhainne ar an nascleanúint nó ar an leathanach baile. Tugann na treoracha thíos cur síos ar conas é seo a bhaint amach. 

### An filltéan `docs` 

Bíonn fillteán comhfhreagrach laistigh den chomhadlann barrleibhéil `docs` ag teastáil ó gach acmhainn doiciméadachta. Dá mbeifeá ag cruthú acmhainn sonraí oscailte le haghaidh API nua, mar shampla, d'fhéadfá filltéan nua a chruthú ag `docs/data/mynewapi`. Dá mbeadh an API leaganaithe, d'fhéadfá fo-fhillteán sa bhreis a chur leis ag `docs/data/mynewapi/v1.0`. Féach an stór le haghaidh tuilleadh samplaí. Tabhair do d'aire gurbh féidir le heagarthóir inneachar an tasc seo a dhéanamh dá mbeadh tuiscint mhaith aige ar struchtúr na comhadlainne. 

### Nascleanúint

Tá an [chomhpháirt](#cur-chuige-comhphairt-bhunaithe) **Nascleanúint.svelte** lonnaithe in `src/node_modules/components`. Nuair a chuirtear an comhad seo in eagar bítear ábalta liosta na n-acmhainní a bhfuil fáil orthu ar an suíomh a leasú (le feiceáil ar thaobh chlé an scáileáin ar ghléasanna deisce).

Mar shampla, chun acmhainn nua bogearraí a chur leis, déanaimid an chuid chuí den chomhad **Navigation.svelte** a chur in eagar:

```svelte
<h2>{$_('navigation.software')}</h2>
<ul>
  <li>
    <NavigationResource category='software' resource='terminologue' heading='Terminologue' index='intro'/>
  </li>
  <li>
    <NavigationResource category='software' resource='geonames2sql' heading='GeoNames2Sql' singleton/>
  </li>
  ...
</ul>
```

Cuir mír liosta nua `<li>` leis agus mac-chomhpháirt `<NavigationResource/>`:

```svelte
<li>
  <NavigationResource
    category='software'
    resource='terminologue'
    heading='Terminologue'
    index='intro'/>
</li>
```

Glacann an chomhpháirt `<NavigationResource/>`le líon **airíonna**: 

| Airí | Cur síos |
| ---- | ---- |
| **category** | An chatagóir doiciméadachta `data` nó `software`. |
| **resource** | Slug na hacmhainne. Freagraíonn sé d'ainm an fhillteán acmhainne faoi `docs`. |
| **heading**  | Ceannteideal na hacmhainne. Má tá roinnt doiciméad ag an acmhainn, beidh sé seo le feiceáil os a gcionn sa nascleanúint. |
| **latestVersion** | Má tá an acmhainn leaganaithe, sainigh an uimhir leagain is déanaí anseo. |
| **index**    | Is éard atá san innéacs ná leathanach baile na hacmhainne. Pasáil an slug doiciméadachta don chéad doiciméad le bheith le feiceáil mar luach innéacs. Ní gá leis seo más acmhainn shingil atá ann. |
| **singleton** | Má tá sé seo sainithe, ciallaíonn sé nach bhfuil san acmhainn ach an t-aon doiciméad amháin agus nach gá duit airí `index` a shainiú. ||

Ná déan dearmad nach mbeidh doiciméid le feiceáil sa nascleanúint mura bhfuil ceannteideal YAML de `public: true` orthu.

### Leathanach Baile

Tá an rogha ann, más mian leat, blurba tuairisciúil faoin acmhainn a chur le leathanach baile an tsuímh gréasáin. Oscail an chomhpháirt **Home.svelte** in `src/node_modules/components`.

Cosúil leis an nascleanúint, is gá dúinn comhpháirt a léiríonn an acmhainn nua a chur leis. 

```svelte
<ul>
  <li>
    <HomeResource 
      href={`/${$locale}/software/terminologue/intro`}
      heading='Terminologue'
      blurb={$_('home.sections.terminologueBlurb')}/>
  </li>
  ...
</ul>
```

| Airí | Cur Síos |
| ---- | ---- |
| **href** | Cosán coibhneasta nó dearbh-URL na hacmhainne. |
| **heading** | Ceannteideal tuairisciúil. |
| **blurb** | Cur síos 1-2 abairt ar an acmhainn. |

Tabhair do d'aire go mb'fhéidir gur mhian leat [teaghráin logánaithe](#loganu) a phasáil le haghaidh cuid de na hairíonna. 

---
title: An cód foinseach a thuiscint
shortTitle: Cód foinseach
description: Turas treoraithe trí bhunchód Terminologue
keywords: téarmaíocht, taighde, bogearraí, foinse oscailte, javascript, Node JS, Fiontar & Scoil na Gaeilge, DCU
resource: Terminologue
github: https://github.com/gaois/terminologue
order: 3
public: true
---

Is éard atá sa doiciméad seo ná turas treoraithe trí bhunchód Terminologue. Tá sé i gceist aige cabhrú leat tuiscint a fháil ar an gcaoi a n-oibríonn Terminologue ar an taobh istigh le gur féidir leat fadhbanna a aithint, fabhtanna a réiteach agus tuilleadh forbartha a dhéanamh ar Terminologue.  

## A bhfuil laistigh de Terminologue

Mar is eol duit faoin am seo, is dócha, tá cúl Terminologue scríofa in [Node.js](https://nodejs.org/). Ciallaíonn sé seo gur JavaScript atá i gceist. Chomh maith le Node.js, baineann Terminologue úsáid as an gcreat [Express](https://expressjs.com/). Is creat beag é Express a chabhraíonn linn críochphointí (= URLs) a chumrú ar an bhfreastalaí agus a insíonn do Node.js na rudaí ba chóir dó a dhéanamh nuair a aimsíonn úsáideoir ceann de na críochphointí seo. Má tá cur amach agat ar Node.js agus ar Express, beidh sé seo an-sothuigthe. Mura bhfuil cur amach agat orthu ach má tá eolas agat ar theicneolaíochtaí eile forbartha gréasáin, ba chóir go mbeifeá in ann na prionsabail a bhaineann lena bhfuil i gceist sa doiciméad seo a leanúint.

Nuair a sheolann Terminologue leathanaigh ghréasáin chuig an gcliant, déanann sé formáidiú orthu ach úsáid a bhaint as inneall formáidithe ar a dtugtar [EJS](https://ejs.co/). Tá comhréir EJS cosúil le ASP agus le ASP.NET: cuirtear `<%` agus `%>` timpeall ar chód atá le rith ar an fhreastalaí, agus scríobhtar an chuid eile i ngnáth-HTML.  

Na codanna de Terminologue atá le rith sa bhrabhsálaí, tá siad scríofa in HTML, in JavaScript agus in CSS atá “beagnach glan”. Is éard atá i gceist le “beagnach glan” ná nach n-úsáidimid creat “uilechuimsitheach” ar bith agus nach n-úsáidimid aon rud óna dteastódh iarphróiseáil nó tiomsú sula gcuirtear ar fáil don chliant é. Úsáidimid scripteanna agus stílbhileoga ar a dtugtar [Screenful](https://github.com/michmech/screenful), áfach, agus cuireann siad seo go leor den fheidhmiúlacht ar fáil sa chliant. Is feidhmchláir aon leathanaigh iad an chuid is mó de na leathanaigh ghréasáin a fheiceann an t-úsáideoir in Terminologue. Cuirtear an leathanach gréasáin ar fáil don bhrabhsálaí agus de réir mar a idirghníomhaíonn an t-úsáideoir le giuirléidí éagsúla ar an scáileán, seolann Screenful iarratais AJAX chuig an bhfreastalaí agus faigheann sé freagairtí uaidh. I bhformáid JSON atá na sonraí ar fad a shreabhann idir an cliant agus an freastalaí.

Is i bhformáid JSON a stóráiltear sonraí go hinmheánach i mbunachair sonraí ar an bhfreastalaí. Maidir le stóras cúil, úsáideann Terminologue [SQLite](https://www.sqlite.org/index.html), inneall bunachair sonraí comhadbhunaithe. Is ionann gach bunachar sonraí in Terminologue agus comhad sa chóras comhad a bhíonn á oscailt agus á dhúnadh ag SQLite de réir mar is gá.

## `terminologue.js`

Is féidir cúl Terminologue a thosú (i measc bealaí eile) ach `node terminologue.js` a rith ón teirminéal nó ón leid ordaithe. Léirmhíníonn agus ritheann Node.js inneachar an chomhaid JavaScript seo. Insíonn an comhad do Node.js cúpla rud a dhéanamh:

1. Cruthaíonn sé *oibiacht feidhmchláir Express* ar a dtugtar `app`.

2. Úsáideann sé modhanna ar nós `app.post()` agus `app.get()` chun chur láimhseálaithe a chruthú le haghaidh na gcríochphointí (= URLs) éagsúla a d’fhéadfadh an t-úsáideoir a iarraidh ón fhreastalaí. Feidhm bheag JavaScript é gach láimhseálaí agus ritheann Node.js é nuair a bhaineann iarratas HTTP an freastalaí amach. De ghnáth, próiseálann láimhseálaí na sonraí a tháinig leis an iarratas agus seolann sé rud éigin ar ais, mar shampla leathanach gréasáin nó oibiacht JSON.

3. Ag deireadh an chomhaid mar sin, glaonn sé `app.listen()`. Insíonn sé seo do Node.js éisteacht le haghaidh iarratais HTTP a thagann isteach. Ón bpointe seo, ritheann Node.js láimhseálaí éigin gach uair a fhaigheann an freastalaí iarratas HTTP a mheaitseálann ceann de na críochphointí a cruthaíodh i gcéim 2 thuas. Leanann Node.js air ag éisteacht leis agus ag rith láimhseálaithe go gcríochnófar an feidhmchlár.

Ar ndóigh, bíonn gach láimhseálaí difriúil, ach déanann siad rudaí cosúil leis na nithe seo a leanas de ghnáth:

- Sonraí a léamh ón iarratas HTTP ach airíonna na hoibiachta `req` a scrúdú.

- Nasc le cnuasach téarmaíochta (is ionann cnuasach téarmaíochta in Terminologue agus bunachar sonraí SQLite) a oscailt ach `ops.getDB()` a ghlaoch.

- Fáil amach an bhfuil an cliant logáilte isteach agus an bhfuil rochtain aige/aici ar an gcnuasach téarmaíochta nó nach bhfuil, ach `ops.verifyLoginAndTermbaseAccess()`, nó rud éigin cosúil leis sin, a ghlaoch.

- Roinnt sonraí a léamh nó a scríobh ó/i gcnuasach téarmaíochta (= bunachar sonraí SQLite) ach modhanna amhail `ops.entryRead()`, `ops.entrySave()` agus go leor modhanna eile a ghlaoch.

- An nasc le bunachar sonraí SQLite a dhúnadh ach `db.close()` a ghlaoch.

- Freagairt a sheoladh chuig an gcliant, mar oibiacht JSON (ach `res.json()` a ghlaoch) nó mar leathanach HTML. Má tá leathanach HTML á sheoladh ón an láimhseálaí, glaonn sé `res.render()`. Tugann sé seo smacht d’inneall formáidithe EJS a bheireann ar cheann de na teimpléid HTML sa chomhadlann `views` (bíonn an iarmhír `.ejs` leis na comhaid), a ritheann aon chód taoibh freastalaí sa teimpléad (= aon rud idir `<%` agus `%>`) agus a sheolann na torthaí chuig an gcliant.

## `ops.js`

Glaonn an chuid is mó de láimhseálaithe in `terminologue.js` ar fheidhmeanna ón oibiacht `ops`, atá sa chomhad `ops.js`. Sa chomhad seo, gheobhaidh tú an chuid is mó den chód íseal-leibhéil a dhéanann ionramháil ar rónna agus ar cholúin sna bunachair sonraí. Dá mbeadh freastalaí bunachar sonraí ar leith á úsáid againn seachas SQLite, gheofaí an chuid is mó den chód seo i ngnásanna stóráilte. Tá SQLite á úsáid againn, áfach, agus ní ann do ghnásanna stóráilte in SQLite, mar sin tá `ops.js` againn dá bharr.

Cuireann an comhad `ops.js` líon mór feidhmeanna ar fáil. Bíonn beagnach gach feidhm *aisioncronach*, is é sin le rá, ní chuireann siad aon luach ar ais. Ina áit sin, tógann siad *feidhm aisghlaoite* mar cheann dá n-argóintí agus, nuair a chuireann siad a gcuid oibre i gcrích, ritheann siad an t-aisghlao chun smacht a thabhairt ar ais don láimhseálaí HTTP in `terminologue.js`. Gnáthnós é in Node.js, aisghlaonna a chur thart seachas luachanna a aisfhilleadh.

Nuair a léann feidhm rud éigin ó bhunachar sonraí SQLite nó nuair a scríobhann sé rud éigin isteach ann, tá oibiacht darb ainm `db` ann a sheasann don bhunachar sonraí. Tháinig an oibiacht seo mar argóint ón láimhseálaí éigin in `terminologue.js`. Cuireann an oibiacht seo modhanna ar fáil, leithéidí `db.run()` agus `db.get()`, a thógann ráitis SQL agus a ritheann ar an mbunachar sonraí iad. Bíonn na modhanna seo aisioncronach freisin agus faigheann muid aisghlaonna astu. Mar sin, feicfidh tú go bhfuil an cód breac le cásanna ina bhfuil aisghlaoch leabaithe taobh istigh d'aisghlaoch atá leabaithe taobh istigh d'aisghlaoch eile, agus mar sin de. Is mar seo a dhéantar rudaí in Node.js.

Leis seo, tá deireadh na treorach buailte linn a bhaineann leis an gcód taoibh freastalaí de Terminologue. Táimid chun súil a chaitheamh ar an gcód taoibh cliaint anois.  

## Screenful

Na leathanaigh HTML ar fad a chuirtear ar fáil don chliant, tá siad le fáil sa chomhadlann `website/views`. Nuair a bhaineann an leathanach gréasáin ríomhaire an chliaint amach agus nuair a lódáiltear ar bhrabhsálaí gréasáin an chliaint é, dáilimid an chuid is mó den fheidhmiúlacht ar an leabharlann [Screenful](https://github.com/michmech/screenful).  

Cuireann Screenful roinnt **cineálacha leathanaigh** ar fáil dúinn a mbainimid úsáid astu in Terminologue. Mar shampla:

- Is feidhmchlár aon leathanaigh é an cineál leathanaigh `Screenful.Login` a dhéanann bainistiú ar an bpróiseas logáil isteach.  

- Is feidhmchlár aon leathanaigh é an cineál leathanaigh `Screenful.Make` agus is féidir le húsáideoir idirghníomhú leis chun bunachar sonraí nua a chruthú. Úsáidimid in Terminologue é chun bainistíocht a dhéanamh ar an bpróiseas a bhaineann le cnuasach nua téarmaíochta a chruthú.  

- Is feidhmchlár aon leathanaigh é an cineál leathanaigh `Screenful.Navigator` ina bhfuil liosta iontrálacha ar thaobh na láimhe clé agus spás ar thaobh na láimhe deise le haghaidh féachaint agus eagarthóireacht a dhéanamh ar iontráil. Úsáideann Terminologue an cineál leathanaigh seo mar phríomhscáileán eagarthóireachta an chnuasaigh téarmaíochta (is é seo an scáileán a gcaitheann téarmeolaithe formhór a gcuid ama ag féachaint air).

- Is feidhmchlár aon leathanaigh é an cineál leathanaigh `Screenful.Editor` ina bhfuil tú in ann eagarthóireacht a dhéanamh ar iontráil ar leith. Tá cnaipí ann le haghaidh iontráil a oscailt, a dhúnadh, a scriosadh agus mar sin de. Úsáidimid ar thaobh na láimhe deise de scáileán eagarthóireachta an bhunachair sonraí é (tá sé leabaithe mar IFRAME ann), chomh maith le cúpla áit eile in Terminologue.

Fógraítear ar gach leathanach gréasáin de chuid Terminologue an cineál leathanaigh atá ann ach na comhaid ábhartha JavaScript agus CSS a iniamh. Mar shampla, fógraítear ar leathanach logáil isteach Terminologue (`website/views/sitewide/login.ejs`) gur leathanach den chineál `Screenful.Login` é mar seo a leanas:

```html
<script type="text/javascript" src="../libs/screenful/screenful-login.js"></script>
<link type="text/css" rel="stylesheet" href="../libs/screenful/screenful-login.css" />
```

Cuireann sé na paraiméadair bhreise seo ar fáil ansin a insíonn do Screenful (i) an URL ar cheart dó an t-iarratas logáil isteach a sheoladh chuige, agus (ii) an áit ar cheart dó an t-úsáideoir a atreorú má éiríonn leis an logáil isteach:

```html
<script type="text/javascript">
  Screenful.Login.loginUrl="../login.json";
  Screenful.Login.redirectUrl="<%=redirectUrl%>";
</script>
```

An t-iarratas AJAX a sheolann Screenful ón gcliant chuig ár bhfreastalaí, agus an freagairt a sheolann ár bhfreastalaí ar ais chuig an gcliant, déantar doiciméadú orthu seo in Screenful. Mar shampla, seolann an cliant iarratas mar seo a leanas chuig `Screenful.Login.loginUrl` agus insíonn sé seo dúinn go dteastaíonn ón úsáideoir `someone@example.com` logáil isteach:

```json
{
  "email": "someone@example.com",
  "password": "Hzwe86R!"
}
```

D’fhéadfadh ár bhfreastalaí freagairt mar seo a thabhairt, a thabharfaidh leid do Screenful an t-úsáideoir a atreorú `Screenful.Login.redirectUrl`.

```json
{
  "success": true
}
```

Nó d’fhéadfadh ár bhfreastalaí freagairt mar seo a thabhairt, a thabharfaidh leid do Screenful a chur in iúl don úsáideoir nár éirigh leis an logáil isteach agus deis a thabhairt dó/di iarracht eile a dhéanamh:

```json
{
  "success": false
}
```

Is mar seo a oibríonn Screenful agus is mar seo a mbainimid úsáid as gach áit in Terminologue, fiú ar chineálacha leathanaigh atá an-chasta, cosúil le scáileán eagarthóireachta an bhunachair sonraí. Fógraímid i gcónaí go mbaineann leathanach gréasáin ar leith le cineál áirithe leathanaigh de chuid Screenful agus cinntímid ansin go bhfuil na críochphointí againn do na ceangail éagsúla taoibh freastalaí a theastaíonn ón gcineál leathanaigh sin.

Aimsítear cóip Terminologue de Screenful in `website/libs/screenful`. Níor cheart duit athruithe a dhéanamh ar aon rud sa chomhadlann sin. Má theastaíonn uait athruithe a dhéanamh ar Screenful, moltar duit athrú a mholadh chuig [stórlann](https://github.com/michmech/screenful) Screenful ina áit sin.

## Eagarthóireacht a dhéanamh ar na hiontrálacha: `fy.js`

Tá an cód a dhéanann eagarthóireacht ar iontráil téarmeolaíochta ar leith ar cheann de na smutáin is casta a bhaineann le cód taoibh freastalaí JavaScript in Terminologue. Léirítear aschur an chóid ar an bpríomhscáileán eagarthóireachta, tar éis don úsáideoir cliceáil ar an gcnaipe 'Eagarthóireacht', mar fhoirm chasta HTML ina bhfuil cluaisíní ag an mbarr (DOM, TRM srl.).

Aimsítear an comhad JavaScript seo sa chomhad `website/libs/fy/fy.js` agus déantar formáidiú ar an HTML a aschuireann sé de réir stílbhileoige sa chomhad `website/libs/fy/fy.css`. Baineann dhá phríomhaidhm leis:

- `Fy.render()` a thógann iontráil téarmeolaíochta in JSON (a fuarthas ó bhunachar téarmaíochta ar an bhfreastalaí) agus léiríonn sé ar an scáileán i bhfoirm HTML í. Is féidir leis an úsáideoir idirghníomhú léi ansin. Is ionann beagnach gach cuid den HTML a fheiceann tú ar thaobh na láimhe deise den scáileán eagarthóireachta agus aschur na feidhme seo.  

- `Fy.harvest()` a thógann staid reatha na foirme HTML agus “bailíonn” sé mar oibiacht JSON í atá réidh le sábháil i gcnuasach téarmaíochta ar an bhfreastalaí.

Glaonn Screenful (is é an cineál leathanaigh `Screenful.Editor` a dhéanann é seo) na feidhmeanna `Fy.render()` agus `Fy.harvest()` nuair a léiríonn an t-úsáideoir (ach cnaipe a chliceáil, mar shampla) go dteastaíonn uaidh/uaithi iontráil a oscailt, iontráil a shábháil agus mar sin de.

## Clómhaisiú a dhéanamh ar na hiontrálacha

Gné chasta eile a bhaineann le cód JavaScript ná an cód a dhéanann formáidiú nó clómhaisiú ar na hiontrálacha téarmeolaíochta. Tá trí áit ann ina ndéantar é seo:  

- Ar thaobh na láimhe clé den scáileán eagarthóireachta san áit a liostaítear na hiontrálacha. Déantar clómhaisiú ar gach iontráil anseo i bhfoirm "ghiorraithe".

- Ar thaobh na láimhe deise den scáileán eagarthóireachta san áit a ndéantar clómhaisiú ar iontráil ar leith i bhfoirm "iomlán". Cliceálann an t-úsáideoir ar an gcnaipe 'Eagarthóireacht' chun athrú idir féachaint ar an iontráil (faoi chlómhaisiú) agus eagarthóireacht a dhéanamh uirthi (le `fy.js`).

- I gcomhéadan poiblí an chnuasaigh téarmaíochta (má tá an bunachar téarmaíochta le feiceáil go poiblí), áit a léirítear na hiontrálacha ina bhfoirm "iomlán". Bíonn roinnt difríochtaí beaga ann, áfach, idir é seo agus an chaoi a léirítear sa chomhéadan eagarthóireachta iad.  

Tá an cód seo le fáil sa chomhadlann `website/widgets`:

- Úsáidtear `pretty-small.js` agus `pretty-small.css` le clómhaisiú a dhéanamh ar liosta na n-iontrálacha ar thaobh na láimhe clé den scáileán eagarthóireachta.

- Úsáidtear `pretty-large.js` agus `pretty-large.css` le clómhaisiú a dhéanamh ar thaobh na láimhe deise den scáileán eagarthóireachta.

- Úsáidtear `pretty-public.js` agus `pretty-public.css` le clómhaisiú a dhéanamh i gcomhéadan poiblí an chnuasaigh téarmaíochta.

I gach ceann de na comhaid JavaScript seo, tá feidhm ann ar a dtugtar `entry()` a thógann iontráil téarmeolaíochta in JSON (a fuarthas ó bhunachar sonraí ar an bhfreastalaí) agus a aschuireann HTML. In `pretty-small.js` agus `pretty-large.js`, ritheann Screenful an fheidhm `entry()` sa chliant nuair a chaithfidh sé iontráil a léiriú ar an scáileán. In `pretty-public.js`, ritheann Node.js an fheidhm `entry()` ar an bhfreastalaí agus seolann sé an t-aschur chuig ár gcliant mar chuid de leathanach HTML.

## Conclúid

Is dócha gur leor sin ag an bpointe seo. Tá súil againn gur tugadh achoimre duit sa doiciméad seo ar (i) chód taoibh freastalaí Terminologue, agus ar (ii) chuid de na codanna níos casta de chód taoibh cliaint Terminologue.

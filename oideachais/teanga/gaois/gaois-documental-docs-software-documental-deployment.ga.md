---
title: Imlonnú
description: Ag imlonnú Documental i dtimpeallacht freastalaí
keywords: doiciméadacht, logánú, idirnáisiúnú, Sapper, Svelte, Gaois, Fiontar & Scoil na Gaeilge, DCU
resource: Documental
order: 4
public: true
---

Is féidir Documental a imlonnú (i) mar fheidhmchlár Node.js, nó (ii) mar shuíomh statach.

## Imlonnú mar fheidhmchlár Node.js

### Cruthaigh tiomsú táirgeachta

An chéad chéim is ea tiomsú táirgeachta de d'fheidhmchlár a chruthú. Rith an t-ordú seo a leanas. Má tá tú ag rith an fheidhmchláir i mód forbartha faoi láthair beidh ort é a stopadh (`Ctrl`/`Cmd` + `C`) sula leanfaidh tú an chéim seo. 

```cmd
npm run build
```

Táirgeann sé seo leagan optamaithe de d'fheidhmchlár atá réidh d'imlonnú táirgeachta. Aschuirtear cód an fheidhmchláir go dtí an chomhadlann `__sapper__/build`. Rith `node __sapper__/build` ó fhréamh an tionscadail chun an tiomsú táirgeachta a thástáil ar do mheaisín.

### Imlonnú chuig freastalaí

Ansin, beidh ort an feidhmchlár a chur ar fhreastalaí, le FTP, RDP, uath-script nó pé modh is fearr leat.

Ní foláir na comhadlanna seo a leanas a imlonnú chuig fréamh an tsuímh gréasáin ar thimpeallacht do fhreastalaí:

```
- __sapper__/build
- docs
- node_modules
- static
```

Chruthaíomar an fillteán aschuir tiomsaithe sa chéim roimhe seo. Istigh sa chomhadlann `docs` a fhaightear do chuid comhad doiciméadachta Markdown. Is ionann an fillteán `node_modules`agus fréamh do thionscadail, NÍ an fillteán ag `src/node_modules`. Sa chomhadlann `static` a fhaightear do chuid sócmhainní statacha. 

Maidir le himlonnuithe ina dhiaidh sin:

- Más í an doiciméadacht amháin a uasghrádaíodh (i.e. níor athraíodh aon chód feidhmchláir), ní gá ach an fillteán `docs` a úsáid
- Má shuiteálann tú nó má uasghrádaíonn tú aon mhodúil Node.js, beidh ort an chomhadlann `node_modules` a imlonnú an athuair.
- A bhuí le do chóras inmheánach leaganaithe docht Sapper, is sábháilte aon úsáid ina dhiaidh sin a chumasc leis an bhfillteán `__sapper__/build` seachas an fillteán a fhorscríobh. Tá de bhua aige seo freisin nach gcuireann sé isteach orthu siúd atá ceangailte leis an suíomh faoi láthair. 

### Á imlonnú in ISS le iisnode

I dtimpeallachtaí Windows Server is féidir freastal a dhéanamh ar fheidhmchláir Node.js trí leas a bhaint as IIS mar sheachfhreastalaí aisiompaithe. 
[Iisnode](https://github.com/Azure/iisnode) a éascaíonn é seo, agus ní mór duit é seo a shuiteáil ar dtús. Caithfear cúpla céim bhreise a leanúint sa chás seo:

1. Cruthaigh comhad nua i gcomhadlann fhréamh an tsuímh gréasáin darb ainm **app.js**. Ní bheidh ach líne amháin sa chomhad seo a ghlaofaidh cód Documental ar thaobh an fhreastalaí:

  ```js
  require('./__sapper__/build/index.js');
  ```

2. Cruthaigh comhad **Web.config** nua i gcomhadlann fhréamh an tsuímh. Istigh i stór Documental tá comhad Web.config samplach le hanótaí. Is iad seo a leanas na rannáin is tábhachtaí den chomhad config:

  ```xml
  <configuration>
    <system.webServer>
      <handlers>
        <add name="iisnode" path="app.js" verb="*" modules="iisnode" />
      </handlers>
      <rewrite>
        <rules>
          <rule name="App">
            <match url="/*" />
            <action type="Rewrite" url="app.js" />
          </rule>
        </rules>
      </rewrite>
    </system.webServer>
  </configuration>
  ```

  Tá na feidhmeanna seo ag na rannáin thuas: (i) lódálann siad an láimhsealaí iisnode agus (ii) atreoraíonn siad gach iarratas go dtí an comhad app.js nuair a n-aistrítear iad go dtí cód feidhmchláir Documental. 



## Imlonnú trí ghiniúint suímh stataigh

Is éard is suíomh statach ann ná bailiúchán de chomhaid réamhghinte HTML, JavaScript agus CSS, murab ionann agus suíomh freastalaí-ghinte ar féidir leis an bhfeidhmchlár an t-ábhar a léiriú agus a sheirbheáil ar eiteog ar an úsáideoir 

Rith an t-ordú seo a leanas chun suíomh statach a aschur ó Documental:

```cmd
npm run export
```
Aschuirfear na comhaid statacha go dtí an chomhadlann `__sapper__/export`. Déanfaidh aon ordú aschurtha dá éis sin forscríobh ar inneachar na comhadlainne go huathoibríoch. 

Rith `npx serve __sapper__/export` chun do shuíomh statach a thástáil.

Nuair atá tú réidh, imlonnaigh inneachar chomhadlann `__sapper__/export` go dtí fréamh an tsuímh i dtimpeallacht do fhreastalaí.

Féach na doiciméid [Sapper](https://sapper.svelte.dev/) i gcomhair tuilleadh eolais. 

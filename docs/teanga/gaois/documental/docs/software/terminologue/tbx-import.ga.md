---
title: Iompórtáil as TBX
shortTitle: Iompórtáil TBX
description: Conas cnuasach téarmaíochta a iompórtáil as TBX go Terminologue
keywords: téarmaíocht, taighde, bogearraí, foinse oscailte, javascript, Node JS, Fiontar & Scoil na Gaeilge, DCU
resource: Terminologue
github: https://github.com/gaois/terminologue
order: 6
public: true
---

Formáid caighdeánach é TBX (Termbase Exchange) atá aitheanta go forleathan i dtionscal na téarmeolaíochta chun sonraí téarmaíochta a mhalartú idir bogearraí. Is iomaí bogearra atá ábalta sonraí a easpórtáil agus a iompórtáil ó/go dtí an fhormáid seo, agus tá Terminologue ina measc. Déanfaidh muid cur síos sa doiciméad seo ar an dóigh ar féidir sonraí a iompórtáil as TBX go Terminologue.

## Iompórtáil as líne

Chun sonraí a iompórtáil as comhad TBX go cnuasach de chuid Terminologue, caithfidh tú an cnuasach a íoslódáil (ón scáileán *Cumrú*) agus ansin script a rith chun an iompórtáil a dhéanamh. Nuair a bheidh sé sin críochnaithe, beidh ort an cnuasach a uaslódáil ar ais chuig Terminologue.

Tá an script le fáil sa stórlann faoi `exportimport/tbx-import.js`. Sa teirminéal (má tá tú ar GNU/Linux) nó sa leid ordaithe (má tá tú ar Microsoft Windows), téigh chuig an bhfochomhadlann `exportimport` agus ansin rith `node tbx-import.js`.

Roimhe sin, áfach, caithfidh tú an script a chumrú. Oscail an script in eagarthóir téacs agus athraigh na hathróga ag tús an chomhaid de réir mar is cuí:

```javascript
const TBXFILE="/mytermbase.tbx";
const SQLITEFILE="../data/termbases/mytermbase.sqlite";
const LIMIT=10000;
```

- `TBXFILE` is ea ainm (agus conair) den chomhad TBX.
- `SQLITEFILE` is ea an chonair chuig do chóip logánta den chnuasach a d'íoslódáil tú ón scáileán *Cumrú*.
- `LIMIT` is ea uasteorainn ar líon na n-iontrálacha a iompórtálfar.

Má tá aon iontrálacha sa chnuasach cheana, cuirfear na hiontrálacha nua leo, mar iontrálacha nua. Is é sin le rá, ní dhéanann an script iarracht a aithint a bhfuil na hiontrálacha ann cheana.

Mar chuid den phróiseas iompórtála, cruthófar meiteashonraí (lipéid réimsí, lipéid ghramadaí agus eile) sa chunasach de réir mar is gá. Má tá meiteashonraí sa chnuasach cheana, déanann an script iarracht iad a athúsáid (is é sin le rá, gan meiteashonraí nua a chruthú) más féidir.

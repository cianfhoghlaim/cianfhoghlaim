---
title: Easpórtáil go téacs tábmharcáilte
shortTitle: Easpórtáil TXT
description: Conas cnuasach téarmaíochta a easpórtáil as Terminologue go téacs lom tábmharcáilte
keywords: téarmaíocht, taighde, bogearraí, foinse oscailte, javascript, Node JS, Fiontar & Scoil na Gaeilge, DCU
resource: Terminologue
github: https://github.com/gaois/terminologue
order: 7
public: true
---

Tá bealach le fáil in Terminologue chun cnuasach téarmaíochta (nó cuid de) a easpórtáil go téacs tábmharcáilte ina bhfuil gach iontráil ar aon líne amháin. Is féidir téacs san fhormáid seo a iompórtáil go bogearra scarbhileoige agus scarbhileog a dhéanamh as.

## Easpórtáil ar líne

Tá áis ar fáil in Terminologue, sa chomhéadan eagarthóireachta, chun cnuasach nó cuid de chnuasach a easpórtáil go téacs tábmharcáilte:

- Ar scáileán eagarthóireachta an chnuasaigh, sa liosta iontrálacha ar chlé, tá cnaipe *TXT* ag bun an liosta chun gach iontráil ar an liosta sin a íoslódáil i bhformáid téacs tábmharcáilte. Is féidir leat liosta na n-iontrálacha a shaincheapadh le cuardach ar bith, agus an fothacar sin den chnuasach a íoslódáil ansin. Má tá liosta torthaí níos faide ná leathanach amháin, is é *inneachar an leathanaigh reatha* a íoslódálfar tar éis duit cliceáil ar an chnaipe.

## Easpórtáil as líne

Más fearr leat, is féidir leat cnuasach a íoslódáil go dtí do ríomhaire (ón scáileán *Cumrú*) agus ansin é a easpórtáil go téacs tábmharcáilte le script. Tá an script le fáil sa stórlann faoi `exportimport/txt-export.js`. Sa teirminéal (má tá tú ar GNU/Linux) nó sa leid ordaithe (má tá tú ar Microsoft Windows), téigh chuig an bhfochomhadlann `exportimport` agus ansin rith `node txt-export.js`.

Roimhe sin, áfach, caithfidh tú an script a chumrú. Oscail an script in eagarthóir téacs agus athraigh na hathróga ag tús an chomhaid de réir mar is cuí:

```javascript
const SQLITEFILE="../data/termbases/mytermbase.sqlite";
const TXXFILE="mytermbase.tbx";
const LIMIT=10000;
```

- `SQLITEFILE` is ea an chonair chuig do chóip logánta den chnuasach a d'íoslódáil tú ón scáileán *Cumrú*.
- `TXXFILE` is ea ainm (agus conair) den chomhad téacs a chruthófar.
- `LIMIT` is ea uasteorainn ar líon na n-iontrálacha a easpórtálfar.

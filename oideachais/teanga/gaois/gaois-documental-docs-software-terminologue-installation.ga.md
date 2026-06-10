---
title: Suiteán áitiúil a chumrú
shortTitle: Suiteáil
description: Terminologue a shuiteáil agus a úsáid
keywords: téarmaíocht, taighde, bogearraí, foinse oscailte, javascript, Node JS, Fiontar & Scoil na Gaeilge, DCU
resource: Terminologue
github: https://github.com/gaois/terminologue
order: 2
toc: false
public: true
---

Mínítear sa doiciméad seo **(i)** na rudaí a chaithfidh tú a dhéanamh chun tús a chur le suiteán áitiúil de Terminologue ar do ríomhaire féin le haghaidh forbairt nó tástáil, agus **(ii)** tugann sé tuilleadh ábhair léitheoireachta duit má theastaíonn uait an chaoi a n-oibríonn Terminologue go hinmheánach, agus/nó an chaoi a gcumraítear ar fhreastalaí táirgthe é, a thuiscint.  

## Cúpla rud a chaithfidh tú a thuiscint ar dtús

Bogearra gréasánbhunaithe é Terminologue. Ciallaíonn sé seo go ritheann Terminologue ar fhreastalaí agus úsáideann daoine brabhsálaithe gréasáin chun rochtain a fháil air tríd an idirlíon, cosúil le suíomh gréasáin ar bith eile. Sa doiciméad seo, mínítear an chaoi le Terminologue a chumrú ar do ríomhaire féin, agus do ríomhaire á úsáid agat amhail is gur freastalaí é, le haghaidh forbairt agus tástáil.

Tá cúl Terminologue (= na píosaí a ritheann ar an bhfreastalaí) scríofa in [Node.js](https://nodejs.org/). Ciallaíonn sé seo gur in JavaScript atá an cód foinseach agus go ritheann sé ar bheagnach gach córas oibriúcháin, lena n-áirítear GNU/Linux agus Microsoft Windows. An t-aon réamhriachtanas a bhaineann leis seo ná Node.js a shuiteáil ar do ríomhaire. Gach réamhriachtanas agus gach spleáchas eile, aimseoidh agus suiteálfaidh Node Package Manager go huathoibríoch iad.

Maidir le sonraí a stóráil ar an bhfreastalaí, lena n-áirítear gach cnuasach téarmaíochta, sonraí na n-úsáideoirí agus mar sin de, úsáideann Terminologue [SQLite](https://www.sqlite.org/). Bainistíonn Node Package Manager an spleáchas seo chomh maith. Bogearra comhadbhunaithe é SQLite (= is ionann gach bunachar sonraí agus comhad éigin ar do ríomhaire). Ciallaíonn sé seo nach gcaithfidh tú inneall bunachar sonraí ar bith a shuiteáil ar do ríomhaire.  

## Na céimeanna

1. Suiteáil [Node.js](https://nodejs.org/) ar do ríomhaire.

2. Íoslódáil gach rud ón stór agus cuir i gcomhadlann ar do ríomhaire iad. Tabharfaidh tú faoi deara go bhfaightear na rudaí a d’íoslódáil tú i bhfochomhadlanna éagsúla, agus is iad `data` (an áit a gcoinníonn Terminologue a bhunachair sonraí) agus `website` (an áit a bhfuil suíomh gréasáin Terminologue) na fochomhadlanna is tábhachtaí.

3. Sa teirminéal (má tá tú ar GNU/Linux) nó sa leid ordaithe (má tá tú ar Microsoft Windows), téigh chuig an bhfochomhadlann `website` agus rith  `npm install`. Lainseálfaidh sé seo Node Package Manager (NPM) a íoslódálfaidh agus a shuiteálfaidh (sa chomhadlann `website/node_modules`) gach spleáchas a theastaíonn ó Terminologue. D’fhéadfadh sé seo cúpla nóiméad a ghlacadh.

4. San fhochomhadlann `data`, athainmnigh an comhad `siteconfig.template.json` agus tabhair `siteconfig.json` air.

5. San fhochomhadlann `data`, athainmnigh an comhad `terminologue.template.sqlite` agus tabhair `terminologue.sqlite` air.  

6. San fhochomhadlann `website`, rith `node init.js`. Is script í seo a chruthóidh cuntas duit i do shuiteán áitiúil de Terminologue. Tabharfaidh an script ainm úsáideora agus pasfhocal duit. Cuimhnigh ar an eolas seo nó scríobh síos é.

7. San fhochomhadlann `website`, rith `node terminologue.js`. Cuirfidh sé seo tús le cúl Terminologue mar fhreastalaí ar do ríomhaire. *Tabhair faoi deara: Ritheann Terminologue ar phort 80, mar réamhshocrú. Tá sé seo dainséarach dar le cineálacha áirithe de GNU/Linux, agus ní cheadóidh siad é, mura ritheann tú Terminologue le pribhléidí ardaithe. Chun Terminologue a rith le pribhléidí ardaithe, rith mar `sudo node terminologue.js` é.*

8. Oscail do bhrabhsálaí gréasáin agus téigh chuig `http://localhost/`. Ba chóir go bhfeicfeá leathanach baile Terminologue anois agus ba chóir go mbeifeá in ann logáil isteach ach an t—ainm úsáideora agus an pasfhocal a tugadh duit i gcéim 6 a úsáid.

Comhghairdeas, tá suiteán áitiúil de Terminologue ag rith ar do ríomhaire anois. Chun deireadh a chur léi am ar bith, brúigh `Ctrl + C` sa teirminéal nó sa leid ordaithe.

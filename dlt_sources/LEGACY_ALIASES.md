# LEGACY_ALIASES — dlt/

Per the
[`2026-07-17-pipeline-directory-consolidation-v1`](../../changes/2026-07-17-pipeline-directory-consolidation-v1/proposal.md)
openspec change. **All old paths remain importable via deprecation
shims for at least one release cycle.**

## European nations — ISO 3-letter → full snake_case

| Old | New |
|:--|:--|
| `dlt/european_nations/{alb,aut,bel,bgr,bih,che,cyp,cze,deu,dnk,esp,est,fin,fra,geo,grc,hrv,hun,isl,ita,lie,ltu,lux,lva,mda,mkd,mlt,mne,nld,nor,pol,prt,rou,srb,svk,svn,swe,tur,ukr,xkx}/` | `dlt/european_nations/{albania,austria,belgium,bulgaria,bosnia_and_herzegovina,switzerland,cyprus,czechia,germany,denmark,spain,estonia,finland,france,georgia,greece,croatia,hungary,iceland,italy,liechtenstein,lithuania,luxembourg,latvia,moldova,north_macedonia,malta,montenegro,netherlands,norway,poland,portugal,romania,serbia,slovakia,slovenia,sweden,turkey,ukraine,kosovo}/` |

## Commonwealth — ISO 3-letter → full snake_case

| Old | New |
|:--|:--|
| `dlt/commonwealth/{aus,can,ind,nga,nzl,zaf}/` | `dlt/commonwealth/{australia,canada,india,nigeria,new_zealand,south_africa}/` |

## Canada — provinces

| Old | New |
|:--|:--|
| `dlt/commonwealth/can/{ab,bc,mb,nb,nl,ns,nt,nu,on,pe,qc,sk,yt}/` | `dlt/commonwealth/canada/provinces/{alberta,british_columbia,manitoba,new_brunswick,newfoundland_and_labrador,nova_scotia,northwest_territories,nunavut,ontario,prince_edward_island,quebec,saskatchewan,yukon}/` |

## Nigeria — states

| Old | New |
|:--|:--|
| `dlt/commonwealth/nigeria/states/nga_{abi,ada,aki,ana,bau,bay,ben,bor,crs,del,ebi,edo,eki,enu,fct,gom,imo,jig,kad,kan,kat,keb,kog,kwa,los,nas,ngr,ogn,ond,osn,oyo,plt,riv,sok,tar,yob,zam}/` | `dlt/commonwealth/nigeria/states/{abia,adamawa,akwa_ibom,anambra,bauchi,bayelsa,benue,borno,cross_river,delta,ebonyi,edo,ekiti,enugu,federal_capital_territory,gombe,imo,jigawa,kaduna,kano,katsina,kebbi,kogi,kwara,lagos,nasarawa,niger,ogun,ondo,osun,oyo,plateau,rivers,sokoto,taraba,yobe,zamfara}/` |

## British Isles — collapse dual naming

| Old | New |
|:--|:--|
| `dlt/british_isles/en/` | `dlt/british_isles/england/` |
| `dlt/british_isles/ni/` | `dlt/british_isles/northern_ireland/` |
| `dlt/british_isles/sct/` | `dlt/british_isles/scotland/` |
| `dlt/british_isles/wls/` | `dlt/british_isles/wales/` |
| `dlt/british_isles/iom/` | `dlt/british_isles/isle_of_man/` |
| `dlt/british_isles/jey/` | `dlt/british_isles/jersey/` |
| `dlt/british_isles/ggy/` | `dlt/british_isles/guernsey/` |

## Americas — `americas/` → `american_nations/`

| Old | New |
|:--|:--|
| `dlt/americas/{bra,mex,us,ven}/` | `dlt/american_nations/{brazil,mexico,united_states,venezuela}/` |
Ogham++: teanga ríomhchlárúcháin oghmóireachta
----------------------------------------------
For a description in English,
see our page on the [Esolang Wiki](https://esolangs.org/wiki/Ogham%2B%2B).

Tá an teanga bunaithe ar
[mheaisín tabhall](https://en.wikipedia.org/wiki/Register_machine)
a úsáideann cúig thabhall darb ainm T1, T2, T3, T4, agus T5.
Cuirtear luach 0 i ngach tabhall nuair a thosaíonn an meaisín.
Níl aon teorainn leis na slánuimhreacha is féidir a stóráil sna tabhaill seo.

Tacaíonn an teanga leis na horduithe seo a leanas:

|Ordú  |Toradh         |
|----- |---------------|
|ᚆ     |incrimintigh T1|
|ᚇ     |incrimintigh T2|
|ᚈ     |incrimintigh T3|
|ᚉ     |incrimintigh T4|
|ᚊ     |incrimintigh T5|
|ᚁ     |deicrimintigh T1|
|ᚂ     |deicrimintigh T2|
|ᚃ     |deicrimintigh T3|
|ᚄ     |deicrimintigh T4|
|ᚅ     |deicrimintigh T5|
|᚛x᚜ᚋ  |déan x chomh fada is T1 != 0|
|᚛x᚜ᚌ  |déan x chomh fada is T2 != 0|
|᚛x᚜ᚍ  |déan x chomh fada is T3 != 0|
|᚛x᚜ᚎ  |déan x chomh fada is T4 != 0|
|᚛x᚜ᚏ  |déan x chomh fada is T5 != 0|
|ᚕ     |stop an meaisín|


Tabhair faoi deara go seiceáiltear an coinníoll nuair a
thosaíonn an lúb agus ní dhéanfar aon rud má tá 0 sa tabhall.
Déantar neamhaird ar aon charachtar eile seachas na cinn sa
tábla thuas; mar sin is féidir
nótaí tráchta a chur in aon áit.
Seo thíos cúpla ríomhchlár simplí in Ogham++:

Cuir 4 i T2, cuir 5 i T3, suimigh iad, agus fág an toradh i T2:
```
ᚇᚇᚇᚇᚈᚈᚈᚈᚈ᚛ᚇᚃ᚜ᚍᚕ
```

Cuir 3 i T2, cuir 6 i T3, iolraigh iad, agus fág an toradh i T2:
```
ᚇᚇᚇᚈᚈᚈᚈᚈᚈ᚛ᚉᚊᚂ᚜ᚌ᚛᚛ᚇᚄ᚜ᚎᚃ᚛ᚆᚉᚅ᚜ᚏ᚛ᚊᚁ᚜ᚋ᚜ᚍᚕ
```

Cuir 7 i T2, ríomh 7! agus fág an toradh i T2:
```
ᚇᚇᚇᚇᚇᚇᚇ᚛ᚆᚂ᚜ᚌ᚛ᚇᚈᚁ᚜ᚋᚃ᚛᚛ᚉᚊᚃ᚜ᚍ᚛᚛ᚈᚄ᚜ᚎᚂ᚛ᚆᚉᚅ᚜ᚏ᚛ᚊᚁ᚜ᚋ᚜ᚌ᚛ᚃᚇ᚜ᚍ᚛ᚄᚅᚈ᚜ᚏᚃ᚜ᚍᚕ
```

Creid nó ná creid, tá an teanga seo *Turing-iomlán*.
Féach http://www.iwriteiam.nl/Ha_bf_Turing.html.
Seo meaisín uilíoch Turing bunaithe ar an leagan URM ó
http://www.hevanet.com/cristofd/brainfuck/urmutm.txt
```
᚛ᚃ᚛ᚉᚉᚉᚉᚉᚉᚃ᚜ᚍ᚛ᚇᚇᚁ᚜ᚋ᚛ᚆᚆᚆᚂ᚜ᚌ᚛ᚉᚅ᚛ᚉᚅ᚛ᚉᚅ᚛ᚉᚅ᚛ᚉᚅ᚛ᚄᚄᚄᚄᚄᚈᚅ᚛ᚇᚅ᚜ᚏ᚜ᚏ᚜ᚏ᚜ᚏ᚜ᚏ᚜ᚏ᚛ᚊᚂ᚜ᚌ᚜ᚏ᚛ᚊᚃ᚜ᚍᚈᚇᚆᚆᚆ᚛ᚄ᚛ᚂᚆᚄ᚛ᚁᚁᚁᚁᚄ᚛ᚇᚆᚆᚄ᚛ᚈᚈᚈᚂᚁᚁᚄ᚛ᚃᚃᚇᚆᚄ᚛ᚂᚁᚄ᚛ᚈᚇᚆᚆᚆᚆᚄ᚛ᚃᚄ᚛ᚂᚁᚄ᚛ᚁᚄ᚛ᚃᚆᚆᚆᚄ᚛ᚈᚈᚁᚁᚁᚁᚄ᚛ᚈᚆᚆᚄ᚛᚛ᚃ᚜ᚍᚄ᚛ᚈᚈᚈᚁᚄ᚛ᚃᚃᚁᚄ᚛ᚈᚇᚆᚆᚆᚆᚄ᚛ᚈᚈᚂᚁᚁᚁᚁᚁᚄ᚛ᚃᚃᚇᚆᚆᚆᚆᚆᚄ᚛ᚈᚈᚂᚁᚁᚄᚄ᚛ᚁᚄ᚜ᚎ᚜ᚎ᚜ᚎ᚜ᚎ᚜ᚎ᚜ᚎ᚜ᚎ᚜ᚎ᚜ᚎ᚜ᚎ᚜ᚎ᚜ᚎ᚜ᚎ᚜ᚎ᚜ᚎ᚜ᚎ᚜ᚎ᚜ᚎ᚜ᚎ᚜ᚎ᚜ᚎ᚜ᚎ᚛ᚂ᚛ᚇᚇᚇᚇᚇᚇᚅ᚜ᚏ᚛ᚇᚁ᚛ᚇᚁ᚛ᚇᚁ᚛ᚇᚁ᚛ᚇᚁ᚛ᚂᚂᚂᚂᚂᚉᚁ᚛ᚊᚁ᚜ᚋ᚜ᚋ᚜ᚋ᚜ᚋ᚜ᚋ᚜ᚋ᚛ᚆᚅ᚜ᚏ᚜ᚋ᚛ᚊᚊᚊᚊᚊᚊᚂ᚜ᚌ᚛ᚊᚄ᚛ᚊᚄ᚛ᚊᚄ᚛ᚊᚄ᚛ᚊᚄ᚛ᚅᚅᚅᚅᚅᚆᚄ᚛ᚇᚄ᚜ᚎ᚜ᚎ᚜ᚎ᚜ᚎ᚜ᚎ᚜ᚎ᚛ᚉᚂ᚜ᚌ᚜ᚎ᚜ᚌ᚜ᚍᚕ
```

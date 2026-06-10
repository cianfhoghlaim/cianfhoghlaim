#!/bin/bash
sed '
s/Cuir focal amháin sa chéad bhosca. Cliceáil an plus chun tuilleadh focal a chur i gcomparáid le chéile (suas le cúig cinn), agus an cnaipe “Seol” nuair a bheidh tú réidh./Enter a word in the box. Click the plus sign to compare additional words (up to five), and click “Submit” when you are ready./
s/Cuir focal amháin i ngach bosca/One word per box/
s/"Seol"/"Submit"/
s/Treochtaí/Trends/
s/Léarscáileanna/Maps/
s/Léarscáil/Map/
s/líon sa milliún focal/frequency per million words/
s/Roinnt de na samplaí is spéisiúla!/Some of the most interesting examples!/
s/Nó, caith súil ar shamplaí spéisiúla sa <a href="samplai.html">nGailearaí<\/a>/Or, check out some interesting examples in the <a href="samplai-en.html">Gallery<\/a>/
'

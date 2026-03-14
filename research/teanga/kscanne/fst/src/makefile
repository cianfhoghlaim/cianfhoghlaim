TSV=${HOME}/seal/biigtigong-private-lex-dat/biigtigong-private-lex-dat.tsv

all: badapost.txt badchar.txt badvowel.txt badcluster.txt
	@echo "bad apostrophes..."
	@cat badapost.txt
	@echo "bad characters..."
	@cat badchar.txt
	@echo "bad vowels..."
	@cat badvowel.txt
	@echo "bad full-vowel clusters..."
	@cat badcluster.txt

comp: depsyncope-comparison.txt syncope-comparison.txt diminutive-comparison.txt locative-comparison.txt obviative-comparison.txt pejorative-comparison.txt possessive-comparison.txt posswithm-comparison.txt plural-comparison.txt singular-comparison.txt

fixcomp:
	cp -f depsyncope-comparison-prev.txt depsyncope-comparison.txt
	cp -f diminutive-comparison-prev.txt diminutive-comparison.txt
	cp -f locative-comparison-prev.txt locative-comparison.txt
	cp -f obviative-comparison-prev.txt obviative-comparison.txt
	cp -f pejorative-comparison-prev.txt pejorative-comparison.txt
	cp -f plural-comparison-prev.txt plural-comparison.txt
	cp -f possessive-comparison-prev.txt possessive-comparison.txt
	cp -f posswithm-comparison-prev.txt posswithm-comparison.txt
	cp -f singular-comparison-prev.txt singular-comparison.txt
	cp -f syncope-comparison-prev.txt syncope-comparison.txt

gentest: FORCE
	cat generation-test.txt | egrep -v '^#' > test-correct.txt
	cat generation-test.txt | egrep -v '^#' | sed 's/\t.*//' | flookup -i nish.bin | egrep '[a-z]' > test-actual.txt
	diff -u test-correct.txt test-actual.txt

generation-test.txt-rebuild: FORCE
	cat generation-test.txt | while read x; do if echo "$$x" | egrep '^#' > /dev/null; then echo "$$x"; else echo "$$x" | sed 's/\t.*//' | flookup -i nish.bin | head -n 1; fi; done > tempfile
	mv -f tempfile generation-test.txt

nish.bin: nish.fst nish.txt syncopate.bin
	foma -f nish.fst

syncopate.bin: syncopate.fst
	foma -f syncopate.fst

# all theoretically possible apostrophes in Biigtigong orthography
allaposts.txt: consonants.txt
	(egrep '^..' consonants.txt | sed "s/^./&'/"; egrep '^...$$' consonants.txt | sed "s/.$$/'&/") | sort -u > $@

ascii-headwords.txt: headwords.txt
	cat headwords.txt | sed 's/ǧ/g/g; s/ȟ/h/g; s/ǩ/k/g' > $@

repeats.txt: pos.txt $(TSV)
	cat pos.txt | while read x; do cat $(TSV) | sed -n "/^[^\t]*\t[^\t]*\t$${x}\t/p" | cut -f 3,6 | sort | uniq -c | sort -r -n | egrep -v ' 1 '; done | egrep '[a-z]$$' > $@

headwords.txt: $(TSV)
	cat $(TSV) | cut -f 2 > $@

fullvowel.txt: $(TSV)
	cat $(TSV) | cut -f 6 > $@

pos.txt: $(TSV)
	cat $(TSV) | cut -f 3 | sort -u > $@

naI.txt: naVI.txt naDim.txt
	cat $(TSV) | sed -n '/^\t[^\t]*\([^aeio]\)\tna\t/p' | cut -f 2,3,6,7 | egrep "^[A-Za-z'-]*[aeio]([bcdfghjkmnprstwyz]+)[^A-Za-z'-].+\1ag$$" | cut -f 3 | egrep '[a-z]' | egrep -v ' ' | keepif -n naDim.txt | keepif -n naVI.txt > $@

# note no naDimDep.txt to worry about
naIDep.txt: naVIDep.txt
	cat $(TSV) | sed -n '/^n[^\t]*\t[^\t]*\([^aeio]\)\tna\t/p' | cut -f 2,3,6,7 | egrep "^[A-Za-z'-]*[aeio]([bcdfghjkmnprstwyz]+)[^A-Za-z'-].+\1ag$$" | cut -f 3 | egrep '[a-z]' | egrep -v ' ' | keepif -n naVIDep.txt > $@

niI.txt: niVI.txt niDim.txt
	cat $(TSV) | sed -n '/^\t[^\t]*\([^aeio]\)\tni\t/p' | cut -f 2,3,6,7 | egrep "^[A-Za-z'-]*[aeio]([bcdfghjkmnprstwyz]+)[^A-Za-z'-].+\1an$$" | cut -f 3 | egrep '[a-z]' | egrep -v ' ' | keepif -n niDim.txt | keepif -n niVI.txt > $@

niIDep.txt: niVIDep.txt niDimDep.txt
	cat $(TSV) | sed -n '/^n[^\t]*\t[^\t]*\([^aeio]\)\tni\t/p' | cut -f 2,3,6,7 | egrep "^[A-Za-z'-]*[aeio]([bcdfghjkmnprstwyz]+)[^A-Za-z'-].+\1an$$" | cut -f 3 | egrep '[a-z]' | egrep -v ' ' | keepif -n niDimDep.txt | keepif -n niVIDep.txt > $@

naCon.txt: $(TSV)
	cat $(TSV) | sed -n '/^\t[^\t]*nh\tna\t/p' | cut -f 2,3,6,7 | egrep "nyag$$" | cut -f 3 | egrep '[a-z]' | egrep -v ' ' > $@

naConDep.txt: $(TSV)
	cat $(TSV) | sed -n '/^n[^\t]*\t[^\t]*nh\tna\t/p' | cut -f 2,3,6,7 | egrep "nyag$$" | cut -f 3 | egrep '[a-z]' | egrep -v ' ' > $@

niCon.txt: $(TSV)
	cat $(TSV) | sed -n '/^\t[^\t]*nh\tni\t/p' | cut -f 2,3,6,7 | egrep "nyan$$" | cut -f 3 | egrep '[a-z]' | egrep -v ' ' > $@

niConDep.txt: $(TSV)
	cat $(TSV) | sed -n '/^n[^\t]*\t[^\t]*nh\tni\t/p' | cut -f 2,3,6,7 | egrep "nyan$$" | cut -f 3 | egrep '[a-z]' | egrep -v ' ' > $@

# no dependent examples
naDim.txt: $(TSV)
	cat $(TSV) | sed -n '/^\t[^\t]*ns\tna\t/p' | cut -f 2,3,6,7 | egrep "nsag$$" | cut -f 3 | egrep '[a-z]' | egrep -v ' ' > $@

niDim.txt: $(TSV)
	cat $(TSV) | sed -n '/^\t[^\t]*ns\tni\t/p' | cut -f 2,3,6,7 | egrep "nsan$$" | cut -f 3 | egrep '[a-z]' | egrep -v ' ' > $@

niDimDep.txt: $(TSV)
	cat $(TSV) | sed -n '/^n[^\t]*\t[^\t]*ns\tni\t/p' | cut -f 2,3,6,7 | egrep "nsan$$" | cut -f 3 | egrep '[a-z]' | egrep -v ' ' > $@

# intentionally allowing even short vowels as final vowel (mkwa, miikna, etc.)
naII.txt: $(TSV)
	cat $(TSV) | sed -n '/^\t[^\t]*[aeio]\tna\t/p' | cut -f 2,3,6,7 | egrep '^(.+)[^a-z].+\1g$$' | cut -f 3 | egrep '[a-z]' | egrep -v ' ' > $@

naIIDep.txt: $(TSV)
	cat $(TSV) | sed -n '/^n[^\t]*\t[^\t]*[aeio]\tna\t/p' | cut -f 2,3,6,7 | egrep '^(.+)[^a-z].+\1g$$' | cut -f 3 | egrep '[a-z]' | egrep -v ' ' > $@

niII.txt: $(TSV)
	cat $(TSV) | sed -n '/^\t[^\t]*[aeio]\tni\t/p' | cut -f 2,3,6,7 | egrep '^(.+)[^a-z].+\1n$$' | cut -f 3 | egrep '[a-z]' | egrep -v ' ' > $@

niIIDep.txt: $(TSV)
	cat $(TSV) | sed -n '/^n[^\t]*\t[^\t]*[aeio]\tni\t/p' | cut -f 2,3,6,7 | egrep '^(.+)[^a-z].+\1n$$' | cut -f 3 | egrep '[a-z]' | egrep -v ' ' > $@

naIII.txt: $(TSV)
	cat $(TSV) | sed -n '/^\t[^\t]*\([aeio]\)\tna\t/p' | cut -f 2,3,6,7 | egrep '^(.+)i?[^a-z].+\1wag$$' | cut -f 3 | egrep '[a-z]' | egrep -v ' ' > $@

naIIIDep.txt: $(TSV)
	cat $(TSV) | sed -n '/^n[^\t]*\t[^\t]*\([aeio]\)\tna\t/p' | cut -f 2,3,6,7 | egrep '^(.+)i?[^a-z].+\1wag$$' | cut -f 3 | egrep '[a-z]' | egrep -v ' ' > $@

# no dependent examples
niIII.txt: $(TSV)
	cat $(TSV) | sed -n '/^\t[^\t]*\([aeio]\)\tni\t/p' | cut -f 2,3,6,7 | egrep '^(.+)i?[^a-z].+\1wan$$' | cut -f 3 | egrep '[a-z]' | egrep -v ' ' > $@

# IVa/IVb labels in Valentine esp. p. 176 are flipped...
# Trusting that tables on p. 178 and p.181 are correct; oo[gn] => IVa
naIVa.txt: $(TSV)
	cat $(TSV) | sed -n '/^\t[^\t]*\([^aeio]\)\tna\t/p' | cut -f 2,3,6,7 | egrep 'oog$$' | cut -f 3 | egrep '[a-z]' | egrep -v ' ' > $@

naIVaDep.txt: $(TSV)
	cat $(TSV) | sed -n '/^n[^\t]*\t[^\t]*\([^aeio]\)\tna\t/p' | cut -f 2,3,6,7 | egrep 'oog$$' | cut -f 3 | egrep '[a-z]' | egrep -v ' ' > $@

niIVa.txt: $(TSV)
	cat $(TSV) | sed -n '/^\t[^\t]*\([^aeio]\)\tni\t/p' | cut -f 2,3,6,7 | egrep 'oon$$' | cut -f 3 | egrep '[a-z]' | egrep -v ' ' > $@

niIVaDep.txt: $(TSV)
	cat $(TSV) | sed -n '/^n[^\t]*\t[^\t]*\([^aeio]\)\tni\t/p' | cut -f 2,3,6,7 | egrep 'oon$$' | cut -f 3 | egrep '[a-z]' | egrep -v ' ' > $@

naIVb.txt: $(TSV)
	cat $(TSV) | sed -n '/^\t[^\t]*\([^aeio]\)\tna\t/p' | cut -f 2,3,6,7 | egrep '^(.+)[^a-z].+[^a-z]\1(o|wa)g$$' | cut -f 3 | egrep '[a-z]' | egrep -v ' ' > $@

naIVbDep.txt: $(TSV)
	cat $(TSV) | sed -n '/^n[^\t]*\t[^\t]*\([^aeio]\)\tna\t/p' | cut -f 2,3,6,7 | egrep '^(.+)[^a-z].+[^a-z]\1(o|wa)g$$' | cut -f 3 | egrep '[a-z]' | egrep -v ' ' > $@

naV.txt: $(TSV)
	cat $(TSV) | sed -n '/^\t[^\t]*\tna\t/p' | cut -f 2,3,6,7 | egrep 'iig$$' | cut -f 3 | egrep -v 'ii$$' > $@

naVDep.txt: $(TSV)
	cat $(TSV) | sed -n '/^n[^\t]*\t[^\t]*\tna\t/p' | cut -f 2,3,6,7 | egrep 'iig$$' | cut -f 3 | egrep -v 'ii$$' > $@

niV.txt: $(TSV)
	cat $(TSV) | sed -n '/^\t[^\t]*\tni\t/p' | cut -f 2,3,6,7 | egrep 'iin$$' | cut -f 3 | egrep -v 'ii$$' | egrep -v "^zaaga'igan$$" > $@

niVDep.txt: $(TSV)
	cat $(TSV) | sed -n '/^n[^\t]*\t[^\t]*\tni\t/p' | cut -f 2,3,6,7 | egrep 'iin$$' | cut -f 3 | egrep -v 'ii$$' > $@

naVI.txt: $(TSV)
	cat $(TSV) | sed -n '/^\t[^\t]*\([^aeio]\)\tna\t/p' | cut -f 2,3,6,7,8 | egrep 'aang$$' | cut -f 3 | egrep '[a-z]' | egrep -v ' ' > $@

naVIDep.txt: $(TSV)
	cat $(TSV) | sed -n '/^n[^\t]*\t[^\t]*\([^aeio]\)\tna\t/p' | cut -f 2,3,6,7,8 | egrep 'aang$$' | cut -f 3 | egrep '[a-z]' | egrep -v ' ' | egrep -v '^diskag$$' > $@

niVI.txt: $(TSV)
	cat $(TSV) | sed -n '/^\t[^\t]*\([^aeio]\)\tni\t/p' | cut -f 2,3,6,7,8 | egrep 'aang$$' | cut -f 3 | egrep '[a-z]' | egrep -v ' ' > $@

niVIDep.txt: $(TSV)
	cat $(TSV) | sed -n '/^n[^\t]*\t[^\t]*\([^aeio]\)\tni\t/p' | cut -f 2,3,6,7,8 | egrep 'aang$$' | cut -f 3 | egrep '[a-z]' | egrep -v ' ' | egrep -v '^skatig$$' > $@

# want the FV stems (col 15) here, *not* column 6 with the -ng or -d ending...
vai.txt: $(TSV)
	cat $(TSV) | sed -n '/^\t[^\t]*\tvai\tvai\t/p' | cut -f 15 | egrep '[a-z]' | egrep -v ' ' | sed 's/^\///; s/-\/$$//' > $@
	cat $(TSV) | sed -n '/^\t[^\t]*\tvai\tvai2\t/p' | cut -f 15 | egrep '[a-z]' | egrep -v ' ' | sed 's/^\///; s/-\/$$//' | sed 's/$$/am/' >> $@

vaio.txt: $(TSV)
	cat $(TSV) | sed -n '/^\t[^\t]*\tvaio\t/p' | cut -f 15 | egrep '[a-z]' | egrep -v ' ' | sed 's/^\///; s/-\/$$//' > $@

vaip.txt: $(TSV)
	cat $(TSV) | sed -n '/^\t[^\t]*\tvaip\t/p' | cut -f 15 | egrep '[a-z]' | egrep -v ' ' | sed 's/^\///; s/-\/$$//' > $@

vii.txt: $(TSV)
	cat $(TSV) | sed -n '/^\t[^\t]*\tvii\tvii\t/p' | cut -f 15 | egrep '[a-z]' | egrep -v ' ' | sed 's/^\///; s/-\/$$//' > $@

vta.txt: $(TSV)
	cat $(TSV) | sed -n '/^\t[^\t]*\tvta\tvta\t/p' | cut -f 15 | egrep '[a-z]' | egrep -v ' ' | sed 's/^\///; s/-\/$$//' > $@

vti1.txt: $(TSV)
	cat $(TSV) | sed -n '/^\t[^\t]*\tvti\tvti\t/p' | cut -f 15 | egrep '[a-z]' | egrep -v ' ' | sed 's/^\///; s/-\/$$//' > $@

vti2.txt: $(TSV)
	cat $(TSV) | sed -n '/^\t[^\t]*\tvti\tvti2\t/p' | cut -f 15 | egrep '[a-z]' | egrep -v ' ' | sed 's/^\///; s/-\/$$//' > $@

vti3.txt: $(TSV)
	cat $(TSV) | sed -n '/^\t[^\t]*\tvti\tvti3\t/p' | cut -f 15 | egrep '[a-z]' | egrep -v ' ' | sed 's/^\///; s/-\/$$//' > $@

vti4.txt: $(TSV)
	cat $(TSV) | sed -n '/^\t[^\t]*\tvti\tvti4\t/p' | cut -f 15 | egrep '[a-z]' | egrep -v ' ' | sed 's/^\///; s/-\/$$//' > $@

classified-nouns.txt: naI.txt niI.txt naII.txt niII.txt naIII.txt niIII.txt naIVa.txt niIVa.txt naIVb.txt naV.txt niV.txt naVI.txt niVI.txt naCon.txt niCon.txt naDim.txt niDim.txt naConDep.txt naIDep.txt naIIDep.txt naIIIDep.txt naIVaDep.txt naIVbDep.txt naVDep.txt naVIDep.txt niConDep.txt niDimDep.txt niIDep.txt niIIDep.txt niIVaDep.txt niVDep.txt niVIDep.txt
	cat naI.txt niI.txt naII.txt niII.txt naIII.txt niIII.txt naIVa.txt niIVa.txt naIVb.txt naV.txt niV.txt naVI.txt niVI.txt naCon.txt niCon.txt naDim.txt niDim.txt naConDep.txt naIDep.txt naIIDep.txt naIIIDep.txt naIVaDep.txt naIVbDep.txt naVDep.txt naVIDep.txt niConDep.txt niDimDep.txt niIDep.txt niIIDep.txt niIVaDep.txt niVDep.txt niVIDep.txt > $@

nish.txt: nish-template.txt naI.txt niI.txt naII.txt niII.txt naIII.txt niIII.txt naIVa.txt niIVa.txt naIVb.txt naV.txt niV.txt naVI.txt niVI.txt naCon.txt niCon.txt naDim.txt niDim.txt naConDep.txt naIDep.txt naIIDep.txt naIIIDep.txt naIVaDep.txt naIVbDep.txt naVDep.txt naVIDep.txt niConDep.txt niDimDep.txt niIDep.txt niIIDep.txt niIVaDep.txt niVDep.txt niVIDep.txt vai.txt vaio.txt vaip.txt vii.txt vta.txt vti1.txt vti2.txt vti3.txt vti4.txt
	rm -f templex.txt $@
	cat naI.txt | sed 's/$$/\tNA_I ;/' > templex.txt
	cat niI.txt | sed 's/$$/\tNI_I ;/' >> templex.txt
	cat naCon.txt | sed 's/$$/\tNA_Con ;/' >> templex.txt
	cat niCon.txt | sed 's/$$/\tNI_Con ;/' >> templex.txt
	cat naDim.txt | sed 's/$$/\tNA_Dim ;/' >> templex.txt
	cat niDim.txt | sed 's/$$/\tNI_Dim ;/' >> templex.txt
	cat naII.txt | sed 's/$$/\tNA_II ;/' >> templex.txt
	cat niII.txt | sed 's/$$/\tNI_II ;/' >> templex.txt
	cat naIII.txt | sed 's/$$/\tNA_III ;/' >> templex.txt
	cat niIII.txt | sed 's/$$/\tNI_III ;/' >> templex.txt
	cat naIVa.txt | sed 's/$$/\tNA_IVa ;/' >> templex.txt
	cat niIVa.txt | sed 's/$$/\tNI_IVa ;/' >> templex.txt
	cat naIVb.txt | sed 's/$$/\tNA_IVb ;/' >> templex.txt
	cat naV.txt | sed 's/$$/\tNA_V ;/' >> templex.txt
	cat niV.txt | sed 's/$$/\tNI_V ;/' >> templex.txt
	cat naVI.txt | sed 's/$$/\tNA_VI ;/' >> templex.txt
	cat niVI.txt | sed 's/$$/\tNI_VI ;/' >> templex.txt
	cat nish-template.txt | sed '/^LEXICON IndependentNouns/r templex.txt' > $@
	cat naIDep.txt | sed 's/$$/\tNA_I ;/' > templex.txt
	cat niIDep.txt | sed 's/$$/\tNI_I ;/' >> templex.txt
	cat naConDep.txt | sed 's/$$/\tNA_Con ;/' >> templex.txt
	cat niConDep.txt | sed 's/$$/\tNI_Con ;/' >> templex.txt
	cat niDimDep.txt | sed 's/$$/\tNI_Dim ;/' >> templex.txt
	cat naIIDep.txt | sed 's/$$/\tNA_II ;/' >> templex.txt
	cat niIIDep.txt | sed 's/$$/\tNI_II ;/' >> templex.txt
	cat naIIIDep.txt | sed 's/$$/\tNA_III ;/' >> templex.txt
	cat naIVaDep.txt | sed 's/$$/\tNA_IVa ;/' >> templex.txt
	cat niIVaDep.txt | sed 's/$$/\tNI_IVa ;/' >> templex.txt
	cat naIVbDep.txt | sed 's/$$/\tNA_IVb ;/' >> templex.txt
	cat naVDep.txt | sed 's/$$/\tNA_V ;/' >> templex.txt
	cat niVDep.txt | sed 's/$$/\tNI_V ;/' >> templex.txt
	cat naVIDep.txt | sed 's/$$/\tNA_VI ;/' >> templex.txt
	cat niVIDep.txt | sed 's/$$/\tNI_VI ;/' >> templex.txt
	sed -i '/^LEXICON DependentNouns/r templex.txt' $@
	cat vai.txt | egrep '[aeio]$$' | sed 's/$$/\tVAI_Vowel_Final_Suffixes ;/' > templex.txt
	cat vai.txt | egrep '[^aeio]$$' | sed 's/$$/\tVAI_Nasal_Final_Suffixes ;/' >> templex.txt
	sed -i '/^LEXICON VAI_Stems/r templex.txt' $@
	cat vaio.txt | sed 's/$$/\tVAIO_Suffixes ;/' > templex.txt
	sed -i '/^LEXICON VAIO_Stems/r templex.txt' $@
	cat vaip.txt | egrep '[aeio]$$' | sed 's/$$/\tVAIP_Vowel_Final_Suffixes ;/' > templex.txt
	cat vaip.txt | egrep '[^aeio]$$' | sed 's/$$/\tVAIP_Nasal_Final_Suffixes ;/' >> templex.txt
	sed -i '/^LEXICON VAIP_Stems/r templex.txt' $@
	cat vii.txt | egrep '[aeio]$$' | sed 's/$$/\tVII_Vowel_Final_Suffixes ;/' > templex.txt
	cat vii.txt | egrep 'n$$' | sed 's/$$/\tVII_N_Final_Suffixes ;/' >> templex.txt
	cat vii.txt | egrep 'd$$' | sed 's/$$/\tVII_D_Final_Suffixes ;/' >> templex.txt
	sed -i '/^LEXICON VII_Stems/r templex.txt' $@
	cat vta.txt | sed 's/$$/\tVTA_Suffixes ;/' > templex.txt
	sed -i '/^LEXICON VTA_Stems/r templex.txt' $@
	cat vti1.txt | sed 's/$$/\tVTI1_Suffixes ;/' > templex.txt
	cat vti2.txt | sed 's/$$/\tVTI2_Suffixes ;/' >> templex.txt
	cat vti3.txt | sed 's/$$/\tVTI3_Suffixes ;/' >> templex.txt
	cat vti4.txt | sed 's/$$/\tVTI4_Suffixes ;/' >> templex.txt
	sed -i '/^LEXICON VTI_Stems/r templex.txt' $@
	rm -f templex.txt
	chmod 444 $@

# nouns in TSV that never ended up in a noun class file naI, niIVa, etc. 
othernouns.txt: classified-nouns.txt
	cat $(TSV) | sed -n '/^[^\t]*\t[^\t]*\tn[ai]\t\(n[ai]\)\?\t/p' | cut -f 6,7 | egrep '[a-z]$$' | cut -f 1 | keepif -n classified-nouns.txt | egrep '[a-z]' > $@
	#cat $(TSV) | sed -n '/^\t[^\t]*\tn[ai]\t\(n[ai]\)\?\t/p' | cut -f 6 | keepif -n classified-nouns.txt > $@

independentnouns.txt: $(TSV) 
	cat $(TSV) | sed -n '/^\t[^\t]*\tn[ai]\t/p' | cut -f 3,6 | sed '/^na/s/^..\t\(.*\)/\1+NA/; /^ni/s/^..\t\(.*\)/\1+NI/' > $@

allnouns.txt: $(TSV) 
	cat $(TSV) | sed -n '/^[^\t]*\t[^\t]*\tn[ai]\t/p' | cut -f 3,6 | sed '/^na/s/^..\t\(.*\)/\1+NA/; /^ni/s/^..\t\(.*\)/\1+NI/' > $@

tsv-singulars.txt: $(TSV)
	cat $(TSV) | sed -n '/^\t[^\t]*\tn[ai]\t/p' | cut -f 2 > $@

tsv-plurals.txt: $(TSV)
	cat $(TSV) | sed -n '/^\t[^\t]*\tn[ai]\t/p' | cut -f 7 > $@

tsv-locatives.txt: $(TSV)
	cat $(TSV) | sed -n '/^\t[^\t]*\tn[ai]\t/p' | cut -f 8 > $@

tsv-diminutives.txt: $(TSV)
	cat $(TSV) | sed -n '/^\t[^\t]*\tn[ai]\t/p' | cut -f 9 > $@

tsv-pejoratives.txt: $(TSV)
	cat $(TSV) | sed -n '/^\t[^\t]*\tn[ai]\t/p' | cut -f 10 > $@

tsv-possessive.txt: $(TSV)
	cat $(TSV) | sed -n '/^[^\t]*\t[^\t]*\tn[ai]\t/p' | cut -f 11 > $@

tsv-posswithm.txt: $(TSV)
	cat $(TSV) | sed -n '/^[^\t]*\t[^\t]*\tn[ai]\t/p' | cut -f 12 > $@

tsv-obviatives.txt: $(TSV)
	cat $(TSV) | sed -n '/^\t[^\t]*\tn[ai]\t/p' | cut -f 13 > $@

# Biigtigong we/wedi (pron dem) aren't just syncopated version of full vowel
tsv-syncopated.txt: $(TSV)
	cat $(TSV) | egrep -v '^[a-z]' | cut -f 2 | egrep -v "^(we|wedi)$$" > $@

tsv-depsyncopated.txt: $(TSV)
	cat $(TSV) | egrep '^[a-z]' | cut -f 1,2 | tr -d "\t" > $@

singular-test.txt: independentnouns.txt nish.bin
	cat independentnouns.txt | sed 's/$$/+Sg/' | flookup -i nish.bin | egrep '.' | sed 's/^.*\t//' > $@

plural-test.txt: independentnouns.txt nish.bin
	cat independentnouns.txt | sed 's/$$/+Pl/' | flookup -i nish.bin | egrep '.' | sed 's/^.*\t//' > $@

locative-test.txt: independentnouns.txt nish.bin
	cat independentnouns.txt | sed 's/$$/+Loc/' | flookup -i nish.bin | egrep '.' | sed 's/^.*\t//' > $@

diminutive-test.txt: independentnouns.txt nish.bin
	cat independentnouns.txt | sed 's/$$/+Dim+Sg/' | flookup -i nish.bin | egrep '.' | sed 's/^.*\t//' > $@

pejorative-test.txt: independentnouns.txt nish.bin
	cat independentnouns.txt | sed 's/$$/+Pej+Sg/' | flookup -i nish.bin | egrep '.' | sed 's/^.*\t//' > $@

possessive-test.txt: allnouns.txt nish.bin
	cat allnouns.txt | sed 's/^/1P+Sg+Poss+/' | sed 's/$$/+Sg/' | flookup -i nish.bin | egrep '.' | sed 's/^.*\t//' > $@

posswithm-test.txt: allnouns.txt nish.bin
	cat allnouns.txt | sed 's/^/1P+Sg+Poss+/' | sed 's/$$/+PossThm+Sg/' | flookup -i nish.bin | egrep '.' | sed 's/^.*\t//' > $@

obviative-test.txt: independentnouns.txt nish.bin
	cat independentnouns.txt | sed 's/$$/+Obv/' | flookup -i nish.bin | egrep '.' | sed 's/^.*\t//' > $@

# Biigtigong we/wedi (pron dem) aren't just syncopated version of full vowel
syncopated-test.txt: $(TSV) syncopate.bin
	cat $(TSV) | egrep -v '^[a-z]' | cut -f 2,6 | egrep -v "^(we|wedi)[^ a-z]" | cut -f 2 | flookup -i syncopate.bin | egrep '.' | sed 's/^.*\t//' > $@

depsyncopated-test.txt: $(TSV) nish.bin
	- cat $(TSV) | egrep '^[a-z]' | cut -f 3,6 | sed 's/^\(n[ai]\)p/\1/' | sed 's/^na\t\(.*\)/\1+NA+Sg/' | sed 's/^ni\t\(.*\)/\1+NI+Sg/' | sed "s/^/1P+Sg+Poss+/" | flookup -i nish.bin | egrep '.' | sed 's/^.*\t//' > $@

singular-comparison.txt: singular-test.txt tsv-singulars.txt 
	touch $@
	mv -f $@ singular-comparison-prev.txt
	-paste singular-test.txt tsv-singulars.txt | tolow | egrep -v '^(.+).\1$$' | egrep -v ' ' | egrep -v '^[^A-Za-z]' | egrep '[A-Za-z]$$' > $@
	-diff -u singular-comparison-prev.txt $@
	wc -l singular-comparison-prev.txt $@

plural-comparison.txt: plural-test.txt tsv-plurals.txt 
	touch $@
	mv -f $@ plural-comparison-prev.txt
	-paste plural-test.txt tsv-plurals.txt | tolow | egrep -v '^(.+).\1$$' | egrep -v ' ' | egrep -v '^[^A-Za-z]' | egrep '[A-Za-z]$$' > $@
	-diff -u plural-comparison-prev.txt $@
	wc -l plural-comparison-prev.txt $@

locative-comparison.txt: locative-test.txt tsv-locatives.txt 
	touch $@
	mv -f $@ locative-comparison-prev.txt
	-paste locative-test.txt tsv-locatives.txt | tolow | egrep -v '^(.+).\1$$' | egrep -v ' ' | egrep -v '^[^A-Za-z]' | egrep '[A-Za-z]$$' > $@
	-diff -u locative-comparison-prev.txt $@
	wc -l locative-comparison-prev.txt $@

diminutive-comparison.txt: diminutive-test.txt tsv-diminutives.txt 
	touch $@
	mv -f $@ diminutive-comparison-prev.txt
	-paste diminutive-test.txt tsv-diminutives.txt | tolow | egrep -v '^(.+).\1$$' | egrep -v ' ' | egrep -v '^[^A-Za-z]' | egrep '[A-Za-z]$$' > $@
	-diff -u diminutive-comparison-prev.txt $@
	wc -l diminutive-comparison-prev.txt $@

pejorative-comparison.txt: pejorative-test.txt tsv-pejoratives.txt 
	touch $@
	mv -f $@ pejorative-comparison-prev.txt
	-paste pejorative-test.txt tsv-pejoratives.txt | tolow | egrep -v '^(.+).\1$$' | egrep -v ' ' | egrep -v '^[^A-Za-z]' | egrep '[A-Za-z]$$' > $@
	-diff -u pejorative-comparison-prev.txt $@
	wc -l pejorative-comparison-prev.txt $@

possessive-comparison.txt: possessive-test.txt tsv-possessive.txt 
	touch $@
	mv -f $@ possessive-comparison-prev.txt
	-paste possessive-test.txt tsv-possessive.txt | tolow | egrep -v '^(.+).\1$$' | egrep -v ' ' | egrep -v '^[^A-Za-z]' | egrep '[A-Za-z]$$' > $@
	-diff -u possessive-comparison-prev.txt $@
	wc -l possessive-comparison-prev.txt $@

posswithm-comparison.txt: posswithm-test.txt tsv-posswithm.txt 
	touch $@
	mv -f $@ posswithm-comparison-prev.txt
	-paste posswithm-test.txt tsv-posswithm.txt | tolow | egrep -v '^(.+).\1$$' | egrep -v ' ' | egrep -v '^[^A-Za-z]' | egrep '[A-Za-z]$$' > $@
	-diff -u posswithm-comparison-prev.txt $@
	wc -l posswithm-comparison-prev.txt $@

obviative-comparison.txt: obviative-test.txt tsv-obviatives.txt 
	touch $@
	mv -f $@ obviative-comparison-prev.txt
	-paste obviative-test.txt tsv-obviatives.txt | tolow | egrep -v '^(.+).\1$$' | egrep -v ' ' | egrep -v '^[^A-Za-z]' | egrep '[A-Za-z]$$' > $@
	-diff -u obviative-comparison-prev.txt $@
	wc -l obviative-comparison-prev.txt $@

# filters out (1) anything correct (2) entries with spaces 
# (3) entries missing full-vowel form (so 1st column in resulting paste empty)
syncope-comparison.txt: syncopated-test.txt tsv-syncopated.txt
	touch $@
	mv -f $@ syncope-comparison-prev.txt
	-paste syncopated-test.txt tsv-syncopated.txt | tolow | egrep -v '^(.+).\1$$' | egrep -v ' ' | egrep -v '^[^A-Za-z]' > $@
	-diff -u syncope-comparison-prev.txt $@
	wc -l syncope-comparison-prev.txt $@

depsyncope-comparison.txt: depsyncopated-test.txt tsv-depsyncopated.txt
	touch $@
	mv -f $@ depsyncope-comparison-prev.txt
	-paste depsyncopated-test.txt tsv-depsyncopated.txt | tolow | egrep -v '^(.+).\1$$' | egrep -v ' ' | egrep -v '^[^A-Za-z]' > $@
	-diff -u depsyncope-comparison-prev.txt $@
	-wc -l depsyncope-comparison-prev.txt $@

diacriticbug.txt: syncope-comparison.txt
	cat syncope-comparison.txt | sed 's/ǧ/g/g; s/ȟ/h/g; s/ǩ/k/g' | egrep '^(.+)[^a-z]\1$$' | sed 's/\t.*//' > $@
	wc -l $@

consonanttypos.txt: syncope-comparison.txt
	cat syncope-comparison.txt | while read x; do if ! echo "$$x" | tr -d "aeiouw'" | egrep '^(.+).\1$$' > /dev/null; then echo $$x; fi; done > $@

# analyze usage of apostrophe in Biigtigong forms 
badapost.txt: allaposts.txt headwords.txt
	cat headwords.txt | egrep -o "[^aeiou-]+'[^aeiou-]+"  | egrep -v ' ' | egrep -v -f allaposts.txt | sort | uniq -c | sort -r -n > $@

badchar.txt: headwords.txt
	-cat headwords.txt | egrep -v '(weǧnesh| OR )' | egrep "[^A-EG-KM-PSTWYZa-eg-km-pstwyzǧǩȟ ?'-]" > $@

badvowel.txt: headwords.txt
	-cat headwords.txt | egrep '(a[eio]|e[aio]|i[aeo]|o[aei])' > $@

clusters.txt: consonants.txt
	(cat consonants.txt; cat consonants.txt | egrep -v '^n([sy]|zh)' | egrep -v '^sht' | egrep -v '^[wy]' | sed 's/$$/w/') | sort -u > clusters.txt

badcluster.txt: fullvowel.txt clusters.txt
	-cat fullvowel.txt | egrep -v ' ' | egrep -o '[^aeiou-]+' | keepif -n clusters.txt | sort | uniq -c | sort -r -n > $@

clean:
	rm -f badapost.txt allaposts.txt badchar.txt badcluster.txt badvowel.txt headwords.txt fullvowel.txt syncopated-test.txt clusters.txt ascii-headwords.txt classified-nouns.txt othernouns.txt naI.txt niI.txt naII.txt niII.txt naIII.txt niIII.txt naIVa.txt niIVa.txt naIVb.txt naV.txt niV.txt naVI.txt niVI.txt naCon.txt niCon.txt naConDep.txt naIDep.txt naIIDep.txt naIIIDep.txt naIVaDep.txt naIVbDep.txt naVDep.txt naVIDep.txt niConDep.txt niDimDep.txt niIDep.txt niIIDep.txt niIVaDep.txt niVDep.txt niVIDep.txt naDim.txt niDim.txt *-prev.txt *-comparison.txt consonanttypos.txt diacriticbug.txt multichar.txt nish.txt plural-test.txt tsv-*.txt independentnouns.txt pos.txt repeats.txt allnouns.txt test-actual.txt test-correct.txt singular-test.txt locative-test.txt diminutive-test.txt pejorative-test.txt possessive-test.txt posswithm-test.txt obviative-test.txt depsyncopated-test.txt vaio.txt vaip.txt vai.txt vii.txt vta.txt vti1.txt vti2.txt vti3.txt vti4.txt

distclean:
	$(MAKE) clean
	rm -f syncopate.bin nish.bin

FORCE:


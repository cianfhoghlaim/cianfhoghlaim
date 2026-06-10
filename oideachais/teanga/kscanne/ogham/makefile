all: factorial.opp fourplusfive.opp threetimessix.opp

factorial.opp: factorial.urm
	cat factorial.urm | sed -f urm2opp.sed > $@

fourplusfive.opp: fourplusfive.urm
	cat fourplusfive.urm | sed -f urm2opp.sed > $@

threetimessix.opp: threetimessix.urm
	cat threetimessix.urm | sed -f urm2opp.sed > $@

utm.opp: utm.urm
	cat utm.urm | sed -f urm2opp.sed > $@

test: test.sh factorial.opp fourplusfive.opp threetimessix.opp utm.opp FORCE
	bash test.sh

clean:
	rm -f factorial.opp fourplusfive.opp threetimessix.opp utm.opp a.out

FORCE:

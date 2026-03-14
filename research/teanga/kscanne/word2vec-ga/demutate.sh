#!/bin/bash
# Pipe in a list of words and it removes any initial mutations
# (naively, doesn't handle "chugat", or initial h's intelligently)
# Handles uppercase too; not needed for this repo but I use this script
# various other places as well so it does no harm
sed "
s/^[nt]-//
s/^[nt]\([AEIOUÁÉÍÓÚ]\)/\1/
s/^[mdbns][’']\(.\)/\1/
s/^h-\?\([aeiouáéíóúAEIOUÁÉÍÓÚ]\)/\1/
s/^m\([Bb]\)/\1/
s/^g\([Cc]\)/\1/
s/^n\([DdGg]\)/\1/
s/^bh\([Ff]\)/\1/
s/^b\([Pp]\)/\1/
s/^t\([Ss]\)/\1/
s/^d\([Tt]\)/\1/
s/^\([bBcCdDfFgGmMpPSsTt]\)h/\1/
"

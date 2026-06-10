#!/usr/bin/perl

# script used to convert gramadoir-ga's comhshuite input file,
# with all it's crazy regexps, into a usable .pot file
# Only used in makefile 'comhshuite.pot' target

use strict;
use warnings;
use utf8;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

while (<STDIN>) {
	unless (/^#/) {
		s/\[.([a-záéíóú])\]/$1/g;
		s/(.*):<([A-Z])([^>]*)>/<$2$3>$1<\/$2>/;
		my $pr;
		if (/\?.h\?/) {   # optional eclipse+lenite
			$pr = $_;
			$pr =~ s/.\?(.)h\?/$1/;
			print $pr;              # unmutated
			$pr = $_;
			$pr =~ s/\?(.)h\?/$1/;
			print $pr;              # eclipsed
			$pr = $_;
			$pr =~ s/.\?(.h)\?/$1/;
			print $pr;              # lenited
		}
		elsif (/\?/) {    # just one optional char (not always eclipse)
			$pr = $_;
			$pr =~ s/\?//;
			print $pr;  # with the optional char
			$pr = $_;
			$pr =~ s/.\?//;
			print $pr;  # without it
		}
		else {
			print;
		}
	}
}

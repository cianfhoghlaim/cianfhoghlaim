#!/usr/bin/perl

# see makefile; used for hussey.tsv target

use strict;
use warnings;
use utf8;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

my $curr='';
while (<STDIN>) {
	chomp;
	if (m/<\/page>/) {
		$curr =~ s/^\s*<page>\s*<title>//;
		print "$curr\n";
		$curr = '';
	}
	else {
		$curr .= "$_ ";
	}
}

exit 0;

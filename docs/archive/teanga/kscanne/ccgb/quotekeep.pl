#!/usr/bin/perl

use strict;
use warnings;

binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

open (INFILE, "<:utf8", $ARGV[0]) or die "Can't open file: $!";
my $max = $ARGV[1];
my $oksofar = 0;
shift @ARGV;
shift @ARGV;
my @regexps;
foreach (@ARGV) {
	push @regexps, qr/$_/ if (m/ /);
}
while (<INFILE>) {
	my $ok = 1;
	foreach my $patt (@regexps) {
		unless (m/$patt/) {
			$ok = 0;
			last;
		}
	}
	if ($ok) {
		s/ .*//;
		print;
		$oksofar++;
		last if ($oksofar == $max);
	}
}
close INFILE;
exit 0;

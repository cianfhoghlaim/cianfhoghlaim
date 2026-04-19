#!/usr/bin/perl

# recomputes full FREQ file for crubadan dir
#  Reads files from /snapshot/aimsigh/FREQ directory

use strict;
use warnings;

binmode STDOUT, ":encoding(iso-8859-1)";
binmode STDERR, ":encoding(iso-8859-1)";
binmode STDIN, ":bytes";

my $base='/snapshot/aimsigh/FREQ';
my %bighash;

opendir DIRH, $base or die "could not open $base: $!\n";
my $N=0;
foreach my $doctxt (readdir DIRH) {
	next if $doctxt !~ /\.txt$/;
	$N++;
	print STDERR "$N..." if ($N % 100 == 0);
	open (FOINSE, "<", "$base/$doctxt") or die "Could not open source file $doctxt: $!\n";
	while (<FOINSE>) {
		chomp;
		(my $w, my $f) = m/^([^ ]+) ([0-9]+)$/;
		if (exists($bighash{$w})) {
			$bighash{$w} += $f;
		}
		else {
			$bighash{$w} = $f;
		}
	}
	close FOINSE;
}
closedir DIRH;

foreach my $k (sort {$bighash{$b} <=> $bighash{$a}} keys %bighash) {
	print "$bighash{$k} $k\n";
}

exit 0;

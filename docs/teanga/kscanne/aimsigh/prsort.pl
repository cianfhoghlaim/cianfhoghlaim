#!/usr/bin/perl

use strict;
use warnings;
my $crub = '/usr/local/share/crubadan/ga';

my %prhash;
while (<STDIN>) {
	chomp;
	my $docid = $_;
	open (SONRAI, "<", "$crub/sonrai/$docid.dat") or die "Could not open $docid.dat file: $!\n";
	while (<SONRAI>) {
		chomp;
		if (m/^pagerank: /) {
			(my $pr) = m/^pagerank: (.*)$/;
			$prhash{$docid} = $pr;
		}
	}
	close SONRAI;
}
print "$_\n" foreach (sort {$prhash{$b} <=> $prhash{$a}} keys %prhash);
exit 0;

#!/usr/bin/perl

use strict;
use warnings;


my %ENGLISH;
my %IRISH;
my %ENGFREQ;
my %IRISHFREQ;

my $cutoff = 2;
my $cosinecutoff = 0.3;
my $ratiolower = $cosinecutoff*$cosinecutoff;
my $ratioupper = 1/$ratiolower;

die "Usage: $0 BEARLA GAEILGE\n" unless ($#ARGV == 1);

open (BEARLA, $ARGV[0]) or die "Error opening English: $!\n";
while (<BEARLA>) {
	chomp;
	my ($word, $hits) = m/^([^:]+): (.*)$/;
	my @arr = split / /,$hits;
	if (@arr > $cutoff) {
		$ENGLISH{$word} = $hits;
		$ENGFREQ{$word} = @arr;
	}
}
close BEARLA;
open (GAEILGE, $ARGV[1]) or die "Error opening Irish: $!\n";
while (<GAEILGE>) {
	chomp;
	my ($word, $hits) = m/^([^:]+): (.*)$/;
	my @arr = split / /,$hits;
	if (@arr > $cutoff) {
		$IRISH{$word} = $hits;
		$IRISHFREQ{$word} = @arr;
	}
}
close GAEILGE;

foreach my $english (sort keys %ENGLISH) {
	my $engfreq = $ENGFREQ{$english};
	my %seen;
	my $best;
	my $bestcos = 0;
	for (split / /,$ENGLISH{$english}) {
		$seen{$_}++;
	}
	foreach my $irish (keys %IRISH) {
		my $irishfreq = $IRISHFREQ{$irish};
		my $ratio = $irishfreq/$engfreq;
		if ($ratio < $ratioupper and $ratio > $ratiolower) {
			my $common = 0;
			for (split / /,$IRISH{$irish}) {
				$common++ if (exists($seen{$_}));
			}
			my $cos = $common/(sqrt($engfreq)*sqrt($irishfreq));
			if ($cos > $cosinecutoff and $cos > $bestcos) {
				$bestcos = $cos;
				$best = sprintf "%1.3f|$english|$irish|$common $engfreq $irishfreq", $cos;
			}
		}
	}
	print "$best\n" if ($bestcos > 0);
}

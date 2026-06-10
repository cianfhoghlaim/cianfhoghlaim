#!/usr/bin/perl

use strict;
use warnings;
use utf8;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

# keys are surface words, vals are hashrefs with stems as keys
my %stem;
my %ans;

sub addto {
	(my $st, my $c) = @_;
	if (exists($ans{$st})) {
		$ans{$st} += $c;
	}
	else {
		$ans{$st} = $c;
	}
}

open(STEMS, "<:utf8", $ARGV[1]) or die "Could not open stem list: $!";
while (<STEMS>) {
	chomp;
	my $line = $_;
	(my $surface, my $st) = $line =~ m/^([^ ]+) (.+)$/;
	$stem{$surface}->{$st} = 1;
}
close STEMS;

open(FREQ, "<:utf8", $ARGV[0]) or die "Could not open freq list at $ARGV[0]: $!";
while (<FREQ>) {
	chomp;
	my $line = $_;
	(my $c, my $w) = $line =~ m/^([0-9]+) (.+)$/;
	if (exists($stem{$w})) {
		for my $st (keys %{$stem{$w}}) {
			addto($st, $c);
		}
	}
	else {
		if (exists($stem{lc($w)})) {
			for my $st (keys %{$stem{lc($w)}}) {
				addto($st, $c);
			}
		}
	}
}
close FREQ;

for my $k (sort { $ans{$b} <=> $ans{$a} } keys %ans) {
	print "$k $ans{$k}\n";
}

exit 0;

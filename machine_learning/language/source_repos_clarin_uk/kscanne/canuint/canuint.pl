#!/usr/bin/perl

use strict;
use warnings;
use utf8;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

my $verbose = (@ARGV > 0 and $ARGV[0] eq '-v');

# three keys: 'M', 'C', 'U'
# values are hashrefs where keys are the feature patterns
my %model;

open(MODEL, "<:utf8", "model.txt") or die "Could not open model file: $!";
while (<MODEL>) {
	chomp;
	(my $patt, my $c, my $m, my $u) = m/^([^\t]+)\t([0-9.+e-]+)\t([0-9.+e-]+)\t([0-9.+e-]+)$/;
	my $compiled = qr/$patt/i;
	$model{'C'}->{$compiled} = $c;
	$model{'M'}->{$compiled} = $m;
	$model{'U'}->{$compiled} = $u;
}
close MODEL;

# keys are M, C, or U, values are logP(text|key)
my %answer;
$answer{$_} = 0 for (keys %model);

# reads one token per line; new lines are '\n'
my @trigram;
while (<STDIN>) {
	chomp;
	unless ($_ eq "\\n") {
		push @trigram, $_;
		shift @trigram if (scalar @trigram > 3);
	}
	my $trigramstr = "@trigram";
	for my $regex (keys %{$model{'C'}}) {
		if ($trigramstr =~ m/$regex/) {
			for my $canuint (keys %model) {
				$answer{$canuint} += $model{$canuint}->{$regex};
			}
		}
	}
}

if ($verbose) {
	for my $c (keys %answer) {
		print "$c: $answer{$c}\n";
	}
}

my $best=$answer{'C'};
my $result='C';
for my $c (keys %answer) {
	next if ($c eq 'C');
	if ($answer{$c} > $best) {
		$best = $answer{$c};
		$result = $c;
	}
}
$result = 'N' if ($answer{'C'} == 0 and $answer{'U'} == 0 and $answer{'M'} == 0);
$result = 'N' if ($result eq 'N' or ($result ne 'U' and (abs($answer{'C'}) != 0 and abs($answer{'C'}-$answer{'M'})/abs($answer{'C'}) < 0.1)));
print "$result\n";

exit 0;

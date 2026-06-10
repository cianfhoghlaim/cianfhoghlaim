#!/usr/bin/perl

use strict;
use warnings;

if ($#ARGV != 1) {
	print "Usage: linecheck.pl ARG1 ARG2\nWhere ARG1 and ARG2 are of the form \"(YYY|YNY|YNN|YYN|NNY|NNN|ABAIRT|ABAIRT-CH)\"\n";
	exit 1;
}
binmode STDOUT, ":encoding(iso-8859-1)";
binmode STDERR, ":encoding(iso-8859-1)";
binmode STDIN, ":bytes";

my $foinse0="/snapshot/aimsigh/$ARGV[0]";
my $foinse1="/snapshot/aimsigh/$ARGV[1]";

my $tot=0;
opendir DIRH, $foinse0 or die "could not open $foinse0: $!\n";
foreach my $doctxt (readdir DIRH) {
	next if $doctxt !~ /\.txt$/;
	my $c1 = 0;
	my $c2 = 0;
	open (FIRST, "<", "$foinse0/$doctxt") or die "Could not open $doctxt in $foinse0\n";
	while (<FIRST>) {
		$c1++; # if m/^<DOC>$/;
	}
	close FIRST;
	open (SECOND, "<", "$foinse1/$doctxt") or die "Could not open $doctxt in $foinse1\n";
	while (<SECOND>) {
		$c2++; # if m/^<DOC>$/;
	}
	close SECOND;
	print "Problem with $doctxt ($c1,$c2)...\n" if ($c1 != $c2);
#	print "No problem with $doctxt ($c1,$c2)...\n" if ($c1 == $c2);
	$tot++;
}
closedir DIRH;
exit 0;

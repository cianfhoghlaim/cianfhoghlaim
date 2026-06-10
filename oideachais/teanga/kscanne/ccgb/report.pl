#!/usr/bin/perl

use strict;
use warnings;

my %SEAN;

die "Usage: $0 OLD NEW\n" unless ($#ARGV == 1);

open (OLD, $ARGV[0]) or die "Error opening old: $!\n";
while (<OLD>) {
	m/\|([^|]+)\|([^|]+)\|/;
	$SEAN{$1} = $2;
}
close OLD;
open (NEW, $ARGV[1]) or die "Error opening new: $!\n";
while (<NEW>) {
	m/\|([^|]+)\|([^|]+)\|/;
	print "$SEAN{$1} -> $2 (via \"$1\")\n" if (exists($SEAN{$1}));
}
close NEW;

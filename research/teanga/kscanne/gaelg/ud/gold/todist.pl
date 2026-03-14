#!/usr/bin/perl

use strict;
use warnings;
use utf8;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

# pipe in gold.tsv
# strips Irish from last column
# adds SpaceAfter=No when needed
my $currsent;
my $toskip = 0;
while (<STDIN>) {
	chomp;
	if (m/^# text = (.+)$/) {
		$currsent = $1;
		print "$_\n";
	}
	elsif (m/^#/ or m/^$/) {
		print "$_\n";
	}
	else {
		my @pieces = split(/\t/); 
		$pieces[9] = '_';  # was Irish translation
		if ($toskip > 0) {  # within a multiword token
			$toskip--;
		}
		else {
			my $tok = $pieces[1];  # surface token should match currsent!
			if (substr($currsent,0,length($tok)) eq $tok) {
				substr($currsent,0,length($tok),'');
				if ($currsent =~ m/^ / or $currsent eq '') {
					$currsent =~ s/^ +//;
				}
				else {
					$pieces[9] = 'SpaceAfter=No';
				}
			}
			else {
				print STDERR "Expected $tok at start of string: \"$currsent\"\n";
			}
			if ($pieces[0] =~ m/^([0-9]+)-([0-9]+)$/) {
				$toskip = 1 + $2 - $1;
			}
		}
		print join("\t", @pieces)."\n";
	}
}

exit 0;

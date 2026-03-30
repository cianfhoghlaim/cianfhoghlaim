#!/usr/bin/perl

## READS DUPELOG looking for candidate URLs for redirection
#  or scurf-cleanup

use strict;
use warnings;

sub longest_common_prefix {
	my $prefix = shift;
	for (@_) {
		chop $prefix while (! /^$prefix/);
	}
	return $prefix;
}

sub longest_common_suffix {
	(my $s1, my $s2) = @_;
	my $r1 = reverse $s1;
	my $r2 = reverse $s2;
	return reverse( longest_common_prefix($r1,$r2));
}


open (LOG, "<", "DUPELOG") or die "Could not open duplicate log: $!\n";

my $curr='';
my %hash;
while (<LOG>) {
	chomp;
	if (/^http/) {
		s/[?*+()]/./g;
		if ($curr) {
			my $lcs = longest_common_suffix($curr, $_);
			$lcs =~ s/^[^\/]*\///;
			if ($lcs) {
				$curr =~ s/$lcs$//;
				s/$lcs$//;
				my $sampla = join(' <-> ',sort($curr, $_));
#				print "$sampla\n";
				$hash{$sampla}++;
			}
			$curr = '';
		}
		else {
			$curr = $_;
		}
	}
}
close LOG;
print "$hash{$_} $_\n" foreach (sort {$hash{$b} <=> $hash{$a}} keys %hash);
exit 0;

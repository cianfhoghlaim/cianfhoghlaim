#!/usr/bin/perl

use strict;
use warnings;
use utf8;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

sub print_batch {
	(my $aref) = @_;
	for my $a (@{$aref}) {
		for my $b (@{$aref}) {
			next if ($a eq $b);
			print "$a $b\n";
		}
	}
}

my @curr;
while (<STDIN>) {
	chomp;
	if (m/^:/) {
		print_batch(\@curr) if ($. > 1);
		print "$_\n";
		@curr = ();
	}
	else {
		s/\t/ /;
		push @curr, $_;
	}
}
print_batch(\@curr);

exit 0;

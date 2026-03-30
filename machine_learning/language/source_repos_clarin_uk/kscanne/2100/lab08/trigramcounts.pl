#!/usr/bin/perl

use strict;
use warnings;
use utf8;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

my %table;
my $curr='';

while (<STDIN>) {
	while (m/(.)/g) {
		my $c = uc($1);
		if ($c =~ /^\p{L}$/ and $c =~ /^\p{Latin}$/) {
			$curr .= $c;
			if (length($curr) > 3) {
				$curr =~ s/^.//;
			}
			if (length($curr) == 3) {
				if (exists($table{$curr})) {
					$table{$curr} += 1;
				}
				else {
					$table{$curr} = 1;
				}
			}
		}
		else {
			$curr = '';
		}
	}
}

print scalar keys %table;
print "\n";
for my $c (sort keys %table) {
	print "\"$c\" ".$table{$c}."\n";
}

exit 0;

#!/usr/bin/perl

use strict;
use warnings;
use utf8;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

my %table;

while (<STDIN>) {
	while (m/(.)/g) {
		my $c = uc($1);
		if ($c =~ /^\p{L}$/ and $c =~ /^\p{Latin}$/) {
			if (exists($table{$c})) {
				$table{$c} += 1;
			}
			else {
				$table{$c} = 1;
			}
		}
	}
}

print scalar keys %table;
print "\n";
for my $c (sort keys %table) {
	print "\"$c\" ".$table{$c}."\n";
}

exit 0;

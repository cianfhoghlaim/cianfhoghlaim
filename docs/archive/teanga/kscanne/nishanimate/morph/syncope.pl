#!/usr/bin/perl

use strict;
use warnings;
use utf8;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

my $weak = 1;
while (<STDIN>) {
	chomp;
	(my $head, my $tail) = /^(.*[^aeiou])([aeio]+[^aeiou]*)$/i;
	while ($head =~ m/([aeio]*)([^aeiou]*)/gi) {
		my $v = $1;
		my $c = $2;
		if ($v =~ /^[aio]$/i) {
			print $v unless ($weak);
		}
		else {
			print $v;
			$weak = 0;
		}
		$weak = 1 - $weak;
		print $c;
	}
	print "$tail\n";
}

exit 0;

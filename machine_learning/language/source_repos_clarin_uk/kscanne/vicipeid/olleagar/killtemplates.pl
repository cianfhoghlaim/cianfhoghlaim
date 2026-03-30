#!/usr/bin/perl

use strict;
use warnings;
use utf8;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

while (<STDIN>) {
	chomp;
	my $op = '';
	my $curlydepth = 0;
	my $sgmldepth = 0;
	while (m/(.)/g) {
		my $c = $1;
		if ($c eq '{') {
			$curlydepth++;
		}
		elsif ($c eq '}') {
			$curlydepth--;
		}
		elsif ($c eq '<') {
			$sgmldepth++;
		}
		elsif ($c eq '>') {
			$sgmldepth--;
		}
		else {
			$op .= $c if ($curlydepth == 0 and $sgmldepth == 0);
		}
	}
	print "$op\n";
}

exit 0;

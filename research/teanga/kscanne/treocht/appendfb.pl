#!/usr/bin/perl

use strict;
use warnings;
use utf8;
use Date::Format;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

my $texttowrite='';
my $currentmonth='xx';
# pipe gaeilge/crubadan/fb/GA.txt through here, but sorted by the
# timestamp in increasing order (see build.sh)
while (<STDIN>) {
	chomp;
	(my $type, my $stamp, my $text) = m/^[0-9_]+\t([0-9_]+|URI)\t([0-9]+)\t[0-9]+\t[^\t]+\t(.*)$/;
	next if ($type eq 'URI');
	my $thisone = time2str("%Y-%m", $stamp, 'GMT');
	if ($thisone ne $currentmonth) {
		if ($texttowrite ne '') {
			open(MONTHLY, ">>:utf8", "corpas/$currentmonth") or die "Could not open corpas/$currentmonth: $!";
			print MONTHLY $texttowrite;
			close MONTHLY;
			$texttowrite = '';
		}
		$currentmonth = $thisone;
	}
	$text =~ s/\\n/\n/g;
	$texttowrite.="$text\n\n";
}

open(MONTHLY, ">>:utf8", "corpas/$currentmonth") or die "Could not open corpas/$currentmonth: $!";
print MONTHLY $texttowrite;
close MONTHLY;

exit 0;

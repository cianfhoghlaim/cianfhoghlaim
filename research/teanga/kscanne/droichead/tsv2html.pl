#!/usr/bin/perl

use strict;
use warnings;
use utf8;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

while (<STDIN>) {
	chomp;
	(my $fgb, my $pos, my $uid, my $edil) = split(/\t/);
	my $fgbprint = $fgb;
	$fgbprint =~ s/\^([0-9])/<sup>$1<\/sup>/;
	$fgbprint .= ", $pos" unless ($pos eq '');
	$fgb =~ s/[.^].*$//;
	print "<div class=\"entry\"><div class=\"fgb\"><a target=\"_blank\" href=\"http://www.teanglann.ie/ga/fgb/$fgb\">$fgbprint</a></div><div class=\"edil\"><a target=\"_blank\" href=\"http://www.dil.ie/$uid\">$edil</a></div></div>\n";
}

exit 0;

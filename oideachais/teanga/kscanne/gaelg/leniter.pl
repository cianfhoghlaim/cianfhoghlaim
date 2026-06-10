#!/usr/bin/perl

use strict;
use warnings;
use utf8;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

# see i.pl
sub lenite
{
    my ( $word ) = @_;
    $word =~ s/^[bm](w)?/v/;
    $word =~ s/^[BM](w)?/V/;
    $word =~ s/^[cç]h/h/;
    $word =~ s/^[CÇ]h/H/;
    $word =~ s/^[ck]([^h])/ch$1/;
    $word =~ s/^[CK]([^h])/Ch$1/;
    $word =~ s/^g([ei])/y$1/;
    $word =~ s/^G([ei])/Y$1/;
    $word =~ s/^g([^hi])/gh$1/;
    $word =~ s/^G([^hi])/Gh$1/;
    $word =~ s/^p([^h])/ph$1/;
    $word =~ s/^P([^h])/Ph$1/;
    $word =~ s/^qu/wh/;
    $word =~ s/^Qu/Wh/;
    $word =~ s/^sh?l/l/;
    $word =~ s/^Sh?l/L/;
    $word =~ s/^sn/n/;
    $word =~ s/^Sn/N/;
    $word =~ s/^str/hr/;
    $word =~ s/^Str/Hr/;
    $word =~ s/^sh?([aeiouy])/h$1/;
    $word =~ s/^Sh?([aeiouy])/H$1/;
    $word =~ s/^j/y/;
    $word =~ s/^J/Y/;
    $word =~ s/^th?/h/;
    $word =~ s/^Th?/H/;
    $word =~ s/^dh?/gh/;
    $word =~ s/^Dh?/Gh/;
    $word =~ s/^[Ff]//;
    return $word;
}

while (<STDIN>) {
	if (m/^(my|dty)_/) {
		s/^(my|dty)_([^ ]+)/"$1_".lenite($2)/e;
	}
	print;
}

exit 0;

#!/usr/bin/perl

# used in makefile; one arg is language code

use strict;
use warnings;
use Encode;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

my $langcode = $ARGV[0];

my %tags;

sub converter
{
	(my $word, my $code) = @_;
	my $tag = $tags{$code};
	my $ans = $tag.$word;
	$tag =~ s/<(.).*/<\/$1>/;
	$ans .= $tag;
	return $ans;
}

my $tagfile = "/home/kps/seal/idirlamha/$langcode/gramadoir-$langcode/pos-$langcode.txt";
$tagfile = "/home/kps/gaeilge/gramadoir/gr/$langcode/pos-$langcode.txt" if ($langcode eq 'ga');

open (POSTAGS, "<:bytes", $tagfile) or die "Could not open POS tags list for $langcode: $!\n";

while (<POSTAGS>) {
	my $curr = decode("iso-8859-1", $_);
	$curr =~ m/^([0-9]+)\s+(<[^>]+>)/;
	$tags{$1} = $2;
}

while (<STDIN>) {
	s/([^ ]+) ([0-9]+)/converter($1,$2)/eg;
	print;
}
exit 0;

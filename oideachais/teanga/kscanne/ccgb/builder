#!/usr/bin/perl
#   Used in makefile to make veicteoir.db
#
#   Not installed as part of package, only used for development
use strict;
use warnings;
use utf8;

use Lingua::GA::Gramadoir;

binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";
# compare gramadoir/gr/bin/abairti-utf and gram-xx.pl - 
# gramadoir module expects bytes even though those bytes are 
# actually a utf-8 stream - job on the "input_encoding" to convert to such
binmode STDIN, ":bytes";

# Irish tokenizer works sufficiently well on English sentences too
my $gr = new Lingua::GA::Gramadoir(input_encoding => 'utf-8');

my %alltokes;
my %stopwords;

open(STOPS, "<:utf8", 'stoplist') or die "Could not open stop word file.\n";
while (<STOPS>) {
	chomp;
	$stopwords{$_}++;
}
close STOPS;

while (<STDIN>) {
	chomp;
	my ( $tag, $sentence ) = m/^([^ ]+) (.*)$/;
	my $tokes = $gr->tokenize($sentence);
	foreach (@$tokes) {
		if (/../) {
			tr/A-ZÁÉÍÓÚ/a-záéíóú/;
			$alltokes{$_} .=" $tag" unless (exists($stopwords{$_}));
		}
	}
}

print "$_$alltokes{$_}\n" foreach (keys %alltokes);

#!/usr/bin/perl
# used to renumber file in case of tokenization changes;
# NB it's not clever enough to update head references when
# applied to gold.tsv

use strict;
use warnings;
use utf8;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

my $word = 1;
while (<STDIN>) {
	chomp;
	if (m/^#/) {
		print "$_\n";
	}
	elsif (m/^$/) {
		print "\n";
		$word = 1;
	}
	elsif (m/^([0-9]+)-([0-9]+)\t/) {   # multi-word token
		my $diff = $2 - $1;
		my $end = $word+$diff;
		my @fields = split(/\t/,$_,-1);
		$fields[0] = "$word-$end";
		print join("\t", @fields)."\n";
		# don't increment word!
	}
	else {   # typical token
		my @fields = split(/\t/,$_,-1);
		$fields[0] = $word;
		print join("\t", @fields)."\n";
		$word++;
	}
}

exit 0;

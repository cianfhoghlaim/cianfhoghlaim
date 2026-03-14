#!/usr/bin/perl

# see makefile; used to find articles with many HusseyBot edits

use strict;
use warnings;
use utf8;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

while (<STDIN>) {
	my $line = $_;
	my $c = () = $line =~ /HusseyBot/g;
	s/^<title>//;
	s/<\/title>.+/\t$c/;
	print;
}

exit 0;

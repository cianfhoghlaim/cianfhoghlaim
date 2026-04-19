#!/usr/bin/perl

use strict;
use warnings;
use utf8;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

my %map;
open(SPLIT, "<:utf8", "split.tsv") or die "Could not open split.tsv: $!";
while (<SPLIT>) {
	chomp;
	(my $sentid, my $dataset) = split(/\t/);
	$map{$sentid} = $dataset;
}
close SPLIT;

my @label = ('train','train','dev','test');
# pipe in a list of sent_id's
# assign proportionally to train/dev/test and output
# in form that can be appended to split.tsv
while (<STDIN>) {
	chomp;
	if (!exists($map{$_})) {
		my $choice = $label[int(rand(4))];
		print "$_\t$choice\n";
	}
}

exit 0;

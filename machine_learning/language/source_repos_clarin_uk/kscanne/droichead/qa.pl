#!/usr/bin/perl

use strict;
use warnings;
use utf8;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

my %poshash = (
	'nm' => 'fir',
	'nf' => 'bain',
	'a' => 'aid',
	'v' => 'br',
	's' => 'af',
	'adv' => 'db',
	'prep' => 'rf',
	'pref' => 'rm',
	'pron' => 'fa',
	'conj' => 'cón',
	'npl' => 'iol',
	'u' => '',
	'interr' => 'ceist',
	'excl' => 'int',
	'poss' => 'aid',
	'ord' => 'ord',
	'pronm' => '',
	'card' => 'uimh',
	'art' => 'alt',
);

open(DROICHEAD, "<:utf8", "droichead.tsv") or die "Could not open droichead.tsv: $!";
while (<DROICHEAD>) {
	chomp;
	my @pieces = split(/\t/);
	print "wrong number of fields on line $.\n" unless (scalar(@pieces)==5);
	(my $ig, my $fgb, my $pos, my $num, my $edil) = split(/\t/);
	my $igw = $ig;
	my $igpos = 'NONE';
	if ($igw =~ m/_(.*)$/) {
		$igpos = $1;
		$igw =~ s/_.*//;
	}
	print "bad eDIL ref on line $.: $num\n" unless ($num =~ m/^[1-9][0-9]*$/ and $num < 44000);
	print "weird eDIL headword on line $.: $edil\n" unless (length($edil)>0);
	print "unknown POS on line $.: $igpos\n" unless (exists($poshash{$igpos}) or $igpos eq 'NONE');
	print "POS strings don't match on line $.: $igpos vs $pos\n" unless ($igpos eq 'NONE' or (exists($poshash{$igpos}) and $poshash{$igpos} eq $pos));
	$fgb =~ s/[.^].*//;
	$igw =~ s/[0-9]$//;
	print "IG/FGB words don't match on line $.: $igw vs $fgb\n" unless ($fgb eq $igw or $fgb eq 'Luan');
	if ($pos eq '') {
		print "missing POS field on line $.: $ig\n" unless ($igpos eq 'u' or $igpos eq 'pronm' or $igw =~ m/ / or $igw =~ m/^-/);
	}
}
close DROICHEAD;

exit 0;

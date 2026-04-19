#!/usr/bin/perl

use strict;
use warnings;
use utf8;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

my $irish = $ARGV[0];

my %name2gv;
open(BOOKS, "<:utf8", "/home/kps/gaeilge/ga2gv/ga2gv/ud/bible/books.tsv") or die "could not open books.tsv: $!";
while (<BOOKS>) {
	chomp;
	(my $enabb, my $gaabb, my $ennm, my $gvnm) = split(/\t/);
	$name2gv{$gaabb} = $gvnm;
}
close BOOKS;

my $manx = $name2gv{$irish};
$manx =~ s/ /_/g;

my %gv2ga;
my %gv2en;
my %gv2verse;
open(THREEWAY, "<:utf8", "/home/kps/gaeilge/ga2gv/ga2gv/ud/bible/3way.txt") or die "Could not open 3way.txt: $!";
while (<THREEWAY>) {
	chomp;
	(my $gv, my $ga, my $en) = split(/\t/);
	(my $verse, my $gvrest) = $gv =~ m/^([0-9]+:[0-9]+): *(.+)$/;
	$gv = $gvrest;
	$ga =~ s/^[0-9]*:[0-9]*: *//;
	$en =~ s/^[0-9]*:[0-9]*: *//;
	$gv =~ s/ *$//;
	$ga =~ s/ *$//;
	$en =~ s/ *$//;
	$gv2ga{$gv} = $ga;
	$gv2en{$gv} = $en;
	$gv2verse{$gv} = $verse;
}
close THREEWAY;

my $sent = '';
my $toprint = 0;
while (<STDIN>) {
	chomp;
	if (m/^$/) {
		print "$sent\n" if ($toprint==1);
		$sent = '';
		$toprint = 0;
	}
	elsif (m/^# sent_id = /) {
		1;
	}
	elsif (m/^# text = (.+)$/) {
		my $full = $1;
		if (exists($gv2ga{$full})) {
			$toprint = 1;
			$sent .= "# sent_id = ${manx}-$gv2verse{$full}\n";
			$sent .= "$_\n";
			$sent .= "# text_en = $gv2en{$full}\n";
			$sent .= "# text_ga = $gv2ga{$full}\n";
		}
	}
	else {
		$sent .= "$_\n";
	}
}

exit 0;

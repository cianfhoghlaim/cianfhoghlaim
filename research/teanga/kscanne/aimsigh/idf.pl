#!/usr/bin/perl

# computes tfidf weightings for all terms in all files
#  Reads from FREQ directory, computes, and writes to
#  TFIDF directory -- see Jurafsky-Martin p.653 for details

use strict;
use warnings;

binmode STDOUT, ":encoding(iso-8859-1)";
binmode STDERR, ":encoding(iso-8859-1)";
binmode STDIN, ":bytes";

my $base='/snapshot/aimsigh/FREQ';
my $range = '/snapshot/aimsigh/TFIDF';
my %bighash;

# just sets up "bighash" global hash
sub read_all_tokens
{
	opendir DIRH, $base or die "could not open $base: $!\n";
	my $N=0;
	foreach my $doctxt (readdir DIRH) {
		next if $doctxt !~ /\.txt$/;
		$N++;
		print "$N..." if ($N % 100 == 0);
		open (FOINSE, "<", "$base/$doctxt") or die "Could not open source file $doctxt: $!\n";
		while (<FOINSE>) {
			chomp;
			s/ .*//;
			$bighash{$_}++;
		}
		close FOINSE;
	}
	closedir DIRH;
	print "Done reading token files; computing logs...\n";
	foreach (keys %bighash) {
		$bighash{$_} = log($N/$bighash{$_});
	}
}

sub do_one_file
{
	(my $foinse, my $sprioc) = @_;

	my %lilhash;
	open (FOINSE, "<", $foinse) or die "Could not open source file $foinse: $!\n";
	my $len = 0;
	while (<FOINSE>) {
		chomp;
		(my $w, my $freq) = /^([^ ]+) ([0-9]+)$/;
		my $temp = $freq*$bighash{$w};
		$lilhash{$w} = $temp;
		$len += ($temp*$temp);
	}
	close FOINSE;
	$len = sqrt($len);
	$lilhash{$_} /= $len foreach (keys %lilhash);

	open(OUTPUT, ">", $sprioc) or die "could not open output file in TFIDF: $!\n";
	print OUTPUT "$lilhash{$_} $_\n" foreach (sort {$lilhash{$b} <=> $lilhash{$a}} keys %lilhash);
	close OUTPUT;
}

sub tfidf_byqueue
{
	open (ANCIU, "<", "/usr/local/share/crubadan/ga/ANCIU") or die "could not open ANCIU: $!\n";
	while (<ANCIU>) {
		chomp;
		my $doctxt = "$_.txt";
		print "Computing tfidf for $doctxt (first time)...\n";
		do_one_file("$base/$doctxt", "$range/$doctxt");
	}
	close ANCIU;
}

sub tfidf_bytimestamp
{
	my $N=0;
	opendir DIRH, $base or die "could not open $base: $!\n";
	foreach my $doctxt (readdir DIRH) {
		next if $doctxt !~ /\.txt$/;
		my $foinse = "$base/$doctxt";
		my $sprioc = "$range/$doctxt";
		$N++;
		print "$N..." if ($N % 100 == 0);
		my $doit = 0;
		if (-e $sprioc) {
			my @stat1 = stat($foinse);
			my @stat2 = stat($sprioc);
			$doit = ($stat1[9] > $stat2[9]);
			print "Computing tfidf for $doctxt (out of date)...\n" if $doit;
		}
		else {
			$doit = 1;
			print "Computing tfidf for $doctxt (first time)...\n";
		}
		do_one_file($foinse, $sprioc) if ($doit);
	}
	closedir DIRH;
}

read_all_tokens();
print "Now rereading token files and computing tfidf...\n";
# tfidf_bytimestamp();
tfidf_byqueue();
exit 0;

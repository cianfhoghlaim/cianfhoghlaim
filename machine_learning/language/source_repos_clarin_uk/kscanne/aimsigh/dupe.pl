#!/usr/bin/perl

# reads in tfidf data for files and uses this to quickly
# find all duplicate pairs. 
# 
# Should only call this from makefile; "make killdupes"
#
# External output is placed in two files; one is 
# "dupescr" script containing the appropriate dockill commands,
# and the other is a "dupelog" that gets added on to the
# global log ./DUPELOG



use strict;
use warnings;

binmode STDOUT, ":encoding(iso-8859-1)";
binmode STDERR, ":encoding(iso-8859-1)";
binmode STDIN, ":bytes";

my $base='/snapshot/aimsigh/TFIDF';
my $dummy;
my $crubadan='/usr/local/share/crubadan/ga';
my %bighash;   # hash of hashes
my $N;
my $SPECIAL=10;       # number of unusual terms to index for each doc
my $VERYSPECIAL=4;    # how many among the most unusual terms must appear 
                      # among the SPECIAL terms of another doc for them
		      # to be treated as dupe candidates

open (TORTHAI, ">", "./dupescr") or die "Could not open script file dupescr: $!\n";
open (LOGCHOMHAD, ">", "./dupelog") or die "Could not open log file dupelog: $!\n";
print "Logs opened...\n";

sub make_a_decision
{
	(my $docnum, my $cand, my $cosine) = @_;
	if ($cosine > 0.999) {
		print "sim($docnum,$cand)=$cosine\n";
		print TORTHAI "dockill $cand\n";
		my $url1;
		my $url2;
		open (INFO, "<", "$crubadan/sonrai/$docnum.dat") or die "Could not open data file $docnum: $!\n";
		while (<INFO>) {
			chomp;
			if (m/^url: /) {
				$url1 = $_;
				$url1 =~ s/^url: //;
			}
		}
		close INFO;
		open (INFO2, "<", "$crubadan/sonrai/$cand.dat") or die "Could not open data file $cand: $!\n";
		while (<INFO2>) {
			chomp;
			if (m/^url: /) {
				$url2 = $_;
				$url2 =~ s/^url: //;
			}
		}
		close INFO2;
		print LOGCHOMHAD "$url1\n$url2\n\n";
	}
}

print "About to open MANIFEST...\n";
open (MANIFEST, "<", "$crubadan/MANIFEST") or die "Could not open MANIFEST: $!\n";
$dummy = <MANIFEST>;  # eat num. lines
print "Opened, numlines chomped, beginning to process tfidf files...\n";
while (<MANIFEST>) {
	chomp;
	(my $dummy, my $doctxt) = m/^([^ ]+) ([0-9]+\.txt)$/;
	(my $docnum) = $doctxt =~ /^([0-9]+)/;
	$N++;
	print "$N..." if ($N % 100 == 0);
	open (FOINSE, "<", "$base/$doctxt") or die "Could not open source file $doctxt: $!\n";
	for (1..$SPECIAL) {
		my $w = <FOINSE>;
		if (defined($w)) {  # in case of very short files!
			chomp $w;
			$w =~ s/^[^ ]+ //;
			$bighash{$w}->{$docnum}++;
		}
	}
	close FOINSE;
}
close MANIFEST;
print "Done reading top-tens from tfidf files...\n";
$N=0;
print "Now rereading document list and looking for dupes...\n";
# open (MANIFEST, "<", "$crubadan/MANIFEST") or die "Could not open MANIFEST: $!\n";
open (ANCIU, "<", "$crubadan/ANCIU") or die "Could not open doclist: $!\n";
#$dummy = <MANIFEST>;  # eat num. lines
#while (<MANIFEST>) {
while (<ANCIU>) {
	chomp;
#	(my $dummy, my $doctxt) = m/^([^ ]+) ([0-9]+\.txt)$/;
	my $doctxt = "$_.txt";
	$N++;
	print "$N..." if ($N % 100 == 0);
	my $docnum = $doctxt;
	$docnum =~ s/\.txt//;
	my %tfidf;
	my %cands;
	my @todo;
	open (FOINSE, "<", "$base/$doctxt") or die "Could not open source file $doctxt: $!\n";
	for (1..$VERYSPECIAL) {
		my $line = <FOINSE>;
		if (defined $line) {  # VERY short token list
			chomp $line;
			$line =~ /^([^ ]+) (.*)$/;
			my $w = $2;
			$tfidf{$w} = $1;
			$cands{$_}++ foreach (keys %{$bighash{$w}});
		}
	}
	foreach (keys %cands) {
		push @todo, $_ if ($cands{$_}==$VERYSPECIAL and $docnum < $_);
	}
	if (scalar @todo > 0) {
		while (<FOINSE>) {
			chomp;
			/^([^ ]+) (.*)$/;
			$tfidf{$2} = $1;
		}
		foreach my $cand (@todo) {
			open (FOINSEEILE, "<", "$base/$cand.txt") or die "Could not open source file $cand: $!\n";
			my $cosine=0;
			while (<FOINSEEILE>) {
				chomp;
				(my $val, my $w) = /^([^ ]+) (.*)$/;
				$cosine += $val*($tfidf{$w}) if (exists($tfidf{$w}));
			}
			close FOINSEEILE;
			make_a_decision($docnum, $cand, $cosine);
		}
	}
	close FOINSE;
}
#close MANIFEST;
close ANCIU;
print TORTHAI "togail ga cman\n";
close TORTHAI;
close LOGCHOMHAD;

exit 0;

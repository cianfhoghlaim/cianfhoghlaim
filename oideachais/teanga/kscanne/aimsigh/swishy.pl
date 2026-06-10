#!/usr/bin/perl

use strict;
use warnings;
use Lingua::GA::Stemmer;  # for TEIDIL

# reads a list of docId's on stdin that have been sorted by PageRank
my $base="/snapshot/aimsigh/$ARGV[0]";
my $ext='txt';
my $obj;
if ($ARGV[0] eq 'TEIDIL') {
	$base="/usr/local/share/crubadan/ga/sonrai";
	$ext='dat';
	$obj = new Lingua::GA::Stemmer;
}
my $count=100000;
while (<STDIN>) {
	chomp;
	my $docId=$_;
	my $doc='';
	open (FOINSE, "<", "$base/$docId.$ext") or die "Could not open $docId: $!\n";
	if ($ARGV[0] eq 'TEIDIL') {
		while (<FOINSE>) {
			if (/^title: /) {
				chomp;
				($doc) = m/^title: (.*)$/;
				if ($doc eq 'Gan teideal') {
					$doc = '';
				}
				else {
					my $tokes = $obj->tokenize($doc);
					$doc='';
					foreach my $toke (@$tokes) {
						$doc .= $obj->tolower($toke)." ";
					}
					$doc =~ s/^(([^ ]+ +){7}).*$/$1/;
				}
			}
		}
	}
	else {
		my $dum=<FOINSE>;   # <DOC>
		$dum=<FOINSE>;      # <DOCNO>...
		while (<FOINSE>) {
			$doc .= $_ unless /^<\/DOC>$/;
		}
	}
	close FOINSE;
	my $size = length $doc;
	if ($size > 0) {
		print "Path-Name: $count-$docId\n";
		print "Content-Length: $size\n";
		print "Document-Type: TXT*\n";
		print "\n";
		print $doc;
		$count++;
	}
}
exit 0;

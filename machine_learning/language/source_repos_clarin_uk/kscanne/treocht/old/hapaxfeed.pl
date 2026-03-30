#!/usr/bin/perl

use strict;
use warnings;
use utf8;
use XML::Feed;
use Encode;
use Unicode::Normalize;
use HTML::Entities;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

my %seen;
open(SEEN, "<:utf8", "seenonline.txt") or die "Could not open seenonline: $!";
while (<SEEN>) {
	chomp;
	$seen{$_} = 1;   # comment out this line if we want to keep everything!
}
close SEEN;

sub demutate {
	(my $w) = @_;
	for ($w) {
		s/^[nt]-//;
		s/^[nt]([AEIOUÁÉÍÓÚ])/$1/;
		s/^[mdbns][’'](.)/$1/;
		s/^h-?([aeiouáéíóúAEIOUÁÉÍÓÚ])/$1/;
		s/^m([Bb])/$1/;
		s/^g([Cc])/$1/;
		s/^n([DdGg])/$1/;
		s/^bh([Ff])/$1/;
		s/^b([Pp])/$1/;
		s/^t([Ss])/$1/;
		s/^d([Tt])/$1/;
		s/^([bBcCdDfFgGmMpPSsTt])h/$1/;
	}
	return $w;
}

sub html2text {
	(my $t) = @_;
	for ($t) {
		s/<hr[^>]*>/\n\n------------------------------------------\n\n/gi;
		s/<tr[^>]*>/\n/gi;
		s/<br *[\/]?> *\n/\n/gi;
		s/<br *[\/]?>/\n/gi;
		s/<p[^>]*>/\n\n/gi;
		s/<li[^>]*>/\n\n * /gi;
		s/<[^>]+>//g;
		s/http[^ ]+//g;
	}
	return decode_entities($t);
}

my %map;

# arg is full pathname of the XML file
my $blog = $ARGV[0];
my $feed = XML::Feed->parse($blog) or die XML::Feed->errstr;
for my $entry ($feed->entries) {
	my $issuedate = $entry->issued->ymd;
	$issuedate =~ s/-[0-9][0-9]$//;
	my $html;
	if (defined($entry->content->body)) {
		if (utf8::is_utf8($entry->content->body)) {
			$html = NFC($entry->content->body);
		}
		else {
			$html = NFC(Encode::decode("utf8", $entry->content->body));
		}
	}
	elsif (defined($entry->summary->body)) {
		$html = NFC(Encode::decode("utf8", $entry->summary->body));
		#$html = NFC($entry->summary->body);
	}
	else {
		1; 
		$html = '';
		#$html = 'No content or summary';
		# just ignore
	}
	if ($html ne '') {
		my $txt = html2text($html);
		# don't bother with aposts since demutating anyway
		while ($txt =~ m/((\p{L}|[0-9-])+)/g) {
			my $w = $1;
			$w =~ s/^-+//;
			$w =~ s/-+$//;
			$w = demutate($w);
			next if ($w eq '' or length($w)>40 or exists($seen{$w}));
			next unless ($w =~ m/\p{L}/);
			if (exists($map{$w})) {
				$map{$w} = $issuedate if ($issuedate lt $map{$w});
			}
			else {
				$map{$w} = $issuedate;
			}
		}
	}
}

for my $k (sort { $a cmp $b } keys %map) {
	print "$k\t$map{$k}\n";
}
exit 0;

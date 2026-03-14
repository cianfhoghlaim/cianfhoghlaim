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
		open(MONTHLY, ">>:utf8", "corpas/$issuedate") or die "Could not open file corpas/$issuedate: $!";
		print MONTHLY "\n\n\n";
		print MONTHLY html2text($html);
		print MONTHLY "\n\n\n";
		close MONTHLY;
	}
}
exit 0;

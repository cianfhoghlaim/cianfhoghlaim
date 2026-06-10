#!/usr/bin/perl

use strict;
use warnings;
use utf8;
use Date::Format;
use HTML::Entities;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

# store the first tweetid in each month as the key
# and the month 20xx-yy as the value
my %stamp;

my $currmonth = 'xxx';
open(TIMESTAMPS, "<:utf8", "/home/kps/gaeilge/crubadan/twitter/times/ga-stamps.txt") or die "Could not open ga-stamps.txt: $!";
while (<TIMESTAMPS>) {
	chomp;
	(my $tweetid, my $epoch) = m/^([0-9]+) ([0-9]+)$/;
	my $thisone = time2str("%Y-%m", $epoch, 'GMT');
	if ($thisone ne $currmonth) {
		$stamp{$tweetid} = $thisone;
		$currmonth = $thisone;
	}
}
close TIMESTAMPS;

my $texttowrite='';
$currmonth = '2007-04';  # hardcoded date of first tweet in ga-tweet.txt

# pipe sonrai/ga-tweets.txt through here
# Note that it doesn't write to the final month in the file,
# so good to run this at the beginning of the month after latest IT crawl
while (<STDIN>) {
	chomp;
	(my $tid, my $uid, my $text) = m/^([0-9]+)\t([0-9]+)\t(.*)$/;
	if (exists($stamp{$tid})) {  # first tweet of a new month
		if ($texttowrite ne '') {
			open(MONTHLY, ">>:utf8", "corpas/$currmonth") or die "Could not open corpas/$currmonth: $!";
			print MONTHLY $texttowrite;
			close MONTHLY;
			$texttowrite = '';
		}
		$currmonth = $stamp{$tid};
	}
	$texttowrite.=decode_entities($text)."\n\n" unless ($text =~ m/^RT/);
}

exit 0;

#!/usr/bin/perl
# picks out the sentences from parsed.conllu that have been marked
# with a + in sent_id, for inclusion in main UD corpus for Manx

use strict;
use warnings;
use utf8;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

my $currsent='';
my $print_p = 0;
while (<STDIN>) {
	chomp;
	if (m/^# newpar/) {
		1;
	}
	elsif (m/^# sent_id = (.+)$/) {
		my $sentid = $1;
		if ($sentid =~ m/[+]$/) {
			$print_p = 1;
			$sentid =~ s/[+]$//;
			$currsent .= "# sent_id = usage_$sentid\n";
		}
		else {
			$print_p = 0;
		}
	}
	elsif (m/^$/) {
		print "$currsent\n" if ($print_p==1);
		$print_p = 0;
		$currsent='';
	}
	else {
		s/SpacesAfter=.*/_/;
		$currsent .= "$_\n";
	}
}

exit 0;

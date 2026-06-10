#!/usr/bin/perl

use strict;
use warnings;
use utf8;
use Encode qw(decode);
use URI::Escape;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

my $ainm;
# set to one if we want table rows to highlight on mouseover (web only)
my $mouseover = 0;

my $verystart = 1;
my $sectionstart = 1;
my $subsectionstart = 1;
my $has_subsections = 0;
my $accordion = 0;
my %seen;
my $rowattrs='';

$rowattrs = " bgcolor=\"#FFFFFF\" onMouseOver=\"this.bgColor='F0F0F0';\" onMouseOut=\"this.bgColor='#FFFFFF';\"" if $mouseover;

chomp($ainm = <STDIN>);
print '<ul id="acc0" class="ui-accordion-container">'."\n";
while (<STDIN>) {
	chomp;
	my $line = $_;
	next if ($line eq '');
	last if ($line eq '<EOF>');
	if ($line =~ m/^\*\*/) {  # subheading
		$line =~ s/^[*]+//;
		$line =~ s/^([^|]+)\|(.+)$/$2 | $1/;
		if ($sectionstart) {
			$accordion++;
			print "<ul class=\"ui-accordion-container\" id=\"acc$accordion\">\n";
		}
		else {
			print "</table></div></li>\n";
		}
		print "<li>\n<div class=\"ui-accordion-left\"></div>\n<a class=\"ui-accordion-link acc$accordion\">$line<span class=\"ui-accordion-right\"></span></a>\n<div>\n";
		$sectionstart = 0;
		$subsectionstart = 1;
		$has_subsections = 1;
	}
	elsif ($line =~ m/^\*/) {  # top-level heading
		$line =~ s/^[*]+//;
		$line =~ s/^([^|]+)\|(.+)$/$2 | $1/;
		if ($has_subsections) {
			print "</table></div></li></ul></div></li>\n";
		}
		else {
			print "</table></div></li>\n" unless $verystart;
		}
		print '<li><div class="ui-accordion-left"></div><a class="ui-accordion-link acc0">'."$line".'<span class="ui-accordion-right"></span></a><div>';
		$verystart = 0;
		$sectionstart = 1;
		$subsectionstart = 1;
		$has_subsections = 0;
	}
	else {
		if ($line =~ m/\|/) {
			(my $bearla, my $duchas) = $line =~ m/^(.+)\|(.+)$/;
			my $normalized  = $duchas;
			$normalized =~ s/\P{L}//g;
			if (exists($seen{$normalized})) {
				print STDERR "Warning ($ainm): msg already seen: $duchas\n";
			}
			else {
				$seen{$normalized} = 1;
			}
			# 14 = length(" #tweet2learn ")
			if (length($duchas) + 14 + length($ainm) > 140) {
				print STDERR "Warning ($ainm): msg too long: $duchas\n";
			}
			my $encoded = uri_escape_utf8($duchas);
			print "<table>" if $subsectionstart;
			# can append &via=IndigenousTweet to the URL, optionally
			print "<tr$rowattrs><td><a href=\"https://twitter.com/intent/tweet?text=$encoded&hashtags=tweet2learn,$ainm\"><span class=\"duchas\">$duchas</span><br/><span class=\"bearla\">$bearla</span></a></td></tr>\n";
			#print "<tr$rowattrs><td><a href=\"twitter://post?message=$encoded%20tweet2learn%20$ainm\"><span class=\"duchas\">$duchas</span><br/><span class=\"bearla\">$bearla</span></a></td></tr>\n";
			$sectionstart = 0;
			$subsectionstart = 0;
		}
		else {
			print STDERR "Warning ($ainm): non-empty, non-heading line without a |\n";
		}
	}
}
if ($has_subsections) {
	print "</table></div></li></ul></div></li>\n";
}
else {
	print "</table></div></li>\n";
}
print "</ul>\n";

exit 0;

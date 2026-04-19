#!/usr/bin/perl

use strict;
use warnings;
use utf8;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

# f(4,7) = 4
# f(7,4) = 4
# f(-1,5) = 5
# f(3,-1) = 3
# f(-1,-1) = -1
sub min_not_minusone {
	(my $a, my $b) = @_;
	return $b if ($a==-1 or $b<=$a);
	return $a if ($b==-1 or $a<=$b);
}

sub kill_images_and_cats {
	(my $s) = @_;
	my $pos = -1;
	while (1) {
		my $filepos = index($s, '[[File', $pos+1);
		my $iomhapos = index($s, '[[Íomhá', $pos+1);
		my $catpos = index($s, '[[Catagóir:', $pos+1);
		my $start = min_not_minusone($filepos, $iomhapos);
		$start = min_not_minusone($start, $catpos);
		last if ($start==-1);
		$pos = $start+2;
		my $depth = 2;
		my $slen = length($s);
		while ($depth!=0 and $pos<$slen) {
			my $c = substr($s,$pos,1);	
			$depth++ if ($c eq '[');
			$depth-- if ($c eq ']');
			$pos++;
		}
		substr($s, $start, $pos-$start) = "";
		$pos = $start-1;
	}
	return $s;
}

sub cleanup {
	(my $s) = @_;
	$s = kill_images_and_cats($s);  # already stripped from ga-full???
	return $s;
}

while (<STDIN>) {
	chomp;
	(my $title, my $text) = split(/\t/);
	my $plain = cleanup($text);
	print "$title\t$plain\n";
}

exit 0;

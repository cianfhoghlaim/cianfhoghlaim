#!/usr/bin/perl

use strict;
use warnings;
use utf8;
use Text::Diff;
use HTML::Entities;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

sub usage {
	print "Usage: cat bigdiffsfile.xml | perl parse.pl [-d|-p]\n";
	print "         -d: report on grammatical fixes\n";
	print "         -p: for primemovers.tsv in makefile\n";
	exit(1);
}

usage() if ($#ARGV != 0);
my $mode=-1;
$mode = 0 if ($ARGV[0] eq '-d');
$mode = 1 if ($ARGV[0] eq '-p');
usage() if ($mode==-1);

# don't consider diff at all if byte difference between revisions 
# is bigger than this...
my $cutoff = 100;
# don't report prime mover if page length is less than this...
#my $shortarticle = 1500;
my $shortarticle = 0;

# global state in XML
my $currpage=undef;
my $curruser=undef;
my $currrev=undef;
my $currlen=undef;
my $prevrev=undef;
my $prevlen=undef;
my $userhref={};
my $in_text_p = 0;
my $skipping_p = 0;  # skipping this revision entirely?
my $skip_page_p = 0;  # skip all revisions for this page?

sub mymin {
	(my $a, my $b, my $c) = @_;
	my $ans = $a;
	$ans = $b if ($b < $ans);
	$ans = $c if ($c < $ans);
	return $ans;
}	

# symmetric except that pruning is based on
# length of the "before" string (1st arg)
sub edit_distance {
	(my $b, my $a, my $cutoff) = @_;
	my $m = length($a);
	my $n = length($b);
	return 10000 if (abs($m-$n) > $cutoff);
	my %d;
	for (my $i=0; $i<=$m; $i++) {
		$d{"$i,0"} = $i;
	}
	for (my $j=1; $j<=$n; $j++) {
		$d{"0,$j"} = $j;
	}
	for (my $i=1; $i<=$m; $i++) {
		my $alet = substr($a,$i-1,1);
		my $down = $i-1;
		my $rowmin = $d{"$i,0"};
		for (my $j=1; $j<=$n; $j++) {
			my $left = $j-1;
			if ($alet eq substr($b,$j-1,1)) {
				$d{"$i,$j"} = $d{"$down,$left"};
			}
			else {
				$d{"$i,$j"} = 1+mymin($d{"$down,$j"},$d{"$i,$left"},$d{"$down,$left"});
			}
			$rowmin = $d{"$i,$j"} if ($d{"$i,$j"} < $rowmin);
		}
		return 10000 if ($rowmin > $cutoff);
	}
	return $d{"$m,$n"};
}

# assume we've applied toasciilower
sub stripmutation {
	(my $s) = @_;
	$s =~ s/^[nt]-([aeiou])/$1/;
	$s =~ s/^h-?([aeiou])/$1/;
	$s =~ s/^mb/b/;
	$s =~ s/^gc/c/;
	$s =~ s/^n([dg])/$1/;
	$s =~ s/^bhf/f/;
	$s =~ s/^bp/p/;
	$s =~ s/^t-?s/s/;
	$s =~ s/^dt/t/;
	$s =~ s/^([bcdfgmpst])h/$1/;
	return $s;
}

sub toasciilower {
	(my $s) = @_;
	$s =~ s/^([nt])([AEIOUÁÉÍÓÚ])/$1-$2/;
	$s = lc($s);
	$s =~ s/[áà]/a/g;
	$s =~ s/[éè]/e/g;
	$s =~ s/[íì]/i/g;
	$s =~ s/[óò]/o/g;
	$s =~ s/[úù]/u/g;
	return $s;
}

sub normalize {
	(my $s) = @_;
	return stripmutation(toasciilower($s));
}

sub replacement2json {
	(my $r, my $ctxt) = @_;
	(my $b, my $a) = $r =~ m/^(.*) -> (.*)$/;
	my $edd = edit_distance($b,$a,10000);
	$a =~ s/  *$//;
	$a =~ s/"/\\"/g;
	$b =~ s/  *$//;
	$b =~ s/"/\\"/g;
	$ctxt =~ s/"/\\"/g;
	return "{\"before\": \"$b\", \"after\": \"$a\", \"distance\": $edd, \"context\": \"$ctxt\", \"user\": \"$curruser\"}";
}

# as a function of the length of the "before" string;
# Same settings as Google paper
# Using the Web for Language Independent Spellchecking and Autocorrection 
sub edit_cutoff {
	(my $beforelen) = @_;
	return 1 if ($beforelen <= 4);
	return 2 if ($beforelen <= 12);
	return 3;
}

sub interesting_to_me {
	(my $b, my $a) = @_;
	return 0 unless ($b =~ m/\p{L}/ and $a =~ m/\p{L}/);
	my $anorm = normalize($a);
	my $bnorm = normalize($b);
	my $ed_cutoff = edit_cutoff(length($bnorm));
	my $ed_dist = edit_distance($bnorm,$anorm,$ed_cutoff);
	return ($ed_dist <= $ed_cutoff);
}

sub processdiff {
	(my $d) = @_;
	my @ans;
	my @lines = split(/\n/,$d);
	my $beforectxt='';
	my $afterctxt='';
	my $before='';
	my $after='';
	my @replacements;
	for my $line (@lines) {
		if ($line =~ m/^@@ /) {
			# in case previous hunk ended with a +/-
			if ($before ne '' or $after ne '') {
				$before =~ s/ $//;
				$after =~ s/ $//;
				push @replacements, "$before -> $after" if (interesting_to_me($before,$after));
				$before = '';
				$after = '';
			}
			for my $r (@replacements) {
				push @ans, replacement2json($r, $beforectxt);
			}
			@replacements = ();
			$beforectxt = '';
			$afterctxt = '';
			$before = '';
			$after = '';
		}
		elsif ($line =~ m/^-(.+)$/) {
			my $word = $1;
			#$beforectxt .= '<<<' if ($before eq '');
			$beforectxt .= "$word ";
			$before .= "$word ";
		}
		elsif ($line =~ m/^[+](.+)$/) {
			my $word = $1;
			$afterctxt .= "$word ";
			$after .= "$word ";
		}
		elsif ($line =~ m/^ (.+)$/) {
			my $word = $1;
			if ($before ne '' or $after ne '') {
				#$beforectxt .= '>>>';
				$before =~ s/ $//;
				$after =~ s/ $//;
				push @replacements, "$before -> $after" if (interesting_to_me($before,$after));
				$before = '';
				$after = '';
			}
			$beforectxt .= "$word ";
			$afterctxt .= "$word ";
		}
		else {
			1;
			#print STDERR "WARNING: malformed line in diff: $d\n";
		}
	}
	for my $r (@replacements) {  # flush remaining
		push @ans, replacement2json($r, $beforectxt);
	}
	return undef if scalar(@ans)==0;
	return join(",\n", @ans).",\n";
}

sub skip_it_p {
	return 1 if !defined($prevlen);
	return (abs($currlen - $prevlen) > $cutoff);
}

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

sub kill_images {
	(my $s) = @_;
	my $pos = -1;
	while (1) {
		my $filepos = index($s, '[[File', $pos+1);
		my $iomhapos = index($s, '[[Íomhá', $pos+1);
		my $start = min_not_minusone($filepos, $iomhapos);
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

sub kill_templates {
	(my $s) = @_;
	my $depth = 0;
	my $ans = '';
	while ($s =~ m/(.)/gs) {
		my $c = $1;
		$depth++ if ($c eq '{');
		$depth-- if ($c eq '}');
		$ans .= $c if ($depth==0 and $c ne '}');
	}
	return $ans;
}

# takes wikitext and converts &amp; -> &, 
# [[Meiriceá]] to Meiriceá and [[Meiriceá|Mheiriceá]] to "Mheiriceá"
sub cleanup {
	(my $s) = @_;
	$s = decode_entities($s);
	$s = kill_templates($s);
	$s = kill_images($s);
	$s =~ s/\[\[[^\[\]]+\|([^|\[\]]*)\]\]/$1/g;
	$s =~ s/\[\[[^\[\]]+\|([^|\[\]]*)\]\]/$1/g;  # again, for nested links
	$s =~ s/\[\[([^\]]*)\]\]/$1/g;
	return $s;
}

# takes a string, and outputs a string with one token per line
sub tokenize {
	(my $s) = @_;
	my $ans = '';
	while ($s =~ m/((http[^ ]+|\p{P}|(\p{N}|\p{L}|\p{M}|[ʼ’'-])+))/g) {
		my $tok = $1;
		while ($tok =~ m/^([ʼ’'-])/) {
			$ans .= "$1\n";
			$tok =~ s/^.//;
		}
		if ($tok =~ m/^(.+?)([ʼ’'-]+)$/) {
			$ans .= "$1\n";
			my $tail = $2;
			while ($tail =~ m/^([ʼ’'-])/) {
				$ans .= "$1\n";
				$tail =~ s/^.//;
			}
		}
		else {
			$ans .= "$tok\n" if length($tok)>0;
		}
	}
	return $ans;
}

sub increment_contribution {
	return unless(defined($curruser));
	my $delta = $currlen;
	$delta -= $prevlen if defined($prevlen);
	$delta = 0 if ($delta < 0);
	if (!exists($userhref->{$curruser})) {
		$userhref->{$curruser} = $delta;
	}
	else {
		$userhref->{$curruser} += $delta;
	}
}

sub dodiff {
	(my $prev, my $curr) = @_;
	my $prevtok = tokenize(cleanup($prev));
	my $currtok = tokenize(cleanup($curr));
	my $diff = diff \$prevtok, \$currtok, { CONTEXT => 4 };
	#print $diff;
	$diff = processdiff($diff);
	if (defined($diff)) {
		#print "  revision by $curruser; ".length($prev).'->'.length($curr)."\n";
		print $diff;
	}
}

sub process_userhref {
	return unless(defined($currpage) and $skip_page_p==0 and $currlen>$shortarticle);
	my $maindriver = undef;
	my $bytesadded = -1;
	for my $u (keys %{$userhref}) {
		if ($userhref->{$u} > $bytesadded) {
			$bytesadded = $userhref->{$u};
			$maindriver = $u;
		}
	}
	if (defined($maindriver)) {
		print $currpage."\t".$maindriver."\n";
	}
	else {
		print STDERR "WARNING: no main driver for $currpage\n";
	}
}

my %nahusaid;
open(INPF, "<:utf8", "nahusaid.txt") or die "Could not open nahusaid.txt: $!";
while (<INPF>) {
	chomp;
	$nahusaid{$_} = 1;
}
close INPF;

while (<STDIN>) {
	chomp;
	if (m/<page>/ or m/<\/page>/) {
		process_userhref() if ($mode==1);
		$currpage = undef;
		$curruser=undef;
		$currrev=undef;
		$currlen=undef;
		$prevrev=undef;
		$prevlen=undef;
		%{$userhref} = ();
		$skipping_p = 0;
		$skip_page_p = 0;
	}
	elsif (m/<title>([^<]*)<\/title>/) {
		$currpage = $1;
		$currpage = decode_entities($currpage);
		$curruser=undef;
		$currrev=undef;
		$currlen=undef;
		$prevrev=undef;
		$prevlen=undef;
		%{$userhref} = ();
		if ($currpage =~ m/^(Catagóir:|Plé[ :]|Teimpléad:|Úsáideoir:|Íomhá:|Vicipéid:|Module:|MediaWiki:|VP:)/) {
			$skip_page_p = 1;
		}
		else {
			$skip_page_p = 0;
			#print "PAGE: $currpage\n";
		}
	}
	elsif (!$skip_page_p) {
		if (m/<revision>/) {
			$curruser=undef;
			$skipping_p = 0;
		}
		elsif (m/<username>([^<]*)<\/username>/) {
			$curruser=$1;
			if (exists($nahusaid{$curruser}) or ($curruser =~ m/bot/i and $curruser ne 'HusseyBot')) {
				$skipping_p = 1;
			}
		}
		elsif (m/<ip>([^<]*)<\/ip>/) {
			$curruser=$1;
		}
		elsif (m/<text bytes="([0-9]+)"[^>]*>([^<]*)<\/text>/) {
			if (defined($currrev)) {
				$prevrev = $currrev;
				$prevlen = $currlen;
			}
			$currrev=$2;
			$currlen=$1;
			increment_contribution();
			$skipping_p |= skip_it_p();
			if ($skipping_p) {
				$skipping_p = 0;
			}
			else {
				dodiff($prevrev, $currrev) if ($mode==0 and defined($curruser));
			}
			$in_text_p = 0;
		}
		elsif (m/<text bytes="([0-9]+)"[^>]*>(.*)$/) {
			if (defined($currrev)) {
				$prevrev = $currrev;
				$prevlen = $currlen;
			}
			$currrev=$2;
			$currlen=$1;
			increment_contribution();
			$in_text_p = 1;
			$skipping_p |= skip_it_p();
		}
		elsif (m/^(.*)<\/text>/) {
			$currrev .= "$1\n";
			if ($skipping_p) {
				$skipping_p = 0;
			}
			else {
				dodiff($prevrev, $currrev) if ($mode==0 and defined($curruser));
			}
			$in_text_p = 0;
		}
		elsif ($in_text_p == 1) {
			$currrev .= "$_\n";
		}
	}
}

exit 0;

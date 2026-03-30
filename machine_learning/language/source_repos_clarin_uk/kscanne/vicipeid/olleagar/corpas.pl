#!/usr/bin/perl
# Used to generate a corpus from white-listed editors

use strict;
use warnings;
use utf8;
use HTML::Entities;
use URI::Encode qw(uri_encode uri_decode);

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

# >>>> SET THIS TO 1 FOR A SOMEWHAT BIGGER CORPUS <<<<
my $include_more_p = 0;
# >>>> SET THIS TO 1 TO KEEP EVERYTHING <<<<
my $include_all_p = 0;

my %morepeople;
$morepeople{'AdamLibh'} = 1;
$morepeople{'DaithíÓ'} = 1;
$morepeople{'Darren J. Prior'} = 1;
$morepeople{'Erigena'} = 1;
$morepeople{'Ériugena'} = 1;
$morepeople{'MacCambridge'} = 1;
$morepeople{'Marcas.oduinn'} = 1;
$morepeople{'Nmacu'} = 1;

my %ok;
if ($include_more_p) {
	for my $u (keys %morepeople) {
		$ok{$u} = 1;
	}
}

$ok{'Antóin'} = 1;
$ok{'Antóin II'} = 1;
$ok{'Cathalpeelo'} = 1;
$ok{'Cmconraoi'} = 1;
$ok{'Colin Ryan'} = 1;
$ok{'Daithimac'} = 1;
$ok{'Dowlinme'} = 1;
$ok{'Eomurchadha'} = 1;
$ok{'Felo de Me'} = 1;
$ok{'Goll Mac Mórna'} = 1;
$ok{'Kevin Scannell'} = 1;
$ok{'Panu Petteri Höglund'} = 1;
$ok{'Rí na Vicipéide'} = 1;
$ok{'Rob Lindsey~gawiki'} = 1;
$ok{'Seananoc'} = 1;
$ok{'SeoMac'} = 1;
$ok{'TGcoa'} = 1;


my %primemover;
open(PRIME, "<:utf8", "../diffs/primemovers.tsv") or die;
while (<PRIME>) {
	chomp;
	(my $title, my $author) = split(/\t/);
	$primemover{$title} = $author;
}
close PRIME;

sub encode_entities_soft {
	(my $s) = @_;
	$s =~ s/&/\&amp;/g;
	$s =~ s/"/\&quot;/g;
	return $s;
}

sub string2json {
	(my $s) = @_;
	$s =~ s/\n/\\n/g;
	$s =~ s/"/\\"/g;
	return $s;
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

sub kill_tail {
	(my $s) = @_;
	$s =~ s/== *(Tagairtí|Féach freisin|Nótaí|Naisc sheachtracha) *==.*$//is;
	$s =~ s/[{][{]reflist.*$//is;
	$s =~ s/Catagóir:.*$//is;
	return $s;
}

# kills from first to last and everything in between if there are multiple
sub kill_galleries_and_refs {
	(my $s) = @_;
	$s =~ s/<gallery.+<\/gallery>//isg;
	$s =~ s/<ref[^<]+<\/ref>//isg;
	return $s;
}

# takes wikitext and converts &amp; -> &, 
# [[Meiriceá]] to Meiriceá and [[Meiriceá|Mheiriceá]] to "Mheiriceá"
sub cleanup {
	(my $s) = @_;
	$s = decode_entities($s);
	$s = kill_templates($s);
	$s = kill_images_and_cats($s);  # already stripped from ga-full???
	$s = kill_galleries_and_refs($s);
	$s = kill_tail($s);
	$s =~ s/\[\[[^\[\]]+\|([^|\[\]]*)\]\]/$1/g;
	$s =~ s/\[\[[^\[\]]+\|([^|\[\]]*)\]\]/$1/g;  # again, for nested links
	$s =~ s/\[\[([^\]]*)\]\]/$1/g;
	$s =~ s/''+//g;
	$s =~ s/(==+)([^=\n]+)\g1/\n\n$1$2$1\n/g;
	$s =~ s/<[^>]*>//g;
	$s =~ s/ [*]/\n*/g;
	$s =~ s/^ +//;
	$s =~ s/ +$//;
	return $s;
}

my $tooshort = 0;
my $notwhitelisted = 0;
my $lists = 0;
my $freamh = 0;
my $glanadh = 0;
my $idirdhealu = 0;
my $kept = 0;
# start JSON output
my $output = "[\n";
while (<STDIN>) {
	chomp;
	(my $title, my $text) = split(/\t/);
	#print "Processing $title...\n";
	my $plain = undef;
	my $plainlen = undef;
	unless ($include_all_p) {
		if ($title =~ m/^[0-9]+($| )/) {
			#print "Year or day...\n";
			next;
		}
		if (length($text) < 1200) {
			#print "Wikitext too short...\n";
			$tooshort++;
			next;
		}
		$plain = cleanup($text);
		$plainlen = length($plain);
		if ($plainlen < 750) {
			#print "Plain text too short...\n";
			$tooshort++;
			next;
		}
		if ($text =~ m/[{]Fréamh an Eolais/i) { 
			#print "Already have it from Fréamh an Eolais...\n";
			$freamh++;
			next;
		}
		if (!exists($primemover{$title})) {
			#print "No prime mover? $title\n";
			# should not happen... just long Category pages?
			next;
		}
		my $PM = $primemover{$title};
		if (!exists($ok{$PM})) {
			$notwhitelisted++;
			next;
		}
		if ($text =~ m/[{]glanadh/i) { 
			#print "Has {{glanadh}} template: $title; PM=$PM\n";
			$glanadh++;
			next;
		}
		if ($text =~ m/[{]idirdhealú/i or $text =~ m/idirdhealán/i) { 
			#print "Looks like a disambiguation page...\n";
			$idirdhealu++;
			next;
		}
		my $bullets = () = $plain =~ /^[*]/mg;
		if ($bullets>0) {
			my $charsperbullet = $plainlen/$bullets;
			if ($charsperbullet < 40) {
				#print "$title: Looks like a list article...\n";
				$lists++;
				next;
			}
		}
	}
	if (!defined($plain)) {
		$plain = cleanup($text);
		$plainlen = length($plain);
	}
	my $url = $title;
	$url =~ s/ /_/g;
	$url = 'https://ga.wikipedia.org/wiki/'.uri_encode($url);
	my $encoded_title = string2json($title);
	my $encoded_text = string2json($plain);
    $output .= "{\n";
    $output .= "  \"teideal\": \"$encoded_title\",\n";
    #$output .= "  \"príomhúdar\": \"$PM\",\n";
    $output .= "  \"url\": \"$url\",\n";
    $output .= "  \"téacs\": \"$encoded_text\"\n";
    $output .= "},\n";
	$kept++;
}
$output =~ s/,\n$/\n]\n/;
print $output;


# Summary stats
print STDERR "Too Short: $tooshort\n";
print STDERR "Fréamh an Eolais: $freamh\n";
print STDERR "Non-whitelisted author: $notwhitelisted\n";
print STDERR "Glanadh: $glanadh\n";
print STDERR "DAB: $idirdhealu\n";
print STDERR "Liostaí: $lists\n";
print STDERR "OK: $kept\n";

exit 0;

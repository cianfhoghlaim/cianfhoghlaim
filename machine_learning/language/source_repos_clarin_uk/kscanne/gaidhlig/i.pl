#!/usr/bin/perl

use strict;
use warnings;
use utf8;
use Encode;
use Unicode::Normalize;
use Locale::PO;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

# GD lexicon manager.  Not part of the ga2gd runtime distribution;
# just used for maintaining critical "cuardach.txt" bilingual lexicon

# TODO: option to output gramadoir-gd eile-gd.bs pairs...
if ($#ARGV != 0 and $ARGV[0] ne '-a') {
	die "Usage: $0 [-a WORD|-f|-g|-s|-t]\n-f: Manual additions to focloir.txt\n-g: Write GD.txt, essentially same as gramadoir lexicon-gd.txt\n-s: Write gd2ga lexicon pairs-gd.txt\n-t: Write ga2gd lexicon cuardach.txt\n";
}

my %lexicon;
my %standard;
my %prestandard;
my %freq;

# generic function for adding key/value pair to hash
# if key exists, append to value, delimited by semicolon
sub add_pair
{
	(my $key, my $val, my $href) = @_;

	if (exists($href->{$key})) {
		$href->{$key} .= ";$val";
	}
	else {
		$href->{$key} = $val;
	}
}

# verbs only...  see "prefixdh" below also
# not used before fr- in standard language, so "cha do fhreagair", etc.
# and not "dh'fhreagair" (though this appears a small number of times in
# corpus)
sub dhorlenite
{
	my ( $word ) = @_;
	$word = lenite($word);
	$word =~ s/^([aeiouàèìòùáéíóúAEIOUÀÈÌÒÙÁÉÍÓÚ]|[Ff]h[aeiouàèìòùáéíóú])/dh'$1/;
	return $word;
}

# used only in conditional
sub delenite
{
	my ( $word ) = @_;
	$word =~ s/^(.)h([^'])/$1$2/;
	return $word;
}

# used only in conditional
sub strip_dh
{
	my ( $word ) = @_;
	$word =~ s/^dh'//;
	return $word;
}

sub eclipse
{
	my ( $word ) = @_;
	$word =~ s/^([aeiouàèìòùáéíóúAEIOUÀÈÌÒÙÁÉÍÓÚ])/n-$1/;
	return $word;
}

sub lenite
{
	my ( $word ) = @_;
	$word =~ s/^([bcdfgmptBCDFGMPT])([^h'-])/$1h$2/;
	$word =~ s/^([Ss])([lnraeiouàèìòùáéíóú])/$1h$2/;
	return $word;
}

# note that we don't include words with inital f- here, even though
# they sometimes appear in the corpus (m'fhacal, etc.)
# currently handling in pairs-local-gd
sub prefixm
{
	my ( $word ) = @_;
	$word =~ s/^([aeiouàèìòùáéíóúAEIOUÀÈÌÒÙÁÉÍÓÚ])/m'$1/;
	return $word;
}

# now defunct - generate these in makefile after the fact...
sub prefixdh
{
	my ( $word ) = @_;
	$word =~ s/^([aeiouàèìòùáéíóúAEIOUÀÈÌÒÙÁÉÍÓÚ])/dh'$1/;
	$word =~ s/^([Ff])([aeiouàèìòùáéíóú])/dh'$1h$2/;
	return $word;
}

# do + noun is properly d' - dh' + noun used after do, de 
sub prefixd
{
	my ( $word ) = @_;
	$word =~ s/^([aeiouàèìòùáéíóúAEIOUÀÈÌÒÙÁÉÍÓÚ])/d'$1/;
	$word =~ s/^([Ff])([aeiouàèìòùáéíóú])/d'$1h$2/;
	return $word;
}

sub prefixb
{
	my ( $word ) = @_;
	$word =~ s/^([aeiouàèìòùáéíóúAEIOUÀÈÌÒÙÁÉÍÓÚ])/b'$1/;
	$word =~ s/^([Ff])([aeiouàèìòùáéíóú])/b'$1h$2/;
	return $word;
}

sub prefixh
{
	my ( $word ) = @_;
	$word =~ s/^([aeiouàèìòùáéíóúAEIOUÀÈÌÒÙÁÉÍÓÚ])/h-$1/;
	return $word;
}

sub prefixt
{
	my ( $word, $code ) = @_;
	if ($code eq '76') {
		$word =~ s/^([aeiouàèìòùáéíóúAEIOUÀÈÌÒÙÁÉÍÓÚ])/t-$1/;
	}
	# 76 is nominative singular masculine
	# which doesn't admit a t prefix in Irish
	# but does in the dative for gd so include here for that
	# only trick is if we translate to an Irish noun starting w/ vowel...
	if ($code eq '72' or $code eq '92' or $code eq '76') {
		$word =~ s/^([Ss][aeiouàèìòùáéíóúlnr])/t-$1/;
	}
	return $word;
}

sub slenderize
{
	my ( $word ) = @_;

	if ($word =~ m/ea[^aeiouàèìòùáéíóú]+$/) {
		if ($word =~ m/ea(?:nn|[cd]h)$/) {
			$word =~ s/ea([^aeiouàèìòùáéíóú]+)$/i$1/;
		}
		else {
			$word =~ s/ea([^aeiouàèìòùáéíóú]+)$/ei$1/;
		}
	}
	else {
		$word =~ s/([aouàòù])([^aeiouàèìòùáéíóú]+)$/$1i$2/;
	}

	return $word;
}

# Brigh nam Facal tables have imperatives for all numbers
sub imperative
{
	my ( $word, $root, $i, $n ) = @_;
	if ($root eq 'their') {
		$root = 'abr';   # irreg
	}
	elsif ($root eq 'cith') {
		$root = 'faic';   # irreg
	}
	elsif ($root eq 'gheibh') {
		$root = 'faigh';   # irreg
	}
	my $broad_p = ($root =~ m/([aouàòùáóú][^aeiouàèìòùáéíóú]+)$/);
	if ($n == 4) {
		$root .= 'e' unless ($broad_p);
		$root .= 'ar';
		return $root;
	}
	if ($i == 0) { # sing
		if ($n == 1) {
			$root .= 'e' unless ($broad_p);
			$root .= 'am';
		}
		elsif ($n == 2) {
			$root = $word;
		}
		else { # no fused pronoun in Irish either
			$root .= 'e' unless ($broad_p);
			$root .= 'adh';
		}
	}
	else { # plural
		if ($n == 1) {
			$root .= 'e' unless ($broad_p);
			$root .= 'amaid';
		}
		elsif ($n == 2) {
			$root .= 'a' if ($broad_p);
			$root .= 'ibh';
		}
		else { # fused ("molaidís") in Irish, so include pronoun here
			$root .= 'e' unless ($broad_p);
			$root .= 'adh iad';
		}
	}
	return $root;
}

# as a hack, for i=1, n=3 we return the relative future
# (chuireas, dh'fhàgas, etc.)
sub future
{
	my ( $root, $i, $n ) = @_;

	if ($root eq 'dèan') {
		return 'nì' if ($n < 4);  # including relative
		return 'nithear';
	}
	elsif ($root eq 'cith') {
		return 'chì' if ($n < 4);  # including relative
		return 'chithear';
	}
	# if root is "bith", "ruig", "cluinn", "beir", can just go ahead
	if ($n < 4 and ($root eq 'their' or $root eq 'gheibh' or $root eq 'thig')) {
		return $root;  # including relative
	}
	elsif ($root eq 'rach') {
		$root = 'thèid';
		return $root if ($n < 4);  # including relative
	}
	elsif ($root eq 'toir') {
		$root = 'bheir';
		return $root if ($n < 4);  # including relative
	}
	my $broad_p = ($root =~ m/([aouàòùáóú][^aeiouàèìòùáéíóú]+)$/);
	if ($n < 4) {
		$root .= 'a' if ($broad_p);
		$root .= 'idh';
		if ($i==1 and $n==3) {
			$root =~ s/aidh$/as/;
			$root =~ s/idh$/eas/;
			$root = dhorlenite($root);
		}
	}
	else {
		$root .= 'e' unless ($broad_p);
		$root .= 'ar';
	}
	
	return $root;
}

# bi =>  bhithinn/bhitheamaid ok, but stick with 'bhiodh' for 2nd/3rd
sub conditional
{
	my ( $root, $i, $n ) = @_;
	my $broad_p = ($root =~ m/([aouàòùáóú][^aeiouàèìòùáéíóú]+)$/);
	if ($n == 1) { # only "fused" forms are in 1st person
		if ($i == 0) {
			$root .= "a" if ($broad_p);
			$root .= "inn";
		}
		else {
			$root .= "e" unless ($broad_p);
			$root .= "amaid";
		}
	}
	else {
		if ($root eq 'bith') {
			$root = 'biodh';
		}
		else {
			$root .= "e" unless ($broad_p);
			$root .= "adh";
		}
	}

	return dhorlenite($root);
}

sub past
{
	my ( $word, $autonomous_p ) = @_;
	if ( $word eq 'abair' ) {
		$word = 'thubhairt';
	}
	elsif ( $word eq 'bi' ) {
		return 'bhathar' if ($autonomous_p);
		return 'bha';
	}
	elsif ($word eq 'thig') {
		return 'thàinigear' if ($autonomous_p);
		return 'thàinig';
	}
	elsif ($word eq 'rach') {
		return 'chaidheas' if ($autonomous_p);
		return 'chaidh';
	}
	elsif ($word eq 'beir') {
		$word = 'rug';
	}
	elsif ($word eq 'cluinn') {
		$word = 'chuala';
	}
	elsif ($word eq 'dèan') {
		$word = 'rinn';
	}
	elsif ($word eq 'faic') {
		$word = 'chunnaic';
	}
	elsif ($word eq 'faigh') {
		$word = 'fhuair';
	}
	elsif ($word eq 'ruig') {
		$word = 'ràinig';
	}
	elsif ($word eq 'tabhair') {
		$word = 'thug';
	}
	$word = dhorlenite($word) unless ($word eq 'fhuair');
	if ($autonomous_p) {
		$word = 'chunnac' if ($word eq 'chunnaic'); # broaden
		$word = 'fhuar' if ($word eq 'fhuair');    # broaden
		$word .= "e" unless ($word =~ m/([aouàòùáóú][^aeiouàèìòùáéíóú]*)$/);
		$word .= "a" unless ($word =~ m/a$/); # except chuala, bha
		$word .= "dh";
	}
	return $word;
}

sub default_pp
{
	my ( $word ) = @_;
	if ($word =~ /([aouàòùáóú])([^aeiouàèìòùáéíóú]+)$/) {
		$word =~ s/$/ta/;
	}
	elsif ($word =~ /([eièìéí])([^aeiouàèìòùáéíóú]+)$/) {
		$word =~ s/$/te/;
	}
	return $word;
}

sub default_verbal_root
{
	my ( $word ) = @_;
	return $word;
}

# unlike others, attaches _nm at end
sub default_vn
{
	my ( $word ) = @_;
	if ($word =~ /[au]ich$/) {
		$word =~ s/ich$/chadh_nm/;
	}
	elsif ($word =~ /ich$/) {
		$word =~ s/ich$/eachadh_nm/;
	}
	elsif ($word =~ /([aouàòùáóú])([^aeiouàèìòùáéíóú]+)$/) {
		$word =~ s/$/adh_nm/;
	}
	elsif ($word =~ /([eièì])([^aeiouàèìòù]+)$/) {
		$word =~ s/$/eadh_nm/;
	}
	return $word;
}

sub default_plural_adj
{
	my ( $word ) = @_;
	unless ($word =~ m/[aeiouàèìòùáéíóú][^aeiouàèìòùáéíóú]+[aeiouàèìòùáéíóú]/) {
		if ($word =~ m/[aouàòùáóú][^aeiouàèìòùáéíóú]+$/) {
			$word =~ s/$/a/;
		}
		elsif ($word =~ m/i[^aeiouàèìòùáéíóú]+$/) {
			$word =~ s/$/e/;
		}
		
	}
	return $word;
}

sub default_gsm
{
	my ( $word ) = @_;
	return slenderize($word);
}

sub default_gsf
{
	my ( $word ) = @_;
	$word = slenderize($word);
	$word =~ s/([^aeiouàèìòùáéíóú])$/$1e/;
	return $word;
}

sub default_plural
{
	my ( $word ) = @_;

	if ($word =~ m/iche$/) {
		$word =~ s/$/an/;
	}
	elsif ($word =~ m/[aeiouàèìòùáéíóú]$/) {
		$word = 'x';
		# or +an, but mostly seem abstract
	}
	elsif ($word =~ m/achd$/) {
		$word = 'x';
	}
	elsif ($word =~ m/eadh$/) {
		$word =~ s/adh$/idhean/;
	}
	elsif ($word =~ m/[^e]adh$/) {
		$word =~ s/dh$/idhean/;
	}
	elsif ($word =~ m/each$/) {
		$word =~ s/each$/ich/;
	}
	elsif ($word =~ m/[^e]ach$/) {
		$word =~ s/ach$/aich/;
	}
	elsif ($word =~ m/[aouàòùáóú][^aeiouàèìòùáéíóú]+$/) {
		$word =~ s/$/an/;
	}
	else {
		$word =~ s/$/ean/;	
	}
	return $word;

}

sub default_gen
{
	my ( $word ) = @_;

	if ($word =~ m/[aeiouàèìòùáéíóú]$/) {
		1;
	}
	elsif ($word =~ m/chd$/) {
		1;
	}
	elsif ($word =~ m/[aouàòù][^aeiouàèìòùáéíóú]+$/) {
		$word = slenderize($word);
	}
	elsif ($word =~ m/air$/) {
		1;
	}
	else {
		$word =~ s/$/e/;	
	}
	return $word;

}

# 5/12/05 returns reference to an array
# 5/23/05; potentially $arg is multiword phrase ("port adhair") 
#  in which case the first word is inflected and the remainder
#  is tacked on to the result
#  First arg is a gd word as it appears in focloir.txt or in msgstr
#  of ga2gd.po; e.g. "athchuinge_nf"; can have spaces too: "aisig air ais_v"
#  Second arg is usually false; but true if this function is called
#  recursively on the verbal noun of a verb
sub gramadoir_output {

	my ( $arg, $constit_p ) = @_;
	(my $word, my $pos) = $arg =~ m/^([^_0-9]+)[0-9]*_(\S+)$/;
	unless (exists($lexicon{$arg})) {
		print STDERR "Gramadoir output failed for $arg... this should not happen!\n";
		return [];
	}
	my $ret = [];
	my $data = $lexicon{$arg};
	my $tail = '';
	($tail) = $arg =~ /( [^_]+)/ if ($arg =~ m/ /);
	$word =~ s/ .*//;
	# nouns: 8 nom sing, 7 gen sin, 8 nom pl, 7 gen pl = 30
	if ($pos =~ /^n[mf]/) {
		(my $gencode, my $plcode) = $data =~ m/^([^\t]+)\t+(.+)$/;
		my $nomnum = 72;
		my $gennum = 88;
		my $plnum = 104;
		my $genplnum = 120;
		if ($pos eq 'nm') {
			$nomnum += 4;
			$gennum += 4;
			$plnum += 4;
			$genplnum += 4;
		}

		push @$ret, "$word$tail $nomnum";
		push @$ret, lenite($word)."$tail $nomnum";
		push @$ret, eclipse($word)."$tail $nomnum";
		push @$ret, prefixm($word)."$tail $nomnum";
		push @$ret, prefixd($word)."$tail $nomnum";
		push @$ret, prefixb($word)."$tail $nomnum";
		push @$ret, prefixh($word)."$tail $nomnum";
		push @$ret, prefixt($word,$nomnum)."$tail $nomnum";
		if ($gencode eq '0') {
			$gencode = default_gen($word);
		}
		push @$ret, $gencode."$tail $gennum";
		push @$ret, lenite($gencode)."$tail $gennum";
		push @$ret, eclipse($gencode)."$tail $gennum";
		push @$ret, prefixm($gencode)."$tail $gennum";
		push @$ret, prefixd($gencode)."$tail $gennum";
		push @$ret, prefixh($gencode)."$tail $gennum";
		push @$ret, prefixt($gencode,$gennum)."$tail $gennum";
		if ($plcode eq '0') {
			$plcode = default_plural($word);
		}
		elsif ($plcode eq '1') {
			$plcode = 'xx';
			$plnum = 4;
			$genplnum = 4;
		}
		unless ($constit_p ) {
			push @$ret, "$plcode$tail $plnum";
			push @$ret, lenite($plcode)."$tail $plnum";
			push @$ret, eclipse($plcode)."$tail $plnum";
			push @$ret, prefixm($plcode)."$tail $plnum";
			push @$ret, prefixd($plcode)."$tail $plnum";
			push @$ret, prefixb($plcode)."$tail $plnum";
			push @$ret, prefixh($plcode)."$tail $plnum";
			$plcode = 'xx'; $plnum = 4; $genplnum = 4; $tail = ''; # KILL GPL 2016-10-18
			push @$ret, "$plcode$tail $plnum";
			push @$ret, "$plcode$tail $genplnum";
			push @$ret, lenite($plcode)."$tail $genplnum";
			push @$ret, eclipse($plcode)."$tail $genplnum";
			push @$ret, prefixm($plcode)."$tail $genplnum";
			push @$ret, prefixd($plcode)."$tail $genplnum";
			push @$ret, prefixh($plcode)."$tail $genplnum";
			push @$ret, "$plcode$tail $genplnum";
		}
	}
	elsif ($pos eq 'n') {   # no gender, but lenited, etc.
		push @$ret, "$word$tail 64";
		push @$ret, lenite($word)."$tail 64";
		push @$ret, eclipse($word)."$tail 64";
		push @$ret, prefixm($word)."$tail 64";
		push @$ret, prefixd($word)."$tail 64";
		push @$ret, prefixb($word)."$tail 64";
		push @$ret, prefixh($word)."$tail 64";
	}
	# adjs: 4 nom, 2 gsm, 3 gsf, 3 pl = 12 total
	elsif ($pos eq 'a') {
		(my $compcode, my $plcode) = $data =~ m/^([^\t]+)\t+(.+)$/;
		push @$ret, "$word$tail 128";
		push @$ret, lenite($word)."$tail 128";
		push @$ret, prefixb($word)."$tail 128";
		push @$ret, prefixh($word)."$tail 128";
		my $gsm = default_gsm($word);
		push @$ret, "$gsm$tail 156";
		push @$ret, lenite($gsm)."$tail 156";
		if ($compcode eq '0') {
			$compcode = default_gsf($word);
		}
		push @$ret, "$compcode$tail 152";
		push @$ret, lenite($compcode)."$tail 152";
		push @$ret, prefixb($compcode)."$tail 152";
		if ($plcode eq '0') {
			$plcode = default_plural_adj($word);
		}
		push @$ret, "$plcode$tail 160";
		push @$ret, lenite($plcode)."$tail 160";
		push @$ret, prefixb($plcode)."$tail 160";
	}
	elsif ($pos eq 'aindec') {
		push @$ret, "$word$tail 128" foreach (1..12);
	}
	elsif ($pos eq 'card' or $pos eq 'ord') {
		push @$ret, "$word$tail 128";
		push @$ret, lenite($word)."$tail 128";
		push @$ret, "$word$tail 128";
		push @$ret, prefixb($word)."$tail 128";
		push @$ret, prefixh($word)."$tail 128";
	}
	# verbs: 8 vn, 7 gen vn, 16 pp (5+3+4+4, see adj),
	# + 21 for each of 1st/2nd/3rd Sing/Pl + Aut, - 2 (no prefix h if 
	# 1st person imperative) => 7*21-2 = 145 verb forms, 176 total
	# NB.  There are a small number of forms in gd in which the 
	# pronoun is fused with the noun; afaik, only in imperative
	# and conditional. Luckily, in these cases, Irish forms are
	# also fused, so gd2ga won't mishandle these
	elsif ($pos eq 'v') {
		(my $vncode, my $rootcode) = $data =~ m/^([^\t]+)\t+(.+)$/;
		$rootcode = $word if ($rootcode eq '0');
		push @$ret, "$word$tail 200";  # extra thing added to Gin 18 output
		my $vnnum = 76;
		if ($vncode eq '0') {
			$vncode = default_vn($word);
			$vncode =~ s/_.*$//;
			push @$ret, "$vncode$tail 76";
			push @$ret, lenite($vncode)."$tail 76";
			push @$ret, eclipse($vncode)."$tail 76";
			push @$ret, prefixm($vncode)."$tail 76";
			push @$ret, prefixd($vncode)."$tail 76";
			push @$ret, prefixb($vncode)."$tail 76";
			push @$ret, prefixh($vncode)."$tail 76";
			push @$ret, prefixt($vncode,76)."$tail 76";
			my $gencode = default_gen($vncode);
			push @$ret, $gencode."$tail 92";
			push @$ret, lenite($gencode)."$tail 92";
			push @$ret, "$gencode$tail 92";
			push @$ret, prefixm($gencode)."$tail 92";
			push @$ret, prefixd($gencode)."$tail 92";
			push @$ret, prefixh($gencode)."$tail 92";
			push @$ret, prefixt($gencode,92)."$tail 92";
		}
		else {  # irreg vn, so look up in lexicon
			# might have a tail, but want to generate forms before adding
			# the tail; see for example "aisig air ais_v", vn = "aiseag_nm"
			my $subret = gramadoir_output($vncode, 1);
			for my $f (@$subret) {
				$f =~ s/ ([0-9]+)$/$tail $1/;
				push @$ret, $f;
			}
			# and vncode, vnnum used below too...
			$vnnum = 72 if ($vncode =~ m/nf$/);
			$vncode =~ s/_.*$//;
		}
		#  16  pp's
		my $pp = default_pp($word);
		push @$ret, "$pp$tail 128";
		push @$ret, lenite($pp)."$tail 128";
		push @$ret, "$pp$tail 128";
		push @$ret, prefixb($pp)."$tail 128";
		push @$ret, prefixh($pp)."$tail 128";
		push @$ret, "$pp$tail 156";
		push @$ret, lenite($pp)."$tail 156";
		push @$ret, "$pp$tail 156";
		push @$ret, "$pp$tail 152";
		push @$ret, lenite($pp)."$tail 152";
		push @$ret, "$pp$tail 152";
		push @$ret, prefixb($pp)."$tail 152";
		push @$ret, "$pp$tail 160";
		push @$ret, lenite($pp)."$tail 160";
		push @$ret, "$pp$tail 160";
		push @$ret, prefixb($pp)."$tail 160";

		# now actual verb forms
		for (my $i=0; $i < 2; $i++) {
		  for (my $n=1; $n < 5; $n++) {
		  	unless ($n==4 and $i==0) {
				my $numer = 200;
				my $pron = '';
				$numer = 192 if ($n==4);
				# imperative
				my $w = imperative($word,$rootcode,$i,$n);	
		  		push @$ret, "$w$tail $numer";
		  		push @$ret, lenite($w)."$tail $numer";
		  		push @$ret, "$w$tail $numer";
		  		push @$ret, prefixh($w)."$tail $numer" unless ($n==1);
				# present
				$numer++;
		  		push @$ret, "xx 4" for (1..3);
		  		#push @$ret, "$vncode $vnnum" for (1..3);
				# past
				$w = past($word, ($n==4));	
				$numer+=2;
				if ($n == 1 and $i == 1) {
					$pron = ' sinn';
				}
				elsif ($n == 3 and $i == 1) {
					$pron = ' iad';
				}
				else {
					$pron = '';
				}
				# always lenited, even in questions and relative clauses
				# an do phòg 	cha do phòg 	nach do phòg 	gun do phòg 
		  		push @$ret, $w."$pron$tail $numer";
		  		push @$ret, $w."$pron$tail $numer";
		  		push @$ret, $w."$pron$tail $numer";
				# future
				$w = future($rootcode,$i,$n);	
				$numer++;
				if ($n == 1 and $i == 1) {
					$pron = ' sinn';
				}
				else {
					$pron = '';
				}
		  		push @$ret, "$w$pron$tail $numer";
				if ($n == 3 and $i == 0) {  # hack for cha(n) + an/am
		  			push @$ret, lenite($word)."$tail $numer";
		  			push @$ret, "$word$tail $numer";
				}
				else {  # the usual
		  			push @$ret, lenite($w)."$pron$tail $numer";
					$w = dhorlenite($w) if ($n==4);  # dh'fhàgar
		  			push @$ret, "$w$pron$tail $numer";
				}
				# imperfect
				$numer++;
		  		push @$ret, "xx 4" for (1..3);
		  		#push @$ret, "$vncode $vnnum" for (1..3);
				# conditional
				$w = conditional($rootcode,$i,$n);	
				$numer++;
				# 2nd sing and 3rd pl are only cases where Irish is fused
				# but gd is not, so need to add explicit pronouns here
				if ($n == 2 and $i == 0) {
					$pron = ' tu';   # sic; not "thu"
				}
				elsif ($n == 3 and $i == 1) {
					$pron = ' iad';
				}
				else {
					$pron = '';
				}
				if ($n == 4) {
		  			push @$ret, "xx 4" for (1..3);
				}
				else {
					# chan itheadh, chan fhanainn
					# matches "ní ithfeadh", "ní fhanfainn" in GA.txt
		  			push @$ret, strip_dh($w)."$pron$tail $numer";
					# Ghabhainn...   Dh'fhuiricheadh
					# matches "ghabhfainn, d'fh.." in Irish
		  			push @$ret, "$w$pron$tail $numer";
					# an iarradh, am postadh, ... 
					# matches eclipsed versions in Irish: an n-iarrfadh, ...
		  			push @$ret, delenite(strip_dh($w))."$pron$tail $numer";
				}
				# subjunctive
				$numer++;
		  		push @$ret, "xx 4" for (1..2);
		  		#push @$ret, "$vncode$tail $vnnum" for (1..2);
			}
		  }
		}
	}
	elsif ($pos eq 'vcop') {
		push @$ret, "$word$tail 194" for (1..177);
	}
	elsif ($pos eq 'pronm') {
		(my $emphcode, my $dummy) = $data =~ m/^([^\t]+)\t+(.+)$/;
		$emphcode='xx' if ($emphcode eq '0');
		push @$ret, "$word$tail 20";
		push @$ret, "$emphcode 22";
	}
	elsif ($pos eq 'art') {
		push @$ret, "$word$tail 8";
	}
	elsif ($pos eq 'prep') {
		push @$ret, "$word$tail 12";
	}
	elsif ($pos eq 'pn') {
		push @$ret, "$word$tail 16";
		push @$ret, "$word$tail 16";   # for é/hé, í/hí, etc.
	}
	elsif ($pos eq 'adv') {
		push @$ret, "$word$tail 24";
	}
	elsif ($pos eq 'conj') {
		push @$ret, "$word$tail 28";
	}
	elsif ($pos eq 'interr') {
		push @$ret, "$word$tail 32";
	}
	elsif ($pos eq 'excl') {
		push @$ret, "$word$tail 36";
	}
	elsif ($pos eq 'poss') {
		push @$ret, "$word$tail 40";
	}
	elsif ($pos eq 'u') {
		push @$ret, "$word$tail 1";
	}
	else {
		print STDERR "Unknown pos code\n";
	}
	return $ret;
}

sub userinput {
	my ($prompt) = @_;
	return '' if ($prompt =~ m/^dummy/);
	print "$prompt: ";
	$| = 1;          # flush
	$_ = getc;
	my $ans;
	while (m/[^\n]/) {
		$ans .= $_;
		$_ = getc;
	}
	return $ans;
}

sub get_prompt {
	my ($pos, $num) = @_;
	if ($pos =~ /^n[mf]/) {
		return "genitive" if ($num == 1);
		return "plural";
	}
	elsif ($pos eq 'a') {
		return "gsf" if ($num == 1);
		return "plural";
	}
	elsif ($pos eq 'v') {
		return "vn" if ($num == 1);
		return "root";
	}
	elsif ($pos eq 'pronm') {
		return "emphatic" if ($num == 1);
		return "dummy";
	}
	else {
		return "dummy";
	}
}

sub print_guesses {
	my ($newword) = @_;
	print "word=$newword\n";
	(my $word, my $pos) = $newword =~ /^([^_0-9]+)[0-9]*_(\S+)$/;
	print "word=$word,pos=$pos\n";
	my $tail = '';
	($tail) = $word =~ /( [^_]+)/ if / /;
	$word =~ s/ .*//;
	if ($pos =~ /^n[fm]/) {
		my $guess = default_gen($word);
		my $f = $freq{$guess};
		$f = '0' unless defined $f;
		print "gen=$guess$tail ($f)\npl =";
		$guess = default_plural($word);
		$f = $freq{$guess};
		$f = '0' unless defined $f;
		print "$guess$tail ($f)\n";
	}
	elsif ($pos eq 'a') {
		my $guess = default_gsf($word);
		my $f = $freq{$guess};
		$f = '0' unless defined $f;
		print "gsf=$guess$tail ($f)\npl =";
		$guess = default_plural_adj($word);
		$f = $freq{$guess};
		$f = '0' unless defined $f;
		print "$guess$tail ($f)\n";
	}
	elsif ($pos eq 'v') {
		my $guess = default_vn($word);
		my $f = $freq{$guess};
		$f = '0' unless defined $f;
		print "vn=$guess$tail ($f)\nroot =";
		$guess = default_verbal_root($word);
		$f = $freq{$guess};
		$f = '0' unless defined $f;
		print "$guess$tail ($f)\n";
	}
	elsif ($pos eq 'pronm') {
		print "emph=NO GUESS\n";
	}
	elsif ($pos eq 'n' or $pos eq 'vcop' or $pos eq 'art' or $pos eq 'prep' or $pos eq 'pn' or $pos eq 'adv' or $pos eq 'conj' or $pos eq 'interr' or $pos eq 'excl' or $pos eq 'poss' or $pos eq 'u' or $pos eq 'aindec' or $pos eq 'card' or $pos eq 'ord') {
		1;  # no guesses for these
	}
	else {
		print STDERR "Unknown pos code\n";
		return 0;
	}
	return 1;
}

# updates global variables "lexicon" and possible "standard"
sub user_add_word
{
	my $newword=userinput('Enter a word_pos (q to quit)');
	if ($newword eq 'q') {
		return 0;
	}
	else {
		(my $pos) = $newword =~ m/^[^_]+_(.*)$/;
		if (print_guesses($newword)) {
			my $currone = '0';
			my $currtwo = '0';
			$currone=userinput(get_prompt($pos,1).' (<CR>=same, no spaces)');
			$currone='0' unless $currone;
			$currtwo=userinput(get_prompt($pos,2).' (<CR>=same,x=none,no spaces)');
			$currtwo='0' unless $currtwo;
			$currtwo='1' if ($currtwo eq 'x');
			$lexicon{$newword} = "$currone\t$currtwo";
			my $stnd=userinput('Alternate of (<CR>=nothing)');
			if (defined($stnd)) {
				$standard{$newword} = $stnd;
				print "Warning: standard form $stnd isn't in lexicon...\n" unless (exists($lexicon{$stnd}));
			}
		}
		return 1;
	}
}

sub write_focloir
{
	open (OUTDICT, ">:utf8", "focloir.txt") or die "Could not open dictionary: $!\n";
	foreach (sort keys %lexicon) {
		my $std = '0';
		$std = $standard{$_} if (exists($standard{$_}));
		print OUTDICT "$_\t".$lexicon{$_}."\t$std\n";
	}
	close OUTDICT;
}

my %tags;
sub read_tags
{
	open (POSTAGS, "<:bytes", "/home/kps/gaeilge/gramadoir/gr/ga/pos-ga.txt") or die "Could not open Irish pos tags list: $!\n";

	while (<POSTAGS>) {
		my $curr = decode("iso-8859-1", $_);
		$curr =~ m/^([0-9]+)\s+(<[^>]+>)/;
		$tags{$1} = $2;
	}

}

sub to_xml
{
	my ($input) = @_;
	$input =~ m/^(.+) ([0-9]+)/;
	my $tag = $tags{$2};
	my $ans = $tag.$1;
	$tag =~ s/<(.).*/<\/$1>/;
	return $ans.$tag;
}

my %tagmap = (
	'A' => 'a',
	'C' => 'conj',
	'D' => 'poss',
	'F' => 'f',
	'I' => 'excl',
	'N' => 'n',
	'O' => 'pronm',
	'P' => 'pn',
	'Q' => 'interr',
	'R' => 'adv',
	'S' => 'prep',
	'T' => 'art',
	'U' => 'u',
	'V' => 'v',
);

sub xml_to_simple
{
	(my $xml) = @_;
	(my $fulltag, my $word, my $tag) = $xml =~ m/^(<[^>]+>)([^<]+)<\/(.)>$/;
	my $simpletag;

	if ($tag eq 'N') {
		$simpletag = 'n';
		$simpletag = 'nm' if ($fulltag =~ m/gnd=.m/);
		$simpletag = 'nf' if ($fulltag =~ m/gnd=.f/);
	}
	elsif ($tag eq 'V') {
		$simpletag = 'v';
		$simpletag = 'vcop' if ($fulltag =~ m/cop=.y/);
	}
	else {
		$simpletag = $tagmap{$tag};
	}
	return $word.'_'.$simpletag;
}

my %tagcount = (
'a' => 12,
'adv' => 1,
'aindec' => 12,
'art' => 1,
'card' => 5,
'conj' => 1,
'excl' => 1,
'interr' => 1,
'n' => 7,
'nf' => 30,
'nm' => 30,
'ord' => 5,
'pn' => 2,
'poss' => 1,
'prep' => 1,
'pronm' => 2,
'u' => 1,
'v' => 177,
'vcop' => 177,
);

# problem when reading GA.txt for gd2ga pairs file...
# when an entry in GA.txt is 127 (<F> tag for rare word)
# we don't know how to look it up in the bilingual hash, which 
# has the "correct" POS tags as they appear in gd2ga.po
#   The 1st argument that comes in is already in the underscore form
#   2nd argument is number of inflection for this word in GA.txt
#   3rd argument is the bilingual hashref in which we want the key
sub fix_F_tags
{
	(my $word, my $count, my $bilingual) = @_;
	return $word unless $word =~ m/_f$/;
	my @indices = ('','2','3');
	$word =~ s/_f//;
	# sort makes it deterministic; prioritizes nf over nm (e.g. bearach)
	for my $pos (sort keys %tagcount) {
		for my $i (@indices) {
			if (exists($bilingual->{$word.$i.'_'.$pos}) and $count == $tagcount{$pos}) {
				# sic; without the index!
				return $word.'_'.$pos;
			}
		}
	}
	return $word.'_f';
}

# last arg is a boolean; true if we want to allow non-stnd gd forms
# in the bilingual lexicon... basically true iff it's gd2ga!
sub maybe_add_pair
{
	(my $ga, my $gd, my $bilingual, my $nonstd_ok_p) = @_;

	if ($gd !~ m/_/) {
		my $win='';
		foreach my $pos (keys %tagcount) {
			if (exists($lexicon{$gd.'_'.$pos})) {
				if ($win) {
					print STDERR "$gd is ambiguous ($win,$pos) as translation of $ga: add a POS to msgstr in ga2gd.po!\n";
				}
				else {
					$win = $pos;
				}
			}
		}
		$gd .= "_$win" if ($win);
	}
	if (exists($lexicon{$gd})) {
		add_pair($ga, $gd, $bilingual);
		print STDERR "Warning: $gd is listed as an alternate form in focloir.txt\n" if (exists($standard{$gd}));
		if ($nonstd_ok_p and exists($prestandard{$gd})) {
			for my $nonstd (split /;/,$prestandard{$gd}) {
				add_pair($ga, $nonstd, $bilingual);
			}
		}
	}
	else {
		print STDERR "$gd: given as xln of $ga; add to gd lexicon!!\n";
	}
}

# reads po file (filename first arg) into bilingual hash (hashref second arg)
# in either case (ga2gd or gd2ga, want the Irish words to be the keys, and
# semi-colon separated gd translations the values)
sub read_po_file
{
	(my $pofile, my $bilingual) = @_;

	my $ga2gd_p = ($pofile =~ m/^ga2gd/);
	my $aref = Locale::PO->load_file_asarray($pofile);
	foreach my $msg (@$aref) {
		my $id = decode("utf8", $msg->msgid());
		my $str = decode("utf8",$msg->msgstr());
		if (defined($id) && defined($str)) {
			unless ($id eq '""' or $str eq '""') {
				$id =~ s/"//g;
				$str =~ s/"//g;
				if ($ga2gd_p) {
					(my $tag, my $rest) = $id =~ m/^(<[^>]+>)([^<]+<\/.>)$/;
					$tag =~ s/'/"/g;
					$id = "$tag$rest";
				}
				for my $aistriuchan (split (/;/,$str)) {
					next if ($aistriuchan eq '?');
					if ($ga2gd_p) {
						maybe_add_pair($id, $aistriuchan, $bilingual, 0);
					}
					else {
						# strictly speaking is msgstr is e.g. fíor1_nf
						# the 1 is optional, but preferred for interface
						# with other systems like gaeilge/sanas
						$aistriuchan =~ s/1_/_/;
						maybe_add_pair($aistriuchan, $id, $bilingual, 1);
					}
				}
			}
		}
	}
}

# argument is 'ga2gd.po' or 'gd2ga.po'!
sub write_pairs_file
{
	(my $pofile) = @_;

	my %outputfile = (
		'ga2gd.po' => 'cuardach.txt',
		'gd2ga.po' => 'pairs-gd.txt',
	);
	my $ga2gd_p = ($pofile =~ m/^ga2gd/);

	# headwords only; keys are Irish either way, and have XML markup
	# in the ga2gd case. Values on Scottish side look like focloir.txt
	# headwords, or else with _pos omitted if no ambiguity.
	my %bilingual;
	read_tags();
	read_po_file($pofile, \%bilingual);

	open (IGLEX, "<:utf8", "GA.txt") or die "Could not open Irish lexicon: $!\n";
	open (OUTLEX, ">:utf8", $outputfile{$pofile}) or die "Could not open pairs file for output: $!\n";
	my $normalized;
	my %ga_used;  # normalized GA headwords we've used for gd2ga
	my $prev_normalized = '';

	while (1) { # while lines to read in IGLEX
		my @entrywords = ();
		while (1) {
			my $igline = <IGLEX>;
			last unless ($igline); # EOF
			chomp($igline);
			last if ($igline eq '-');
			my $mykey = to_xml($igline);
			$mykey = xml_to_simple($mykey) unless $ga2gd_p;
			push @entrywords, $mykey;
		}
		last if scalar @entrywords == 0; # EOF
		$normalized = fix_F_tags($entrywords[0], scalar @entrywords, \%bilingual);
		if (exists($ga_used{$normalized})) {
			#print STDERR "Have already seen normalized $normalized in GA.txt\n" unless $ga2gd_p;
			$ga_used{$normalized}++;
			$normalized =~ s/_/$ga_used{$normalized}_/;
			#print STDERR "New normalized: $normalized\n" unless $ga2gd_p;
		}
		else {
			$ga_used{$normalized} = 1;
		}
		next unless exists($bilingual{$normalized});
		my @allforms = ();  # array of arrayrefs...
		for my $geedee (split /;/,$bilingual{$normalized}) {
			my $arrref=gramadoir_output($geedee, 0);
			if (scalar @entrywords == scalar @$arrref) {
		# sic, one arrayref pushed for each semi-colon separated translation
				push @allforms,$arrref;
			}
			else {
				print STDERR "GD word $geedee (".scalar(@$arrref).") and GA word $normalized (".scalar(@entrywords).") have different numbers of inflections... discarding this pair\n";
			}
		}
		next unless scalar @allforms > 0;
		my $index = 0;
		for my $gaform (@entrywords) {
			if ($ga2gd_p) {   # prints just one line
				my $toshow = "$gaform ";
				for my $transls (@allforms) {
					my $thisgd = @$transls[$index];
					$thisgd =~ s/ [0-9]+$//;
					$toshow .= "$thisgd;";
				}
				$toshow =~ s/;$//;
				print OUTLEX "$toshow\n";
			}
			else { # gd2ga pairs file; many lines if many translations
				for my $transls (@allforms) {
					my $toshow = @$transls[$index];
					$toshow =~ s/ [0-9]+$//; # kill gd pos code
					$toshow =~ s/ /_/g;      # multiword on gd side
					$toshow =~ s/$/ $gaform/;  # add corresponding Irish
					$toshow =~ s/_[^_]+$//;    # kill POS from Irish
					print OUTLEX "$toshow\n";
				}
			}
			$index++;
		}
	}

	close IGLEX;
	close OUTLEX;
}



#-#-#-#-#-#-#-#-#-#-#-#-#  START OF MAIN PROGRAM #-#-#-#-#-#-#-#-#-#-#-#-#-#

# focloir.txt is really a tsv; tabs separate four fields on
# each line; spaces allowed within a field
open (DICT, "<:utf8", "focloir.txt") or die "Could not open dictionary: $!\n";
while (<DICT>) {
	chomp;
	/^([^_]+_\S+)\t+(.+)\t+([^\t]+)$/;
	$lexicon{$1} = $2;
	if ($3 ne '0') {
		$standard{$1} = $3;
		add_pair($3, $1, \%prestandard);
	}
}
close DICT;

if ($ARGV[0] eq '-f') {
	open (FREQ, "<:utf8", '/usr/local/share/crubadan/gd/FREQ') or die "Could not open frequency file: $!\n";
	while (<FREQ>) {
		chomp;
		m/^ *([0-9]+) (.*)/;
		$freq{$2} = $1;
	}
	close FREQ;

	1 while (user_add_word());
	write_focloir();
}
elsif ($ARGV[0] eq '-a') {
	my %to_output;
	my $word = NFC(decode('utf-8', $ARGV[1]));
	my $forms = gramadoir_output($word, 0);
	if (exists($prestandard{$word})) {
		for my $nonstd (split /;/,$prestandard{$word}) {
			my $forms2 = gramadoir_output($nonstd, 0);
			push @$forms, @$forms2;
		}
	}
	foreach (@$forms) {
		s/ [0-9]+$//;
		#s/ .*$//;  # pronouns on verbs e.g.
		$to_output{$_}++ unless ($_ =~ m/^xx/ or $_ eq 'x');
	}
	for my $k (sort keys %to_output) {
		print "$k\n";
	}
}
elsif ($ARGV[0] eq '-g') {
	# currently includes alternate forms (for checking coverage in gd2ga)
	# if using this for gramadoir-gd, would want those in eile-gd.bs
	open (OUTLEX, ">:utf8", "GD.txt") or die "Could not open lexicon: $!\n";
	foreach (sort keys %lexicon) {
		#unless (/ / or exists($standard{$_})) {
		unless (/ /) {
			my $forms = gramadoir_output($_, 0);
			print OUTLEX "-\n";
			foreach (@$forms) {
				#s/^([^ ]+) ([^ ]+) ([0-9]+)$/$1 $3/;  # strip pronouns
				print OUTLEX "$_\n";
			}
		}
	}
	close OUTLEX;
}
elsif ($ARGV[0] eq '-s') {
	write_pairs_file('gd2ga.po');
}
elsif ($ARGV[0] eq '-t') {
	write_pairs_file('ga2gd.po');
}
else {
	die "Unrecognized option: $ARGV[0]\n";
}

exit 0;

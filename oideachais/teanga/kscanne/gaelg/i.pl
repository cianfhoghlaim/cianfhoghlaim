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

# -a is used in script "clar/script/gv"
if ($#ARGV != 0 and $ARGV[0] ne '-a') {
	die "Usage: $0 [-a WORD|-f|-g|-s|-t]\n-f: Manual additions to focloir.txt\n-g: Write GV.txt, essentially same as gramadoir lexicon-gv.txt\n-s: Write gv2ga lexicon pairs-gv.txt\n-t: Write ga2gv lexicon cuardach.txt\n";
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

sub eclipse
{
	# PM p.19; order matters here since we cascade through all substs
	my ( $word ) = @_;
	return $word if $word =~ m/^(beign|beagh)$/;
	$word =~ s/^g/ng/;  # n'gh- possible too, handled in rules-gv.txt
	$word =~ s/^G/Ng/;
	$word =~ s/^j/y/;  # n'y- possible too, handled in rules-gv.txt
	$word =~ s/^J/Y/;
	$word =~ s/^d/n/;  # or gh-?
	$word =~ s/^D/N/;
	$word =~ s/^b/m/;
	$word =~ s/^B/M/;
	$word =~ s/^f/v/;
	$word =~ s/^F/V/;
	$word =~ s/^[ck]/g/;
	$word =~ s/^[CK]/G/;
	$word =~ s/^[cç]h/j/;
	$word =~ s/^[CÇ]h/J/;
	$word =~ s/^p/b/;
	$word =~ s/^P/B/;
	$word =~ s/^t/d/;
	$word =~ s/^T/D/;
	$word =~ s/^([aeiou]|y[^aeiou])/n$1/;  # P.M. 1.9 p.16
	$word =~ s/^([AEIOU]|Y[^aeiou])/"N".lc($1)/e;
	return $word;
}

sub lenite
{
	my ( $word ) = @_;
	#$word =~ s/^[bm](w|oo)?/v/;  # or "w"
	#$word =~ s/^[BM](w|oo)?/V/;  PM p.19 has moo -> v, but mooar->vooar?
	$word =~ s/^[bm](w)?/v/;  # or "w"
	$word =~ s/^[BM](w)?/V/;
	$word =~ s/^[cç]h/h/;
	$word =~ s/^[CÇ]h/H/;
	$word =~ s/^[ck]([^h])/ch$1/;
	$word =~ s/^[CK]([^h])/Ch$1/;
	$word =~ s/^g([ei])/y$1/;  # or ghi, but handle that in rules-gv
	$word =~ s/^G([ei])/Y$1/;  # not in PM, but gennallys->yennallys too
	$word =~ s/^g([^hi])/gh$1/;
	$word =~ s/^G([^hi])/Gh$1/;
	$word =~ s/^p([^h])/ph$1/;
	$word =~ s/^P([^h])/Ph$1/;
	$word =~ s/^qu/wh/;
	$word =~ s/^Qu/Wh/;
	$word =~ s/^sh?l/l/;
	$word =~ s/^Sh?l/L/;
	$word =~ s/^sn/n/;
	$word =~ s/^Sn/N/;
	$word =~ s/^str/hr/;
	$word =~ s/^Str/Hr/;
	$word =~ s/^sh?([aeiouy])/h$1/;
	$word =~ s/^Sh?([aeiouy])/H$1/;
	$word =~ s/^j/y/;
	$word =~ s/^J/Y/;
	$word =~ s/^th?/h/;
	$word =~ s/^Th?/H/;
	$word =~ s/^dh?/gh/;
	$word =~ s/^Dh?/Gh/;
	$word =~ s/^[Ff]//;
	return $word;
}

# nouns only; possessive 1st sing
# never in gv corpus before an f - lenition drops the f!
# sometimes fused, sometimes not in corpus
# would make sense to lenite when it's not a vowel in preparation
# for prefixing "my" in pairs-gv, but since I don't do this in GA.txt
# doesn't really work to do it here...
sub prefixm
{
	my ( $word ) = @_;
	$word =~ s/^([aeiouyAEIOUY])/m'$1/;
	$word =~ s/^[Ff]([aeiou])/m'$1/;
	return $word;
}

# nouns only; possessive 2nd sing
# at first I thought it didn't appear with f-, but this was only
# because lenition drops the f!  So you'll see fegooish -> dt'egooish, 
# fenish -> dt'enish, etc quite frequently
# sometimes fused, sometimes not
sub prefixd
{
	my ( $word ) = @_;
	$word =~ s/^([aeiouyAEIOUY])/dt'$1/;
	$word =~ s/^[Ff]([aeiou])/dt'$1/;
	return $word;
}

# only in rare set phrases in gv, and sometimes written without
# an apostophe: "begin" = "b'éigean"
# ignore for now.
sub prefixb
{
	my ( $word ) = @_;
	#$word =~ s/^([aeiouAEIOU])/b'$1/;
	return $word;
}

# sometimes h-, sometimes just h: h-ellanyn and hellanyn both common enough
# I set a rule in rules-gv.txt that strips the hyphen, so don't include here
sub prefixh
{
	my ( $word ) = @_;
	$word =~ s/^([aeiouAEIOU]|[Yy][^aeiou])/h$1/;
	return $word;
}

# nouns only
# this is "type 2" lenition in PM p.19
# nothing like t- in "an t-anam, an t-uisce" in gv AFAIK; cf. yn ushtey
sub prefixt
{
	my ( $word, $code ) = @_;
	# For Irish, this is only applied to initial s for nom fem sing (72)
	# and gen masc sing (92)... here, though, like gd, 
	# 76 is nominative singular masculine which admits prefix t
	# in the dative 
	if ($code eq '72' or $code eq '92' or $code eq '76') {
		$word =~ s/^s([aeioun])/t$1/;
		$word =~ s/^S([aeioun])/T$1/;
		$word =~ s/^str/tr/;
		$word =~ s/^Str/Tr/;
		$word =~ s/^sl/cl/;  # also (rare) tl: PM p.19
		$word =~ s/^Sl/Cl/;
		$word =~ s/^sh/çh/;
		$word =~ s/^Sh/Çh/;
	}
	return $word;
}

my $gow_seen_hack = 0;

# PM p.121
sub imperative
{
	my ( $word, $root, $i, $n ) = @_;
	$root .= '-jee' if ($i == 1);  # -shiu handled in rules-gv.txt
	return $root;
}

# As a hack, return future relative (chaillys, hilgys, etc. PM 9.1.4)
# for i=1, n=3... same thing I did for gd!
sub future
{
	my ( $root, $i, $n ) = @_;

	# root = bee if root = bee...
	$root = 'jir' if ($root eq 'abbyr');
	$root = 'cluinn' if ($root eq 'clasht');
	$root = 'ver' if ($root eq 'cur');
	$root = 'hee' if ($root eq 'faik');
	$root = 'yiow' if ($root eq 'fow');
	$root = 'hed' if ($root eq 'gow' and $gow_seen_hack==0);
	$root = 'nee' if ($root eq 'jean');
	$root = 'hig' if ($root eq 'tar');
	if ($n == 1) {
		$root = 'hem' if ($root eq 'hed');
		if ($i == 0) {
			$root = 'yio' if ($root eq 'yiow');
			$root = 'go' if ($root eq 'gow');
			if ($root eq 'bee') {
				$root .= "'m";
			}
			else {
				$root .= 'ym' unless ($root eq 'hem');
			}
		}
		else {
			$root = 'cluin' if ($root eq 'cluinn');
			$root .= 'mayd';
		}
	}
	elsif ($n == 3 and $i ==1) {	# fut. rel. PM p. 119
		unless ($root =~ m/^(nee|hig|ver|hee|hed|yiow|jir)$/) {
			if ($root =~ /..ee$/) {
				$root =~ s/ee$/ys/;
			}
			elsif ($root eq 'bee') {
				$root = 'bees';  # lenites to "vees"
			}
			elsif ($root eq 'gow') {
				$root = 'goys';  # lenites to "ghoys"
			}
			else {
				$root .= 'ys';
			}
		}
	}
	else {
		unless ($root =~ m/^(hig|hed|jir|ver|yiow)$/ or $root =~ /ee$/) {
			if ($root =~ /ys$/) {
				$root =~ s/$/see/;
			}
			elsif ($root =~ /e$/) {
				$root =~ s/$/e/;
			}
			else {
				$root =~ s/$/ee/;
			}
		}
	}
	return $root;
}

# PM 9.1.1
sub future_dependent
{
	my ( $root, $i, $n ) = @_;
	my $fut = future($root, $i, $n);
	return $fut if ($root eq 'gow' and $gow_seen_hack==1);  # PM p.137, no special dependent form?
	$fut = $root if ($fut eq $root.'ee' or $fut eq $root.'e');  # caill -> caillee (n!=1)
	#$fut =~ s/ee$// if ($fut eq $root.'ee' or $fut eq $root.'e');  # caill -> caillee (n!=1)
	$fut = 'cluin' if ($fut eq 'cluinnee');
	if ($root eq 'jean') {
		$fut =~ s/^nee/jean/;
	}
	elsif ($root eq 'abbyr') {
		$fut =~ s/^jir/niarr/;  # or n'arr; neither in corpus?!
	}
	elsif ($root eq 'cur') {
		$fut =~ s/^v/d/;  # verym -> derym, etc.
	}
	elsif ($root eq 'faik') {
		$fut =~ s/^hee/vaik/;
	}
	elsif ($root eq 'fow') {
		$fut =~ s/^yi/v/;
	}
	elsif ($root eq 'gow' or $root eq 'tar') {
		$fut =~ s/^h/j/;
	}
	else {
		$fut = eclipse($fut);
	}
	return $fut;
}

# don't mutate here - handle in routine where this is called
sub conditional
{
	my ( $root, $i, $n ) = @_;
	$root = 'be' if ($root eq 'bee');
	$root = 'jinn' if ($root eq 'jean');
	$root = 'tarr' if ($root eq 'tar');
	$root = 'cluinn' if ($root eq 'clasht');
	$root = 'verr' if ($root eq 'cur');
	$root = 'hee' if ($root eq 'faik');
	$root = 'yio' if ($root eq 'fow');
	$root = 'ragh' if ($root eq 'gow' and $gow_seen_hack==0);
	$root = 'go' if ($root eq 'gow' and $gow_seen_hack==1);
	$root = 'jiarr' if ($root eq 'abbyr');
	if ($n == 1 and $i == 0) {
		if ($root eq 'be') {
			$root .= 'ign';
		}
		else {
			$root .= 'in';
		}
	}
	else {
		if ($root eq 'yio' or $root eq 'go') {
			$root .= 'ghe';
		}
		else {
			unless ($root eq 'ragh') {
				$root =~ s/a$//;
				$root .= 'agh';
			}
		}
	}

	return $root;
}

sub dependify_conditional
{
	(my $condl) = @_;
	$condl =~ s/^hee/vaik/ if ($condl =~ m/^hee/);
	$condl =~ s/^yi/v/ if ($condl =~ m/^yio/);
	$condl =~ s/^j/n/ if ($condl =~ m/^jiarr/);
	$condl = eclipse($condl) unless ($condl =~ m/^jinn/ or $condl =~ m/^(goin|goghe)/);
	$condl =~ s/^v/d/ if ($condl =~ m/^verr/);
	return $condl;
}

# caill->chaill, tilg->hilg
sub past
{
	my ($root) = @_;
	$root = 'ba' if ($root eq 'bee');
	$root = 'ren' if ($root eq 'jean');
	$root = 'haink' if ($root eq 'tar');
	$root = 'ceayll' if ($root eq 'clasht');
	$root = 'tug' if ($root eq 'cur');
	$root = 'honnick' if ($root eq 'faik');
	$root = 'hooar' if ($root eq 'fow');
	$root = 'hie' if ($root eq 'gow' and $gow_seen_hack==0);
	$root = 'dooyrt' if ($root eq 'abbyr');
	$root = lenite($root) unless ($root eq 'dooyrt');
	return $root;
}

# pass verb root in, not the past tense, since we
# still need to add d to words like (f)reggyr
sub past_with_prefixd
{
	(my $root) = @_;
	return 'hooar' if ($root eq 'fow');
	return 'dooyrt' if ($root eq 'abbyr');
	if ($root =~ /^[aeiouyf]/ and $root ne 'faik') {
		$root =~ s/^f/d/;  # fenee->denee, freggyr->dreggyr
		$root =~ s/^([aeiouy])/d$1/;  # insh -> dinsh, oardee->doardee
		return $root;
	}
	return past($root);
}

# usually no special dependent form in past/preterite
sub dependify_past
{
	(my $pastform) = @_;
	return 'vaik' if ($pastform eq 'honnick');
	return 'jagh' if ($pastform eq 'hie');
	$pastform =~ s/^h/d/ if ($pastform =~ m/^(haink|hooar|hug)$/);
	$pastform =~ s/^ch/g/ if ($pastform eq 'cheayll');
	return $pastform;
}

my %irreg_pp = (
	'aase' => 'aasit',
    'abbyr' => 'grait',
    'brish' => 'brisht',
    'cass' => 'cast',
    'clasht' => 'cluinit',
    'cur' => 'currit',
    'dooin' => 'dooint',
	'faik' => 'faikinit',
    'foshil' => 'foshlit',
	'fow' => 'feddynit',
    'gow' => 'goit',
    'jean' => 'jeant',
    'kiangle' => 'kianglt',
    'lhieg' => 'lhieggit',
    'lhieen' => 'lhieent',
    'poose' => 'poost',
    'reih' => 'reiht',
    'reill' => 'reillt',
    'sheean' => 'sheeant',
    'skeayl' => 'skeaylt',
);

sub default_pp
{
	my ( $word ) = @_;
	if (exists($irreg_pp{$word})) {
		return $irreg_pp{$word};
	}
	elsif ($word =~ m/ys$/) {
		$word .= 's';
	}
	elsif ($word =~ m/[^i]e+$/) {
		$word =~ s/e*$//;
	}
	return $word.'it';
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
	if ($word =~ /ee$/) {
		$word =~ s/ee$/aghey_nm/;
	}
	return $word;
}

# PM p.69: "usually identical in form in both singular and plural"
sub default_plural_adj
{
	my ( $word ) = @_;
	return $word;
}

# default is no change in gv
sub default_gsm
{
	my ( $word ) = @_;
	return $word;
}

# see PM p. 90... agh -> ee in classical manx
sub default_gsf
{
	my ( $word ) = @_;
	if ($word =~ m/..[^e]agh$/) {
		$word =~ s/agh$/ee/;
	}
	return $word;
}

sub default_plural
{
	my ( $word ) = @_;

	if ($word =~ m/..[^e]agh$/) {
		$word =~ s/agh$/ee/;
	}
	elsif ($word =~ m/ysy$/) {
		$word =~ s/$/syn/; # yindys->yindyssyn
	}
	elsif ($word =~ m/ey$/) {
		$word =~ s/ey$/aghyn/;
	}
	elsif ($word =~ m/aght$/) {  # foalsaght, creenaght, etc.
		$word = 'xx';
	}
	else {
		$word =~ s/$/yn/;	
	}
	return $word;

}

# default is no change
sub default_gen
{
	my ( $word ) = @_;
	return $word;

}

# 5/12/05 returns reference to an array
# 5/23/05; potentially $arg is multiword phrase ("port adhair") 
#  in which case the first word is inflected and the remainder
#  is tacked on to the result
#  First arg is a gv word as it appears in focloir.txt or in msgstr
#  of ga2gv.po; e.g. "trollag_nb"; can have spaces too: "billey ooyl_nf"
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
	# n, nm, nf
	if ($pos =~ /^n/) {
		(my $gencode, my $plcode) = $data =~ m/^([^\t]+)\t+(.+)$/;
		my $nomnum = 64;
		my $gennum = 80;
		my $plnum = 96;
		my $genplnum = 112;
		if ($pos eq 'nf') {
			$nomnum += 8;
			$gennum += 8;
			$plnum += 8;
			$genplnum += 8;
		}
		elsif ($pos eq 'nm') {
			$nomnum += 12;
			$gennum += 12;
			$plnum += 12;
			$genplnum += 12;
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
		#my $genplstr = $plcode;
		my $genplstr = 'xx';
		unless ($constit_p ) {
			push @$ret, "$plcode$tail $plnum";
			push @$ret, lenite($plcode)."$tail $plnum";
			push @$ret, eclipse($plcode)."$tail $plnum";
			push @$ret, prefixm($plcode)."$tail $plnum";
			push @$ret, prefixd($plcode)."$tail $plnum";
			push @$ret, prefixb($plcode)."$tail $plnum";
			push @$ret, prefixh($plcode)."$tail $plnum";
			push @$ret, "$plcode$tail $plnum";
			# gpl's follow
			push @$ret, "$genplstr$tail $genplnum";
			push @$ret, lenite($genplstr)."$tail $genplnum";
			push @$ret, eclipse($genplstr)."$tail $genplnum";
			push @$ret, prefixm($genplstr)."$tail $genplnum";
			push @$ret, prefixd($genplstr)."$tail $genplnum";
			push @$ret, prefixh($genplstr)."$tail $genplnum";
			push @$ret, "$genplstr$tail $genplnum";
		}
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
	# NB.  There are a small number of forms in gv in which the 
	# pronoun is fused with the noun; afaik, only in imperative
	# and conditional. Luckily, in these cases, Irish forms are
	# also fused, so gv2ga won't mishandle these
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
				if ($n == 1) {
		  			push @$ret, "xx 4" for (1..3);
				}
				elsif ($n == 2) {
					my $w = imperative($word,$rootcode,$i,$n);	
		  			push @$ret, "$w$tail $numer";
		  			push @$ret, lenite($w)."$tail $numer";
		  			push @$ret, "$w$tail $numer";
		 	 		push @$ret, prefixh($w)."$tail $numer"; # unless ($n==1);
				}
				else {  # n = 3 or 4
		  			push @$ret, "xx 4" for (1..4);
				}
				# present
				$numer++;
		  		push @$ret, "xx 4" for (1..3);
		  		#push @$ret, "$vncode $vnnum" for (1..3);
				# past
				my $w = past($rootcode);
				$numer+=2;
				if ($n == 1 and $i == 1) {
					$pron = ' shin';
				}
				elsif ($n == 3 and $i == 1) {
					$pron = ' ad';
				}
				else {
					$pron = '';
				}
				# always lenited, even in questions and relative clauses
				if ($n == 4) {
		  			push @$ret, "xx 4" for (1..3);
				}
				else {
					# in Irish: (níor) aithin, d'aithin, n-aithin
					#           (níor) fhág, d'fhág, bhfág
					#           (níor) chaill, chaill, gcaill
		  			push @$ret, dependify_past($w)."$pron$tail $numer";
		  			push @$ret, past_with_prefixd($rootcode)."$pron$tail $numer";
		  			push @$ret, dependify_past($w)."$pron$tail $numer";
				}
				# future
				$w = future($rootcode,$i,$n); # returns fut.rel. when n=3,i=1
				$numer++;
				$pron = '';  # 1st person singular is a problem... fixed in makefile
				my $fd = future_dependent($rootcode,$i,$n);
				my $fd_ecl = $fd;
				if ($n == 4) {
		  			push @$ret, "xx 4" for (1..3);
				}
				else {
					if ($n==3 and $i==1) { #lenite fut. rel. (hack)
						# $w = lenite($w); $fd = $w;
						$fd = lenite($w); $w = 'xx'; $fd_ecl = 'xx';
						# properly, fut. rel. *can* map to eclipsed Irish, e.g.
						# Lev. 16:9, "y ghoayr huittys lot y Chiarn er" ==
						# "an pocán ar a dtitfidh crann an Tiarna"
						# but rare enough to skip?
					}
			  		push @$ret, "$w$pron$tail $numer";
			  		push @$ret, "$fd$pron$tail $numer";
			  		push @$ret, "$fd_ecl$pron$tail $numer";
				}

				# imperfect
				$numer++;
		  		push @$ret, "xx 4" for (1..3);
		  		#push @$ret, "$vncode $vnnum" for (1..3);
				# conditional
				$w = conditional($rootcode,$i,$n);	
				my $cd = dependify_conditional($w);
				$numer++;
				# 2nd sing, 1st/3rd pl are only cases where Irish is fused
				# but gv is not, so need to add explicit pronouns here
				if ($n == 1 and $i == 1) {
					$pron = ' shin';
				}
				elsif ($n == 2 and $i == 0) {
					$pron = ' oo';
				}
				elsif ($n == 3 and $i == 1) {
					$pron = ' ad';
				}
				else {
					$pron = '';
				}
				if ($n == 4) {
		  			push @$ret, "xx 4" for (1..3);
				}
				# the conditional dependent:
				else {
					# On Irish side, first is form after "ní"
					# so "aithneofá" or "chaillfeá"
					# Next is the independent: d'aithneofá or chaillfeá
					# and finally the eclipsed form after go, etc.
					# n-aithneofá or gcaillfeá
					# so in Manx I want dependent forms first and third
		  			push @$ret, "$cd$pron$tail $numer";
		  			push @$ret, lenite($w)."$pron$tail $numer";
		  			push @$ret, "$cd$pron$tail $numer";
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
	$gow_seen_hack = 1 if ($word eq 'gow');
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
	if ($pos =~ /^n/) {
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
	if ($pos =~ /^n/) {
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
	elsif ($pos eq 'vcop' or $pos eq 'art' or $pos eq 'prep' or $pos eq 'pn' or $pos eq 'adv' or $pos eq 'conj' or $pos eq 'interr' or $pos eq 'excl' or $pos eq 'poss' or $pos eq 'u' or $pos eq 'aindec' or $pos eq 'card' or $pos eq 'ord') {
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

# for reading GA.txt
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

# used only for gv2ga, while reading in GA.txt
# we convert numerical POS tag to XML, and from XML to simple tag
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

# problem when reading GA.txt for gv2ga pairs file...
# when an entry in GA.txt is 127 (<F> tag for rare word)
# we don't know how to look it up in the bilingual hash, which 
# has the "correct" POS tags as they appear in gv2ga.po
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

# last arg is a boolean; true if we want to allow non-stnd gv forms
# in the bilingual lexicon... basically true iff it's gv2ga!
sub maybe_add_pair
{
	(my $ga, my $gv, my $bilingual, my $nonstd_ok_p) = @_;

	if ($gv !~ m/_/) {
		my $win='';
		foreach my $pos (keys %tagcount) {
			if (exists($lexicon{$gv.'_'.$pos})) {
				if ($win) {
					print STDERR "$gv is ambiguous ($win,$pos) as translation of $ga: add a POS to msgstr in ga2gv.po!\n";
				}
				else {
					$win = $pos;
				}
			}
		}
		$gv .= "_$win" if ($win);
	}
	if (exists($lexicon{$gv})) {
		add_pair($ga, $gv, $bilingual);
		print STDERR "Warning: $gv is listed as an alternate form in focloir.txt\n" if (exists($standard{$gv}));
		if ($nonstd_ok_p and exists($prestandard{$gv})) {
			for my $nonstd (split /;/,$prestandard{$gv}) {
				add_pair($ga, $nonstd, $bilingual);
			}
		}
	}
	else {
		print STDERR "$gv: given as xln of $ga; add to gv lexicon!!\n";
	}
}

# reads po file (filename first arg) into bilingual hash (hashref second arg)
# in either case (ga2gv or gv2ga, want the Irish words to be the keys, and
# semi-colon separated gv translations the values)
sub read_po_file
{
	(my $pofile, my $bilingual) = @_;

	my $ga2gv_p = ($pofile =~ m/^ga2gv/);
	my $aref = Locale::PO->load_file_asarray($pofile);
	foreach my $msg (@$aref) {
		my $id = decode("utf8", $msg->msgid());
		my $str = decode("utf8",$msg->msgstr());
		if (defined($id) && defined($str)) {
			unless ($id eq '""' or $str eq '""') {
				$id =~ s/"//g;
				$str =~ s/"//g;
				if ($ga2gv_p) {
					(my $tag, my $rest) = $id =~ m/^(<[^>]+>)([^<]+<\/.>)$/;
					$tag =~ s/'/"/g;
					$id = "$tag$rest";
				}
				for my $aistriuchan (split (/;/,$str)) {
					next if ($aistriuchan eq '?');
					if ($ga2gv_p) {
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

# argument is 'ga2gv.po' or 'gv2ga.po'!
sub write_pairs_file
{
	(my $pofile) = @_;

	my %outputfile = (
		'ga2gv.po' => 'cuardach.txt',
		'gv2ga.po' => 'pairs-gv.txt',
	);
	my $ga2gv_p = ($pofile =~ m/^ga2gv/);

	# headwords only; keys are Irish either way, and have XML markup
	# in the ga2gv case. Values on Manx side look like focloir.txt
	# headwords, or else with _pos omitted if no ambiguity.
	my %bilingual;
	read_tags();
	read_po_file($pofile, \%bilingual);

	open (IGLEX, "<:utf8", "GA.txt") or die "Could not open Irish lexicon: $!\n";
	open (OUTLEX, ">:utf8", $outputfile{$pofile}) or die "Could not open pairs file for output: $!\n";
	my $normalized;
	my %ga_used;  # normalized GA headwords we've used for gv2ga
	my $prev_normalized = '';

	while (1) { # while lines to read in IGLEX
		my @entrywords = ();
		while (1) {
			my $igline = <IGLEX>;
			last unless ($igline); # EOF
			chomp($igline);
			last if ($igline eq '-');
			my $mykey = to_xml($igline);
			$mykey = xml_to_simple($mykey) unless $ga2gv_p;
			push @entrywords, $mykey;
		}
		last if scalar @entrywords == 0; # EOF
		$normalized = fix_F_tags($entrywords[0], scalar @entrywords, \%bilingual);
		if (exists($ga_used{$normalized})) {
			#print STDERR "Have already seen normalized $normalized in GA.txt\n" unless $ga2gv_p;
			$ga_used{$normalized}++;
			$normalized =~ s/_/$ga_used{$normalized}_/;
			#print STDERR "New normalized: $normalized\n" unless $ga2gv_p;
		}
		else {
			$ga_used{$normalized} = 1;
		}
		next unless exists($bilingual{$normalized});
		my @allforms = ();  # array of arrayrefs...
		for my $geevee (split /;/,$bilingual{$normalized}) {
			my $arrref=gramadoir_output($geevee, 0);
			if (scalar @entrywords == scalar @$arrref) {
		# sic, one arrayref pushed for each semi-colon separated translation
				push @allforms,$arrref;
			}
			else {
				print STDERR "GV word $geevee (".scalar(@$arrref).") and GA word $normalized (".scalar(@entrywords).") have different numbers of inflections... discarding this pair\n";
			}
		}
		next unless scalar @allforms > 0;
		my $index = 0;
		for my $gaform (@entrywords) {
			if ($ga2gv_p) {   # prints just one line
				my $toshow = "$gaform ";
				for my $transls (@allforms) {
					my $thisgv = @$transls[$index];
					$thisgv =~ s/ [0-9]+$//;
					$toshow .= "$thisgv;";
				}
				$toshow =~ s/;$//;
				print OUTLEX "$toshow\n";
			}
			else { # gv2ga pairs file; many lines if many translations
				for my $transls (@allforms) {
					my $toshow = @$transls[$index];
					$toshow =~ s/ [0-9]+$//; # kill gv pos code
					$toshow =~ s/ /_/g;      # multiword on gv side
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
	open (FREQ, "<:utf8", '/usr/local/share/crubadan/gv/FREQ') or die "Could not open frequency file: $!\n";
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
	# currently includes alternate forms (for checking coverage in gv2ga)
	# if using this for gramadoir-gv, would want those in eile-gv.bs
	open (OUTLEX, ">:utf8", "GV.txt") or die "Could not open lexicon: $!\n";
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
	write_pairs_file('gv2ga.po');
}
elsif ($ARGV[0] eq '-t') {
	write_pairs_file('ga2gv.po');
}
else {
	die "Unrecognized option: $ARGV[0]\n";
}

exit 0;

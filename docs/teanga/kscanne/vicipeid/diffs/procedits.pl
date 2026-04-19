#!/usr/bin/perl

use strict;
use warnings;
use utf8;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

my %pronomials;
my %stems;
open(TAGDICT, "<:utf8", "/home/kps/gaeilge/parsail/treebank/tagdict.tsv") or die;
while (<TAGDICT>) {
	chomp;
	(my $surf, my $lemma, my $pos, my $features) = m/^(\S+)\t(\S+)\t([A-Z]+)\t_\t(.+)$/;
	$stems{$surf}->{$lemma} = 1;
	if ($pos eq 'ADP') {
		$pronomials{$surf}->{$features} = 1;
	}
}
close TAGDICT;
$stems{'aicmiú'}->{'aicmigh'} = 1;
$stems{'aistriú'}->{'aistrigh'} = 1;
$stems{'baint'}->{'bain'} = 1;
$stems{'bhaint'}->{'bain'} = 1;
$stems{'bheith'}->{'bí'} = 1;
$stems{'bhualadh'}->{'buail'} = 1;
$stems{'bualadh'}->{'buail'} = 1;
$stems{'caitheamh'}->{'caith'} = 1;
$stems{'chaitheamh'}->{'caith'} = 1;
$stems{'chluais'}->{'cluas'} = 1;
$stems{'chosaint'}->{'cosain'} = 1;
$stems{'cluais'}->{'cluas'} = 1;
$stems{'cosaint'}->{'cosain'} = 1;
$stems{'déanamh'}->{'déan'} = 1;
$stems{'déanta'}->{'déan'} = 1;
$stems{'dhéanamh'}->{'déan'} = 1;
$stems{'dhóite'}->{'dóigh'} = 1;
$stems{'dóite'}->{'dóigh'} = 1;
$stems{'ghabháil'}->{'gabh'} = 1;
$stems{'ghlaoch'}->{'glaoigh'} = 1;
$stems{'glaoch'}->{'glaoigh'} = 1;
$stems{'gréin'}->{'grian'} = 1;
$stems{'iarraidh'}->{'iarr'} = 1;
$stems{'imirt'}->{'imir'} = 1;
$stems{'labhairt'}->{'labhair'} = 1;
$stems{'léamh'}->{'léigh'} = 1;
$stems{'ligean'}->{'lig'} = 1;
$stems{'loscadh'}->{'loisc'} = 1;
$stems{'mharbhsháinniú'}->{'marbhsháinnigh'} = 1;
$stems{'mhíniú'}->{'mínigh'} = 1;
$stems{'mhó'}->{'mór'} = 1;
$stems{'minice'}->{'minic'} = 1;
$stems{'minicí'}->{'minic'} = 1;
$stems{'míniú'}->{'mínigh'} = 1;
$stems{'ngréin'}->{'grian'} = 1;
$stems{'oibriú'}->{'oibrigh'} = 1;
$stems{'oscailt'}->{'oscail'} = 1;
$stems{'roinnt'}->{'roinn'} = 1;
$stems{'seinm'}->{'seinn'} = 1;
$stems{'sheinm'}->{'seinn'} = 1;
$stems{'síniú'}->{'sínigh'} = 1;
$stems{'sular'}->{'sula'} = 1;
$stems{'tabhairt'}->{'tabhair'} = 1;
$stems{'tarraingt'}->{'tarraing'} = 1;
$stems{'tugtha'}->{'tabhair'} = 1;
$stems{'tsaol'}->{'saol'} = 1;
$stems{'thógáil'}->{'tóg'} = 1;
$stems{'tógáil'}->{'tóg'} = 1;
$stems{'threascairt'}->{'treascair'} = 1;
$stems{'treascairt'}->{'treascair'} = 1;
$stems{'úsáidte'}->{'úsáid'} = 1;

sub shared_adp_features_p {
	(my $s1, my $s2) = @_;
	return 0 unless (exists($pronomials{$s2}) and exists($pronomials{$s1}));
	for my $s2feats (keys %{$pronomials{$s2}}) {
		return 1 if (exists($pronomials{$s1}->{$s2feats}));
	}
	return 0;
}

sub shared_lemma_p {
	(my $s1, my $s2) = @_;
	$s2 =~ s/^[mbdt]'//;
	$s1 =~ s/^[mbdt]'//;
	return 0 unless (exists($stems{$s2}) and exists($stems{$s1}));
	for my $s2lem (keys %{$stems{$s2}}) {
		return 1 if (exists($stems{$s1}->{$s2lem}));
	}
	return 0;
}

my %ok;
my %clean;
open(CLEAN, "<:utf8", "../../gaelspell/gaelspell.txt") or die;
while (<CLEAN>) {
	chomp;
	$clean{$_} = 1;
}
close CLEAN;
open(OK, "<:utf8", "../olleagar/OK.txt") or die;
while (<OK>) {
	chomp;
	$ok{$_} = 1;
}
close OK;

my %p;
open(PAIRS, "<:utf8", "../../caighdean/pairs.txt") or die;
while (<PAIRS>) {
	chomp;
	(my $b, my $a) = m/^([^ ]+) (.+)$/;
	$p{$b}->{$a} = 1;
}
close PAIRS;

# assumes lower
sub violates_broadslender_p {
	(my $s) = @_;
	return ($s =~ m/[aáoóuú][^aeiouáéíóú ]+[eéií]/ or
	        $s =~ m/ae[^aeiouáéíóú ]+[eéií]/ or
	        $s =~ m/[éií][^aeiouáéíóú ]+[aáoóuú]/ or
	        $s =~ m/^e[^aeiouáéíóú ]+[aáoóuú]/ or
	        $s =~ m/[^a]e[^aeiouáéíóú ]+[aáoóuú]/);
}

sub masculinize {
	(my $s) = @_;
	return 'é' if ($s eq 'í');
	return "b'é" if ($s eq "b'í");
	return 'sé' if ($s eq 'sí');
	return $s;
}

# assumes lowercase
sub stripmutation {
	(my $s) = @_;
	$s =~ s/^[nt]-([aeiouáéíóú])/$1/;
	$s =~ s/^h-?([aeiouáéíóú])/$1/;
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

# might be several words separated by spaces
sub spelled_ok_p {
	(my $s) = @_;
	my @pieces = split(/ /,$s);
	for my $p (@pieces) {
		next unless ($p =~ m/\p{L}/);
		return 0 if (!exists($clean{$p}) and !exists($clean{lc($p)}) and !exists($ok{$p}) and !exists($ok{lc($p)}));
	}
	return 1;
}

# assumes lowercase
sub toascii {
	(my $s) = @_;
	$s =~ s/[áà]/a/g;
	$s =~ s/[éè]/e/g;
	$s =~ s/[íì]/i/g;
	$s =~ s/[óò]/o/g;
	$s =~ s/[úù]/u/g;
	return $s;
}

sub stripspaces {
	(my $s) = @_;
	$s =~ s/ //g;
	return $s;
}

# assumes hyphens have been asciified (see below)
sub striphyphens {
	(my $s) = @_;
	$s =~ s/-//g;
	return $s;
}

sub striphaitches {
	(my $s) = @_;
	$s =~ s/h//g;
	return $s;
}

# asciify aposts and hyphens
sub normalize {
	(my $s) = @_;
	$s =~ s/[ʼ’]/'/g;
	$s =~ s/[−‑‐]/-/g;
	return $s;
}

# ", shocraigh" -> "shocraigh"
sub killnonwords {
	(my $s) = @_;
	$s =~ s/^\p{P}+ //;
	$s =~ s/ \p{P}+$//;
	return $s;
}

while (<STDIN>) {
	chomp;
	next unless (m/^[{]/);
	(my $b, my $a, my $dst, my $u) = m/^[{]"before": "(.*)", "after": "(.*)", "distance": ([0-9]+), "context":.*", "user": "(.*)"[}]/;
	next if ($b =~ m/ /);
	next if ($b =~ m/\p{Lu}/ or $a =~ m/\p{Lu}/);
	$b = killnonwords(normalize($b));
	$a = killnonwords(normalize($a));
	next if ($a eq $b); # possible after normalization
	my $code = 0;
	$code +=2 if (spelled_ok_p($b));
	$code +=1 if (spelled_ok_p($a));
	if (toascii($b) eq toascii($a)) {
		$code .= '-fadas';
	}
	elsif (striphyphens($b) eq striphyphens($a)) {
		$code .= '-hyphen';
	}
	elsif (stripmutation($b) eq stripmutation($a)) {
		$code .= '-mutation';
	}
	elsif (shared_lemma_p($b,$a)) {
		$code .= '-inflection';
	}
	elsif (masculinize($b) eq masculinize($a)) {
		$code .= '-gender';
	}
	elsif (stripspaces($a) eq $b) {
		$code .= '-runtogether';
	}
	elsif (exists($ok{$b})) {
		$code .= '-standardize';
	}
	elsif (violates_broadslender_p($b) and !violates_broadslender_p($a)) {
		$code .= '-broadslender';
	}
	elsif (striphaitches($b) eq striphaitches($a)) {
		$code .= '-internalseimhiu';
		# includes common cases like unnec. len "caolsheans" with dentals
	}
	elsif (exists($pronomials{$a}) and exists($pronomials{$b}) and shared_adp_features_p($b,$a)) {
		$code .= '-preposition';
	}
	my $bstrip = $b;
	$bstrip =~ s/-//g;
	#next if ($bstrip eq $a);  # skip if not useful for earraidi
	#if (exists($p{$b})) {
		#next if (exists($p{$b}->{$a}));
	#}
	#elsif (exists($p{lc($b)})) {
		#next if (exists($p{lc($b)}->{lc($a)}));  # Condae Contae
	#}
	print "$code\t$b\t$a\t$dst\t$u\n";
}

exit 0;

#!/usr/bin/perl

use strict;
use warnings;
use utf8;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

my %tags = (
	'0' => 'X~_',	# placeholder
	'1' => 'PART~_',	# <U>
	'4' => 'PART~_',	# <U>
	'8' => 'DET~_',	# <T>
	'12' => 'ADP~_',	# <S>
	'16' => 'PRON~_',	# <P>
	'18' => 'PRON~_',	# <P h="y">
	'20' => 'ADP~_',	# <O>
	'22' => 'ADP~_',	# <O em="y">
	'24' => 'ADV~_',	# <R>
	'28' => 'SCONJ~_',	# <C>
	'32' => 'PRON~_',	# <Q>
	'36' => 'INTJ~_',	# <I>
	'40' => 'DET~_',	# <D>
	'64' => 'NOUN~Case=Nom|Number=Sing',	# <N pl="n" gnt="n">
	'65' => 'NOUN~Case=Dat|Number=Sing',	# <N pl="n" gnt="d">
	'66' => 'NOUN~Case=Nom|Form=HPref|Number=Sing', # <N pl="n" gnt="n" h="y">
	'67' => 'NOUN~Case=Dat|Form=HPref|Number=Sing', # <N pl="n" gnt="d" h="y">
	'72' => 'NOUN~Case=Nom|Gender=Fem|Number=Sing',	# <N pl="n" gnt="n" gnd="f">
	'74' => 'NOUN~Case=Nom|Form=HPref|Gender=Fem|Number=Sing', # <N pl="n" gnt="n" gnd="f" h="y">
	'76' => 'NOUN~Case=Nom|Gender=Masc|Number=Sing',	# <N pl="n" gnt="n" gnd="m">
	'78' => 'NOUN~Case=Nom|Form=HPref|Gender=Masc|Number=Sing',	# <N pl="n" gnt="n" gnd="m" h="y">
	'80' => 'NOUN~Case=Gen|Number=Sing',	# <N pl="n" gnt="y">
	'88' => 'NOUN~Case=Gen|Gender=Fem|Number=Sing',	# <N pl="n" gnt="y" gnd="f">
	'90' => 'NOUN~Case=Gen|Form=HPref|Gender=Fem|Number=Sing',	# <N pl="n" gnt="y" gnd="f" h="y">
	'92' => 'NOUN~Case=Gen|Gender=Masc|Number=Sing',	# <N pl="n" gnt="y" gnd="m">
	'94' => 'NOUN~Case=Gen|Form=HPref|Gender=Masc|Number=Sing',	# <N pl="n" gnt="y" gnd="m" h="y">
	'96' => 'NOUN~Case=Nom|Number=Plur',	# <N pl="y" gnt="n">
	'97' => 'NOUN~Case=Dat|Number=Plur', # <N pl="y" gnt="d">
	'98' => 'NOUN~Case=Nom|Form=HPref|Number=Plur',	# <N pl="y" gnt="n" h="y">
	'99' => 'NOUN~Case=Dat|Form=HPref|Number=Plur', # <N pl="y" gnt="d" h="y">
	'104' => 'NOUN~Case=Nom|Gender=Fem|Number=Plur',	# <N pl="y" gnt="n" gnd="f">
	'106' => 'NOUN~Case=Nom|Form=HPref|Gender=Fem|Number=Plur',	# <N pl="y" gnt="n" gnd="f" h="y">
	'108' => 'NOUN~Case=Nom|Gender=Masc|Number=Plur',	# <N pl="y" gnt="n" gnd="m">
	'110' => 'NOUN~Case=Nom|Form=HPref|Gender=Masc|Number=Plur',	# <N pl="y" gnt="n" gnd="m" h="y">
	'112' => 'NOUN~Case=Gen|Number=Plur',	# <N pl="y" gnt="y">
	'114' => 'NOUN~Case=Gen|Form=HPref|Number=Plur',	# <N pl="y" gnt="y" h="y">
	'120' => 'NOUN~Case=Gen|Gender=Fem|Number=Plur',	# <N pl="y" gnt="y" gnd="f">
	'122' => 'NOUN~Case=Gen|Form=HPref|Gender=Fem|Number=Plur',	# <N pl="y" gnt="y" gnd="f" h="y">
	'124' => 'NOUN~Case=Gen|Gender=Masc|Number=Plur',	# <N pl="y" gnt="y" gnd="m">
	'126' => 'NOUN~Case=Gen|Form=HPref|Gender=Masc|Number=Plur',	# <N pl="y" gnt="y" gnd="m" h="y">
	'127' => '!!!!',	# <F>   SKIP...
	'128' => 'ADJ~Case=Nom|Number=Sing',	# <A pl="n" gnt="n">
	'130' => 'ADJ~Degree=Pos|Form=HPref',	# <A pl="n" gnt="n" h="y">
	'152' => 'ADJ~Case=Gen|Gender=Fem|Number=Sing',	# <A pl="n" gnt="y" gnd="f">
	'156' => 'ADJ~Case=Gen|Gender=Masc|Number=Sing',	# <A pl="n" gnt="y" gnd="m">
	'160' => 'ADJ~Number=Plur',	# <A pl="y" gnt="n">
	'192' => 'VERB~Mood=Imp|Person=0',	# <V p="n" t="ord">
	'193' => 'VERB~Mood=Ind|Person=0|Tense=Pres',	# <V p="n" t="láith">
	'194' => 'AUX~_',	# <V cop="y">
	'195' => 'VERB~Mood=Ind|Person=0|Tense=Past',	# <V p="n" t="caite">
	'196' => 'VERB~Mood=Ind|Person=0|Tense=Fut',	# <V p="n" t="fáist">
	'197' => 'VERB~Aspect=Imp|Person=0|Tense=Past',	# <V p="n" t="gnáth">
	'198' => 'VERB~Mood=Cnd|Person=0',	# <V p="n" t="coinn">
	'199' => 'VERB~Mood=Sub|Person=0',	# <V p="n" t="foshuit">
	'200' => 'VERB~Mood=Imp',	# <V p="y" t="ord">
	'201' => 'VERB~Mood=Ind|Tense=Pres',	# <V p="y" t="láith">
	'203' => 'VERB~Mood=Ind|Tense=Past',	# <V p="y" t="caite">
	'204' => 'VERB~Mood=Ind|Tense=Fut',	# <V p="y" t="fáist">
	'205' => 'VERB~Aspect=Imp|Tense=Past',	# <V p="y" t="gnáth">
	'206' => 'VERB~Mood=Cnd',	# <V p="y" t="coinn">
	'207' => 'VERB~Mood=Sub',	# <V p="y" t="foshuit">
);

# for POS; keys are word, vals are hash with POS's as keys
my %pos;
# for stems; keys are "word|POS", vals are hashes with possible stems as keys
my %stem;
my %toskip;  # IG headwords we don't want as stems, e.g. "dámáistí"
my %indef_gen_ok;  # mostly languages
my $mode = 0; # 0==GA.txt (words and numbers), 1=athfhocail (w/ standard/lemma)

sub add_feature {
    (my $tag, my $newfeature, my $newfeatureval) = @_;
	(my $upos, my $featstring) = $tag =~ m/^([A-Z]+)~(.+)$/;
    my %tb_dict;
	unless ($featstring eq '_') {
    	for my $f (split(/\|/,$featstring)) {
      	  (my $k, my $v) = split(/=/,$f);
      	  $tb_dict{$k} = $v;
		}
	}
   	$tb_dict{$newfeature} = $newfeatureval;
	my @ans;
	for my $k (sort keys %tb_dict) {
		push @ans, $k.'='.$tb_dict{$k};
	}
    return $upos.'~'.join('|',@ans);
}

# pass word/tag/lemma and adds to both %pos and %stem hashes
# which are used at the end for printing out dict
sub add_one {
	(my $w, my $t, my $s) = @_;
	if (exists($pos{$w})) {
		$pos{$w}->{$t} = 1;
	}
	else {
		$pos{$w} = { $t => 1 };
	}
	my $stemkey = "$w|$t";
	if (exists($stem{$stemkey})) {
		$stem{$stemkey}->{$s} = 1;
	}
	else {
		$stem{$stemkey} = { $s => 1 };
	}
}

sub read_skip {
	open(SKIP, "<:utf8", "skip.txt") or die "Could not open skip.txt: $!";
	while (<SKIP>) {
		chomp;
		$toskip{$_} = 1;
	}
	close SKIP;
}

read_skip();

sub read_langs {
	open(TEANGACHA, "<:utf8", "teangacha.txt") or die "Could not open teangacha.txt: $!";
	while (<TEANGACHA>) {
		chomp;
		$indef_gen_ok{$_} = 1;
	}
	close TEANGACHA;
}
# read others from "properButIndefinite"?
$indef_gen_ok{'Aidbhint'} = 1; # féilire Aidbhinte
$indef_gen_ok{'Aifreann'} = 1; # leabhar Aifrinn
$indef_gen_ok{'Breatimeacht'} = 1; # cúrsaí Breatimeachta
$indef_gen_ok{'Críostaíocht'} = 1; # teagasc Críostaíochta
$indef_gen_ok{'Gaeltacht'} = 1; # fear Gaeltachta
$indef_gen_ok{'Galltacht'} = 1; # ceantar Galltachta

read_langs();

# pipe GA.txt or athfhocail through this (see makefile)

# nouns that have a capital that I want to assign NOUN, not PROPN
my %nonproper = (
# Irish...
'Aifreann' => 1, 'Béarlóir' => 1, 'Bíobla' => 1, 'Bráman' => 1, 'Breatnaiseoir' => 1, 'Búdaí' => 1, 'Cóir-Thrádáil'=>1, 'Críostaí'=>1, 'dea-Ghael' => 1, 'Falangaí'=>1, 'Fínín' => 1, 'fíor-Ghael'=>1, 'Forann'=>1, 'Frainciseoir' => 1, 'Gaeilgeoir' => 1, 'Gael' => 1, 'Gall'=>1, 'Gall-Ghael'=>1, 'Gréagóir'=> 1, 'iar-Aire'=>1, 'iar-Phríomh-Aire'=>1, 'iar-Uachtarán'=>1, 'Laidineoir'=> 1, 'Lár-Limistéar'=>1, 'L-phláta'=>1, 'Luath-Óige'=>1, 'Móróg'=>1, 'Naitsí' => 1, 'Neamh-Chríostaí'=>1, 'Nósadóir' => 1, 'nua-Naitsí'=>1, 'Páiseadóir' => 1, 'Piocht'=>1, 'Poncán' => 1, 'Rúisiseoir'=>1, 'Sabóidire'=>1, 'Saorstátaire'=>1, 'Saraistín'=>1, 'Sean-Airteagal'=>1, 'Sean-Ghall'=>1, 'Sean-Ghael'=>1, 'sean-Pharlaimint'=>1, 'Séicire'=>1, 'Sior'=>1, 'Sóivéid'=>1, 'Stát-Pháirtí'=>1, 'Teamplóir' => 1, 'Trípháirtíocht'=>1, 'Úcráiniseoir'=>1, 'Vandal'=>1, 'Vicipéideoir'=>1, 'X-chrómasóm'=>1, 'Y-chrómasóm'=>1,
# Manx...
'dellal-L' => 1, 'lheiney-T' => 1, 'meir-Voirrey' => 1, 'post-L' => 1, 'scell-X' => 1,
);
# nouns ending in -a[e]ch, -[áoóú]ch that should be PROPN, not NOUN
# Nationalities are currently NOUN (since not Definite by default)
my %properach = (
'Atlantach' => 1, 'Ceatharlach' => 1, 'Domhnach' => 1, 'Gaelbhratach' => 1, 'Grásach' => 1, 'Luimneach' => 1, 'Naomhtheaghlach' => 1, 'Peintiteoch'=>1, 'Seisreach' => 1, 'Sligeach' => 1,
);
my $new_word_p = 1;
my $not_headword_p = 0;
my $st;
my $offset = 0;   # how many inflected forms into this headword are we
my $verb_p = 0;
my $plural = undef;
my $weakpl = undef;
my $focal;
my $vn;
my $pp;
while (<STDIN>) {
	chomp;
	my $line = $_;
	my $skipcheck = $line;
	if ($line =~ m/\t/) {
		$mode = 1;
		$skipcheck =~ s/^.+\t//;
	}
	if ($line eq '-') {
		$new_word_p = 1;
		$not_headword_p = 0;
	}
	# * examples with two spaces happen in GV.txt (verbs + oo, etc.)
    #   and also in athfhocail  "teine-abhar ábhar tine" e.g.
	#   Can't use either for tagdict of course.
	# * 127 occurs for OD77b stuff, for example (e.g. ata, eisc, inne)
	# as the first word of an entry (=> will skip all inflections)
	# and also with some verb tenses in the middle of an entry
	# (in which case it just skips those)
	# * 0 only occurs in athfhocail, for stuff like "bhfaighidh", etc.
	# * xx occurs as first word in GA.txt for similar stuff:"bhfaighidh", etc.
	elsif (($line =~ m/^xx / and $mode==0) or $line =~ m/ (0|127)$/ or $line =~ m/^[^\t]+ [^\t]+ /) {
		if ($new_word_p==1) {
			$new_word_p = 0;
			$offset = 0;
			$not_headword_p = 1;
		}
		else {
			$offset++;
		}
	}
	# more stuff to skip: 65/97 are datives
	elsif ((exists($toskip{$skipcheck}) or $line =~ m/ (65|97)$/) and $new_word_p==1) {
		$new_word_p = 0;
		$offset = 0;
		$not_headword_p = 1;
	}
	else {
		if ($not_headword_p) {
			$offset++;
			next;
		}
		my $tag;
		if ($mode==0) {
			$line =~ m/^(.+) ([0-9]+)$/;
			$focal = $1;
			$tag = $tags{$2};
		}
		elsif ($mode==1) {
			$line =~ m/^([^ ]+) .+\t([^ ]+) ([0-9]+)$/;
			$focal = $1;
			$st = $2;
			my $tagnum = $3;
			# future self: yes I'm throwing info away to reconsruct below
			$tagnum = 200+($tagnum % 8) if ($tagnum>207);
			if (exists($tags{$tagnum})) {
				$tag = $tags{$tagnum};
			}
			else {
				print STDERR "Problem converting numerical tag $tagnum on this line: $line\n";
				exit(1);
			}
		}
		else {
			print STDERR "Error: unexpected mode $mode\n";
			exit(1);
		}
		if ($new_word_p==1) {
			$new_word_p = 0;
			$st = $focal if ($mode==0);
			$plural = undef;
			$weakpl = undef;
			$offset = 0;
			$verb_p = ($tag =~ m/^VERB~/);
		}
		if ($tag =~ m/^(ADP|AUX|DET|PRON)~/) {  # handled in moretags.tsv now
			$offset++;
			next;
		}
		if ($focal eq 'xx') { # only gets here for mode==1
			$offset++;
			next;
		}
		if ($focal =~ m/^(n[AEIOUÁÉÍÓÚ]|n-[aeiouáéíóú]|m[Bb]|g[Cc]|n[DdGg]|bh[Ff]|b[Pp]|d[Tt])/) {
			$tag = add_feature($tag, 'Form', 'Ecl');
		}
		elsif ($focal =~ m/^[BbCcDdFfGgMmPpSsTt]h/ and $st !~ m/^.h/) {
			$tag = add_feature($tag, 'Form', 'Len');
		}
		elsif ($focal =~ m/^h[AEIOUÁÉÍÓÚaeiouáéíóú]/ and $st !~ m/^h/) {
			$tag = add_feature($tag, 'Form', 'HPref');
		}
		# anything with a cap treated as PROPN, except for
		# nationalities like Sasanach, Francach, etc.
		# and stuff in the hash nonproper above...
		if ($tag =~ m/^NOUN~/ and $focal =~ m/[A-ZÁÉÍÓÚ]/ and !exists($nonproper{$st}) and (exists($properach{$st}) or $st !~ m/(ae?|[áóú]|[eí]o)ch$/)) {
			$tag =~ s/^NOUN/PROPN/;
		}
		if ($verb_p) {  # add Person= feature if needed
			# MAJOR MAGIC NUMBER SITCH!!
			if (($offset>=32 and $offset<=37)or($offset>=44 and $offset<=49)) {
				# Person=1, Number=Sing
				$tag = add_feature($tag, 'Person', '1');
				$tag = add_feature($tag, 'Number', 'Sing');
			}
			elsif ($offset==52 or ($offset>=65 and $offset<=70)) { # imperative, imperfect, conditional
				# Person=2, Number=Sing
				$tag = add_feature($tag, 'Person', '2');
				$tag = add_feature($tag, 'Number', 'Sing');
			}
			elsif ($offset>=94 and $offset<=113) {
				# Person=1, Number=Plur
				$tag = add_feature($tag, 'Person', '1');
				$tag = add_feature($tag, 'Number', 'Plur');
			}
			elsif ($offset>=114 and $offset<=117) {
				# Person=2, Number=Plur
				$tag = add_feature($tag, 'Person', '2');
				$tag = add_feature($tag, 'Number', 'Plur');
			}
			elsif (($offset>=135 and $offset<=138)or($offset>=142 and $offset<=144)or($offset>=148 and $offset<=153)) {
				# Person=3, Number=Plur
				$tag = add_feature($tag, 'Person', '3');
				$tag = add_feature($tag, 'Number', 'Plur');
			}
			#elsif (($offset>=156 and $offset<=162)or($offset>=166 and $offset<=176)) {
				# Person=0
			#	$tag = add_feature($tag, 'Person', '0');
			#}
		}
		$tag = 'DET~_' if ($tag =~ m/^ADJ~/ and $focal =~ m/^(gach|seo|sin|dagh|shoh|shen)$/);
		$tag = 'PRON~Reflexive=Yes' if ($tag =~ m/^ADJ~/ and $focal =~ m/^(féin|hene)$/);
		$tag =~ s/^S/C/ if ($tag =~ m/^SCONJ~/ and $focal =~ m/^(ach|agus|nó|agh|as|ny)$/);

		$vn = $focal if ($verb_p and $offset==1);   # ugh magic numbers
		$pp = $focal if ($verb_p and $offset==16);   # ugh magic numbers
		if ($verb_p and $offset >= 1 and $offset <= 15) {
			add_one($focal,$tag, $vn);  # add with Case/Gender/Number
			my $origtag = $tag;
			$tag = add_feature($tag, 'Definite', 'Def');
			add_one($focal,$tag, $vn);  # add with Case/Gender/Number/Definite
			$tag = $origtag;
			if ($tag =~ m/Case=Nom/) {
				$tag =~ s/Case=Nom\|//;
				$tag =~ s/Gender=.+$/VerbForm=Vnoun/; # keeps Form if there
				add_one($focal,$tag,$vn) unless ($tag =~ m/[^a-z]Form=/); # ag cur
				$tag =~ s/=Vnoun/=Inf/;
				# if eclipsed must be Definite=Def "á n-achtáil"
				# note that prefix-h can be Def or Indef (rud éigin le hithe)
				add_one($focal,$tag,$vn) unless ($tag =~ m/Form=Ecl/);
				$tag = add_feature($tag, 'Definite', 'Def');
				add_one($focal,$tag,$vn);
			}
		}
		elsif ($verb_p and $offset >= 16 and $offset <= 31) {
			add_one($focal, $tag, $pp);
			if ($tag =~ m/Number=Plur$/) {
				$tag =~ s/Number=Plur/VerbForm=Part/;
				add_one($focal, $tag, $pp);
			}
		}
		elsif ($verb_p and $offset >= 32) {
			add_one($focal, $tag, $st);
			# could require initial bcdfgpt to be mutated
			# but there's also non-std "ná fuil", "ná taithíonn", srl.
			$tag = add_feature($tag, 'Polarity', 'Neg');
			add_one($focal, $tag, $st);
		}
		elsif ($tag =~ m/^(PROPN|NOUN)~/) {
			if (!defined($plural) and $tag =~ m/Number=Plur/) {
				$plural = $focal;
			}
			if ($tag =~ m/Case=Gen.*Number=Plur/) {
				if (!defined($weakpl)) {
					$weakpl = ($focal ne $plural);
				}
				if ($weakpl) {
					$tag = add_feature($tag, 'NounType', 'Weak');
				}
				else {
					$tag = add_feature($tag, 'NounType', 'Strong');
				}
			}
			# if PROPN, should only write w/o Def in select cases...
			if ($tag =~ m/^NOUN/ or ($tag =~ m/^PROPN.*Case=Gen/ and exists($indef_gen_ok{$st}))) {
				add_one($focal,$tag, $st);
			}
			$tag = add_feature($tag, 'Definite', 'Def');
			add_one($focal,$tag, $st);
		}
		elsif ($tag =~ m/^ADJ~/) {
			my $lenited_p = 0;
			$lenited_p = 1 if ($tag =~ m/Form=Len/);
			my $unlenitedlenitable_p = 0;
			$unlenitedlenitable_p = 1 if ($tag !~ m/Form=Len/ and $focal =~ m/^([BbCcDdFfGgMmPpTt]|[Ss][lnraeiouáéíóú])/);
			if ($tag =~ m/Number=Plur/) {
				$tag = add_feature($tag, 'Case', 'Nom');
				$tag = add_feature($tag, 'Gender', 'Masc');
				$tag = add_feature($tag, 'NounType', 'Slender');
				add_one($focal,$tag, $st) unless ($unlenitedlenitable_p);
				$tag =~ s/Gender=Masc/Gender=Fem/;
				add_one($focal,$tag, $st) unless ($unlenitedlenitable_p);
				unless ($lenited_p) {
					$tag =~ s/NounType=Slender/NounType=NotSlender/;
					add_one($focal,$tag, $st);
					$tag =~ s/Gender=Fem/Gender=Masc/;
					add_one($focal,$tag, $st);
					$tag =~ s/Case=Nom/Case=Gen/;
					$tag =~ s/NounType=NotSlender/NounType=Strong/;
					add_one($focal,$tag, $st);
					$tag =~ s/Gender=Masc/Gender=Fem/;
					add_one($focal,$tag, $st);
				}
			}
			elsif ($tag =~ m/Case=Nom.*Number=Sing/) {
				$tag = add_feature($tag, 'Gender', 'Masc');
				add_one($focal,$tag, $st) unless ($lenited_p);
				$tag =~ s/Gender=Masc/Gender=Fem/;
				add_one($focal,$tag, $st) unless ($unlenitedlenitable_p);
				$tag =~ s/Case=Nom/Case=Gen/;
				$tag =~ s/Number=Sing/Number=Plur/;
				$tag = add_feature($tag, 'NounType', 'Weak');
				add_one($focal,$tag, $st) unless ($lenited_p);
				$tag =~ s/Gender=Fem/Gender=Masc/;
				add_one($focal,$tag, $st) unless ($lenited_p);
				$tag =~ s/\|Gender=.+$//;
				$tag =~ s/Case=Gen/Degree=Pos/;
				add_one($focal,$tag, $st);
			}
			elsif ($tag =~ m/Case=Gen.*Number=Sing/) {
				if ($tag =~ m/Case=Gen.*Gender=Masc/) {
					add_one($focal,$tag, $st) unless ($unlenitedlenitable_p);
				}
				elsif ($tag =~ m/Case=Gen.*Gender=Fem/) {
					add_one($focal,$tag, $st) unless ($lenited_p);
					$tag =~ s/\|Gender=Fem.*$//;
					$tag =~ s/Case=Gen/Degree=Cmp,Sup/; # can be lenited in past
					add_one($focal,$tag, $st);
				}
			}
			else { # code=130, Degree=Pos|Form=HPref
				add_one($focal,$tag, $st);
			}
		}
		else { # not VERB, NOUN, ADJ
			add_one($focal,$tag, $st);
		}
		$offset++;
	}
}

# k's are surface forms
for my $k (sort keys %pos) {
	# tag is a combo POS~Feature=X
	for my $tag (sort keys %{$pos{$k}}) {
		(my $pos, my $feats) = $tag =~ m/^([A-Z]+)~(.+)$/;
		for my $lemma (sort keys %{$stem{"$k|$tag"}}) {
			print "$k\t$lemma\t$pos\t_\t$feats\n";
		}
	}
}
exit 0;

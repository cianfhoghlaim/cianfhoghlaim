#!/usr/bin/perl

use strict;
use warnings;
use utf8;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

my %morphemes = (
	'PP' => ['','ni','nti'], # preprefix (neg.), incompat. with non-empty NM
	'SM' => ['n','u','mu','tu','a','ba','i','ri','ki','bi','zi','ru','ka','bu','ku','ha'],	# subject markers
	'NM' => ['','ta'], # negative marker, incompatible with non-empty PP
	'TM' => ['','ra','aa','aara','zaa','racyaa','ka','raka','ooka','ii'],  # tense marker; Kimenyi 1980, p.212; 0,1,or 2 allowed, all possibilities here?
	'NA' => ['','na'],  # morpheme meaning "also"
	'OM' => ['ku','ba','tu','mu','wu','yi','ri','ya','ki','bi','zi','ru','ka','bu','ha','n'],	# object markers, 0-4 permitted - up to user=>not optional here
	'REFL' => ['','íi'],	# reflective morpheme
	# 'VR' => [''],   # verbal roots read from a file
	'EXT' => [''],  # extensions are included in VR now
	'REV' => ['','uur','uuk'],	# reversive suffix
	'RECIP' => ['','an'],	# reciprocal suffix
	'INSTR' => ['','iish','y'],	# instrumental suffix
	'NEUT' => ['','ik'],	# neutral suffix
	'APPL' => ['','ir'],	# applicative suffix
	'IZ' => ['','iz'],	# Kimenyi p.6 - suffix
	'PASSIVE' => ['','w'],	# passive suffix
	'AM' => ['ye','a','aga'], # aspect marker ('e' subjunctive Kim. p.1532?) - 'y'+'e' confused with 'ye' by affix file?
	'PS' => ['','ho','mo'],		# post-suffix
	);


open(ROOTS, "<:utf8", "roots.txt") or die "Could not open file of verb roots: $!\n";
while (<ROOTS>) {
	chomp;
	s/[ \t].*$//;
	push @{$morphemes{'VR'}}, $_;
}
close ROOTS;

# standard orthography => no tones, no short-long distinction in vowels
# three or more can happen, ba+ta+aa+na+...
sub standardize {
	(my $str) = @_;
	for ($str) {
		tr/áéíóú/aeiou/;
		s/aa+/a/g;
		s/ee+/e/g;
		s/ii+/i/g;
		s/oo+/o/g;
		s/uu+/u/g;
	}
	return $str;
}

# Input like "+uuk+an+y+ik++iz+w+a+mo+"
# output is surface string
sub alternations {
	(my $str) = @_;

	my $copy = $str;

	for ($str) {
		s/\++/+/g;
		s/\+\^/^/g;
		s/\^\+/^/g;
#print "$_\n";
		s/\+n([\^+][aeiouáéíóú])/+ny+$1/g; # palatize -n- = "I, me" b4 vowel
		s/([fghkv])u([\^+][aeiouáéíóú])/$1$2/g;  # deletion, more specific than glide rule below
		s/[eéií]([\^+][aeiouáéíóú])/y$1/g;  # glide; Kimenyi p.15
		s/[oóuú]([\^+][aeiouáéíóú])/w$1/g;  # glide; Kimenyi p.15
		s/[aá]+([\^+])[ií]+/$1é/g;  # vowel coalescence; Kimenyi p.16
		s/[aá]+([\^+][aeouáéóú])/$1/g;  # a-deletion, top p.15
		s/([eéoó][^aeiouáéíóú+])\^iish\+/$1^eesh+/;  # vowel harmony, only applies to three suffixes 
		s/([eéoó][^aeiouáéíóú+])\^i([rk])\+/$1^e$2+/; #  "    "   (note not global)
		s/\+k([^+\^]*\^[chfkpst])/+g$1/;  # Dahl's law, k->g  (not global)
		s/\+t([^+\^]*\^[chfkpst])/+d$1/;  # Dahl's law, t->d  (not global)
		s/n([\^+][bfhpv])/m$1/g;  # nasal assimilation
#		s/([mn][\^+]?)k/$1h/g;  # consonant aspiration
#		s/([mn][\^+])p([^f])/$1h$2/g;  # consonant aspiration, not on +pf!
#		s/([mn][\^+])t([^s])/$1h$2/g;  # consonant aspiration, not on +ts!
#print "$_\n";
		s/(n[\^+])r/$1d/g;  # consonant strengthening
		s/m([\^+])pf/m$1f/g;  # deaffrication; no need for "n"- changed above
		s/n([\^+])ts/n$1s/g;  # deaffrication - JM has preceding "n" only
		s/y([\^+]?y)/$1/g;    # consonant deletion, yy,y+y->y
		s/y([\^+]?w)/$1/g;    # consonant deletion, yw->w
		s/(w[\^+]?)[wy]/$1/g;    # consonant deletion, wy or ww -> w
#print "$_\n";
		s/r([\^+]y[ei](\+[hm][oó])?[\^+])$/$1/;    # consonant deletion, r+ye$ -> ye, including with optional postsuffix -ho or -mo
		# AM -ye- => ize after some consonants, Kimenyi p.19
#		s/([sz][\^+])y(e(\+[hm][oó])?[\^+])$/$1iz$2/;
		s/mn([\^+])y(e(\+[hm][oó])?[\^+])$/m$1iz$2/;
		# other mutations before the -ye aspect marker
		s/p([\^+])y([ei](\+[hm][oó])?[\^+])$/p$1k$2/;
		s/b([\^+])y([ei](\+[hm][oó])?[\^+])$/b$1g$2/;
		s/m([\^+])y([ei](\+[hm][oó])?[\^+])$/m$1n$2/;
		s/([hjnsz][\^+])y([ei](\+[hm][oó])?[\^+])$/$1$2/;
		s/[dg]([\^+])y([ei](\+[hm][oó])?[\^+])$/z$1$2/;
		s/t([\^+])y([ei](\+[hm][oó])?[\^+])$/s$1$2/;
		s/k([\^+])y([ei](\+[hm][oó])?[\^+])$/ts$1$2/;
		s/n([\^+]?n)/$1/g;    # consonant deletion, nn or n+n->n
#print "$_\n";
	}
	if ($copy eq $str) {
		$str =~	s/[\^+]//g;
		return $str;
	}
	else {
		return alternations($str);
	}
}

sub generate {
	(my $arg) = @_;
	if ($arg =~ m/[\^+]([A-Z]+)[\^+]/) {
			my $code = $1;
			die "Illegal morpheme code: $code" unless (exists($morphemes{$code}));
			foreach my $str ( @{$morphemes{$code}} ) {
				my $copy = $arg;
				# long-distance dependencies; tense/aspect Kimenyi p.212
				$copy =~ s/\+NM\+/++/ if ($code eq 'PP' and $str ne '');
				$copy =~ s/\+AM\+/+a+/ if ($code eq 'TM' and ($str ne 'ra' and $str ne 'aa' and $str ne 'aara'));
				$copy =~ s/([\^+])$code([\^+])/$1$str$2/;
				generate($copy);
			}
		}
	else {
		my $op = standardize(alternations($arg));
		print "$op ($arg)\n";
	}
}

# input strings look like: PP+SM+NM+TM+NA+OM+REFL, etc. - see list above
# or else it's possible to hardcode in particular values for these
# if VR or a specific verb root is included, surround it by ^'s and not +'s
while (<STDIN>) {
	chomp;
	s/^/+/;
	s/$/+/;
	generate($_);
}

exit 0;

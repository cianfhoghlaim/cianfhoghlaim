#!/usr/bin/perl

use strict;
use warnings;
use utf8;
use Locale::PO;
use Encode;


binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

my %pos = (
	'a' => 'aid',
	'adv' => 'db',
	'aindec' => 'aid',
	'art' => 'alt',
	'card' => 'uimhir',
	'conj' => 'cónasc',
	'excl' => 'uaill',
	'interr' => 'aid',
	'n' => 'af',
	'nf' => 'bain',
	'nm' => 'fir',
	'ord' => 'uimhir',
	'pn' => 'for',
	'poss' => 'sealbh',
	'prep' => 'réamh',
	'pronm' => 'réamh',
	'u' => '',
	'v' => 'br',
	'vcop' => 'cop',
);


my %hard;
my %incorpus;
my %hirank;
my %fauxamis;
my %altdone;
my %gd2ga;
my $aref = Locale::PO->load_file_asarray('gd2ga.po');
foreach my $msg (@$aref) {
	my $comment = decode("utf8", $msg->comment());
	my $id = decode("utf8", $msg->msgid());
	my $str = decode("utf8",$msg->msgstr());
	if (defined($id) && defined($str)) {
		unless ($id eq '""' or $str eq '""') {
			$id =~ s/"//g;
			$str =~ s/"//g;
			if (defined($comment)) {
				$fauxamis{$id} = 1 if ($comment =~ /false friend/i);
				$hard{$id} = 1 if ($comment =~ /focal doiléir/i);
			}
			$gd2ga{$id} = $str;  # semi-colon separated often
		}
	}
}

my $rank = 1;
open(STEMFREQ, "<:utf8", "stemfreq.txt") or die "Could not open stemfreq.txt: $!";
while (<STEMFREQ>) {
	chomp;
	s/ .*//;
	$incorpus{$_} = 1;
	$hirank{$_} = 1 if ($rank <= 1000);
	$rank++;
}
close STEMFREQ;

sub normalu {
	(my $l) = @_;
	$l = uc($l);
	$l =~ s/À/A/g;
	$l =~ s/Á/A/g;
	$l =~ s/È/E/g;
	$l =~ s/É/E/g;
	$l =~ s/Ì/I/g;
	$l =~ s/Í/I/g;
	$l =~ s/Ò/O/g;
	$l =~ s/Ó/O/g;
	$l =~ s/Ù/U/g;
	$l =~ s/Ú/U/g;
	$l =~ s/[ -]//g;  # ban-righ => banrigh
	return $l;
}

my $letter = '';
open(FOCLOIR, "<:utf8", "focloir.txt") or die "Could not open focloir.txt: $!";
while (<FOCLOIR>) {
	chomp;
	(my $focal, my $g1, my $g2, my $std) = /^(.+)\t(.+)\t(.+)\t(.+)$/;
	$focal =~ m/^'*(.)/;	
	my $thisletter = normalu($1);
	if ($thisletter ne $letter) {
		print '\chapter*{'.$thisletter."}\n";
		print '\addcontentsline{toc}{chapter}{'.$thisletter."}\n";
		$letter = $thisletter;
	}
	if ($std eq '0') {
		my $uid = $focal;
		$uid =~ s/ /_/g;
		(my $focalamhain, my $roinncainte) = $focal =~ m/^([^_]+)_(.+)$/;
		my $rc = $pos{$roinncainte};
		print '\setlength{\hangindent}{10pt}'."\n";
		print '\noindent';
		print '\textdbend' if (exists($fauxamis{$focal}));
		print '$\bigstar$' if (exists($hard{$focal}) and exists($hirank{$focalamhain}));
		print '\textdagger' unless ($focalamhain =~ m/ / or exists($incorpus{$focalamhain}));
		print '\hypertarget{'.$uid.'}{\textbf{'.$focalamhain.'}}';
		print ', \textit{'.$rc.'}:' unless ($rc eq '');
		print "\n";
		print '\markboth'."{$focalamhain}{$focalamhain}\n";
		if (exists($gd2ga{$focal})) {
			my $hack = $gd2ga{$focal};
			if ($hack =~ m/^an /) {
				$hack =~ s/;na .+$//;
			}
			$hack =~ s/[0-9]*_[a-z]+//g;
			$hack =~ s/;/, /g;
			$hack =~ s/$/./;
			$hack =~ s/^([^,]+), \1([,.])/$1$2/;
			$hack =~ s/, ([^,]+), \1([,.])/, $1$2/;
			print "$hack\n";
		}
		else {
			print STDERR "Gan sainmhíniú Gaeilge: $focal\n";
		}
		print "\n";
	}
	else {  # $std ne '0' => $focal is an alt spelling
		$focal =~ s/[0-9]*_/_/;
		if (normalu($focal) ne normalu($std)) {
			my $xref = $std;
			$xref =~ s/ /_/g;
			(my $focalamhain, my $roinncainte) = $focal =~ m/^([^_]+)_(.+)$/;
			(my $stdamhain, my $stdroinncainte) = $std =~ m/^([^_]+)_(.+)$/;
			my $rc = $pos{$roinncainte};
			my $stdrc = $pos{$stdroinncainte};
			if (!exists($altdone{normalu($focal)})) {
				print '\setlength{\hangindent}{10pt}'."\n";
				print '\noindent\textbf{'.$focalamhain.'}';
				print ', \textit{'.$rc.'}' unless ($rc eq '');
				print "\n";
				print '\markboth'."{$focalamhain}{$focalamhain}\n";
				print '$\rightarrow$ \hyperlink{'.$xref."}{$stdamhain, \\textit{$stdrc}}.\n";
				print "\n";
				$altdone{normalu($focal)} = 1;
			}
		}
	}
}
close FOCLOIR;

exit 0;

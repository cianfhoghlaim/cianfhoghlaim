#!/usr/bin/perl

use strict;
use warnings;
use DB_File;
use Fcntl;
use Locale::PO;
use Lingua::EN::Sentence qw( get_sentences );
use Lingua::EN::Tagger;
# use Text::Diff;
use File::Copy;

if (@ARGV == 0) {
	die "Usage: $0 COMHAIDPO\n";
}

my %veic;
my %corpas;
my %lemmat_wordlist;
my %lemmat_rules;
my %stoplist;
my %currentlemmas;
my %freqhash;
my %lenhash;
my @focloir;
my $N = 0;
my $en_tagger = new Lingua::EN::Tagger;
my $corpaspath = '/usr/local/share/corpas';

my $vdb = tie %veic, "DB_File", "$corpaspath/veicteoir.db", O_RDONLY, 0644, $DB_HASH || die $!;
my $cdb = tie %corpas, "DB_File", "$corpaspath/mor.db", O_RDONLY, 0644, $DB_HASH || die $!;
open (STOPS, "$corpaspath/stoplist");
while (<STOPS>) {
	chomp;
	$stoplist{$_}++;
}
close STOPS;
open (FREQFILE, "<:utf8", '/usr/local/share/crubadan/en/FREQ') or die "Error opening English frequencies: $!\n";
while (<FREQFILE>) {
	chomp;
	my ($freq,$word) = split;
	$word =~ tr/A-Z/a-z/;
	$freq++;  # smoothing
	$freqhash{$word} = 0 unless (exists($freqhash{$word}));
	$freqhash{$word} += $freq;
	$N += $freq;
}
close FREQFILE;
# actually store probability that a random word is NOT the key
foreach (keys %freqhash) {
	$freqhash{$_} = 1 - $freqhash{$_}/$N;
}
open (LENFILE, "$corpaspath/lengths.txt") or die "Error opening sentence length file: $!\n";
while (<LENFILE>) {
	chomp;
	my ($tag,$len) = split;
	$lenhash{$tag} = $len;
}
close LENFILE;
open (DICT, "<:utf8", '/home/kps/gaeilge/diolaim/c/en') or die "Error opening English-Irish dictionary: $!\n";
while (<DICT>) {
	push @focloir,$_ if (/^([^ ]+)  /);
}
close DICT;
# ASCII
readrules('/home/kps/clar/sonrai/rules.bnc');
# ASCII
readirregfile('/home/kps/clar/sonrai/words.bnc');
my $done_p = "";


sub my_warn
{
return 1;
}

sub keep_if_keepable
{
my ($cand) = @_;
if ($cand =~ m/../ && $cand =~ m/[a-z]/ && $cand =~ m/^[A-Za-z'-]+$/) {
	$currentlemmas{$cand}++ unless (exists($stoplist{$cand}));
}
}

# takes input text and fills currentlemmas hash with all lemmas
sub lemmatize
{
	my ($input) = @_;
	my $sentences = get_sentences($input);
	%currentlemmas = ();
	foreach (@$sentences) {
		my $tagged = $en_tagger->add_tags( $_ );
		while ($tagged =~ m/<([^>]+)>([^<]+)<\/[^>]+>/g) {
			my $pos = "\U$1";
			my $word = $2;
			my $lemma=lc($word);
			if ($word=~/[\w\'-]+/) {
			    if (exists $lemmat_wordlist{$pos}{$lemma}) { 
				$lemma=$lemmat_wordlist{$pos}{$lemma};
			    } elsif (exists $lemmat_rules{$pos}) {
				my @rules=@{$lemmat_rules{$pos}};
				my $i=0;
				$_=$lemma;
				do { 
				    if ($rules[$i]) {
					eval($rules[$i]) ;
					warn "error in $word: $rules[$i]: $@" if $@;
				    }
				} until (($_ ne $lemma) or ($i++>$#rules));
				$lemma=$_;
			    }
			} else { #punctuation marks
			    if ($pos=~/\W+/) {$pos='PUN'};
			};
			$pos=~s/PUNCT/PUN/;
			$pos=~s/CS22/IN22/;
			keep_if_keepable("\L$word");
			keep_if_keepable($lemma);
		}
	}
}



sub userinput {
	my ($prompt) = @_;
	print "$prompt: ";
	$| = 1;          # flush
	$_ = getc;
	my $ans = $_;
	$_ = getc while (m/[^\n]/);
	return $ans;
}


# called right after lemmatize, so %currentlemmas is full
# job of this function is to write out /tmp/focloirin.txt hits file
sub get_focloir_hitz
{
	open OUTPUT, ">", "/tmp/focloirin.txt";
	print OUTPUT "English-Irish dictionary\n";
	my @hitz;
	foreach my $word (keys %currentlemmas) {
		push @hitz, grep(/^$word  /i, @focloir);
	}
	print OUTPUT $_ foreach (sort @hitz);
	close OUTPUT;
}

# called right after lemmatize, so %currentlemmas is full
# job of this function is to write out /tmp/fuzzies.po hits file
sub get_best_corpus_hitz
{
	my %candidates;
	foreach my $word (keys %currentlemmas) {
		my $prob = 1 - 1/$N;
		$prob = $freqhash{$word} if (exists($freqhash{$word}));
		$word =~ s/$/\x{000}/;
		if (exists($veic{$word})) {
			my $vec = $veic{$word};
			$vec =~ s/.$//;
			my @tags = split / /,$vec;
	                my @engtags = grep(/-b:/, @tags);
			my %tags;
			$tags{$_}++ foreach (@engtags);  # must make unique!
			foreach my $tag (keys %tags) {
				if ($lenhash{$tag} == 0) {
					print STDERR "Warning: word $word apparently found in sentence with no words or stopwords only: $tag\n";
				}
				else {
					$candidates{$tag} = 0 unless (exists($candidates{$tag}));
					$candidates{$tag} += -log(1 - $prob**$lenhash{$tag});
				}
			}

		}
	}
	my $count = 1;
	# don't use utf8 here...
	open OUTPUT, ">", "/tmp/fuzzies.po";
	foreach my $en (sort {$candidates{$b} <=> $candidates{$a}} keys %candidates) {
		print OUTPUT "#: >>F$count<< ($en)";
		printf OUTPUT " E=%.3f\n", $candidates{$en};
		$en =~ s/$/\x{000}/;
		my $temp = $corpas{$en};
		$temp =~ s/(^|[^\\])"/$1\\"/g;
		$temp =~ s/^/msgid "/;
		$temp =~ s/.$/"/;
		print OUTPUT "$temp\n";
		my $ga = $en;
		$ga =~ s/-b:/:/;
		$temp = $corpas{$ga};
		$temp =~ s/(^|[^\\])"/$1\\"/g;
		$temp =~ s/^/msgstr "/;
		$temp =~ s/.$/"/;
		print OUTPUT "$temp\n";
		$count++;
		last if ($count > 25);
	}
	close OUTPUT;
}

sub vim_translate
{
my ($id) = @_;
my $stripped = $id;
$stripped =~ s/[&~]//g;
$stripped =~ s/"_:[^"]*\\n"/""/;  # KDE comments in msgid
$stripped =~ s/\\.//g;
$stripped =~ s/[=:<?*>_\/+]/ /g;
$stripped =~ s/^msgid //;
lemmatize($stripped);
get_best_corpus_hitz();
get_focloir_hitz();
open OUTPUT, ">/tmp/toedit.po";
print OUTPUT "$id\nmsgstr \"\"\n";
close OUTPUT;
system 'cp -f /home/kps/.vimrc /home/kps/.vimrcpo.bak';
system 'cp -f /home/kps/.poeditrc /home/kps/.vimrc';
system 'vim -n /tmp/toedit.po';
system 'cp -f /home/kps/.vimrcpo.bak /home/kps/.vimrc';
open INPUT, "</tmp/toedit.po";
my $msgstr_started = '';
my $ans = '';
while (<INPUT>) {
	chomp;
	if (/^msgstr "/) {
		$msgstr_started = 'true';
		s/^msgstr +"/"/;
		s/"\s*$//;
		$ans .= $_;
	}
	else {
		if ($msgstr_started) {
			s/^ *"//;
			s/"\s*$//;
			$ans .= $_;
		}
	}
}
close INPUT;
$ans =~ s/$/"/ if $ans;
return $ans;
}


# takes a msg, go through all of the UI motions and return the
# hopefully translated msgstr
sub translate_me
{
	my ($msg) = @_;
	my $clean_id = $msg->dump;
	$clean_id =~ s/^.*\nmsgid "/msgid "/s;
	$clean_id =~ s/\nmsgstr ".*//s;
	my $temp = vim_translate($clean_id);
	if ($temp) {
		$msg->msgstr($msg->dequote($temp));
	}
	else {
		$done_p = 'true';
	}
	return 1;
}

my $toskip=0;

#### MAIN STARTS HERE #####
while ($ARGV = shift @ARGV) {
	if ($ARGV =~ m/^\+([0-9]+)/) {
		$toskip = $1;
		next;
	}
	my $aref;
	system "sed '/^#~/,\$d' $ARGV > /tmp/tmpinput.po";
{

	local $SIG{__WARN__} = 'my_warn';
	$aref = Locale::PO->load_file_asarray('/tmp/tmpinput.po');
}
	my $counter = 0;
	foreach my $msg (@$aref) {
		my $id = $msg->msgid();
		my $str = $msg->msgstr();
		$counter++;
		if (defined($id) && defined($str) && $counter > $toskip) {
			if ($str and $id) {
				if ($str eq '""') {
					Locale::PO->save_file_fromarray('/tmp/temp.po',$aref) if (translate_me($msg));
				}
				last if $done_p;
			}
		}
	}
	Locale::PO->save_file_fromarray('/tmp/temp.po',$aref);
	my $rv = system '/usr/bin/msgcat --width=80 /tmp/temp.po > /tmp/temp2.po';
	if ($rv > 0) {
		print STDERR "Syntax errors in PO file, aborting...\n";
		exit 1;
	}
	else {
		system "/home/kps/clar/libexec/defunctfix $ARGV /tmp/temp2.po";
		my $rv2 = system "diff -u $ARGV /tmp/temp2.po";
#		my $diff = diff $ARGV, '/tmp/temp2.po', { STYLE => "Unified" };
		if ($rv2) {
#			print $diff;
			my $ok='?';
			while ($ok =~ m/^[^YNyn]/) {
				$ok=userinput('Commit changes (y/n)?');
			}
			copy('/tmp/temp2.po', $ARGV) if ($ok =~ m/^[Yy]/);
		}
		else {
			print "File unchanged.\n";
		}
	}
	print "Restart with \"$0 +$counter $ARGV\"\n";
}

# untie %corpas;
# untie %veic;
exit 0;


sub readrules {
    my ($input)=@_;
    my $curpos='';
    my $left;
    my $right;
    my $lengthstr;
    open(IN,$input) or die "Can't open file $input\n";
    while (<IN>) {
	s/\#.*//;
#	chomp; the last space is left for deleting rules
	if (/^([\w\$]+)/) {
	    $curpos=$1;
	    $lemmat_rules{$curpos}=[];
	} elsif (($lengthstr,$left,$right)=/\s+([<>\d]*)\s+([\w\'-]+)\s+(\w*)/) {
	    my $nextreplt=1;
	    my $direction;
	    my $length;
	    if (($direction,$length)=$lengthstr=~/([<>])(\d+)/) {
		if ($direction eq '>') {
		    $left="(..)".$left; 
		    $right='$'.$nextreplt.$right;
		    $nextreplt++;
		} elsif ($direction eq '<') {
		    $length--;
		    $left="^(.{1,$length})".$left; 
		    $right='$'.$nextreplt.$right;
		    $nextreplt++;
		} else {
		    print "error: wrong direction in $_ \n" if $_;
		}
	    };
	    if ($left=~/CC/) {
		$left=~s/CC/([^aeiouy])\\1/g;
		$right=~s/C/\$$nextreplt/;
		$nextreplt++;
	    } elsif ($left=~s/([VCR]+)/($1)/) {
		my $phonolog=$1;
		$left=~s/V/[aeiouyr]/g;
		$left=~s/C/[^aeiouy]/g;
		$left=~s/R/r/g;
		$right=~s/$phonolog/\$$nextreplt/;
		$nextreplt++;
	    };
	    my $rule="s/$left\$/$right/";
	    my @rules=@{$lemmat_rules{$curpos}};
	    push @rules, $rule;
	    $lemmat_rules{$curpos}=[@rules];
	} else {
	    print "error: cannot read the rule in $_ \n" if $_=~/\S/;
	}
    }
    close(IN);
}

sub readirregfile {
    my ($input)=@_;
    my $curpos='';
    my $lemma;
    my $word;
    open(IN,$input) or die "Can't open file $input\n";
    while (<IN>) {
	s/\#.*//;
#	chomp; the last space is left for 
	if (/^([\w\$]+)/) {
	    $curpos=$1;
	} elsif (($word,$lemma)=/\s+([\w\'-]+)\s+([\w\'-]*)/) {
	    $lemmat_wordlist{$curpos}{$word}=($lemma)? $lemma : $word;
	} else {
	    print "error: cannot read the word-lemma pair in $_ \n" if $_=~/\S/;
	}
    }
    close(IN);
}

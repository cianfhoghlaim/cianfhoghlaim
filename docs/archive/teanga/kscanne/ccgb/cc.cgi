#!/usr/bin/perl -wT

use strict;
use CGI;
use utf8;
use Encode qw(decode_utf8 is_utf8);

binmode STDOUT, ":utf8";

$CGI::DISABLE_UPLOADS = 1;
$CGI::POST_MAX        = 1024;

$ENV{PATH}="/bin:/usr/bin";
delete @ENV{ 'IFS', 'CDPATH', 'ENV', 'BASH_ENV' };

my $SEARCHENGINE = '/usr/local/bin/ccweb';
my @shellargs;
my $q = new CGI;
$q->charset('UTF-8');
my( $ionchur ) = $q->param( "foirm_ionchur" ) =~ /^([^\x{00}-\x{1F}#%&()*+\/:;<>{}|~`_@]+)$/;
#if (!is_utf8($ionchur)) {
#	$ionchur = decode_utf8($ionchur);
#}
my( $hits ) = $q->param( "hits" ) =~ /^([0-9]+)$/;
my( $format ) = $q->param( "format" ) =~ /^([a-z]+)$/;

my @allargs = $q->param;
push @shellargs, "--max=$hits";
push @shellargs, "--html"   if ( $format eq "html" );
push @shellargs, "--mutate" if ( "@allargs" =~ /mutate/ );

print $q->header( "text/$format",
	-charset=>'UTF-8');     # http headers, not html headers!

unless ( $ionchur ) {
	print '<HTML><META HTTP-EQUIV="REFRESH" CONTENT="0;URL=http://borel.slu.edu/corpas/"></HTML>';
	exit 0;
}


while ($ionchur =~ m/("[^"]+"|[^" ]\S+)/g) {
	my $term = $1;
	$term =~ s/^"//;
	$term =~ s/"$//;
	push @shellargs, $term;
}


local *PIPE;


#unless ( $ionchur ) {
#print "<a href=\"http://borel.slu.edu/corpas/\">Corpas Comhthreomhar</a>: carachtair neamhbhailí sa théacs";
#exit;
#}

$ionchur =~ s/'/\'/g;

my $pid = open PIPE, "-|";
die "Fork failed: $!" unless defined $pid;
unless ( $pid ) {
	     exec $SEARCHENGINE, @shellargs or die "Can't open pipe: $!";
	}

binmode PIPE, ":utf8";

while (<PIPE>) {
	print;
}
close PIPE;

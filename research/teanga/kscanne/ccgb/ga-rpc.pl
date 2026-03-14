#!/usr/bin/perl -w
use Frontier::Daemon;
use Encode 'from_to';

$ENV{PATH}="/bin:/usr/bin";
delete @ENV{ 'IFS', 'CDPATH', 'ENV', 'BASH_ENV' };

# input to both subroutines is assumed to be utf8
#  Therefore the grxml/ccxml need to handle utf8 input correctly
#  (and should output utf8 as well; though this could be switched
#   at some point and the output converted before returning here).

#  then there is terrible hack in both functions; since the XML
# parser on the client side seems to decode the on-the-wire UTF-8
# back into latin1, I add on more level of utf8 encoding before returning!!

sub corpas {
	my $CORPAS = '/usr/local/libexec/ccxml';
	my $ionchur = "@_";
	$ionchur =~ s/'/\'/g;
	local *PIPE;
	my $pid = open PIPE, "-|";
	die "Fork failed: $!" unless defined $pid;
	unless ( $pid ) {
		exec $CORPAS, "$ionchur" or die "Can't open pipe: $!";
	}
	my @alloutput = <PIPE>;
	my $toclient = "@alloutput";
	$toclient =~ s/^ //gm;
	from_to($toclient, "iso-8859-1", "utf-8"); 	
	close PIPE;
        return $toclient;
}
    
$methods = {'gaeilge.corpas' => \&corpas
	    };
Frontier::Daemon->new(LocalPort => 8080, methods => $methods)
     or die "Couldn't start HTTP server: $!";

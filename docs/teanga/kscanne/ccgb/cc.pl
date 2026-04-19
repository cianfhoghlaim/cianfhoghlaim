#!/usr/bin/perl
use Frontier::Client;
use Encode 'from_to';
$server_url = 'http://borel.slu.edu:8080/RPC2';
$server = Frontier::Client->new(url => $server_url,  debug => 0, );
local $/; # slurp
my $toserver = <STDIN>;
from_to($toserver, "iso-8859-1", "utf-8");
print $server->call('gaeilge.corpas', $toserver);

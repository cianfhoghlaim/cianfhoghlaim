# An Crúbadán - Web

This repository contains the components of the (under development)
website of the **[An Crúbadán](http://borel.slu.edu/crubadan/index.html)**
project.

## Back-end usage and installation

(If you are installing from a ```.deb``` package under 'releases', all
files and init-scripts are installed for you)

An init-script is included which can be installed in ```/etc/init.d```
on debian and ubuntu systems with which the back-end search service
can be started and stopped with

    sudo /etc/init.d/crbackend start|stop|restart

This will start the back-end FCGI process under the control of user
'crbackend' of group 'crbackend'. These must be created before the
init-script is used (unless you are installing this as a ```.deb```
package, in which case it should be done for you).

If not using the init-script, place ```crbackend``` and
```crbackend-fcgi_``` from the ```bin``` directory somewhere in your
```PATH```, and then run ```crbackend```.  If it succeeds, you will be
given the PID on which the FCGI process is running.

**Please note that if ```/data/crubadan``` does not exist or is not
  readable by the user controlling the FCGI process, the process will
  fail to start!**

It is also important to note that the back-end service must be
restarted whenever the EOLAS files it reads are updated or added to.


## Front-end usage and installation

(If installing from a ```.deb``` package under 'releases', everything
is done for you except for your webserver configuration.  Note that
the package also **does not** install the HTML found in the /content/
directory)

Building this requires [GHCJS](https://github.com/GHCJS/GHCJS.git) and
its accompanying patched cabal-install in your ```PATH```.

Upon successfully running the ```make``` command, simply put the
contents of the ```res``` directory somewhere and configure a
webserver to serve them.  You will also need to make your webserver
proxy requests for ```/cgi/``` to FCGI processes listening on port
8892.

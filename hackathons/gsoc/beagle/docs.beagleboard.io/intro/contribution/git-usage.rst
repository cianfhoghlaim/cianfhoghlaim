.. _beagleboard-git-usage:

Git Usage
#########

.. note:: 

    For detailed information on Git and OpenBeagle GitLab checkout the official 
    `help page <https://openbeagle.org/help#git-and-gitlab>`_.

.. note::

    Most of these guidelines were taken from the
    `BioPython project <https://biopython.org/wiki/GitUsage>`_ 
    to be used for BeagleBoard Docs (and other OpenBeagle-hosted project) development using
    ``git``. Please provide feedback via the
    `site-feedback category on our forum <https://forum.beagleboard.org/c/site-feedback>`_.

This document is meant as an outline of the way the BeagleBoard Docs project is developed.
It should include all essential technical information as well as typical
procedures and usage scenarios. It should be helpful for core
developers, potential documentation contributors, testers and everybody
interested in BeagleBoard Docs and other BeagleBoard projects.

Relevance
**********

This page is about using ``git`` for tracking and submitting changes.

If you have found a problem with any BeagleBoard project, and think you know how to
fix it, then we suggest following the simple route of filing an
`issue <https://openbeagle.org/help/user/project/issues/index.md>`_ and describe
your fix. Ideally, you would upload a patch file showing the differences
between the latest version of BeagleBoard project (from our repository) and your
modified version. Working with the command line tools ``diff`` and ``patch``
is a very useful skill to have, and is almost a precursor to working
with a version control system.

This page provides a technical introduction into ``git`` usage including
required software and integration with OpenBeagle. If you want to start
contributing to BeagleBoard projects, you definitely need to install ``git`` and learn
how to obtain a branch of the OpenBeagle project to which you want to contribute. 
If you want to share your changes easily with others, you should also 
sign up for an `OpenBeagle (BeagleBoard Gitlab) <https://openbeagle.org/users/sign_up>`_ 
account and read the corresponding section of the manual. Finally, if you are
engaged in one of the collaborations on experimental BeagleBoard projects,
you should look also into code review and branch merging.

Installing ``git``
********************

You will need to install ``git`` on your computer. `git <http://git-scm.com/>`_
is available for all major operating systems. Please use the appropriate
installation method as described below.

.. tab-set:: 

    .. tab-item:: Linux

        ``git`` is now packaged in all major Linux distributions. You should find it
        in your package manager.

        **Ubuntu/Debian**

        You can install ``git`` from the `git-core` package. e.g.,

        .. code-block:: shell

            sudo apt-get install git-core

        You'll probably also want to install the following packages: `gitk`,
        `git-gui`, and `git-doc`

        **Redhat/Fedora/Mandriva**

        ``git`` is also packaged in rpm-based linux distributions.

        .. code-block:: shell

            dnf install gitk

        should do the trick for you in any recent Fedora/Mandriva or
        derivatives

    .. tab-item:: Mac OS X

        Download the `.dmg` disk image from
        http://code.google.com/p/git-osx-installer/

    .. tab-item:: Windows

        .. note::

            It is worthwhile to consider using Linux at least inside of a virtual machine (VM).

        Download the official installers from
        `Windows installers <https://git-scm.com/download/win>`_

Testing your ``git`` installation
**********************************

If your installation succeeded, you should be able to run

.. code-block:: console

    $ git --help

in a console window to obtain information on git usage. If this fails,
you should refer to
`official git documentation <https://git-scm.com/doc>`_ for troubleshooting.

Creating an OpenBeagle account (optional)
******************************************

.. note::

   `OpenBeagle <https://openbeagle.org>`_ runs an open source instance of
   `GitLab Community Edition <https://about.gitlab.com/>`_.

Once you have ``git`` installed on your machine, you can obtain the code and
start developing. Since the code is hosted by OpenBeagle, however, you may
wish to take advantage of the site's offered features by signing up for
an OpenBeagle account. While an OpenBeagle account is completely optional and not
required for obtaining the BeagleBoard Docs code or participating in
development, an OpenBeagle account will enable all other BeagleBoard Docs developers
to track (and review) your changes to the code base, and will help you
track other developers' contributions. This fosters a social,
collaborative environment for the BeagleBoard community.

If you don't already have an OpenBeagle account, you can create one
`here <https://openbeagle.org/users/sign_up>`_.
Once you have created your account, upload an SSH public key by clicking
on `SSH and GPG keys <https://openbeagle.org/-/profile/keys>` after logging in. For more
information on generating and uploading an SSH public key, see `this
OpenBeagle guide on SSH keys <https://openbeagle.org/help/user/ssh.html>`_.

Working with the source code
******************************

In order to start working with the BeagleBoard Docs source code, you need to
obtain a local clone of our ``git`` repository. In ``git``, this means you will
in fact obtain a complete clone of our ``git`` repository along with the
full version history. Thanks to compression, this is not much bigger
than a single copy of the tree, but you need to accept a small overhead
in terms of disk space.

There are, roughly speaking, two ways of getting your own version of the source code tree:

1. by simply "cloning" the repository to your own computer,

2. or by "forking" the repository on OpenBeagle.
    
They're not that different, in fact both will
result in a directory containing a customizable full copy of the
repository. However, if you have a OpenBeagle account, you can make your
repository a publicly visible branch of the project. If you do so, other people
will be able to easily review your code, make their own branches from it
or merge it back to the trunk.

Using branches on OpenBeagle is the preferred way to work on updates to
BeagleBoard Docs, so it's useful to learn it and use it even if you think
your changes are not for immediate inclusion into the main trunk of
BeagleBoard Docs. But even if you decide not to use OpenBeagle, you can always
change this later using the ``.git/config`` file in your clone. For
simplicity, we describe these two possibilities separately.

Cloning BeagleBoard Docs directly
==================================

Getting a copy of the repository (called "cloning" in ``git`` terminology)
without an OpenBeagle account is very simple:

.. code-block:: shell

    git clone https://openbeagle.org/docs/docs.beagleboard.io.git

This command creates a local copy of the entire BeagleBoard repository on
your machine (your own personal copy of the official repository with its
complete history). You can now make local changes and commit them to
this local copy (although we advise you to use named branches for this,
and keep the main branch in sync with the official BeagleBoard code).

If you want other people to see your changes, however, you must publish
your repository to a public server yourself (e.g. OpenBeagle, Github, GitLab).

Forking BeagleBoard with your OpenBeagle account
=================================================

.. todo::

   We need to describe how to use the "Web IDE" to work with OpenBeagle respositories.

If you are logged in to OpenBeagle, you can go to the BeagleBoard Docs repository
page:

https://openbeagle.org/docs/docs.beagleboard.io

and click on the button named 'Fork'. This will create a fork (basically a
copy) of the official BeagleBoard Docs repository, publicly viewable on OpenBeagle,
but listed under your personal account. It should be visible under a URL
that looks like this:

https://openbeagle.org/yourusername/docs.beagleboard.io

Since your new BeagleBoard Docs repository is publicly visible, it's considered
good practice to change the description and homepage fields to something
meaningful (i.e. different from the ones copied from the official
repository).

If you haven't done so already, setup an SSH key and `upload it to
OpenBeagle <https://openbeagle.org/help/user/ssh.html>`_ for
authentication.

Now, assuming that you have ``git`` installed on your computer, execute the
following commands locally on your machine. This "url" is given on the
OpenBeagle page for your repository (if you are logged in):

.. code-block:: shell

    git clone git@openbeagle.org:yourusername/docs.beagleboard.io.git

Where `yourusername`, not surprisingly, stands for your OpenBeagle username.
You have just created a local copy of the BeagleBoard Docs repository on your
machine.

You may want to also link your branch with the official distribution
(see below on how to keep your copy in sync):

.. code-block:: shell

    git remote add upstream https://openbeagle.org/docs/docs.beagleboard.io

If you haven't already done so, tell git your name and the email address
you are using on OpenBeagle (so that your commits get matched up to your
OpenBeagle account). For example,

.. code-block:: shell

    git config --global user.name "David Jones" config --global user.email "d.jones@example.com"

Making changes locally
***********************

Now you can make changes to your local repository - you can do this
offline, and you can commit your changes as often as you like. In fact,
you should commit as often as possible, because smaller commits are much
better to manage and document.

First of all, create a new branch to make some changes in, and switch to
it:

.. code-block:: shell

    git checkout -b demo-branch

To check which branch you are on, use:

.. code-block:: shell

    git branch

Let us assume you've made changes to the file boards/beagleplay/01-introduction.rst Try this:

.. code-block:: shell

    git status

So commit this change you first need to explicitly add this file to your
change-set:

.. code-block:: shell

    git add boards/beagleplay/01-introduction.rst

and now you commit:

.. code-block:: shell

    git commit -m "added updates X in BeaglePlay introduction"

Your commits in ``git`` are local, i.e. they affect only your working branch
on your computer, and not the whole BeagleBoard Docs tree or even your fork on
OpenBeagle. You don't need an internet connection to commit, so you can do
it very often.

Pushing changes to OpenBeagle
******************************

If you are using OpenBeagle, and you are working on a clone of your own
branch, you can very easily make your changes available for others.

Once you think your changes are stable and should be reviewed by others,
you can push your changes back to the OpenBeagle server:

.. code-block:: shell

    git push origin demo-branch

.. note::
        This will not work if you have cloned directly from the official
        BeagleBoard branch, since only the core developers will have write access
        to the main repository.

Merging upstream changes
*************************

We recommend that you don't actually make any changes to the **main**
branch in your local repository (or your fork on OpenBeagle). Instead, use
named branches to do any of your own work. The advantage of this
approach it is the trivial to pull the upstream **main** (i.e. the
official BeagleBoard branch) to your repository.

Assuming you have issued this command (you only need to do this once):

.. code-block:: shell

    git remote add upstream https://openbeagle.org/docs/docs.beagleboard.io

Then all you need to do is:

.. code-block:: shell

    git checkout main
    git pull upstream main

Provided you never commit any change to your local **main** branch,
this should always be a simple *fast forward* merge without any
conflicts. You can then deal with merging the upstream changes from your
local main branch into your local branches (and you can do that offline).

If you have your repository hosted online (e.g. at OpenBeagle), then push
the updated main branch there:

.. code-block:: shell

    git push origin main

Submitting changes for inclusion in BeagleBoard Docs
*****************************************************

If you think you changes are worth including in the main BeagleBoard Docs
distribution, then file a report on our issue
tracker, and include a link to your updated branch (i.e. your branch on 
OpenBeagle, or another public ``git`` server). You could also attach a patch to the bug. 
If the changes are accepted, one of the BeagleBoard Docs developers will have to check
this code into our main repository.

On OpenBeagle itself, you can inform keepers of the main branch of your
changes by sending a 'merge request' from the page of your branch.

If other things have happened since you began your work, it may require
merging when applied to the official repository's main branch. In this
case, we might ask you to help by rebasing your work:

.. code-block:: shell

    git fetch upstream
    git checkout demo-branch
    git rebase upstream/main

Hopefully, the only changes between your branch and the official repository's
main branch are trivial and ``git`` will handle everything automatically.
If not, you would have to deal with the clashes manually. If this works,
you can update the merge request by replacing the existing (pre-rebase)
branch:

.. code-block:: shell

    git push origin demo-branch

If however the rebase does not go smoothly, give up with the following command
(and hopefully the BeagleBoard Docs developers can sort out the rebase or merge for you):

.. code-block:: shell

    git rebase --abort

Evaluating changes
******************

Since ``git`` is a fully distributed version control system, anyone can
integrate changes from other people, assuming that they are using
branches derived from a common root. This is especially useful for
people working on new features who want to accept contributions from
other people.

This section is going to be of particular interest for the BeagleBoard Docs
core developers, or anyone accepting changes on a branch.

For example, suppose Jason has some interesting changes on his public
repository:

https://openbeagle.org/jkridner/docs.beagleboard.io

You must tell ``git`` about this by creating a reference to this remote
repository:

.. code-block:: shell

    git remote add jkridner https://openbeagle.org/jkridner/docs.beagleboard.io

Now we can fetch *all* of Jason's public repository with one line:

.. code-block:: shell

    git fetch jkridner

Now we can run a diff between any of our own branches and any of Jason's
branches. You can list your own branches with:

.. code-block:: shell

    git branch

Remember the asterisk shows which branch is currently checked out.

To list the remote branches you have setup:

.. code-block:: shell

    git branch -r

For example, to show the difference between your **main** branch and
Jason's **main** branch:

.. code-block:: shell

    git diff main jkridner/main

If you are both keeping your **main** branch in sync with the upstream
BeagleBoard repository, then his **main** branch won't be very
interesting. Instead, try:

.. code-block:: shell

    git diff main jkridner/awesomebranch

You might now want to merge in (some) of Jason's changes to a new branch
on your local repository. To make a copy of the branch (e.g. awesomebranch)
in your local repository, type:

.. code-block:: shell

    git checkout --track jkridner/awesomebranch

If Jason is adding more commits to his remote branch and you want to update
your local copy, just do:

.. code-block:: shell

    git checkout awesomebranch  # if you are not already in branch awesomebranch

If you later want to remove the reference to this particular branch:

.. code-block:: console

    $ git branch -r -d jkridner/awesomebranch
    Deleted remote branch jkridner/awesomebranch (#######)

Or, to delete the references to all of Jason's branches:

.. code-block:: console

    $ git remote rm jkridner
    $ git branch -r
        upstream/main
        origin/HEAD
        origin/main

Alternatively, from within OpenBeagle you can use the fork-queue to cherry
pick commits from other people's forked branches. While this
defaults to applying the changes to your current branch, you would
typically do this using a new integration branch, then fetch it to your
local machine to test everything, before merging it to your public working branch.

Additional Resources
********************

There are a lot of different nice guides to using ``git`` on the web:

-   `Understanding Git
    Conceptually <https://www.sbf5.com/~cduan/technical/git/>`_
-   `git ready: git tips <http://gitready.com/>`_
-   https://web.archive.org/web/20121115132047/http://cheat.errtheblog.com/s/git
-   https://docs.scipy.org/doc/numpy-1.15.1/dev/gitwash/development_workflow.html Numpy is also
    evaluating git
-   https://github.github.com/training-kit/downloads/github-git-cheat-sheet
-   https://skills.github.com/
-   `Pro Git <https://git-scm.com/book/en/v2>`_


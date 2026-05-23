#!/bin/bash -xe

function do_build() {
	echo "**** Updating $PAGES_URL: $1 ****"

	cat << EOF > PAGES
PAGES_URL =  $PAGES_URL
GITLAB_USER = $GITLAB_USER
PROJECT_BRANCH = $PROJECT_BRANCH
GITLAB_HOST = $GITLAB_HOST
PROJECT_REPO = $PROJECT_REPO
EOF

	echo "**** make librobotcontrol xml ****"
	if [ -e projects/librobotcontrol/docs ] ; then
		cd projects/librobotcontrol/docs
		doxygen
		cd ../../..
	fi

	if [ "x$1" == "xhtml" ]; then
		mkdir -p public/html
		echo "**** make html ****"
		# Build HTML
		make html BUILDDIR=public
	fi

	if [ "x$1" == "xpdf" ]; then
		echo "**** make latexpdf ****"
		# Build, optimize, and serve PDF
		make latexpdf BUILDDIR=public

		# echo "**** pdfcpu ****"
		# pdfcpu version
		# pdfcpu optimize public/latex/*.pdf

		echo "**** cleanup ****"
		mkdir -p public/pdf
		mv public/latex/*.pdf public/pdf
		rm -rf public/doctrees
		rm -rf public/latex
	fi

	if [ "x$1" == "xpublish" ]; then
		# Move files
		mkdir -p public/
		mv public/html/* public/
		mv public/pdf/*.pdf public/

		# Update docs.beagleboard.org
		if [ "$CI_COMMIT_TAG" != "" ]; then
			mkdir -p ~/.ssh
			eval "$(ssh-agent -s)"
			echo "${PRIVATE_KEY}" | base64 -d | ssh-add -
			rsync -e 'ssh -p 45 -o "StrictHostKeyChecking=no"' -avP --delete public/. docs@beagleboard.org:/var/www/docs
		fi
	fi
}

if [ "$CI_COMMIT_BRANCH" != "" ]; then
	export PAGES_URL=$CI_PAGES_URL
	export GITLAB_USER=$CI_PROJECT_NAMESPACE
	export GITLAB_HOST=$CI_SERVER_HOST
	export PROJECT_BRANCH=$CI_COMMIT_BRANCH
	export PROJECT_REPO=$CI_PROJECT_NAME
	do_build $1
elif [ "$CI_COMMIT_TAG" != "" ]; then
	export PAGES_URL=https://docs.beagleboard.org
	export GITLAB_USER=docs
	export GITLAB_HOST=$CI_SERVER_HOST
	export PROJECT_REPO=docs.beagleboard.io
	git fetch --all -v
	export GIT_BRANCH=$(git branch -a --contains tags/$CI_COMMIT_TAG | grep origin | tr -d '* ' | sed 's/.*origin\///' | head -n 1)
	export PROJECT_BRANCH=$GIT_BRANCH
	export SPHINXOPTS="-D todo_include_todos=0"
	do_build $1
else
	echo "***** Not on a branch or tag *****"
fi

echo "**** env ****"
env


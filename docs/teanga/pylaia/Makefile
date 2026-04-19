.PHONY: release docs

docs:
	npx antora antora-playbook.yml

release:
	# Grep the version from pyproject.toml, squeeze multiple spaces, delete double and single quotes, get 3rd val.
	# This command tolerates multiple whitespace sequences around the version number.
	$(eval version:=$(shell grep -m 1 version pyproject.toml | tr -s ' ' | tr -d '"' | tr -d "'" | cut -d' ' -f3))
	echo Releasing version $(version)
	git commit pyproject.toml -m "Version $(version)"
	git tag $(version)
	git push origin master $(version)

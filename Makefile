help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

init: ## Init development setup
	npm install
	./node_modules/.bin/webpack --config webpack.dev.js

run:
	python3 -m http.server


prod:
	./node_modules/.bin/webpack --config webpack.prod.js

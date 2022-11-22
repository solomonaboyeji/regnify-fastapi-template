start-uvicorn:
	uvicorn src.main:app --reload --port 8100

start-dev-postgres:
	docker-compose -f ./docker/local/compose-files/docker-compose-postgres.yml up

# ** ALEMBIC

run-db-upgrade:
	alembic upgrade head

# ** END ALEMBIC

# *** TESTS

build-test:
	docker compose -f docker/test/docker-compose-test.yml build 

kill-test:
	docker compose -f docker/test/docker-compose-test.yml down

run-test-migrations:
	docker compose -f docker/test/docker-compose-test.yml run -v ${PWD}:/usr/src/regnify-api  --rm regnify-api alembic upgrade head


# * ------ User Modules ------ * #
run-test-users:
	make kill-test

	make run-test-migrations

	# * run the tests
	docker compose -f docker/test/docker-compose-test.yml run -v ${PWD}:/usr/src/regnify-api  --rm regnify-api python -m pytest --cov=src/users tests/users

	make kill-test

run-test-users-crud:
	make kill-test

	make run-test-migrations
	
	# * run the tests
	docker compose -f docker/test/docker-compose-test.yml run -v ${PWD}:/usr/src/regnify-api  --rm regnify-api python -m pytest --cov=src/users tests/users/crud

	make kill-test

run-test-users-services:
	make kill-test

	make run-test-migrations
	
	# * run the tests
	docker compose -f docker/test/docker-compose-test.yml run -v ${PWD}:/usr/src/regnify-api --rm regnify-api python -m pytest --cov=src/users tests/users/services/

	make kill-test

run-test-users-http:
	make kill-test

	make run-test-migrations
	
	# * run the tests
	docker compose -f docker/test/docker-compose-test.yml run -v ${PWD}:/usr/src/regnify-api --rm regnify-api python -m pytest --cov=src/users tests/users/http/

	make kill-test

# * ------ End User Modules ------ * #

# *** END TESTS

create-network:
	docker network create regnify-network

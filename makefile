
# ****************** DIRECT DEVELOPMENT ****************** #

start-uvicorn:
	uvicorn src.main:app --reload --port 8100

start-dev-postgres:
	docker-compose -f ./docker/local/compose-files/docker-compose-postgres.yml up

down-dev-postgres:
	docker-compose -f ./docker/local/compose-files/docker-compose-postgres.yml down

# ****************** END DIRECT DEVELOPMENT ****************** #

# -- 
# -- 
# -- 

# ****************** ALEMBIC ****************** #

run-db-upgrade:
	alembic upgrade head

# ****************** END ALEMBIC ****************** #



# -- 
# -- 
# -- 


# ****************** TESTS ****************** #

build-local:
	docker compose -f docker/local/docker-compose.yml build 

kill-local:
	docker compose -f docker/local/docker-compose.yml down

run-local-migrations:
	docker compose -f docker/local/docker-compose.yml run -v ${PWD}:/usr/src/regnify-api  --rm regnify-api  alembic upgrade head

make init-platform:
	docker compose -f docker/local/docker-compose.yml run -v ${PWD}:/usr/src/regnify-api --rm regnify-api python ./src/init_platform.py

run:
	make run-local-migrations

	make make init-platform

	docker compose -f docker/local/docker-compose.yml up  --remove-orphans  -d

run-prod:
	docker build -f Dockerfile.prod -t regnify-api .
	docker run -p 8100:8000 regnify-api

restart:
	docker compose -f docker/local/docker-compose.yml down regnify-api
	make run


follow-logs:
	docker compose -f docker/local/docker-compose.yml logs regnify-api -f


# ****************** END TESTS ****************** #

# -- 
# -- 
# -- 

# ****************** TESTS ****************** #

build-test:
	docker compose -f docker/test/docker-compose-test.yml build 

kill-test: kill-local
	docker compose -f docker/test/docker-compose-test.yml down

run-test-migrations:
	docker compose -f docker/test/docker-compose-test.yml run -v ${PWD}:/usr/src/regnify-api  --rm regnify-api alembic upgrade head

run-tests:
	make kill-test

	make run-test-migrations

	# * run the tests
	docker compose -f docker/test/docker-compose-test.yml run -v ${PWD}:/usr/src/regnify-api  --rm regnify-api python -m pytest --cov-report term-missing --cov=src/

	make kill-test

# * ------ User Module ------ * #

# Runs all tests under the user modules
run-test-users:
	make kill-test

	make run-test-migrations

	# * run the tests
	docker compose -f docker/test/docker-compose-test.yml run -v ${PWD}:/usr/src/regnify-api  --rm regnify-api python -m pytest --cov-report term-missing --cov=src/users tests/users 

	make kill-test

run-test-users-crud:
	make kill-test

	make run-test-migrations
	
	# * run the tests
	docker compose -f docker/test/docker-compose-test.yml run -v ${PWD}:/usr/src/regnify-api  --rm regnify-api python -m pytest --cov-report term-missing --cov=src/users tests/users/crud/test_users.py

	make kill-test

run-test-roles-crud:
	make kill-test

	make run-test-migrations
	
	# * run the tests
	docker compose -f docker/test/docker-compose-test.yml run -v ${PWD}:/usr/src/regnify-api  --rm regnify-api python -m pytest --cov-report term-missing --cov=src/users tests/users/crud/test_roles.py

	make kill-test

run-test-users-services:
	make kill-test

	make run-test-migrations
	
	# * run the tests
	docker compose -f docker/test/docker-compose-test.yml run -v ${PWD}:/usr/src/regnify-api --rm regnify-api python -m pytest --cov-report term-missing --cov=src/users/services tests/users/services/test_users.py

	make kill-test

run-test-roles-services:
	make kill-test

	make run-test-migrations
	
	# * run the tests
	docker compose -f docker/test/docker-compose-test.yml run -v ${PWD}:/usr/src/regnify-api --rm regnify-api python -m pytest --cov-report term-missing --cov=src/users/services tests/users/services/test_roles.py

	make kill-test

run-test-users-http:
	make kill-test

	make run-test-migrations
	
	# * run the tests
	docker compose -f docker/test/docker-compose-test.yml run -v ${PWD}:/usr/src/regnify-api --rm regnify-api python -m pytest --cov-report term-missing --cov=src/users/routers tests/users/http/test_users.py

	make kill-test

run-test-roles-http:
	make kill-test

	make run-test-migrations
	
	# * run the tests
	docker compose -f docker/test/docker-compose-test.yml run -v ${PWD}:/usr/src/regnify-api --rm regnify-api python -m pytest --cov-report term-missing --cov=src/users tests/users/http/test_roles.py

	make kill-test

# * ------ End User Modules ------ * #

# ****************** END TESTS ****************** #

# -- 
# -- 
# -- 

# ****************** MISC ****************** #

create-network:
	docker network create regnify-network

# ****************** END MISC ****************** #
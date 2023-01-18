# A basic HTTP template to run different APIs

# Requirements
- python3.9
- Docker
- makefile
    * Please install makefile if you are not using Linux.
- MinIO: High Performance Object Storage (already dockerized)
    * [How to install](https://hub.docker.com/r/minio/minio)
- Better Comments Visual Studio Plugin
- Black Python Formatter

## Auto Generation of Libraries
[Link Here](https://github.com/codelorhd/regnify-fastapi-template/tree/main/docs/client-libraries)

# 

# Running API
Open the makefile and understand the file before running the makefile commands.

```sh
# Run this first, Create Network for the containers
make create-network
```

```sh
# Build or rebuild the API image
make build-local
```

```sh
# Run at the root of the project
make run
```

```sh
# Follow docker compose logs
make follow-logs
```

```sh
# Kill the API
make kill-local
```

### Migrations

```sh
# Run local alembic migrations
make run-local-migrations
```

### Tests

```sh
# Run all the tests in the project
make run-tests
```


```sh
# Run all the tests in the users module
make run-test-users
```



# 

# Using Alembic

```sh
    # This will run all head() of all revisions
    alembic upgrade head
```

```sh
    # This will create a revision file
    alembic revision -m "create account table"
```

```sh
   # Auto Generate alembic migration file
   # Add the model to auto generate for in env.py 
   # target_metadata = [User.metadata]

   alembic revision --autogenerate -m "updated users and user_roles table"

   # Then run upgrade head
   alembic upgrade head
```

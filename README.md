# A basic HTTP template to run different APIs

Features
- SQL + SqlAlchemy
- Supports both HTTP / 2.0 and HTTP / 1.0
- Upload to Local S3 Storage
- Auto Generation of client libraries

#

# Tips
1. CRUD classes should only communicate with the database, do not add any FastAPI elements therein.
2. Tes your services and crud implementations by writing test cases for them, not via routers. 

#

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


# Serving HTTP/1.1 and HTTP/2.0
Ensure you have these saved in the environment variables
- `USE_SSL` = True
- `USE_TCP` = True
- `TCP_PORT` should be the port to listen on (e.g. 80 or 8100)
- `SSL_PORT` should be the port to listen on (e.g. 443 or 8101)
- `MAX_WORKERS` to the number of workers the system has.

For local development
- HTTP 2.0 is serve on `https://localhost:8101/docs`
- HTTP 1.1 is serve on `http://localhost:8100/docs`
- The `hypercorn/cert.pem` and `hypercorn/key.pem` can be generated with this command `openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes`

For Production
- Save the file path of the mounted `key.pem` to environment variable `KEYFILE` 
- Save the file path of the mounted `cert.pem` to environment variable `CERTFILE` 


# 

# Using Alembic

Ensure you have .env in the root folder of the project. See the .env.copy for the expected variables needed.

```sh
    # This will run all head() of all revisions
    alembic upgrade head
```

```sh
    # This will create a revision file
    alembic revision -m "create account table"
```

## Generating Alembic Versions
Alembic can help you automatically generate your alembic version files rather than writing them out.
When you make changes to or add a new SqlAlchmey model, indicate the name of the file of the model in the `env.py` file in `almebic` folders, 
as the target_metadata as shown below
```python
target_metadata = [User.metadata]
```

After that run the alembic auto generation command below:

```sh

   alembic revision --autogenerate -m "updated users and user_roles table"

   # Then run upgrade head
   alembic upgrade head
```

#

# How to Use TypeScript Generated Package
1. Clone the repository into your project.
2. Run this line in the library's folder: `npm install && npx parcel build`
3. Include in your project's package.json like this
    ```
    "@dbulletin/dbulletin-api-ts-client": "file:./dbulletin-api-ts-client",
    ```
4. Run `npm install` in the root of your project.

## To build this package
Initialized the package
```sh
npm init
```

Install Parcel
```sh
npm install --save-dev parcel
```

Add the following to the package.json
```json
{
    "name": "@dbulletin/dbulletin-api-ts-client",
    "version": "1.0.0",
    "description": "",
    "source": "index.ts",
    "main": "dist/main.js",
    "module": "dist/module.js",
    "types": "dist/types.d.ts"
}
```

Install axios
```sh
npm i axios
```

Build the files. Building will be required from time to time when the package is updated.
```sh
npx parcel build
```

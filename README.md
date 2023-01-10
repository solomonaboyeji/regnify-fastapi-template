# A basic HTTP template to run different APIs

# Requirements
- python3.9

## Auto Generation of Libraries
[Link Here](../regnify-core/docs/client-libraries/README.md)

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
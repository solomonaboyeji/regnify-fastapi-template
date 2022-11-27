# A basic HTTP template to run different APIs


# TODO
- [x] Implement Relational Database with option to switch
    -  1st Read: https://fastapi.tiangolo.com/tutorial/sql-databases/ 
    -  2nd Read: https://fastapi.tiangolo.com/advanced/async-sql-databases/
    -  3rd Read: Using Alembic
- [-] Class Based Views for endpoints: https://fastapi-utils.davidmontague.xyz/user-guide/class-based-views/
- [x] Testings:
    -  Read number 14 https://github.com/zhanymkanov/fastapi-best-practices
    -  Testing a Database File: https://fastapi.tiangolo.com/advanced/testing-database/
    -  Async Testing: https://fastapi.tiangolo.com/advanced/async-tests/
    -  https://docs.pytest.org/en/latest/
    -  https://coverage.readthedocs.io/en/6.6.0b1/

    -  https://github.com/augustogoulart/awesome-pytest
    -  https://calmcode.io/pytest/introduction.html
- [x] Implement Pydantic BaseSettings: https://fastapi.tiangolo.com/advanced/settings/#pydantic-settings
- [] Additional Error Responses: https://fastapi.tiangolo.com/advanced/additional-res


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
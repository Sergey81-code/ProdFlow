# ProdFlow Backend

## Running the Database with Docker Compose

Before setting up migrations, you can start the database using Docker Compose:

```bash
docker-compose up -d
```

This will start the db service in detached mode.
Make sure your docker-compose.yml defines the db service with PostgreSQL or your DB and the correct ports.

## Set up migrations

To set up migrations, if the file "alembic.ini" does not yet exist, run the following command in the terminal:

```bash
alembic init db/migrations
```

If you have any problems with Alembic not being found even though it’s already set up, run:

```
where python
```

If the output does not include the path to the Python interpreter inside your virtual environment, run:

```
set PATH={your_project_path}\{your_venv_folder_name}\Scripts;%PATH%
```

Then check again — your Python interpreter should now be added to your environment.

This will create a folder named migrations and a configuration file for Alembic

- In the alembic.ini file, set the database URL for the database you want to manage migrations for.
- Then, navigate to the migrations folder and open env.py. In that file, make the necessary changes in the section where you add the following import:

...
from myapp import mymodel
...

- Next, run the following command to create a new migration: `alembic revision --autogenerate -m "comment"` - also doing if you want to change any models
- This will generate a migration file
- Finaly, apply the migration useing: `alembic upgrade heads`

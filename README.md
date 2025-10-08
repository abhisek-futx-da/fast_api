# FastAPI User Management API

This project is a simple user management API built with FastAPI, PostgreSQL, SQLAlchemy, and Alembic, demonstrating a modern backend stack for creating web services.

## Core Technologies

- **API Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Database Migrations**: Alembic

---

## Setup and Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/theraaajj/fastapi-sqlalchemy-alembic
    cd fastapi_user_project
    ```

2.  **Create and Activate a Virtual Environment**
    ```bash
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    .\venv\Scripts\activate
    ```

3.  **Install Dependencies**
    *(First, create a requirements.txt file by running `pip freeze > requirements.txt`)*
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Database Connection**
    - Update the `DATABASE_URL` in `app/database.py`.
    - Update the `sqlalchemy.url` in `alembic.ini`.

---

## Database Migrations

[cite_start]This project uses Alembic to manage database schema versions[cite: 4].

-   **To apply all migrations** and bring the database to the latest version, run:
    ```bash
    alembic upgrade head
    ```

-   **To roll back the last migration**, you can use:
    ```bash
    alembic downgrade -1
    ```

---

## Running the Application

To run the live development server, use Uvicorn:

```bash
uvicorn app.main:app --reload
```

The server will be available at http://127.0.0.1:8000.

### Testing the API

Once the server is running, navigate to 

`http://12.0.0.1:8000/docs` in your browser. This provides an interactive Swagger UI where you can test all the API endpoints directly.

---

## The Role of Each Key File

`database.py`: This file's only job is to connect to the PostgreSQL database. It creates the SQLAlchemy engine, a SessionLocal to manage database conversations, and the Base class that our database models inherit from.

`models.py`: Defines our database tables as Python classes. The User class in this file is a direct representation of the users table in PostgreSQL. SQLAlchemy uses this model to understand how to query and manipulate the table.

`schemas.py`: This file contains our Pydantic models. They define the shape of the data for our API—what data to expect in a POST request and what data to send back in a response. This gives us automatic data validation.

`crud.py`: This file separates our database logic from our API logic. All functions that perform Create, Read, Update, or Delete operations on the database are here. This keeps our main.py file clean and focused on handling web requests.

`main.py`: This is the heart of the API. It creates the FastAPI application instance and defines all the URL endpoints (like /users/ and /users/{id}). Each endpoint function uses the other files to get a database session, validate incoming data, call the appropriate CRUD function, and return a response.

---

## Alembic and Database Migrations

Instead of creating our database tables manually, we used Alembic to manage changes to our database schema in a controlled, versioned way. (version control for our DB)

`alembic.ini`: This is Alembic's main configuration file. Its most important job is to tell Alembic how to connect to our database. We set the sqlalchemy.url here to point to our PostgreSQL database.

`alembic/env.py`: This is a runtime configuration file. We modified it to connect Alembic to our SQLAlchemy models (defined in app/models.py). This is what enables the powerful --autogenerate feature, where Alembic can automatically detect changes between our models and the database.

`alembic/versions/`: This folder contains the actual migration scripts. Each script is a Python file with an upgrade() function to apply a change and a downgrade() function to reverse it.

### The Migration Strategy: We demonstrated a two-stage migration process, which is very common in real-world projects.

Version 1 - Initial Table: We created an initial migration that built the users table with just the essential columns (id, name, email, created_at). This established the baseline for our database.

Version 2 - Schema Evolution: We then created a second migration that added two new columns (phone_number and address) to the existing users table

By running `alembic upgrade head`, we can bring any new database to the latest version, and by using `alembic downgrade`, we can roll back changes if needed.

---

## Final Workflow: Running and Testing

Finally, we established a clear, repeatable workflow for running and testing the application.

Activate Environment: Always start by activating the virtual environment `.\.venv\Scripts\activate` to ensure you're using the project-specific Python interpreter and libraries.

Run Migrations: Before starting the app, run `alembic upgrade head` to ensure the database schema is up-to-date with your models.

Start the Server: Use the command `uvicorn app.main:app --reload` to run the live development server.

Test with Swagger UI: The most effective way to test is to open a browser to `http://127.0.0.1:8000/docs`. This auto-generated interactive documentation allows you to test every endpoint, see the expected data formats, and get immediate feedback.

---

## Understanding Pydantic Schemas

### Schemas? (The "Blueprint")
Think of a schema as a strict blueprint or a form. It defines exactly what kind of data your API expects to receive and what kind of data it promises to send back.

In our project, we used a library called Pydantic to create these blueprints. A Pydantic schema is simply a Python class that inherits from BaseModel. Inside the class, you declare the fields you expect and their data types (e.g., `name: str`, `email: EmailStr`).

### Why Do We Need Them? (The "Rules and Translation")
Schemas are crucial for creating robust and reliable APIs. They serve three main purposes:

- Data Validation: When a request comes into your API (e.g., a POST request to create a user), FastAPI uses the schema to check the incoming data. If a user sends a name that is a number instead of a string, or an email that isn't a valid email format, the schema will automatically reject the request and send back a helpful error message. This protects your database from bad data.

- Data Serialization: When you fetch data from your database (which is a SQLAlchemy model object), the schema translates it into a clean JSON format that can be sent over the web. The `orm_mode = True` setting in our User schema tells Pydantic to read the data directly from our SQLAlchemy database objects.

- API Contract: Schemas act as a clear contract between your backend and any frontend or client that uses it. They are the foundation of FastAPI's automatic interactive documentation (the Swagger UI at /docs). The docs page reads your schemas and instantly shows every developer what data they need to send and what they will get in return.

---

## Breakdown of `schemas.py` file:

We created three different schemas, each with a specific job.

1. UserBase

```bash
class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone_number: Optional[str] = None
    address: Optional[str] = None
```
This is the "base" blueprint containing all the fields that are common to both creating and reading a user. Optional[str] means these fields are not required.

2. UserCreate

```bash
class UserCreate(UserBase):
    pass
```
This schema is specifically for creating a user. It inherits all the fields from UserBase. We use this in our POST /users endpoint to validate the incoming request body.

3. User

```bash
class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
```
This is our "output" schema, used for returning user data from the API. It inherits from UserBase but also includes fields that are generated by the database, like `id` and `created_at`. We would never want a client to send us an id when creating a user, which is why it's only in this output model.

---

## How It Works: The Journey of a Request

Here’s the journey of a POST /users request to illustrate the workflow:

A client sends a JSON request to create a user: {"name": "Raj", "email": "aryan@example.com"}.

FastAPI receives the request and validates it against the UserCreate schema. It confirms that name is a string and email is a valid email.

The validated data is passed to your endpoint function.

Your endpoint calls the `crud.create_user()` function, which creates a SQLAlchemy User model object and saves it to the database.

The database saves the record and automatically generates an `id` and `created_at` timestamp.

The crud function returns the SQLAlchemy model object.

FastAPI takes this database object and filters it through the User schema (our output model).

The User schema translates the database object into a clean JSON response, including the `id` and `created_at` fields, which is then sent back to the client.

---

## Errors Handled

### 1. Alembic Configuration Errors
This was a group of errors related to setting up Alembic to talk to our database and our code.

**The Bug**: `sqlalchemy.dialects:driver error.`

- **Diagnosis**: This was our first major bug. The error message indicated that Alembic didn't recognize the database "dialect" named driver.

- **Resolution**: We identified that the `sqlalchemy.url` in the `alembic.ini` file contained a placeholder. The fix was to replace `driver://` with the correct `postgresql://` connection string.

**The Bug**: Alembic couldn't find the MetaData object when using `--autogenerate`.

- **Diagnosis**: This meant Alembic was connected to the database but had no idea what our Python models looked like, so it couldn't compare them.

- **Resolution**: We had to edit alembic/env.py. The fix involved adding code to tell Python where our app folder was and then setting target_metadata = Base.metadata to link Alembic to our SQLAlchemy models.

**The Bug**: `InterpolationSyntaxError` in `alembic.ini` after URL-encoding a password.

- **Diagnosis**: The % symbol in the URL-encoded password was being misinterpreted by the .ini file parser as a variable.

- **Resolution**: We escaped the percent sign by doubling it (%%) in the alembic.ini file only.

### 2. File System and Editor Issues
This was the most persistent and tricky set of bugs, as they weren't caused by code but by the development environment itself.

**The Bug**: The `MetaData` error continued even after we corrected the `env.py` file.

- **Diagnosis**: This was a critical lesson. We moved from checking the code to checking the file system. By running type `alembic\env.py` in the terminal, we got definitive proof that the file had not been saved correctly, even though it looked right in the editor.

- **Resolution**: We forced the file to save by running the editor as an administrator and using the "Save As..." command to overwrite the old file.

**The Bug**: An `ImportError` where Base couldn't be imported, even with the correct code.

- **Diagnosis**: We used the same type command diagnostic on `app/database.py` and `app/models.py`. The result showed that `app/database.py` was completely empty on the disk.

- **Resolution**: We deleted the corrupted, empty file and created a new `database.py` with the correct code, which finally fixed the import chain.

### 3. Database Integrity Errors
These errors came from the database itself, rejecting operations that violated its rules.

**The Bug**: `NotNullViolation` on the id column when creating a new user.

- **Diagnosis**: The full traceback from the Uvicorn terminal showed the database was trying to insert a NULL value for the id, which is a forbidden operation for a primary key. This meant the auto-increment feature was not working.

- **Resolution**: We created a new Alembic migration that manually added the auto-incrementing sequence to the id column of the users table in the database, correcting the initial setup.

**The Bug**: The alembic `downgrade` command didn't remove the new columns.

- **Diagnosis**: We discovered that while the `upgrade()` function was correct, the corresponding `downgrade()` function in the migration script was empty. Alembic didn't know how to reverse the change.

- **Resolution**: We manually edited the `downgrade()` function in the migration script to include the `op.drop_column()` commands, providing an explicit set of instructions for the rollback.

---

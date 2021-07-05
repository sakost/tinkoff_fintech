# Films

### Description:
    This projects implements film-review service
    
### Create venv:
    make venv

### Run tests:
    make test
    
### Run linters:
    make lint
    
### Run formatters:
    make format
    
### Run initializing of databse:
    make init_db

### Run admin panel:
    make admin

### Run application:
    make up

## Pre-requirements:

### Production

This project requires the `.env` file with such content(all values are optional):
```dotenv
TESTING=false # or true
SQLALCHEMY_DATABASE_URI=sqlite:///db.sqlite3  # database URI
FIRST_SUPERUSER=admin  # super secret admin name
FIRST_SUPERUSER_PASSWORD=admin  # super secret password for admin user
FIRST_SUPERUSER_ROLE=superuser  # or other name of admin role(admin i.e.)
USER_ROLE_NAME=user  # or other name of simple user role
OBJECTS_PER_PAGE=100  # for pagination
```

All values above are default ones.

### Testing
There is another file - `tests.env`. It is used to get settings within tests. All key-value pairs are the same.

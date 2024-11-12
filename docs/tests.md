
# Table of Contents

- [Table of Contents](#table-of-contents)
- [About](#about)
- [Tests summary](#tests-summary)
    - [Models](#models)
    - [Connection](#connection)
    - [Database](#database)
- [Setup](#setup)
  - [Get the repo and install dependencies](#get-the-repo-and-install-dependencies)
  - [Configuring the test databases](#configuring-the-test-databases)
    - [Docker install](#docker-install)
    - [Creating the docker Images](#creating-the-docker-images)
- [Running the test](#running-the-test)

# About

Built on Pytest. The tests check to ensure that the core features of the library are functioning properly. The tests rely on the docker images and will not run without them. They are currently only scoped to the default drivers listed in the readme.

All tests are ran against the four active dialects - mysql, mssql, postgres, and oracle. Sqlite is not in scope at the moment and mariadb performs similarly to mysql, so it was left out.

# Tests summary

### Models

Pydantic Models are used to validate any configuration that is imported into the DatabaseConnection or SqlAlchemyConnection objects to ensure that there are not conflicting settings and everything required for a connection is present. Refer to the readme for configuration options.

Notes

- The primary model is the DatabaseModel. The MultiDatabase model is simply nested Database models.
  - Refer to the readme for full configuration options.

Tests

- Valid Models
  - These models test various valid configurations that can be used with the models. They focus on the individual settings a user can deploy with the model.
- Invalid Models
  - Various settings that will not function together. These can include an invalid setting or an invalid value.

### Connection

The connection tests the basic connectivity function of the Connection object. By default, the configuration passed into the Connection object will have to pass validation as well.

Tests

- Test Connect()
  - Ensure a Connection object is properly assigned to self.connection
- Test connection to database
  - Tests to ensure the connection can execute a query "SELECT 1", which properly validates that the connection has achieved a successful connection to the database.

### Database

The database checks basic select statements, statements with parameters, and stored procedures for properly functionality. Keep in mind that the library has many entry points for param cleansing and execution handling that a user can supplement the object with. In addition, it formats raw queries in various ways such as injecting offset, limit, and fetching rules.

- Test db.execute(statement)
  - Tests to ensure a simple select statement retrieves the proper value from `test_data` (the table created in the docker images for each dialect)
    - db.execute(query)
  - Similar to above, except a parameter is passed in.
    - db.execute(query, args)
- Test db.execute_sp(statement)
  - For postgresql and oracle, a stored procedure is used to update a user's uuid and a db query is run to check if the value has changed. For mysql and mssql, the stored procedure simply retrieves a value.

# Setup

The tests require that you have docker and the repo cloned off the github repo. Some instructions on docker are provided. Perhaps I may just build a docker image so that everything is nice and set, but for now, here are the full instructions.

**NOTE** - These instructions are primarily for windows users. Your instructions may differ slightly depending on system.


## Get the repo and install dependencies

**Clone the repo**

Ensure you are cloning the repo and not using pip to install. The pypi dist will not include the testing functionality.

```bash
git clone https://github.com/hotnsoursoup/quik-db.git
```



**Install uv**

The project was built with uv astral as the dependency manager, but you can modify the pyproject build-system to use hatch or poetry if you prefer.

```console
pip install uv
```

**Create the virtual environment**

Ensure you are at the root of the project and the terminal is set there as well.

```console
uv venv
```

**Activate the virtual environment**

```console
.venv\scripts\activate
```


**Install dependencies into the venv**

```console
uv pip install -r pyproject.toml --all-extras
```

Now your environment is set.





## Configuring the test databases
### Docker install

If you do not have docker, you will need to install it. There are various ways, including visiting https://docs.docker.com/desktop/.


**Windows users**

The easiest way to get docker desktop for `Windows` is if you already have a package manager like chocolatey. Visit https://chocolatey.org/install. You won't regret getting it if you are not familiar.

Once you have chocolatey installed, you can simply run the below command to have docker desktop installed. Then, just create your account and launch it and you're good to go.

```bash
choco install docker-desktop
```

### Creating the docker Images

If you're not familiar with docker, its a containerization and orchestration tool. What this means is it basically wraps your application into a virtual container where it can run without worrying about things like the OS or environment. For these tests, it will spin up 4 docker containers for each database dialect.

To get started, ensure you are at the root of the project - Where the pyproject.toml file is found.

Next, simply run the command below.

```bash
Docker-compose up -d
```

Depending on your computer speed, it may take a minute. For others, it may only take 10 seconds. You should see something similar to the below.

```bash
[+] Running 8/8
 ✔ Network
 quik_db_default
 Created
 ✔ Network ez_net
 Created
 ✔ Container quikdb-postgres
 Started
 ✔ Container quikdb-sqlserver
 Healthy
 ✔ Container quikdb-oracle
 Healthy
 ✔ Container quikdb-mysql
 Started
 ✔ Container quikdb-oracle.configure
 Started
 ✔ Container quik_db-quikdb-sqlserver.configure-1
 Started
```

Wait until all the containers are green and you are good to go!

# Running the test

Now all you have to do is run the pytest in the command line of the virtual environment.

```console
pytest
```

By running the command below, a few things occur.

- pytest checks the pyproject.toml for the configuration
- The tests are run
- a report is generated in `/tests/reports/report.html`
- a pytest_{datetime}.csv file is created in `/tests/reports`

And thats it! You can review the tests in the reports folder described above.

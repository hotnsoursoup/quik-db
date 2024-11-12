# quik_db

[![PyPI - Version](https://img.shields.io/pypi/v/quik_db.svg)](https://pypi.org/project/quik_db)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/quik_db.svg)](https://pypi.org/project/quik_db)

-----

- [quik\_db](#quik_db)
- [Introduction](#introduction)
    - [Key Features](#key-features)
    - [In Development](#in-development)
    - [Feature Roadmap](#feature-roadmap)
    - [Optional Dependencies](#optional-dependencies)
    - [Quick Reference Table](#quick-reference-table)
    - [Testing](#testing)
- [Quick Start](#quick-start)
  - [Installation](#installation)
  - [Executing queries with parameters](#executing-queries-with-parameters)
    - [Calling stored procedures](#calling-stored-procedures)
    - [Auto prefix schema](#auto-prefix-schema)
  - [The Result Object](#the-result-object)
  - [Fetch, Offset, and Limit](#fetch-offset-and-limit)
    - [Using Limit](#using-limit)
    - [Using fetch](#using-fetch)
  - [Disable all fetching](#disable-all-fetching)
- [Configuration File Models](#configuration-file-models)
    - [Single Database Model](#single-database-model)
    - [Available Configuration Options](#available-configuration-options)
    - [ConnectionParams](#connectionparams)
    - [QuerySettings](#querysettings)
    - [MultiDatabaseModel](#multidatabasemodel)
- [Model Validation](#model-validation)
  - [ValidationError](#validationerror)
  - [ModelValidationError / model\_validator](#modelvalidationerror--model_validator)
- [Handlers and Methods](#handlers-and-methods)
    - [Execution flow handlers (Connection)](#execution-flow-handlers-connection)
- [SQLAlchemyConnection](#sqlalchemyconnection)
    - [Connection Types in `SQLAlchemyConnection`](#connection-types-in-sqlalchemyconnection)
    - [Generating new sessions](#generating-new-sessions)
- [License](#license)

# Introduction

This library provides a lightweight and straightforward way to create database
connection objects from a configuration file. It includes utilities for input sanitization,
paging, generating stored procedure queries, execution handling, and result
processing.

The primary connection object leverages **SQLAlchemy's** DBAPI, with the flexibility
to subclass for other DBAPI implementations.

### Key Features

- **Flexible Configurations**: Supports both single and multi-database configurations.
  - Configurations support both `url` and `connection_params` configurations for database connections.
    - Can generate the `url` for the database connection from `connection_params`, including query args in a configuration setting so its easier to manage.
  - Direct support of SqlAlchemy engine options in configuration.
  - Modify the config after instantiation
    - (e.g.) db.config.query_settings.enable_fetch = False
    - (e.g.) db.config.connection_params.query = {} # Insert a dictionary of query arguments for url generation.
- **Pydantic Validation**: Ensures configurations adhere to predefined models to ensure functionality.
  - (e.g.) db = Connection(config) # Config is validated on import
- **Raw SQL Support**: Supports generation and modification of raw sql statements.
  - Auto generates stored procedure calls by simply providing the procedure name in `execute_sp`.
    - (e.g.)  db.execute_sp('my_procedure') # Generates based on `dialect` in the configuration.
  - Can auto-prefix stored procedures with a schema.
  - Can auto-prefix all tables in a sql statement with the given schema. The library has CTE detection and supports sub queries.
  - Can modify sql queries to include offset and limit
- **Result object Management**: Includes various features for managing results
  - Control result output with `result_as_mappings` config (converts results to a list of mappings instead of tuples)
    - Done in config, or db.config.result_as_mappings = True
  - Saves execution state data `including` query/params through each stage of transformation.
  - Auto saves columns retrieves in db.vars.columns
- **Extensibility**: Allows adding custom handlers for pre/post-execution data processing.
  - (e.g.) db.param_handlers = [sanitizer_params, my_param_converter]
  - (e.g.) db.result_handlers = [myfunc, my_redact_func]
  - (e.g.) db.execution_handler = my_custom_execution_flow_handler
  - You can also add them all at once during instantiation.

### In Development

- **Types**: Adding in a types file for code readability.
- **Testing**: Complete testing suite for all available commands. Add in log to DB (instead of csv and html), etc.
- **Docs**: Comprehension docs, split into smaller, readable formats. ReadtheDocs integration.
- **Error Handler**: A better error handling mechanism for error_handler function(s).
- **Direct Config File Management**: Provide your configuration as a path into the connection object and it will import it for you. (With initial design to support yaml/json)

### Feature Roadmap

- **ORM Support**: Possible better ORM integration with an easier to use join functionality.
- **Pydantic Dataclasses**: Reduce code and redudancy using pydantic dataclasses.
- **Schema Generation to Model Files**: Using SqlAlchemy's schema generation functionality to generate model files with associated config files to sync.
- **Support for Event Listners**: Event detection and handling
- **Logging**: Automatic logging at designated intervals - set in a config file.
- **Native Connectors**: Native connector support. Use the BaseConnection with native DBAPIs.

### Optional Dependencies

Project optional dependencies include depedencies for development and testing.

### Quick Reference Table

| **Extra** | **Description**                  | **Packages Included**                                |
| :-------- | :------------------------------- | :--------------------------------------------------- |
| `dev`     | Development tools                | `bandit`, `ruff`, `black`, `isort`                   |
| `test`    | Testing tools                    | `pytest`, `pyaml-env`, `pytest-order`, `pytest-html` |
| `all_dbs` | All database drivers for testing | `mysql`, `mssql`, `psycopg2`, `oracledb`             |
| `all`     | All optional dependencies        | `dev`, `test`, `all_dbs`                             |

Set up your configuration file and import it (as a dictionary). You can use any configuration type you want so long as it matches the model defined below. For the following example, we will use yaml.
### Testing

The github repo for quik-db includes a full test configuration, including docker compose, and instructions for configuring the test environment. Read the full documentation here:  https://github.com/hotnsoursoup/quik-db/blob/master/docs/tests.md.


# Quick Start

## Installation

```console
pip install quik_db
```


```yaml
# YAML configuration file
dialect: mysql
url:"mysql+pymysql://user:pass@localhost:3306/mysql"
```

Alternative configuration file with connection_params.

```yaml
# YAML file with environment variable support (via pyaml_env)
dialect: mysql
connection_params:
  drivername: mysql+mysqldb
  host: localhost
  user: !ENV {DB_USER}
  password: !ENV {DB_PASSWORD}
```

A more advanced example supports sqlalchemy engine options. (Support for the exact settings may change/vary depending on driver). See https://docs.sqlalchemy.org/en/20/core/engines.html#sqlalchemy.create_engine for more information on what can be passed in.

```yaml
dialect: oracle
description: PrimaryOracle database used for logging.
connection_params:
  drivername: oracle+oracledb
  host: localhost
  user: !ENV {DB_USER}
  password: !ENV {DB_PASSWORD}
  query:
    schema_name: FREEPDB1
  options:
    hide_parameters: True
    echo: False
    encoding: utf-8
    execution_options:
      isolation_level: SERIALIZABLE
      logging_name: mysql_db1
    pool_size: 15
    max_overflow: 5
```

A shorthand import of the SQLAlchemy connection.

```python
from quik_db import connection
```

Full import with alias.

```python
from quik_db import SQLAlchemyConnection
```

Creating the connection and executing the query.

```python
from pyaml_env import parse_config

config_file = "\path\to\config.yaml"
config = parse_yaml(config_file)

# Load the connection using the configuration file
db = connection(config)

# Execute a raw SQL query
query = "select * from mytable"

# A connection is made when execute is run.
result = db.execute(query)
```

If you want to control the connection timing you can call connect.

```python
db.connect()
```

## Executing queries with parameters

The library uses SQLAlchemy's `text()` function to protect against injection
attacks for `all` Queries with parameters must use <span style="color:orange">**:variable**</span> notation to identify the variable to be formatted.

```python
# Parameters must be a dictionary/mapping
params = {"id": 1}
query = "SELECT * FROM mytable WHERE id = :id"
result = db.execute(query, params)

```

Or you can use tuples for the values. Note the use of IN.

```python
query = "select * from mytable where id IN :id"
params = {"id": (1, 2, 3)}

result = db.execute(query, params)
```

### Calling stored procedures

Calling the `execute_sp` method with the name of the stored procedure will generate the
sql query for the dialect selected and then pass it to execute. There is no paging
capability, but you can still fetch results from the result object if the database
supports it. (e.g. Postgresql and oracle do not natively support it.)

```python
# Call a stored procedure and fetch results
procedure_name = "{schema}.{procedure_name}"
result = db.execute_sp(procedure_name, params)

```

### Auto prefix schema

You can enable auto-prefixing of the schema by enabling it in query_settings.
Any procedures already prefixed `will not` have the schema added. If queries
or stored procedures are not explicitly enabled, both are enabled when a prefix_schema is provided.

Both are enabled when only `prefix_schema` is set.

```yaml
# Enabled for both
query_settings:
   prefix_schema: dbo.schema
```

```yaml
# Enabled for both, explicitly defined.
query_settings:
   prefix_schema: dbo.schema
   prefix_queries: True
   prefix_procedures: True
```

```yaml
# Enabled only for queries
query_settings:
   prefix_schema: dbo.schema
   prefix_queries: True
   prefix_procedures: False
```

This functions by taking the prefix_schema and modifying either the stored procedure (and its query) and a sql query.

```python
# At runtime, db.execute_sp will send in dbo.schema.getuser by calling self.add_schema_prefix()
procedure_name = "getuser"
db.execute_sp(procedure_name)
```

NOTE: The library automatically detects if there is already a schema/table name attached the procedure name by looking for a `.` in the name. If it does find it, it will not make a change. For queries, the library will examine the sql query and add the schema to tables in the query, with respect to CTE's.

The method can be called directly as well.

```python
formatted_query = db.add_schema_prefix(query)
```

<span style="color:orange">NOTE: This functionality has not been fully tested with advanced queries.</span>

Example:

<details>
  <summary>Original SQL - Click to Expand</summary>

```sql
WITH CustomerOrders AS (
  SELECT
    Customer_ID,
    Order_ID,
    Order_Date
  FROM
    Orders
),
CustomerInfo AS (
  SELECT
    Customer_ID,
    Customer_Name,
    Customer_City
  FROM
    Customers
)
SELECT
  ci.Customer_Name,
  ci.Customer_City,
  (
    SELECT COUNT(*)
    FROM CustomerOrders co
    WHERE co.Customer_ID = ci.Customer_ID
  ) AS TotalOrders,
  (
    SELECT AVG(DATEDIFF(DAY, co.Order_Date, GETDATE()))
    FROM CustomerOrders co
    WHERE co.Customer_ID = ci.Customer_ID
  ) AS AverageOrderAge,
  pi.Product_Name,
  pi.Product_Category,
  od.Quantity,
  od.Total_Price
FROM
  CustomerInfo ci
JOIN
  CustomerOrders co ON ci.Customer_ID = co.Customer_ID
JOIN
  OrderDetails od ON co.Order_ID = od.Order_ID
JOIN
  ProductInfo pi ON od.Product_ID = pi.Product_ID
GROUP BY
  ci.Customer_Name,
  ci.Customer_City,
  pi.Product_Name,
  pi.Product_Category,
  od.Quantity,
  od.Total_Price

```

</details>

<details>
  <summary>Formatted Query</summary>

```sql
WITH CustomerOrders AS
  (SELECT Customer_ID,
          Order_ID,
          Order_Date
   FROM dbo.Orders),
     CustomerInfo AS
  (SELECT Customer_ID,
          Customer_Name,
          Customer_City
   FROM dbo.Customers)
SELECT ci.Customer_Name,
       ci.Customer_City,

  (SELECT COUNT(*)
   FROM CustomerOrders AS co
   WHERE co.Customer_ID = ci.Customer_ID) AS TotalOrders,

  (SELECT AVG(DATEDIFF(DAY, co.Order_Date))
   FROM CustomerOrders AS co
   WHERE co.Customer_ID = ci.Customer_ID) AS AverageOrderAge,
       pi.Product_Name,
       pi.Product_Category,
       od.Quantity,
       od.Total_Price
FROM CustomerInfo AS ci
JOIN CustomerOrders AS co ON ci.Customer_ID = co.Customer_ID
JOIN dbo.OrderDetails AS od ON co.Order_ID = od.Order_ID
JOIN dbo.ProductInfo AS pi ON od.Product_ID = pi.Product_ID
GROUP BY ci.Customer_Name,
         ci.Customer_City,
         pi.Product_Name,
         pi.Product_Category,
         od.Quantity,
         od.Total_Price
```

</details>

## The Result Object

The `Result` object for SQLAlchemy provides numerous features. It can act similar to
a cursor where you may want to iterate through the rows to process your data or
access the attributes to see if your data manipulation query was successful.

Here's how you can access the Result object **after** execution. This is important
when you only fetch a subset of the data . After fetching all results,
the result object will lose any metadata associated with the rows (such as columns), but the
connection object will retain that information for you.

In some unsupported dialects, the obj.result will return the result and not the result object.

```python
# Accessing the result object
print(db.result)

# Counting remaining rows (select query) OR see affected rows (data manipulation query)
print(db.result.rowcount)

# Get the columns from the result
print(db.vars.columns)

# Fetching any additional results via fetch. See below for more fetch options
if db.result.rowcount > 1:
   db.result.fetchall()
```

## Fetch, Offset, and Limit

This library supports the ability to set the automatic fetching and limiting of results
through a configuration or at execution. The offset can only be set at execution.
`Limit` is intended for query modification directly whereas fetch is to retrieve
results from the `Result object`.

### Using Limit

Setting `limit` in the configuration will automatically attempt to add paging,
based on dialect, to any `raw sql queries`. It will detect if any query already has
paging in place.

```yaml
# YAML - Set in the configuration for all instances using this configuration
dialect: mysql
url: "mysql+pymysql://user:pass@localhost:3306/mysql"
query_settings:
   limit: 30
```

```python
# Set on the specific instance. This will modify all select queries.
db.config.limit = 10

# Set at execution, used with offset, and passed in as function args
result = db.execute(query, params, offset=50, limit=30)

# Set at execution using method chaining. Execute must be last in the chain.
result = db.offset(50).limit(30).execute(query, params)

```

### Using fetch

Fetch is used for post execution retrieval of the results. Fetch may not be
available if you have created a subclass of connection and your
connection object does not support it. Using fetch will return the result(data)
and any remaining rows will stay on the Result object.

```python
# Execute query with fetch, returning a subset of rows
data = db.execute(query, args, fetch=50)

# Or method chaining
data = db.fetch(50).execute(query, args)

```

Accessing the remaining rows on the `Result` object.

```python
# Fetch only 50 rows in a result set of over 50.
data = db.execute(query, args, fetch=50)

# Fetch remaining by accessing the result object
if db.result.rowcount > 1:
   fetched_results = db.result.fetchall()
```

Using the fetch method will automatically fetch from the current result object
for that instance.

```python
while db.result.rowcount > 0:
    fetched_data = db.fetch(5)
    myfunc(fetched_data)

```

## Disable all fetching

You can disable automatic fetching after execution by setting `enable_fetch: False` in the configuration or on the instance.
```yaml
# yaml
dialect: mysql
url: "mysql+pymysql://user:pass@localhost:3306/mysql"
enable_fetch: False
```

```python
# Changed at the intance. Default is True.
db.config.query_settings.enable_fetch = False
```

# Configuration File Models

The configuration models are models that ensure that your configuration is set
correctly to function properly with the connection. There are currently two
models - a single database or a multidatabase config.  Please note that despite
both `url` and `connection_params` being listed as Optional, the model validation
<span style="color:orange">**expects**</span> one of them is present.

Examples shown are using the **SQLAlchemyConnection** class.

### Single Database Model

- **Required Fields:**
  - **Valid Dialect**
    - Dialect must be one of the supported dialects listed below in the default drivers section.
  - **For SQLite:**
    - `url`: Specify the path to your SQLite database file.
  - **For Other Dialects:**
    - `dialect`: Specify the database dialect (e.g., "mysql", "postgresql", "sqlite").
    - Either `url` (which is the connection string) or `connection_params` must be provided. If both are present, the model will error. (Future versions may just provide one superceding the other)
      - If `connection_params` are used for the connection, host and username are required.
    - Setting `query_settings.prefix_schema` requires either `query_settings.prefix_procedures` or `query_settings.prefix_queries` to be set True or neither of them set. (If neither are set, the model will assume both are `True`). They both cannot be `False`.
      - Conversely, if either option is set to `True`, the value in `prefix_schema` must be set.
    - If a `drivername` is not specified in `connection_params`, the default driver will be used. See below.
- **Dialect Drivers:**
  - **Description:**
      Each supported dialect comes with its associated driver string.

  - **Default Drivers:**

      | Dialect    | Connection String   |
      | ---------- | ------------------- |
      | postgresql | postgresql+psycopg2 |
      | mysql      | mysql+pymysql       |
      | sqlite     | sqlite              |
      | oracle     | oracle+cx_oracle    |
      | mssql      | mssql+pymssql       |

Example:

```yaml
# yaml
dialect: mysql
url:"mysql+pymysql://username:password@localhost:3306/mysql"
query_settings:
  limit: 30  # Validation fails if set to 0 or None
```

Example with `connection_params`:

```yaml
# yaml
dialect: mysql
connection_params:
   drivername: mysql+mysqldb
   host: localhost
   user: myuserid
   password: mypass1
   database: mydatabase
   query: # passed as a query argument and not a sqlalchemy option
      pool_size: 20
      pool_timeout: 30
```

Sqlite databases require a path to the `.db` file in the url. It does not support connection_params at this time.

```yaml
dialect: sqlite
url: mysqlitedb.db
```

### Available Configuration Options

Note - some are not yet be implemented (such as odbc and orm)

| Field                | Type                                                       | Required                                     | Description                                                                                                                                                                    | Development Notes                                   |
| -------------------- | ---------------------------------------------------------- | -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------- |
| `connection_params`  | ConnectionParams(BaseModel)                                | Yes (see note)                               | Connection parameters (host, username, etc.).                                                                                                                                  | Alternative to url for defining connection details. |
| `default`            | bool                                                       | No                                           | Marks this as the default connection. Default: False.                                                                                                                          | Set to True if this is the default connection.      |
| `description`        | str                                                        | No                                           | A brief description of the database connection.                                                                                                                                | Used for documentation or metadata.                 |
| `dialect`            | Literal[mysql, mariadb, mssql, postgresql, oracle, sqlite] | Yes                                          | The database dialect to use.                                                                                                                                                   | Required to specify the database type.              |
| `limit`              | int                                                        | No                                           | The number of results per request when querying.                                                                                                                               | Helps manage query result pagination.               |
| `query_settings`     | QuerySettings(BaseModel)                                   | No                                           | The number of results per page when querying.                                                                                                                                  | Helps manage query result pagination.               |
| `result_as_mappings` | bool                                                       | No                                           | Return query results as mappings instead of tuples.                                                                                                                            | Helps manage the format of returned query results.  |
| `schema_name`        | str                                                        | No                                           | The schema to use with the connection.                                                                                                                                         | Useful for queries requiring schema specification.  |
| `url`                | str                                                        | No                                           | Connection string (for SQL Alchemy or ODBC).                                                                                                                                   |
| `options`            | dict[str, str]                                             | Additional options to pass to the connection | Mapping to be passed into the connect() method. For `SQLAlchemyConnection`, these are sent as engine options. May not be supported by all database libraries when subclassing. | Refer to SqlAlchemy docs for more information. https://docs.sqlalchemy.org/en/20/core/engines.html#sqlalchemy.create_engine
| `schema_name`        | str                                                        |                                              | Currently unused                                                                                                                                                               |

### ConnectionParams

Nested Model under DatabaseModel.

- <span style="color: orange;">**ONLY** required if `url` is not present. </span>
- Can be used just to add `options` and `args` without the connections if `url` is used.
- `host` and `username` are required if used for connection settings

| Field        | Type           | Description                                          | Development Notes                                       |
| ------------ | -------------- | ---------------------------------------------------- | ------------------------------------------------------- |
| `drivername` | str            | The driver to use with the connection.               | Needed for ODBC or certain dialects.                    |
| `host`       | str            | The database host.                                   | Required if used for connection (`url` is not present). |
| `password`   | str            | The password for database authentication.            | Required for most connections except SQLite.            |
| `port`       | int            | The port number for the database connection.         | Standard ports apply, e.g., 3306 for MySQL.             |
| `username`   | str            | The username for database authentication.            | Required if used for connection (`url` is not present). |
| `query`      | dict[str, str] | url query parameters to add to the connection string |

### QuerySettings

Nested in DatabaseModel

| Field               | Type | Default | Description                                         | Development Notes                                                                                            |
| ------------------- | ---- | ------- | --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `disable_fetch`     | bool | False   | Disables fetching of results after query execution. | Useful for queries where fetching results is not needed (e.g., updates). This will return the result object. |
| `add_schema_prefix` | bool | False   | Adds schema prefix to table names in queries.       | Enables automatic prefixing with the schema name for cross-schema queries.                                   |
| `limit`             | int  | 0       | Number of results per page.                         | Used to control pagination for query results. Setting to 0 disables limit.                                   |

### MultiDatabaseModel

This model supports configurations for multiple databases. Each database is
represented by a `name` (key) in the configuration file and the value is a dictionary that conforms to the DatabaseModel. (Utilizes a nested structure).

Note, only one db can be configured as the default DB, otherwise the model validation will fail.

Example:

```yaml
# Yaml
mydefaultdatabase:
   dialect: mysql
   default: True
   connection_params:
      drivername: mysql+mysqldb
      host: localhost
      user: myuserid
      password: mypass1
      database: mydatabase
myloggingdb:
   dialect: sqlite
   path: mysqlitedb.db
```

Code, assume the above has been imported as `config`.

```python
from quik_db import SQLAlchemyConnection as connection

# A name (key) is used to select the database
db = connection(config=config, name='mydatabase1')

# name is not provided and the config is multi database
db = connection(config)
```

If a MultidatabaseModel config is used, one of
these scenarios will occur.

1. A **name** argument is provided with the configuration.

   - ```python
      db = connection(config=config, name=name)
      ```

2. A **default** key with a value of **True**.

   - ```yaml
      mydb1:
         default: True
         dialect: mysql
         url: "mysql+pymysql://username:password@localhost:3306/mysql"
      ```

   - The model validation ensures only 1 can be set to default.
3. A default config assigned to the class.
   - db.`default_config`
4. A default config **name** assigned to the class
   - db.`default_config_name`
5. The first database listed in the multidatabase configuration.

# Model Validation

The model validation using the configuration models above is done automatically when using SQLAlchemyConnection or any subclass of the Connection. If you need to be able to test the configuration files outside of the connection to ensure
your configuration is functioning properly, you have a couple different options.

To validate your configuration with these models, all you have to do is pass the configuration (as a dict) into the model.

Example:

```python
from pyaml_env import parse_config
from quik_db.models.models import DatabaseModel, MultiDatabaseModel


config_file = '/path/to/config.yaml'
config = parse_config(config_file)

validated_config = DatabaseModel(**config)
# Read the url field.
validated_config.url
# Converts it from a model, to a dict.
config_dict = validated_config.model_dump()
# model_json_dump() dumps to json.
config_json = validated_config.model_dump_json()
```

If there are `no validation errors`, it will return the `model` of the data - including keys and default values that do not exist in your config file.

## ValidationError

The Pydantic library provides different types of errors, but the one used in this library is the ValidationError. This is built into the models DatabaseModel and MultiDatabase Model. These models are designed so that any mismatch in field type, field value, or missing required fields are brought to your attention.

If you pass your configuration into the model and there is an exception, you will see something like this.

```python
try:
   validated_config = DatabaseModel(**config)
   print(validated_config.url)
except ValidationError as e:
   print(e)
```

The exception message.

```console
2 validation errors for DatabaseModel
dialect
  Field required [type=missing, input_value=None, input_type=NoneType]
    For further information visit https://errors.pydantic.dev/2.9/v/missing
url.connection_params
  Field required [type=missing, input_value=None, input_type=NoneType]
    For further information visit https://errors.pydantic.dev/2.9/v/missing

```

## ModelValidationError / model_validator

This library provides an alternative way to validate the models with a custom exception
object, `ModelValidationError`, and a function to support it.

```python
# models = [DatabaseModel, MultiDatabaseModel]

def model_validator(
    db_config: dict[str, Any],
    models: dict[str, Type[BaseModel]] = models,
    model_name: str = None,
) -> BaseModel:
```

You can use this function to validate a configuration without specifying the model you want to validate it
against. It will iterate through and provide any validation errors it may find for all models. The validation
errors are collected and then raised using `ModelValidationError`.

Example:

```yaml
# yaml file
mydatabase1:
   description: "My Favorite DB"
   default: True
   url:"mariadb+pymysql://root:nguyen11@localhost:3306/mydb"
   query_settings:
      limit: 0
   one_row_output: dict
mysqlitedb:
   dialect: sqlite

```

```python
# Python
try:
   model_validator(config)
except ModelValidationError as e:
   print(e)
```

This will yield the output seen below.

```console
2 models tested for validation.

Model 'DatabaseModel' encountered 2 errors:
  - Location: dialect
    Message: Dialect is required for the database configuration.
    Type: missing
    valid_values: ['mysql', 'mariadb', 'mssql', 'postgresql', 'oracle', 'sqlite']
  - Location: url .connection_params
    Message: Either `url` or `connection_params` must be provided for non-sqlite dialects.
    Type: missing
    example: {'url': 'sqlite:///path/to/sqlite.db', 'connection_params': {'host': 'localhost', 'username': 'user', 'password': 'pass1', 'port': 3306, 'database': 'mydb'}}

Model 'MultiDatabaseModel' encountered 3 errors:
  - Location: mydatabase1.dialect
    Message: Dialect is required for the database configuration.
    Type: missing
    valid_values: ['mysql', 'mariadb', 'mssql', 'postgresql', 'oracle', 'sqlite']
  - Location: mysqlitedb.path
    Message: `path` is required when `dialect` is `sqlite`.
    Type: missing
    example: {'path: /path/to/sqlite.db'}

Total Errors: 5
```

You can also specify if you want it to test against only one particular model and any other models you may want to build on top.

```python

model_validator(config, models=my_models)

validate_db_config(config, model_name='single') # Or use `multi` for MultiDatabaseModel
```

# Handlers and Methods

This library offers multiple ways to control execution flow without subclassing.
Handlers can be assigned directly as attributes or passed in lists. They are executed
in the order provided.

Example:

```python
from quik_db.core.handlers import result_to_dict

def redact_names(data):
    # Redact sensitive names from data
    pass

def my_exc_handler(result_data):
  # do things

# if the handler supports a list of Callables. (result handler does)
db.result_handlers = [redact_names, result_to_dict]

# Execution handler only allows for one callable
db.execution_handler = myexc_handlr

```

### Execution flow handlers (Connection)

| Handler/method    | Type                       | Description                                                                                                                                                      | Notes                                                                                                                                                                            |
| ----------------- | -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| param_handlers    | Callable \| list[Callable] | A callable function or list of functions to process on query parameters.                                                                                         | Only works for raw sql and stored procedures. May be useful parameter sanitizing or transformations.                                                                             |
| execution_handler | Callable                   | A handler to override the execution of the query to obtain the result_object                                                                                     | It will also override any fetch logic as well. It assumes you will build the fetch logic self.execution_handler(query, fetch)                                                    |
| result_handlers   | list[Callable]             | Processes the data after execution/fetch. It will iterate through and run each handler in order.                                                                 | You can use self.result_handlers(handlers) to add additional handlers or simply reassign using self.process_handlers = [handler1, handler2]                                      |
| error_handlers    | list[Callable]             | Functions to handle errors that occur during execution. Each handler takes the exception as an argument and can return a modified exception or any other object. | Useful for custom error handling or logging.                                                                                                                                     |
| exit              | Callable                   | Define a custom **exit** method for the class                                                                                                                    | Useful if the connection does not have a native **exit** method. The default use of SQLAlchemy provides one already so there is no need to implement unless you are subclassing. |

# SQLAlchemyConnection

SQLAlchemyConnection is the primary connection object of the library. It is a subclass of the DatabaseConnection class with methods for session management. The input args provide flexibility in configuring the type of connection or session you may want to use.

| argument     | Type                                                | default | Description                                                                       |
| ------------ | --------------------------------------------------- | ------- | --------------------------------------------------------------------------------- |
| config       | dict                                                |         | The database configuration                                                        |
| name         | str                                                 | None    | For multidatabase models, the name (key) of the database connection configuration |
| connection_type | Literal["scoped", "session", "direct"]    | direct  | Determines the connection type to be created when self.connect() is called.  |
| session      | Session \| scoped_session \| None |  None | A variable used to pass in an existing session_factory from another SqlAlchemyConnection object. See below for more information.  |

### Connection Types in `SQLAlchemyConnection`

The `SQLAlchemyConnection` class supports different connection types: `scoped`, `session`, and `direct`.

- **direct**: Establishes a one-time connection using `engine.connect()`.
- **session**: Maintains a persistent session created by `sessionmaker`.
- **scoped**: Creates a thread-safe `scoped_session` for use across threads.

Example of creating a scoped session.

```python
from quik_db import db
from pyaml_env import parse_config

config_file = "\path\to\config.yaml"
config = parse_config(config_file)

# Create the connection using scoped session
connection = db(config, connection_type="scoped")

# Execute as normal
connection.execute("select * from users")
```

### Generating new sessions

You can generate a new session by directly calling the session method. The new session object will retain all the original configuration details of the original object. (Please keep in mind that changes to any mutable configurations will affect all instances)
```python
# Generate a new SqlAlchemyConnection object using an existing session. (Has to be session type and not direct)
new_session = connection.session()

new_session.execute("select 1")
```


# License
`quik_db` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

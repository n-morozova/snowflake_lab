# snowflake & dbt workshop

# DBT Fundamentals

## Prerequisites

1. GitHub
2. Creation of the Database
3. Docker Desktop


## Install dbt and VENV

Windows:

```bash
python3 -m venv venv
source venv/bin/Activate.ps1
```

Install dbt for Postgress

```bash
python -m pip install dbt-core dbt-postgres
```

Create `requirements.txt` file:

```bash
pip freeze -l > requirements.txt
```

Check if we have dbt

```bash
dbt --version
```

## Create new dbt project

```bash
dbt init
```

We can us ENV variables to avoid putting password into profile.

Finally, we will move all content from `dbtworkshop` into the root directory.

We can test that dbt is working with `dbt

## Running sample models
 `dbt run`

Review folder `logs`

## Build dbt model for our example

Let's delete the models and create new models for an example.

Create folder and 3 files: .sql + .yml for each model
after that:
And modify the `dbt_project.yaml`


## Documentation for our new models and generic tests

Generic tests are simple:

```yaml
data_tests:
  - unique
  - not_null

data_tests:
  - accepted_values:
      values:
        - completed
        - shipped
        - returned
        - return_pending
        - placed
```

We can also add a Singular test as an example:

`tests/fct_orders_negative_discount_amount.sql

```sql
--If no discount is given it should be equal to zero
--Otherwise it will be negative

select *
  from {{ ref('fct_orders') }}
 where item_discount_amount > 0
```

As a result we have 3 models and their tests.

We can run models with

```bash
dbt run --select tag:staging
```

And test:

```bash
dbt test --select tag:staging
```

## Adding Freshness test

For source models we can add a freshness test base on specific timestamp column

```yml
version: 2

models:
  - name: _tpch_sources.yml
    description: This model cleans up order data
    loaded_at_field: _etl_loaded_at
    freshness:
      warn_after: {count: 12, period: hour}
      error_after: {count: 24, period: hour}

## Adding Pre-Commit

We can add Pre-Commit File to check local quality of code

Install the `pre-commit` package

```bash
pip install pre-commit
```

Create file `.pre-commit-config.yaml`


Activate pre-commit

```bash
pre-commit install
```

## Creating Pull Request

Add into the `.gitignore` folder with VENV `venv/`.

Let's create actual branch for development work (usually it starts before anything else)

```bash
git checkout -b feature/new-dbt-model
```

```bash
git add .
git commit -m "Adding initial models"
```

It will test everything and commit.

We also would like to add a template for PR. Create a new folder `.github` and inside a new file `pull_request_template.md`

## Adding CI step

We want to make sure same checks run in GitHub.

Let's create a GitHub Action to run it

Add new file `.github/workflows/dbt-ci-jobs.yml`

```yaml
name: Run Pre-commit Hooks

on:
  pull_request:
    branches:
      - main
  push:
    branches:
      - main

jobs:
  pre-commit:
    runs-on: ubuntu-latest

    steps:
      # Checkout the code and fetch all branches
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0 # Ensure the full history is fetched, not just the last commit

      # Set up Python environment
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.11

      # Install dependencies
      - name: Install dependencies
        run: |
          python -m venv venv
          . venv/bin/activate
          pip install --upgrade pip
          pip install -r requirements.txt
          pre-commit install --install-hooks

      # Fetch the main branch to ensure it's available for comparison
      - name: Fetch main branch
        run: git fetch origin main

      # Run pre-commit on all files changed between the current branch and main
      - name: Run pre-commit on all changed files
        run: |
          . venv/bin/activate
          # Get the list of files changed between the current branch and main
          files=$(git diff --name-only origin/main)
          if [ -n "$files" ]; then
            pre-commit run --files $files
          else
            echo "No modified files to check."
          fi
```

## Adding Marts

We leveraged dbt package: `dbt_utils` and we need to add package and install.

Add file `packages.yml`

```yaml
packages:
  - package: dbt-labs/dbt_utils
    version: 1.3.0
  - package: calogica/dbt_expectations
    version: 0.10.4
  - package: calogica/dbt_date
    version: 0.10.1
```
And install packages

```bash
dbt deps
```

We also need to update `dbt_project.yml` file:

```yml
models:
  dbtworkshop:
    # Config indicated by + and applies to all files under models/example/
    staging:
      +materialized: view
      +tags: staging
    mart:
      +materialized: view
      +tags: mart
```

We can run the models

```bash
dbt build --select tag:mart
```

## How to control profiles

When we run dbt we can specify `target` env and `profile` path.

```bash
dbt build --select fct_orders --target dev --profiles-dir ~/.dbt/
```

## Adding macro with ETL timestamp

Add file with macro `macros/add_etl_timestamp.sql`

```sql
{% macro add_etl_timestamp() %}
    CURRENT_TIMESTAMP as etl_timestamp_utc
{% endmacro %}
```

And we can add this marco into existing models:

## Checking the dbt docs

```bash
 dbt docs generate
 dbt docs serve --host localhost --port 8091
 ```

 Open in browser `http://localhost:8091/#!/overview`.

## Running dbt check in CI

We need to update our GitHub actions to run dbt checks because it will require to run dbt and connect database.

DBT checkpoint is checking the dbt artifacts, we should make sure it can run and compile dbt.

For this we will add new profile `profiles.yaml`


```yaml
default:
  outputs:
    dev:
      type: postgres
      host: '{{ env_var("DBT_HOST") }}'
      user: '{{ env_var("DBT_USER") }}'
      password: '{{ env_var("DBT_PASSWORD") }}'
      port: 5432
      dbname: '{{ env_var("DBT_DATABASE") }}'
      schema: dev
  target: dev
```

In GitHub we can assign values for these env variables in GitHub Repository -> Settings.

We can modify our GitHub Actions to include the `dbt complie` part:

```yaml
name: Run Pre-commit Hooks with Postgres

on:
  pull_request:
    branches:
      - main
  push:
    branches:
      - main

jobs:
  pre-commit:
    runs-on: ubuntu-latest

    steps:
      # Checkout the code
      - name: Checkout code
        uses: actions/checkout@v3
        with:
          fetch-depth: 0

      # Set up Python environment
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.11

      # Install dependencies
      - name: Install dependencies
        run: |
          python -m venv venv
          . venv/bin/activate
          pip install --upgrade pip
          pip install -r requirements.txt

      # Install dbt package dependencies
      - name: Install dbt package dependencies
        run: |
          . venv/bin/activate
          dbt deps

      # Copy the profiles.yml file to the correct location
      - name: Copy profiles.yml to /home/runner/.dbt
        run: |
          mkdir -p /home/runner/.dbt
          cp ./profiles.yml /home/runner/.dbt/profiles.yml

      # Compile the dbt project
      - name: Compile dbt project
        run: |
          . venv/bin/activate
          dbt compile
        env:
          DBT_USER: ${{ secrets.DBT_USER }}
          DBT_PASSWORD: ${{ secrets.DBT_PASSWORD }}
          DBT_HOST: ${{ secrets.DBT_HOST }}
          DBT_DATABASE: ${{ secrets.DBT_DATABASE }}

      # Run pre-commit hooks
      - name: Run pre-commit on all changed files
        run: |
          . venv/bin/activate
          files=$(git diff --name-only origin/main)
          if [ -n "$files" ]; then
            pre-commit run --files $files
          else
            echo "No modified files to check."
          fi
```

To make is pass, lets delete the singular test.

## Running dbt models in Staging env

We can also add one more step to run dbt models in another Schema `CI`.

Let's add the schema CI into Postgres

```sql
create schema if not exists ci;
```

We should add one more profile:

```yaml
dbtworkshop:
  outputs:
    dev:
      type: postgres
      host: '{{ env_var("DBT_HOST") }}'
      user: '{{ env_var("DBT_USER") }}'
      password: '{{ env_var("DBT_PASSWORD") }}'
      port: 5432
      dbname: '{{ env_var("DBT_DATABASE") }}'
      schema: dev
    ci:
      type: postgres
      host: '{{ env_var("DBT_HOST") }}'
      user: '{{ env_var("DBT_USER") }}'
      password: '{{ env_var("DBT_PASSWORD") }}'
      port: 5432
      dbname: '{{ env_var("DBT_DATABASE") }}'
      schema: ci_schema

  target: dev
```
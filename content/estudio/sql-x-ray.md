---
title: "sql-x-ray"
weight: 40
description: "A privacy-safe SQL schema dump tool for LLM context priming. Single-file SQL scripts for eight engines (PostgreSQL, MySQL, MariaDB, SQL Server, Oracle, SQLite, BigQuery, Firebird) produce a structured JSON map of tables, columns, keys, and indexes. Structure only, never row data, defaults, or constraint expressions."
summary: "SQL schema dump for LLMs."
tags: ["sql", "postgresql", "mysql", "mariadb", "sql-server", "oracle", "sqlite", "bigquery", "firebird", "json", "llm"]
showDate: false
showReadingTime: true
showAuthor: false
---

{{< lead >}}
Dumps a SQL database's structure as privacy-safe JSON, so an LLM can write accurate queries without seeing any rows.
{{< /lead >}}

## At a Glance

Copying a full SQL schema into an LLM chat sounds easy. Then you try it on a real database and three things happen at once: the schema is too big for the context window, the view bodies and check constraint expressions are leaking literal values from production data, and your security review committee never approved any of it.

`sql-x-ray` is a single SQL script (one per engine) that produces a privacy-safe JSON map of a database's structure. Run it from any client that can return a multi-line cell ([DBeaver](https://dbeaver.io/), [DataGrip](https://www.jetbrains.com/datagrip/), psql, [SSMS](https://learn.microsoft.com/en-us/sql/ssms/), Metabase). One result row comes back. Copy it, paste it into an LLM session, and from that point forward the model can write accurate queries against tables it has never seen a single row of.

Eight engines are supported: PostgreSQL, MySQL, MariaDB, SQL Server, Oracle, SQLite, BigQuery, and Firebird. The scripts share a consistent structure and emit a consistent JSON shape (Firebird emits Markdown instead, because Firebird 4.0 lacks native JSON aggregation), so an LLM that has seen one dump can read any of them.

## The Problem

Three concrete frictions show up in real LLM-assisted query work.

**Schemas are too big to paste.** A sixty-table operational database produces three thousand lines of `CREATE TABLE` if you `pg_dump --schema-only` it. That is most of the context budget gone before the first question, and most of those lines are restating column types the LLM already understands.

**The schema you can paste leaks values.** `DEFAULT 'TRIAGE_QUEUE_2'` and `CHECK (department IN ('cardiology', 'oncology', 'ortho'))` both surface real business strings. View bodies are worse: they bake in filter literals, role assumptions, and sometimes hardcoded identifiers. A view named `active_high_risk_patients` becomes a one-line description of exactly which patient subset is sensitive. None of that should leave the database.

**Sample queries are slow and wrong.** Asking the LLM "what does this table look like, send me five rows" runs round trips, and the model cheerfully invents data when no rows come back. What the model needs is structure, not samples.

`sql-x-ray` answers all three: a compact JSON dump, structure only, generated in a single round trip by SQL that runs entirely against system catalogs.

## The Approach

A single SQL script per engine queries the catalog views, aggregates per-table metadata, and assembles one JSON document. No installs, no Python runtime, no extensions; whatever client you already use to query the database can produce the dump.

The script is a single `WITH ... SELECT` query. The CTEs build the dump incrementally:

{{< mermaid >}}
flowchart TD
    A["SQL Client (DBeaver, psql, SSMS, ...)"] --> B["sql-x-ray script (engine-specific)"]
    B --> C["INFORMATION_SCHEMA / system catalogs"]
    C --> D1["cols (per-table column lists)"]
    C --> D2["pks (primary key columns)"]
    C --> D3["fks (foreign key relationships)"]
    C --> D4["idx (user-created indexes)"]
    D1 --> E["tables_json (assembled per-table objects)"]
    D2 --> E
    D3 --> E
    D4 --> E
    E --> F["Final SELECT: JSON assembly"]
    F --> G["Single result cell"]
    G --> H["Paste into LLM session"]
{{< /mermaid >}}

The CTE chain has the same shape across engines: columns, then primary keys, then foreign keys, then unique constraints, then indexes, then trigger counts, then the per-table assembly, then views, routines, and metadata. The script-per-engine factoring exists because catalog views differ between vendors; the *output shape* does not.

## Walking Through the Dump

### Reading the Catalog

Every engine exposes its schema metadata through a catalog. PostgreSQL has `pg_catalog` and `information_schema`; SQL Server has `sys.*`; Oracle has `USER_*` and `ALL_*`; SQLite has `sqlite_master` plus pragma table-valued functions; BigQuery has dataset-scoped `INFORMATION_SCHEMA.*`; Firebird has the `RDB$` system tables. The scripts read from whichever catalog the engine provides, never from user data.

A representative `cols` CTE, taken from the SQLite script, shows the shape:

```sql
cols AS (
    SELECT
        m.name AS table_name,
        json_group_array(
            json_object(
                'name',        p.name,
                'position',    p.cid + 1,
                'data_type',   p.type,
                'nullable',    CASE p."notnull" WHEN 1 THEN json('false') ELSE json('true') END,
                'has_default', CASE WHEN p.dflt_value IS NOT NULL THEN json('true') ELSE json('false') END,
                'is_pk',       CASE WHEN p.pk > 0 THEN json('true') ELSE json('false') END
            )
            ORDER BY p.cid
        ) AS columns
    FROM sqlite_master m, pragma_table_info(m.name) p
    WHERE m.type = 'table'
      AND m.name NOT LIKE 'sqlite_%'
    GROUP BY m.name
)
```

Three things are worth pointing out. The `has_default` field records *whether* a default exists, never *what* it is, because the literal could be sensitive. The `+ 1` on the position is for cross-engine parity, since SQLite is 0-indexed and every other engine reports columns as 1-indexed. And the `NOT LIKE 'sqlite_%'` filter drops the internal catalog tables SQLite carries inside the database itself, which would otherwise pollute the dump.

### Composing a Table Entry

The per-table CTEs (`cols`, `pks`, `fks`, `idx`, `trigger_counts`) join in the final assembly to produce one JSON object per table. The output for a single table in an e-commerce schema looks like this:

```json
{
  "schema": "public",
  "name": "orders",
  "kind": "table",
  "primary_key": { "columns": ["order_id"] },
  "foreign_keys": [
    {
      "from_columns": ["customer_id"],
      "to_schema":    "public",
      "to_table":     "customers",
      "to_columns":   ["customer_id"],
      "on_update":    "NO ACTION",
      "on_delete":    "RESTRICT"
    }
  ],
  "check_constraint_count": 2,
  "indexes": [
    { "name": "orders_status_created_idx", "method": "btree",
      "unique": false, "partial": true,
      "columns": ["status", "created_at"] }
  ],
  "trigger_count": 1,
  "columns": [
    { "name": "order_id",    "position": 1, "data_type": "bigint",  "nullable": false, "has_default": false },
    { "name": "customer_id", "position": 2, "data_type": "bigint",  "nullable": false, "has_default": false },
    { "name": "status",      "position": 3, "data_type": "text",    "nullable": false, "has_default": true  },
    { "name": "total_cents", "position": 4, "data_type": "integer", "nullable": false, "has_default": false }
  ]
}
```

An LLM can read this and produce a correct join to `customers` on the first try: it has the FK direction, the matching columns, and the types. It also knows there is a partial index covering `(status, created_at)`, so it can write a query that uses that index profitably. None of this required showing the model a single order.

### Recording What's Not There

Some metadata matters but the contents would leak. The dump records *existence* with a count rather than reading the underlying expression. `check_constraint_count: 2` tells the model there are check constraints on the table without revealing what they enforce. `trigger_count: 1` does the same for triggers. The model can ask the human about specifics when relevant, rather than receiving them up front.

The shape stays the same across engines that don't support a concept. BigQuery has no traditional indexes, so `indexes` is always an empty array; it has no CHECK constraints, so `check_constraint_count` is always 0; it has no triggers, so `trigger_count` is always 0. SQLite has no stored procedures or functions, so `routines` is an empty array at the top level. Empty arrays are emitted explicitly so downstream code can iterate without checking for missing keys.

### The Metadata Block

Every dump opens with a `metadata` object describing the dump itself. Reading it first tells a downstream consumer everything they need to know about what they're about to parse:

```json
{
  "tool_name":      "sql-x-ray",
  "engine":         "postgresql",
  "engine_version": "16.4",
  "database":       "shop",
  "generated_at":   "2026-05-14T14:30:00Z",
  "schema_filter":  "public",
  "schemas":        ["public"],
  "object_counts":  { "tables": 4, "views": 0, "routines": 0, "sequences": 1, "types": 0 },
  "privacy_note":   "This document contains only structural metadata..."
}
```

The `object_counts` field is the size-at-a-glance signal: a dump with 40 tables is comfortably within any LLM context window, a dump with 400 tables may need trimming. The `engine` and `engine_version` fields let the consumer reason about engine-specific features (for example, the LLM knows BigQuery foreign keys are unenforced metadata, not referential integrity guarantees). The `privacy_note` is the same string on every dump, available for the LLM to lift verbatim into a system message confirming what the document is and is not.

## Why Structure-Only Matters

The privacy stance is the design. It isn't a sanitization step applied to a richer dump; it's what the script doesn't read in the first place.

Default value literals are excluded because they can carry personal data (`DEFAULT 'recipient@hospital.org'`) or business strings (`DEFAULT 'PEDIATRIC_OVERFLOW'`). Check constraint expressions are excluded because they often enumerate domains that are themselves sensitive (`CHECK (department IN ('cardiology', 'oncology', ...))` exposes the institution's service line taxonomy). View bodies are excluded because they bake in filter conditions, role assumptions, and sometimes hardcoded identifiers. Function and procedure bodies are excluded for the same reason. Enum value labels are excluded by design. Comments and descriptions are excluded because they are free-text fields that can contain anything.

What's left is unambiguous: schema names, table names, column names, types, nullability, key relationships, and index columns. None of these can carry sensitive *values* by design. The guarantee comes from the read pattern, not from filtering applied afterward.

In healthcare and education contexts this distinction matters operationally. [HIPAA's minimum-necessary principle](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/minimum-necessary-requirement/index.html) and [FERPA's directory-information rules](https://studentprivacy.ed.gov/faq/what-directory-information) both work better with a tool that demonstrably *cannot* leak protected fields than with one that requires manual review of every dump. "Structure only, never values" is a stronger claim than "we tried to filter the sensitive bits."

## What You Can Build From the Dump

The output is JSON in a stable, predictable shape. Anything that can read JSON can walk it: [`jq`](https://jqlang.github.io/jq/), Python's [`json`](https://docs.python.org/3/library/json.html) module, JavaScript's `JSON.parse`. The most common path is paste-into-LLM and ask for the artifact you want; programmatic access is the fallback when the artifact is being produced at scale or needs to drop into an automated pipeline.

### Visual ER Diagrams

The dump's `foreign_keys` array contains everything needed to construct an ER diagram: source table, source columns, target table, target columns, plus the nullability and uniqueness signals that determine cardinality. An LLM can read it and produce a [Mermaid](https://mermaid.js.org/) `erDiagram` in one prompt:

> Convert this schema dump into a Mermaid `erDiagram`. Show primary keys with `PK`, foreign keys with `FK`, and connect tables using FK relationships with proper cardinality.

A small e-commerce schema renders as:

{{< mermaid >}}
erDiagram
    customers ||--o{ orders : places
    orders ||--|{ order_items : contains
    products ||--o{ order_items : appears_in
    customers {
        bigint id PK
        text email
        text full_name
        timestamp created_at
    }
    orders {
        bigint id PK
        bigint customer_id FK
        numeric total_cents
        timestamp placed_at
    }
    order_items {
        bigint id PK
        bigint order_id FK
        bigint product_id FK
        integer quantity
    }
    products {
        bigint id PK
        text sku
        text name
        numeric price_cents
    }
{{< /mermaid >}}

[DBML](https://dbml.dbdiagram.io/home/) for [dbdiagram.io](https://dbdiagram.io/), [PlantUML](https://plantuml.com/), [Graphviz/DOT](https://graphviz.org/), and [D2](https://d2lang.com/) all work the same way: paste the dump, ask for the diagram language, get back ready-to-paste output. GitHub, GitLab, Notion, Obsidian, and most static-site generators render Mermaid natively.

### Code Generation

The dump gives an LLM the types and FK relationships in one place, which is what every code generator needs to produce something correct on the first try. A short prompt for SQLAlchemy 2.0:

> Generate SQLAlchemy 2.0 declarative models from this schema dump. Use `Mapped[]` annotations, match column types properly, and add `relationship()` calls based on the foreign keys.

Returns a clean models file with proper `Mapped[int]` and `Mapped[str | None]` annotations, foreign-key columns wired to the right targets, and `relationship()` declarations on both sides of each FK. The same dump produces working [Prisma](https://www.prisma.io/) schemas, [Drizzle ORM](https://orm.drizzle.team/) definitions, [Pydantic](https://docs.pydantic.dev/) v2 models, TypeScript interfaces, [GraphQL SDL](https://graphql.org/learn/schema/), [OpenAPI](https://www.openapis.org/) specs, and [Alembic](https://alembic.sqlalchemy.org/) or [Flyway](https://www.red-gate.com/products/flyway/) migration scaffolding from variations of the same prompt.

### Schema Analysis

Walking the JSON surfaces a handful of useful audits that would otherwise require ad-hoc SQL:

- **Orphan tables:** tables with no inbound or outbound foreign keys. Often dead tables, audit logs, or stranded imports worth flagging for review.
- **Hub tables:** tables with the most inbound FKs. The central entities (`users`, `orders`, `patients`) a new team member should learn first.
- **Missing PK audit:** tables whose `primary_key.columns` array is empty. Worth flagging in any operational database.
- **FK without supporting index:** foreign keys whose source columns are not the leading column of any index in the same table. Likely sources of slow joins.
- **Naming convention audits:** column suffix patterns (`_id`, `_at`, `_count`), casing consistency (snake vs camel), plural-vs-singular table names. All visible from the column-name strings alone.
- **Schema diff:** two dumps of the same database taken weeks apart, compared field-by-field. New tables, dropped columns, type changes, added or removed foreign keys all surface clearly.

A natural diff prompt:

> Here are two schema dumps of the same database taken a month apart. Summarize what changed: new tables, dropped columns, type changes, added or removed foreign keys.

### Documentation

The dump is enough to produce a usable data dictionary, one section per table, columns with types and FK references. It is also enough for the LLM to produce a high-level domain map that groups tables into clusters (auth, billing, content, audit, and so on) inferred from naming patterns and FK density. Both artifacts are the kind of thing that takes a senior engineer half a day to draft from scratch and an LLM about a minute given the dump as priming context.

## Under The Hood

For the technically curious, three of the more interesting implementation pieces.

{{< accordion mode="collapse" separated="true" >}}

{{< accordionItem title="The CTE chain, in detail" >}}

Every script is a single `WITH ... SELECT` query with no temp tables, no procedures, and no DDL of any kind. The CTE chain is the entire implementation. From the SQLite script, a representative end-to-end flow looks like this:

```sql
WITH
cols AS (
    -- per-table column list with name, position, type, nullability, has_default
    ...
),
pks AS (
    -- per-table primary key columns, ordered by position in composite PK
    ...
),
fks AS (
    -- per-table foreign keys: from_columns, to_table, to_columns, on_delete
    ...
),
idx AS (
    -- per-table indexes, EXCLUDING PK-backing and unique-backing indexes
    -- (origin = 'c' filter in pragma_index_list)
    ...
),
trigger_counts AS (
    -- count of triggers per table (existence-only, no bodies)
    ...
),
tables_json AS (
    SELECT json_group_array(
        json_object(
            'schema', 'main',
            'name',   m.name,
            'kind',   'table',
            'primary_key',   json(pks.primary_key),
            'foreign_keys',  json(fks.foreign_keys),
            'indexes',       json(idx.indexes),
            'trigger_count', COALESCE(tc.trigger_count, 0),
            'columns',       json(cols.columns)
        )
        ORDER BY m.name
    ) AS payload
    FROM sqlite_master m
    LEFT JOIN cols           ON cols.table_name = m.name
    LEFT JOIN pks            ON pks.table_name  = m.name
    LEFT JOIN fks            ON fks.table_name  = m.name
    LEFT JOIN idx            ON idx.table_name  = m.name
    LEFT JOIN trigger_counts tc ON tc.table_name = m.name
    WHERE m.type = 'table' AND m.name NOT LIKE 'sqlite_%'
)
SELECT json_object(
    'metadata',  json((SELECT payload FROM meta)),
    'tables',    json(COALESCE((SELECT payload FROM tables_json), '[]')),
    'views',     json(COALESCE((SELECT payload FROM views_json),  '[]')),
    'routines',  json('[]'),
    'sequences', json('[]'),
    'packages',  json('[]')
) AS schema_dump;
```

The chain is read-only: every CTE queries `sqlite_master` or a `PRAGMA` table-valued function, neither of which touches user data. The final `SELECT` assembles the JSON document and returns it as a single text cell. No temporary tables are created, no DDL fires, and the database is never modified. This makes the scripts safe to run against production databases with a read-only role.

The same shape appears in every other script in the repo, with engine-specific catalog queries substituted in. PostgreSQL reads from `pg_class`, `pg_attribute`, `pg_constraint`, and `pg_index`; SQL Server reads from `sys.tables`, `sys.columns`, `sys.indexes`; Oracle reads from `USER_TAB_COLS`, `USER_CONSTRAINTS`, `USER_INDEXES`. The CTE *names* are the same across all scripts, so a contributor who has read one can navigate any of them.

{{< /accordionItem >}}

{{< accordionItem title="Engine quirks the scripts paper over" >}}

Each engine has at least one quirk in its catalog views that, left unhandled, would either crash the dump or pollute it with noise. Three representative examples.

**PostgreSQL: extension-owned objects.** Any database with PostGIS, pgcrypto, or Supabase auth has dozens of extension-owned tables, views, and functions sitting in the catalog. Including them in the dump would bury the user's actual schema under plumbing. The PostgreSQL script filters them via `pg_depend`:

```sql
extension_owned AS (
    SELECT d.objid AS oid
    FROM pg_depend d
    WHERE d.deptype = 'e'
      AND d.classid = 'pg_class'::regclass
)
```

Every later CTE excludes any object whose OID appears in `extension_owned`, so the dump shows only the user's real tables. The same filter pattern handles `pg_proc` for extension-owned functions.

**SQL Server: index deduplication.** SQL Server's `sys.indexes` reports an entry for every index, including the ones that back primary keys and unique constraints. Emitting all of them would duplicate constraint information in the `indexes` section. The script filters via three columns:

```sql
WHERE i.is_primary_key       = 0
  AND i.is_unique_constraint = 0
  AND i.type > 0
  AND ic.is_included_column  = 0
```

`is_primary_key` and `is_unique_constraint` drop the constraint-backing indexes; `type > 0` drops the heap entry (which is not an index); `is_included_column` drops INCLUDE columns from the key column list, since those belong in a separate INCLUDE array in the output.

**Firebird: no `ORDER BY` inside aggregates.** Firebird's `LIST()` aggregate, equivalent to other engines' `STRING_AGG` and `GROUP_CONCAT`, does not support `ORDER BY` directly. A naive aggregation produces output rows in arbitrary order. The Firebird script works around this by wrapping each aggregation in a derived table with an outer `ORDER BY`:

```sql
(SELECT LIST(row_md, ASCII_CHAR(10))
 FROM (SELECT row_md FROM table_column_md_rows tcm
       WHERE tcm.relation_name = ut.relation_name
       ORDER BY pos))
```

The optimizer feeds the rows to `LIST()` in the derived table's order, which is reliable on the small sample databases this is tested against. On very large databases with parallel execution the ordering may vary, which is called out in the script header so consumers don't rely on it more than the engine actually guarantees.

{{< /accordionItem >}}

{{< accordionItem title="Firebird's Markdown fallback (and why no JSON)" >}}

Firebird 4.0 has no native JSON functions. `JSON_OBJECT`, `JSON_ARRAYAGG`, and `JSON_QUERY` are still in proposal stage and unlikely to land before Firebird 6.0. The straightforward path would be hand-rolled string concatenation: every key wrapped in quotes, every value escaped, every brace tracked by hand, every comma added or skipped depending on position. That path is technically doable but operationally fragile: a single bad escape produces a parse-time failure that breaks the entire dump, and the script would be twice as long as any of the other seven engines just on quote handling.

The Firebird script instead emits Markdown. Building a Markdown table with `LIST()` is structurally similar to building JSON, but skips every structural concern at once: no quote escaping, no brace matching, no comma logic. A row that has to render a column name containing a special character just needs to handle the Markdown pipe character; in JSON the same row would need to handle quotes, backslashes, newlines, and the rest of the JSON escape set.

The trade-off is that Firebird dumps are not programmatically parseable the way the JSON dumps are. A consumer pipeline that walks `tables[*].foreign_keys[*]` works on seven engines; Firebird needs separate handling. For the original use case (paste into an LLM), this doesn't matter; the LLM reads Markdown and JSON equally well. For downstream tooling, it's a real divergence, and the right answer is to wait for native JSON support in a future Firebird release rather than build a fragile string-concatenation version now.

The single-engine asymmetry is acknowledged in the script's header and in the project README. It is the one place where the eight scripts do not produce shape-identical output, and the choice was made deliberately rather than by oversight.

{{< /accordionItem >}}

{{< /accordion >}}

## Stack

- **Language:** SQL (pure; no installs, no extensions, no Python runtime required)
- **Engines and catalog sources:**
  - PostgreSQL 12+ → `pg_catalog` and `information_schema`
  - MySQL 8.0.16+ and MariaDB 10.5+ → `information_schema`
  - SQL Server 2022+ → `sys.*`
  - Oracle 18c+ → `USER_*` and `ALL_*`
  - SQLite 3.44+ → `sqlite_master` and pragma table-valued functions
  - BigQuery (GoogleSQL) → dataset-scoped `INFORMATION_SCHEMA.*`
  - Firebird 4.0+ → `RDB$RELATIONS`, `RDB$RELATION_FIELDS`, `RDB$FIELDS`
- **JSON aggregation primitives:** [`jsonb_agg`](https://www.postgresql.org/docs/current/functions-aggregate.html) (PostgreSQL), [`JSON_ARRAYAGG`](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/JSON_ARRAYAGG.html) (Oracle), [`JSON_OBJECT`](https://learn.microsoft.com/en-us/sql/t-sql/functions/json-object-transact-sql) (SQL Server, MySQL, MariaDB), [`json_group_array`](https://www.sqlite.org/json1.html#jgrouparray) (SQLite), [`TO_JSON_STRING`](https://cloud.google.com/bigquery/docs/reference/standard-sql/json_functions#to_json_string) over structs (BigQuery)
- **Output format:** JSON for seven engines; Markdown for Firebird (Firebird 4.0 has no native JSON aggregation)
- **Validation:** [Sakila](https://dev.mysql.com/doc/sakila/en/) for MySQL, [AdventureWorks](https://learn.microsoft.com/en-us/sql/samples/adventureworks-install-configure) for SQL Server, [HR](https://docs.oracle.com/en/database/oracle/oracle-database/19/comsc/installing-sample-schemas.html) for Oracle, [Bookings](https://postgrespro.com/community/demodb) for PostgreSQL, the [Employee](https://firebirdsql.org/manual/qsg2-installing.html) sample for Firebird, and a custom [Palmer Penguins](https://allisonhorst.github.io/palmerpenguins/) SQLite database, all on [sqlize.online](https://sqlize.online). Largest validated run: a 251-table Oracle schema producing a 263 KB dump in a single query.
- **License:** [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)

## Repo

[github.com/hihipy/sql-x-ray](https://github.com/hihipy/sql-x-ray)

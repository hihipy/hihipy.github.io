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

## A Worked Example: A Live Database in the Browser

Every example above uses a synthetic e-commerce schema. Here is the tool against a real one: `penobscot-nclex.sqlite`, the SQLite database behind the [Penobscot NCLEX case study](/archivo/penobscot-nclex/), running entirely in your browser through [Datasette Lite](https://lite.datasette.io/). No install, no server, and nothing leaves the page.

[Open it in Datasette Lite with the script pre-loaded](https://lite.datasette.io/?url=https://pgbd.casa/data/penobscot-nclex.sqlite#/penobscot-nclex?sql=--%20%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%0A--%20sql-x-ray%20for%20SQLite%203.16%2B%20%28compatibility%20build%29%0A--%20%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%0A--%20Same%20output%20as%20the%203.44%2B%20script%2C%20but%20avoids%20ORDER%20BY%20inside%0A--%20aggregate%20functions%20%28a%203.44%20feature%29.%20Ordering%20is%20established%20in%0A--%20inner%20subqueries%20and%20preserved%20by%20the%20outer%20aggregation%2C%20so%20this%0A--%20runs%20on%20older%20engines%20such%20as%20the%20SQLite%20build%20inside%20Datasette%0A--%20Lite%20%2F%20Pyodide.%0A--%20%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%0A%0AWITH%0A%0A--%20COLUMNS%20------------------------------------------------------------%0Acols_src%20AS%20%28%0A%20%20%20%20SELECT%0A%20%20%20%20%20%20%20%20m.name%20AS%20table_name%2C%0A%20%20%20%20%20%20%20%20p.cid%20%20AS%20sort_key%2C%0A%20%20%20%20%20%20%20%20json_object%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%27name%27%2C%20%20%20%20%20%20%20%20%20p.name%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%27position%27%2C%20%20%20%20%20p.cid%20%2B%201%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%27data_type%27%2C%20%20%20%20p.type%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%27nullable%27%2C%20%20%20%20%20CASE%20p.%22notnull%22%20WHEN%201%20THEN%20json%28%27false%27%29%20ELSE%20json%28%27true%27%29%20END%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%27has_default%27%2C%20%20CASE%20WHEN%20p.dflt_value%20IS%20NOT%20NULL%20THEN%20json%28%27true%27%29%20ELSE%20json%28%27false%27%29%20END%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%27is_pk%27%2C%20%20%20%20%20%20%20%20CASE%20WHEN%20p.pk%20%3E%200%20THEN%20json%28%27true%27%29%20ELSE%20json%28%27false%27%29%20END%0A%20%20%20%20%20%20%20%20%29%20AS%20obj%0A%20%20%20%20FROM%20sqlite_master%20m%2C%20pragma_table_info%28m.name%29%20p%0A%20%20%20%20WHERE%20m.type%20%3D%20%27table%27%0A%20%20%20%20%20%20AND%20m.name%20NOT%20LIKE%20%27sqlite_%25%27%0A%20%20%20%20ORDER%20BY%20m.name%2C%20p.cid%0A%29%2C%0Acols%20AS%20%28%0A%20%20%20%20SELECT%20table_name%2C%20json_group_array%28json%28obj%29%29%20AS%20columns%0A%20%20%20%20FROM%20cols_src%0A%20%20%20%20GROUP%20BY%20table_name%0A%29%2C%0A%0A--%20PRIMARY%20KEYS%20-------------------------------------------------------%0Apks_src%20AS%20%28%0A%20%20%20%20SELECT%20m.name%20AS%20table_name%2C%20p.pk%20AS%20sort_key%2C%20p.name%20AS%20col_name%0A%20%20%20%20FROM%20sqlite_master%20m%2C%20pragma_table_info%28m.name%29%20p%0A%20%20%20%20WHERE%20m.type%20%3D%20%27table%27%0A%20%20%20%20%20%20AND%20m.name%20NOT%20LIKE%20%27sqlite_%25%27%0A%20%20%20%20%20%20AND%20p.pk%20%3E%200%0A%20%20%20%20ORDER%20BY%20m.name%2C%20p.pk%0A%29%2C%0Apks%20AS%20%28%0A%20%20%20%20SELECT%20table_name%2C%0A%20%20%20%20%20%20%20%20%20%20%20json_object%28%27columns%27%2C%20json_group_array%28col_name%29%29%20AS%20primary_key%0A%20%20%20%20FROM%20pks_src%0A%20%20%20%20GROUP%20BY%20table_name%0A%29%2C%0A%0A--%20FOREIGN%20KEYS%20-------------------------------------------------------%0Afk_cols_src%20AS%20%28%0A%20%20%20%20SELECT%0A%20%20%20%20%20%20%20%20m.name%20AS%20table_name%2C%0A%20%20%20%20%20%20%20%20f.id%20%20%20AS%20fk_id%2C%0A%20%20%20%20%20%20%20%20f.%22table%22%20AS%20to_table%2C%0A%20%20%20%20%20%20%20%20f.on_delete%2C%0A%20%20%20%20%20%20%20%20f.seq%20%20AS%20sort_key%2C%0A%20%20%20%20%20%20%20%20f.%22from%22%20AS%20from_col%2C%0A%20%20%20%20%20%20%20%20f.%22to%22%20%20%20AS%20to_col%0A%20%20%20%20FROM%20sqlite_master%20m%2C%20pragma_foreign_key_list%28m.name%29%20f%0A%20%20%20%20WHERE%20m.type%20%3D%20%27table%27%0A%20%20%20%20%20%20AND%20m.name%20NOT%20LIKE%20%27sqlite_%25%27%0A%20%20%20%20ORDER%20BY%20m.name%2C%20f.id%2C%20f.seq%0A%29%2C%0Afk_grouped%20AS%20%28%0A%20%20%20%20SELECT%0A%20%20%20%20%20%20%20%20table_name%2C%20fk_id%2C%20to_table%2C%20on_delete%2C%0A%20%20%20%20%20%20%20%20json_group_array%28from_col%29%20AS%20from_columns%2C%0A%20%20%20%20%20%20%20%20json_group_array%28to_col%29%20%20%20AS%20to_columns%0A%20%20%20%20FROM%20fk_cols_src%0A%20%20%20%20GROUP%20BY%20table_name%2C%20fk_id%2C%20to_table%2C%20on_delete%0A%29%2C%0Afk_obj_src%20AS%20%28%0A%20%20%20%20SELECT%0A%20%20%20%20%20%20%20%20table_name%2C%0A%20%20%20%20%20%20%20%20fk_id%20AS%20sort_key%2C%0A%20%20%20%20%20%20%20%20json_object%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%27from_columns%27%2C%20json%28from_columns%29%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%27to_table%27%2C%20%20%20%20%20to_table%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%27to_columns%27%2C%20%20%20json%28to_columns%29%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%27on_delete%27%2C%20%20%20%20on_delete%0A%20%20%20%20%20%20%20%20%29%20AS%20obj%0A%20%20%20%20FROM%20fk_grouped%0A%20%20%20%20ORDER%20BY%20table_name%2C%20fk_id%0A%29%2C%0Afks%20AS%20%28%0A%20%20%20%20SELECT%20table_name%2C%20json_group_array%28json%28obj%29%29%20AS%20foreign_keys%0A%20%20%20%20FROM%20fk_obj_src%0A%20%20%20%20GROUP%20BY%20table_name%0A%29%2C%0A%0A--%20INDEXES%20%28origin%20%27c%27%20only%29%20------------------------------------------%0Aidx_col_src%20AS%20%28%0A%20%20%20%20SELECT%0A%20%20%20%20%20%20%20%20m.name%20%20AS%20table_name%2C%0A%20%20%20%20%20%20%20%20il.name%20AS%20index_name%2C%0A%20%20%20%20%20%20%20%20il.%22unique%22%20AS%20is_unique%2C%0A%20%20%20%20%20%20%20%20ii.seqno%20AS%20sort_key%2C%0A%20%20%20%20%20%20%20%20ii.name%20%20AS%20col_name%0A%20%20%20%20FROM%20sqlite_master%20m%2C%0A%20%20%20%20%20%20%20%20%20pragma_index_list%28m.name%29%20il%2C%0A%20%20%20%20%20%20%20%20%20pragma_index_info%28il.name%29%20ii%0A%20%20%20%20WHERE%20m.type%20%3D%20%27table%27%0A%20%20%20%20%20%20AND%20m.name%20NOT%20LIKE%20%27sqlite_%25%27%0A%20%20%20%20%20%20AND%20il.origin%20%3D%20%27c%27%0A%20%20%20%20ORDER%20BY%20m.name%2C%20il.name%2C%20ii.seqno%0A%29%2C%0Aidx_cols%20AS%20%28%0A%20%20%20%20SELECT%20table_name%2C%20index_name%2C%20is_unique%2C%0A%20%20%20%20%20%20%20%20%20%20%20json_group_array%28col_name%29%20AS%20columns%0A%20%20%20%20FROM%20idx_col_src%0A%20%20%20%20GROUP%20BY%20table_name%2C%20index_name%2C%20is_unique%0A%29%2C%0Aidx_obj_src%20AS%20%28%0A%20%20%20%20SELECT%0A%20%20%20%20%20%20%20%20table_name%2C%0A%20%20%20%20%20%20%20%20index_name%20AS%20sort_key%2C%0A%20%20%20%20%20%20%20%20json_object%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%27name%27%2C%20%20%20%20index_name%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%27method%27%2C%20%20%27btree%27%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%27unique%27%2C%20%20CASE%20is_unique%20WHEN%201%20THEN%20json%28%27true%27%29%20ELSE%20json%28%27false%27%29%20END%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%27columns%27%2C%20json%28columns%29%0A%20%20%20%20%20%20%20%20%29%20AS%20obj%0A%20%20%20%20FROM%20idx_cols%0A%20%20%20%20ORDER%20BY%20table_name%2C%20index_name%0A%29%2C%0Aidx%20AS%20%28%0A%20%20%20%20SELECT%20table_name%2C%20json_group_array%28json%28obj%29%29%20AS%20indexes%0A%20%20%20%20FROM%20idx_obj_src%0A%20%20%20%20GROUP%20BY%20table_name%0A%29%2C%0A%0A--%20TRIGGER%20COUNTS%20-----------------------------------------------------%0Atrigger_counts%20AS%20%28%0A%20%20%20%20SELECT%20tbl_name%20AS%20table_name%2C%20COUNT%28%2A%29%20AS%20trigger_count%0A%20%20%20%20FROM%20sqlite_master%0A%20%20%20%20WHERE%20type%20%3D%20%27trigger%27%0A%20%20%20%20GROUP%20BY%20tbl_name%0A%29%2C%0A%0A--%20TABLES%20-------------------------------------------------------------%0Atables_src%20AS%20%28%0A%20%20%20%20SELECT%0A%20%20%20%20%20%20%20%20json_object%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%27schema%27%2C%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%27main%27%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%27name%27%2C%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20m.name%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%27kind%27%2C%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%27table%27%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%27is_partitioned%27%2C%20%20%20%20%20%20%20%20%20json%28%27false%27%29%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%27primary_key%27%2C%20%20%20%20%20%20%20%20%20%20%20%20json%28pks.primary_key%29%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%27foreign_keys%27%2C%20%20%20%20%20%20%20%20%20%20%20json%28fks.foreign_keys%29%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%27unique_constraints%27%2C%20%20%20%20%20json%28%27%5B%5D%27%29%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%27check_constraint_count%27%2C%200%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%27indexes%27%2C%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20json%28idx.indexes%29%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%27trigger_count%27%2C%20%20%20%20%20%20%20%20%20%20COALESCE%28tc.trigger_count%2C%200%29%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%27columns%27%2C%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20json%28cols.columns%29%0A%20%20%20%20%20%20%20%20%29%20AS%20obj%0A%20%20%20%20FROM%20sqlite_master%20m%0A%20%20%20%20LEFT%20JOIN%20cols%20%20%20%20%20%20%20%20%20%20%20ON%20cols.table_name%20%3D%20m.name%0A%20%20%20%20LEFT%20JOIN%20pks%20%20%20%20%20%20%20%20%20%20%20%20ON%20pks.table_name%20%20%3D%20m.name%0A%20%20%20%20LEFT%20JOIN%20fks%20%20%20%20%20%20%20%20%20%20%20%20ON%20fks.table_name%20%20%3D%20m.name%0A%20%20%20%20LEFT%20JOIN%20idx%20%20%20%20%20%20%20%20%20%20%20%20ON%20idx.table_name%20%20%3D%20m.name%0A%20%20%20%20LEFT%20JOIN%20trigger_counts%20tc%20ON%20tc.table_name%20%3D%20m.name%0A%20%20%20%20WHERE%20m.type%20%3D%20%27table%27%0A%20%20%20%20%20%20AND%20m.name%20NOT%20LIKE%20%27sqlite_%25%27%0A%20%20%20%20ORDER%20BY%20m.name%0A%29%2C%0Atables_json%20AS%20%28%0A%20%20%20%20SELECT%20json_group_array%28json%28obj%29%29%20AS%20payload%20FROM%20tables_src%0A%29%2C%0A%0A--%20VIEWS%20--------------------------------------------------------------%0Aview_col_src%20AS%20%28%0A%20%20%20%20SELECT%0A%20%20%20%20%20%20%20%20m.name%20AS%20view_name%2C%0A%20%20%20%20%20%20%20%20p.cid%20%20AS%20sort_key%2C%0A%20%20%20%20%20%20%20%20json_object%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%27name%27%2C%20%20%20%20%20%20p.name%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%27position%27%2C%20%20p.cid%20%2B%201%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%27data_type%27%2C%20p.type%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%27nullable%27%2C%20%20CASE%20p.%22notnull%22%20WHEN%201%20THEN%20json%28%27false%27%29%20ELSE%20json%28%27true%27%29%20END%0A%20%20%20%20%20%20%20%20%29%20AS%20obj%0A%20%20%20%20FROM%20sqlite_master%20m%2C%20pragma_table_info%28m.name%29%20p%0A%20%20%20%20WHERE%20m.type%20%3D%20%27view%27%0A%20%20%20%20%20%20AND%20m.name%20NOT%20LIKE%20%27sqlite_%25%27%0A%20%20%20%20ORDER%20BY%20m.name%2C%20p.cid%0A%29%2C%0Aview_cols%20AS%20%28%0A%20%20%20%20SELECT%20view_name%2C%20json_group_array%28json%28obj%29%29%20AS%20columns%0A%20%20%20%20FROM%20view_col_src%0A%20%20%20%20GROUP%20BY%20view_name%0A%29%2C%0Aviews_src%20AS%20%28%0A%20%20%20%20SELECT%0A%20%20%20%20%20%20%20%20json_object%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%27schema%27%2C%20%20%27main%27%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%27name%27%2C%20%20%20%20m.name%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%27kind%27%2C%20%20%20%20%27view%27%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%27columns%27%2C%20json%28COALESCE%28vc.columns%2C%20%27%5B%5D%27%29%29%0A%20%20%20%20%20%20%20%20%29%20AS%20obj%0A%20%20%20%20FROM%20sqlite_master%20m%0A%20%20%20%20LEFT%20JOIN%20view_cols%20vc%20ON%20vc.view_name%20%3D%20m.name%0A%20%20%20%20WHERE%20m.type%20%3D%20%27view%27%0A%20%20%20%20%20%20AND%20m.name%20NOT%20LIKE%20%27sqlite_%25%27%0A%20%20%20%20ORDER%20BY%20m.name%0A%29%2C%0Aviews_json%20AS%20%28%0A%20%20%20%20SELECT%20json_group_array%28json%28obj%29%29%20AS%20payload%20FROM%20views_src%0A%29%2C%0A%0A--%20METADATA%20-----------------------------------------------------------%0Ameta%20AS%20%28%0A%20%20%20%20SELECT%20json_object%28%0A%20%20%20%20%20%20%20%20%27tool_name%27%2C%20%20%20%20%20%20%27sql-x-ray%27%2C%0A%20%20%20%20%20%20%20%20%27engine%27%2C%20%20%20%20%20%20%20%20%20%27sqlite%27%2C%0A%20%20%20%20%20%20%20%20%27engine_version%27%2C%20sqlite_version%28%29%2C%0A%20%20%20%20%20%20%20%20%27database%27%2C%20%20%20%20%20%20%20%27main%27%2C%0A%20%20%20%20%20%20%20%20%27generated_at%27%2C%20%20%20strftime%28%27%25Y-%25m-%25dT%25H%3A%25M%3A%25SZ%27%2C%20%27now%27%29%2C%0A%20%20%20%20%20%20%20%20%27schema_filter%27%2C%20%20%27main%27%2C%0A%20%20%20%20%20%20%20%20%27schemas%27%2C%20%20%20%20%20%20%20%20json_array%28%27main%27%29%2C%0A%20%20%20%20%20%20%20%20%27object_counts%27%2C%20%20json_object%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%27tables%27%2C%20%28SELECT%20COUNT%28%2A%29%20FROM%20sqlite_master%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20WHERE%20type%20%3D%20%27table%27%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20AND%20name%20NOT%20LIKE%20%27sqlite_%25%27%29%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%27views%27%2C%20%20%28SELECT%20COUNT%28%2A%29%20FROM%20sqlite_master%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20WHERE%20type%20%3D%20%27view%27%29%0A%20%20%20%20%20%20%20%20%29%2C%0A%20%20%20%20%20%20%20%20%27privacy_note%27%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%27This%20document%20contains%20only%20structural%20metadata.%20%27%20%7C%7C%0A%20%20%20%20%20%20%20%20%20%20%20%20%27It%20deliberately%20excludes%20default%20value%20literals%2C%20%27%20%7C%7C%0A%20%20%20%20%20%20%20%20%20%20%20%20%27check%20constraint%20expressions%20%28SQLite%20stores%20these%20%27%20%7C%7C%0A%20%20%20%20%20%20%20%20%20%20%20%20%27inside%20CREATE%20TABLE%20SQL%20which%20we%20do%20not%20parse%29%2C%20%27%20%7C%7C%0A%20%20%20%20%20%20%20%20%20%20%20%20%27view%20and%20trigger%20bodies%2C%20and%20all%20row%20data.%20Existence%20%27%20%7C%7C%0A%20%20%20%20%20%20%20%20%20%20%20%20%27is%20recorded%20via%20counts%20%28e.g.%20trigger_count%29%3B%20%27%20%7C%7C%0A%20%20%20%20%20%20%20%20%20%20%20%20%27contents%20are%20not.%27%0A%20%20%20%20%29%20AS%20payload%0A%29%0A%0A--%20FINAL%20ASSEMBLY%20-----------------------------------------------------%0ASELECT%20json_object%28%0A%20%20%20%20%27metadata%27%2C%20%20json%28%28SELECT%20payload%20FROM%20meta%29%29%2C%0A%20%20%20%20%27tables%27%2C%20%20%20%20json%28COALESCE%28%28SELECT%20payload%20FROM%20tables_json%29%2C%20%27%5B%5D%27%29%29%2C%0A%20%20%20%20%27views%27%2C%20%20%20%20%20json%28COALESCE%28%28SELECT%20payload%20FROM%20views_json%29%2C%20%20%27%5B%5D%27%29%29%2C%0A%20%20%20%20%27routines%27%2C%20%20json%28%27%5B%5D%27%29%2C%0A%20%20%20%20%27sequences%27%2C%20json%28%27%5B%5D%27%29%2C%0A%20%20%20%20%27packages%27%2C%20%20json%28%27%5B%5D%27%29%2C%0A%20%20%20%20%27types%27%2C%20%20%20%20%20json%28%27%5B%5D%27%29%0A%29%20AS%20schema_dump%3B%0A). The SQL editor opens already filled in, so just press **Run SQL** and one JSON cell comes back. (The full script is also in the accordion at the end of this section if you would rather paste it by hand.)

### Why This Is a Good Fit

`penobscot-nclex` is a hypothetical nursing school and the data is synthetic, but it is shaped to mirror the kind of internal record a real program actually keeps: one row per student per NCLEX licensure attempt, carrying region, campus, program, cohort timing, attempt number, and a pass-or-fail result. Were it live data it would sit squarely under FERPA, and several of those columns are quasi-identifiers, since region plus campus plus program plus cohort can narrow to a single person well before any name is involved.

That is the textbook case for a structure-only dump. You might reasonably want an LLM to help write a cohort pass-rate query, draft an ER diagram, or scaffold ORM models against this schema, but you cannot paste student records into a consumer chat, and you should not paste the full `CREATE TABLE` text either, because defaults and check constraint expressions can carry sensitive strings of their own. sql-x-ray threads that needle: the model receives the table names, columns, types, keys, and indexes it needs to be useful, while a data governance reviewer has nothing to flag, because no row, no value, and no constraint expression ever leaves the database. Everything below is that trade running on a realistic stand-in for protected institutional data.

### The SQLite 3.44 Wrinkle

Datasette Lite runs SQLite compiled to WebAssembly through [Pyodide](https://pyodide.org/), and that build currently reports `3.39.0`. The canonical script targets 3.44+ because it sorts inside the aggregate, putting `ORDER BY` directly in `json_group_array`, which is a feature added in [SQLite 3.44](https://www.sqlite.org/releaselog/3_44_0.html). On 3.39 the parser stops at the first one with `near "ORDER": syntax error`.

The fix is the same move the Firebird script makes for the same reason (see *Engine quirks the scripts paper over* below): relocate every `ORDER BY` out of the aggregate and into a subquery that pre-sorts the rows, so the outer aggregation consumes them already in order. Set against the `cols` CTE shown earlier:

```sql
cols_src AS (
    SELECT
        m.name AS table_name,
        p.cid  AS sort_key,
        json_object( 'name', p.name, 'position', p.cid + 1, 'data_type', p.type, ... ) AS obj
    FROM sqlite_master m, pragma_table_info(m.name) p
    WHERE m.type = 'table' AND m.name NOT LIKE 'sqlite_%'
    ORDER BY m.name, p.cid          -- ordering lives here now, not in the aggregate
),
cols AS (
    SELECT table_name, json_group_array(json(obj)) AS columns
    FROM cols_src
    GROUP BY table_name             -- plain aggregate, no ORDER BY argument
)
```

The output is byte-identical to the 3.44+ script; only the sorting mechanism changes. This compatibility build runs unchanged on any SQLite from 3.16 upward.

### The Output

Trimmed to the metadata header and one table:

```json
{
  "metadata": {
    "tool_name":      "sql-x-ray",
    "engine":         "sqlite",
    "engine_version": "3.39.0",
    "database":       "main",
    "schemas":        ["main"],
    "object_counts":  { "tables": 3, "views": 0 }
  },
  "tables": [
    {
      "schema": "main",
      "name":   "attempts",
      "kind":   "table",
      "primary_key":  null,
      "foreign_keys": null,
      "check_constraint_count": 0,
      "indexes": [
        { "name": "ix_attempts_campus",         "method": "btree", "unique": false, "columns": ["campus"] },
        { "name": "ix_attempts_student_attempt","method": "btree", "unique": true,  "columns": ["student_id", "attempt_number"] },
        { "name": "ix_attempts_testing_cohort", "method": "btree", "unique": false, "columns": ["testing_cohort"] }
      ],
      "trigger_count": 0,
      "columns": [
        { "name": "student_id",        "position": 1, "data_type": "TEXT",    "nullable": false, "has_default": false, "is_pk": false },
        { "name": "region",            "position": 2, "data_type": "TEXT",    "nullable": false, "has_default": false, "is_pk": false },
        { "name": "campus",            "position": 3, "data_type": "TEXT",    "nullable": false, "has_default": false, "is_pk": false },
        { "name": "program",           "position": 4, "data_type": "TEXT",    "nullable": false, "has_default": false, "is_pk": false },
        { "name": "starting_cohort",   "position": 5, "data_type": "TEXT",    "nullable": true,  "has_default": false, "is_pk": false },
        { "name": "graduating_cohort", "position": 6, "data_type": "TEXT",    "nullable": true,  "has_default": false, "is_pk": false },
        { "name": "testing_cohort",    "position": 7, "data_type": "TEXT",    "nullable": false, "has_default": false, "is_pk": false },
        { "name": "attempt_number",    "position": 8, "data_type": "INTEGER", "nullable": false, "has_default": false, "is_pk": false },
        { "name": "result",            "position": 9, "data_type": "INTEGER", "nullable": false, "has_default": false, "is_pk": false }
      ]
    }
  ]
}
```

Every column name is exposed (`student_id`, `region`, `campus`, `program`); not one student record is. That is the structure-only guarantee made concrete on data shaped like the protected real thing.

### What the Nulls Tell You

`foreign_keys` is `null` on all three tables. This database declares no foreign keys, so sql-x-ray, which reports only what the catalog declares and infers nothing, draws an edgeless diagram: three tables, no connections.

{{< mermaid >}}
erDiagram
    attempts {
        TEXT student_id
        TEXT region
        TEXT campus
        TEXT program
        TEXT starting_cohort
        TEXT graduating_cohort
        TEXT testing_cohort
        INTEGER attempt_number
        INTEGER result
    }
    students {
        TEXT student_id PK
        TEXT region
        TEXT campus
        TEXT program
        INTEGER total_attempts
        INTEGER eventually_passed
        INTEGER first_visible_attempt
        TEXT first_testing_cohort
        TEXT last_testing_cohort
        INTEGER terms_grad_to_first_test
        TEXT graduating_cohort
        TEXT starting_cohort
    }
    term_order {
        TEXT cohort PK
        INTEGER year
        TEXT term
        INTEGER term_idx
        INTEGER ordinal
    }
{{< /mermaid >}}

The relationships are nonetheless real. `attempts.student_id` matches `students.student_id`, and the `*_cohort` columns match `term_order.cohort`. They live in the pipeline that built the tables, not in the schema. Drawn from column names and join logic rather than read from the catalog, the **implied** schema is this:

{{< mermaid >}}
erDiagram
    students ||--o{ attempts : student_id
    term_order ||--o{ attempts : "cohort lookups"
    term_order ||--o{ students : "cohort lookups"
    attempts {
        TEXT student_id FK
        TEXT region
        TEXT campus
        TEXT program
        TEXT starting_cohort FK
        TEXT graduating_cohort FK
        TEXT testing_cohort FK
        INTEGER attempt_number
        INTEGER result
    }
    students {
        TEXT student_id PK
        TEXT region
        TEXT campus
        TEXT program
        INTEGER total_attempts
        INTEGER eventually_passed
        INTEGER first_visible_attempt
        TEXT first_testing_cohort FK
        TEXT last_testing_cohort FK
        INTEGER terms_grad_to_first_test
        TEXT graduating_cohort FK
        TEXT starting_cohort FK
    }
    term_order {
        TEXT cohort PK
        INTEGER year
        TEXT term
        INTEGER term_idx
        INTEGER ordinal
    }
{{< /mermaid >}}

This second diagram is an inference, not a reading. The `FK` markers and the edges are what a careful analyst (or an LLM handed the dump) would reconstruct from the naming, and they are labeled as implied for exactly that reason. The database is deliberately left unchanged. SQLite cannot add a foreign key without rebuilding each table, and for a derived, read-only analytical dataset whose referential integrity is already guaranteed by the build pipeline, that rebuild would be a manual mutation drifting away from the pipeline for no query-time benefit. Documenting the implied schema here is the honest middle path: it shows the relationships without pretending the engine enforces them.

The gap between the two diagrams is the entire argument for declared constraints. A database can be perfectly relational in practice while telling an introspection tool, a new analyst, or an LLM nothing about how its tables connect. sql-x-ray draws only the first diagram, because the first diagram is the only one that is true of the schema as written.

{{< accordion mode="collapse" separated="true" >}}

{{< accordionItem title="Full compatibility script (SQLite 3.16+)" >}}

The complete browser-ready build. Paste it into the Datasette Lite SQL box linked above.

```sql
-- =====================================================================
-- sql-x-ray for SQLite 3.16+ (compatibility build)
-- =====================================================================
-- Same output as the 3.44+ script, but avoids ORDER BY inside
-- aggregate functions (a 3.44 feature). Ordering is established in
-- inner subqueries and preserved by the outer aggregation, so this
-- runs on older engines such as the SQLite build inside Datasette
-- Lite / Pyodide.
-- =====================================================================

WITH

-- COLUMNS ------------------------------------------------------------
cols_src AS (
    SELECT
        m.name AS table_name,
        p.cid  AS sort_key,
        json_object(
            'name',         p.name,
            'position',     p.cid + 1,
            'data_type',    p.type,
            'nullable',     CASE p."notnull" WHEN 1 THEN json('false') ELSE json('true') END,
            'has_default',  CASE WHEN p.dflt_value IS NOT NULL THEN json('true') ELSE json('false') END,
            'is_pk',        CASE WHEN p.pk > 0 THEN json('true') ELSE json('false') END
        ) AS obj
    FROM sqlite_master m, pragma_table_info(m.name) p
    WHERE m.type = 'table'
      AND m.name NOT LIKE 'sqlite_%'
    ORDER BY m.name, p.cid
),
cols AS (
    SELECT table_name, json_group_array(json(obj)) AS columns
    FROM cols_src
    GROUP BY table_name
),

-- PRIMARY KEYS -------------------------------------------------------
pks_src AS (
    SELECT m.name AS table_name, p.pk AS sort_key, p.name AS col_name
    FROM sqlite_master m, pragma_table_info(m.name) p
    WHERE m.type = 'table'
      AND m.name NOT LIKE 'sqlite_%'
      AND p.pk > 0
    ORDER BY m.name, p.pk
),
pks AS (
    SELECT table_name,
           json_object('columns', json_group_array(col_name)) AS primary_key
    FROM pks_src
    GROUP BY table_name
),

-- FOREIGN KEYS -------------------------------------------------------
fk_cols_src AS (
    SELECT
        m.name AS table_name,
        f.id   AS fk_id,
        f."table" AS to_table,
        f.on_delete,
        f.seq  AS sort_key,
        f."from" AS from_col,
        f."to"   AS to_col
    FROM sqlite_master m, pragma_foreign_key_list(m.name) f
    WHERE m.type = 'table'
      AND m.name NOT LIKE 'sqlite_%'
    ORDER BY m.name, f.id, f.seq
),
fk_grouped AS (
    SELECT
        table_name, fk_id, to_table, on_delete,
        json_group_array(from_col) AS from_columns,
        json_group_array(to_col)   AS to_columns
    FROM fk_cols_src
    GROUP BY table_name, fk_id, to_table, on_delete
),
fk_obj_src AS (
    SELECT
        table_name,
        fk_id AS sort_key,
        json_object(
            'from_columns', json(from_columns),
            'to_table',     to_table,
            'to_columns',   json(to_columns),
            'on_delete',    on_delete
        ) AS obj
    FROM fk_grouped
    ORDER BY table_name, fk_id
),
fks AS (
    SELECT table_name, json_group_array(json(obj)) AS foreign_keys
    FROM fk_obj_src
    GROUP BY table_name
),

-- INDEXES (origin 'c' only) ------------------------------------------
idx_col_src AS (
    SELECT
        m.name  AS table_name,
        il.name AS index_name,
        il."unique" AS is_unique,
        ii.seqno AS sort_key,
        ii.name  AS col_name
    FROM sqlite_master m,
         pragma_index_list(m.name) il,
         pragma_index_info(il.name) ii
    WHERE m.type = 'table'
      AND m.name NOT LIKE 'sqlite_%'
      AND il.origin = 'c'
    ORDER BY m.name, il.name, ii.seqno
),
idx_cols AS (
    SELECT table_name, index_name, is_unique,
           json_group_array(col_name) AS columns
    FROM idx_col_src
    GROUP BY table_name, index_name, is_unique
),
idx_obj_src AS (
    SELECT
        table_name,
        index_name AS sort_key,
        json_object(
            'name',    index_name,
            'method',  'btree',
            'unique',  CASE is_unique WHEN 1 THEN json('true') ELSE json('false') END,
            'columns', json(columns)
        ) AS obj
    FROM idx_cols
    ORDER BY table_name, index_name
),
idx AS (
    SELECT table_name, json_group_array(json(obj)) AS indexes
    FROM idx_obj_src
    GROUP BY table_name
),

-- TRIGGER COUNTS -----------------------------------------------------
trigger_counts AS (
    SELECT tbl_name AS table_name, COUNT(*) AS trigger_count
    FROM sqlite_master
    WHERE type = 'trigger'
    GROUP BY tbl_name
),

-- TABLES -------------------------------------------------------------
tables_src AS (
    SELECT
        json_object(
            'schema',                 'main',
            'name',                   m.name,
            'kind',                   'table',
            'is_partitioned',         json('false'),
            'primary_key',            json(pks.primary_key),
            'foreign_keys',           json(fks.foreign_keys),
            'unique_constraints',     json('[]'),
            'check_constraint_count', 0,
            'indexes',                json(idx.indexes),
            'trigger_count',          COALESCE(tc.trigger_count, 0),
            'columns',                json(cols.columns)
        ) AS obj
    FROM sqlite_master m
    LEFT JOIN cols           ON cols.table_name = m.name
    LEFT JOIN pks            ON pks.table_name  = m.name
    LEFT JOIN fks            ON fks.table_name  = m.name
    LEFT JOIN idx            ON idx.table_name  = m.name
    LEFT JOIN trigger_counts tc ON tc.table_name = m.name
    WHERE m.type = 'table'
      AND m.name NOT LIKE 'sqlite_%'
    ORDER BY m.name
),
tables_json AS (
    SELECT json_group_array(json(obj)) AS payload FROM tables_src
),

-- VIEWS --------------------------------------------------------------
view_col_src AS (
    SELECT
        m.name AS view_name,
        p.cid  AS sort_key,
        json_object(
            'name',      p.name,
            'position',  p.cid + 1,
            'data_type', p.type,
            'nullable',  CASE p."notnull" WHEN 1 THEN json('false') ELSE json('true') END
        ) AS obj
    FROM sqlite_master m, pragma_table_info(m.name) p
    WHERE m.type = 'view'
      AND m.name NOT LIKE 'sqlite_%'
    ORDER BY m.name, p.cid
),
view_cols AS (
    SELECT view_name, json_group_array(json(obj)) AS columns
    FROM view_col_src
    GROUP BY view_name
),
views_src AS (
    SELECT
        json_object(
            'schema',  'main',
            'name',    m.name,
            'kind',    'view',
            'columns', json(COALESCE(vc.columns, '[]'))
        ) AS obj
    FROM sqlite_master m
    LEFT JOIN view_cols vc ON vc.view_name = m.name
    WHERE m.type = 'view'
      AND m.name NOT LIKE 'sqlite_%'
    ORDER BY m.name
),
views_json AS (
    SELECT json_group_array(json(obj)) AS payload FROM views_src
),

-- METADATA -----------------------------------------------------------
meta AS (
    SELECT json_object(
        'tool_name',      'sql-x-ray',
        'engine',         'sqlite',
        'engine_version', sqlite_version(),
        'database',       'main',
        'generated_at',   strftime('%Y-%m-%dT%H:%M:%SZ', 'now'),
        'schema_filter',  'main',
        'schemas',        json_array('main'),
        'object_counts',  json_object(
            'tables', (SELECT COUNT(*) FROM sqlite_master
                       WHERE type = 'table'
                         AND name NOT LIKE 'sqlite_%'),
            'views',  (SELECT COUNT(*) FROM sqlite_master
                       WHERE type = 'view')
        ),
        'privacy_note',
            'This document contains only structural metadata. ' ||
            'It deliberately excludes default value literals, ' ||
            'check constraint expressions (SQLite stores these ' ||
            'inside CREATE TABLE SQL which we do not parse), ' ||
            'view and trigger bodies, and all row data. Existence ' ||
            'is recorded via counts (e.g. trigger_count); ' ||
            'contents are not.'
    ) AS payload
)

-- FINAL ASSEMBLY -----------------------------------------------------
SELECT json_object(
    'metadata',  json((SELECT payload FROM meta)),
    'tables',    json(COALESCE((SELECT payload FROM tables_json), '[]')),
    'views',     json(COALESCE((SELECT payload FROM views_json),  '[]')),
    'routines',  json('[]'),
    'sequences', json('[]'),
    'packages',  json('[]'),
    'types',     json('[]')
) AS schema_dump;
```

{{< /accordionItem >}}

{{< /accordion >}}

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

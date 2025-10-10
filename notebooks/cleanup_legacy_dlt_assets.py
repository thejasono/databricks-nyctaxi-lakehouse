# Databricks notebook source
"""Utility notebook to reset the NYCTaxi Delta Live Tables pipeline artifacts.

The cleanup uses Databricks REST APIs so the Unity Catalog objects are removed
even if no cluster is available.  When this notebook runs inside Databricks it
automatically reuses the workspace host and API token from the active context;
when executed elsewhere you can still provide ``DATABRICKS_HOST`` and
``DATABRICKS_TOKEN`` environment variables.
"""

# COMMAND ----------
from __future__ import annotations

import os
import sys
from functools import lru_cache
from typing import Iterable

import requests
from requests.exceptions import HTTPError
from urllib.parse import quote


CATALOG = "mainyc_taxic"
DBFS_PATH = "dbfs:/pipelines/nyctaxi"


@lru_cache(maxsize=1)
def _resolve_workspace_config() -> tuple[str, str]:
    """Return the Databricks host and token for REST calls."""

    host = os.getenv("DATABRICKS_HOST")
    token = os.getenv("DATABRICKS_TOKEN")
    if host and token:
        return host, token

    dbutils = globals().get("dbutils")
    if dbutils is not None:
        try:  # pragma: no cover - requires notebook context
            entry_point = dbutils.notebook.entry_point.getDbutils()
            context = entry_point.notebook().getContext()
            host = context.apiUrl().get()
            token = context.apiToken().get()
            if host and token:
                return host, token
        except Exception:  # noqa: BLE001 - surface error below if no credentials
            pass

    print(
        "Unable to determine workspace credentials. Set DATABRICKS_HOST and "
        "DATABRICKS_TOKEN environment variables or run inside Databricks.",
        file=sys.stderr,
    )
    sys.exit(1)


def _workspace_request(method: str, path: str, **kwargs):
    """Call a Databricks REST API endpoint and return the JSON response."""

    host, token = _resolve_workspace_config()

    url = host.rstrip("/") + path
    headers = kwargs.pop("headers", {})
    headers.setdefault("Authorization", f"Bearer {token}")
    headers.setdefault("Content-Type", "application/json")

    response = requests.request(method, url, headers=headers, timeout=30, **kwargs)
    try:
        response.raise_for_status()
    except HTTPError as exc:  # pragma: no cover - requires API access
        # Swallow 404 errors to make cleanup idempotent.
        if response.status_code == 404:
            return None
        raise exc
    if response.content:
        return response.json()
    return None


def _list_tables(schema: str) -> list[dict]:
    result = _workspace_request(
        "GET",
        "/api/2.1/unity-catalog/tables",
        params={"catalog_name": CATALOG, "schema_name": schema},
    )
    if not result:
        return []
    return result.get("tables", [])


def _print_existing_objects() -> None:
    for schema in ["raw", "ref", "mart"]:
        objects = _list_tables(schema)
        if objects:
            print(f"Existing objects in {CATALOG}.{schema}:")
            for obj in objects:
                full_name = obj.get("full_name", "<unknown>")
                obj_type = obj.get("table_type", "TABLE")
                print(f"  - {full_name} ({obj_type})")
        else:
            print(f"No objects found in {CATALOG}.{schema}.")


def _drop_table(table: dict) -> None:
    full_name = table.get("full_name")
    if not full_name:
        return

    table_type = table.get("table_type", "TABLE")
    encoded_name = quote(full_name, safe="")

    if table_type == "VIEW":
        _workspace_request("DELETE", f"/api/2.1/unity-catalog/views/{encoded_name}")
        print(f"Dropped view {full_name} (if it existed).")
    elif table_type == "MATERIALIZED_VIEW":
        _workspace_request("DELETE", f"/api/2.1/unity-catalog/materialized-views/{encoded_name}")
        print(f"Dropped materialized view {full_name} (if it existed).")
    else:
        _workspace_request("DELETE", f"/api/2.1/unity-catalog/tables/{encoded_name}")
        print(f"Dropped table {full_name} (if it existed).")


def _drop_tables(tables: Iterable[dict]) -> None:
    for table in tables:
        _drop_table(table)


def _delete_dbfs_path(path: str) -> None:
    status = _workspace_request("GET", "/api/2.0/dbfs/get-status", params={"path": path})
    if status is None:
        print(f"DBFS path {path} not found; skipping metadata cleanup.")
        return
    _workspace_request("POST", "/api/2.0/dbfs/delete", json={"path": path, "recursive": True})
    print(f"Removed DBFS path {path}.")


def main() -> None:
    print(f"Cleaning catalog '{CATALOG}' using REST APIs...")
    print("Current state before cleanup:")
    _print_existing_objects()
    for schema in ["raw", "ref", "mart"]:
        tables = _list_tables(schema)
        if tables:
            _drop_tables(tables)
        else:
            print(f"No tables found in {CATALOG}.{schema}; nothing to drop.")
    print("State after cleanup:")
    _print_existing_objects()
    _delete_dbfs_path(DBFS_PATH)
    print("Cleanup complete.")


if __name__ == "__main__":
    main()

# COMMAND ----------
# MAGIC -- The pipeline is now ready to be recreated with Unity Catalog enabled.
# MAGIC -- After the first successful run you can validate the new assets with:
# MAGIC -- DESCRIBE HISTORY mainyc_taxic.ref.trips_clean;

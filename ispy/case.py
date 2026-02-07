"""
iSpy Case Builder - Parse iOS backups into a searchable case file
"""

from __future__ import annotations

import json
import plistlib
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .backup import BackupCatalog, BackupFileRecord

APPLE_EPOCH = datetime(2001, 1, 1, tzinfo=timezone.utc)


def _apple_time_to_iso(value: Optional[int]) -> Optional[str]:
    if value is None:
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None

    # Heuristic: nanoseconds since 2001 or seconds since 2001
    if numeric > 1e12:
        seconds = numeric / 1e9
    else:
        seconds = numeric
    ts = APPLE_EPOCH + timedelta(seconds=seconds)
    return ts.isoformat()


def _safe_plist_load(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        with path.open("rb") as handle:
            return plistlib.load(handle)
    except Exception:
        return None


def _sqlite_tables(path: Path) -> List[str]:
    try:
        with sqlite3.connect(path) as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            return [row[0] for row in cursor.fetchall()]
    except Exception:
        return []


def _sqlite_columns(path: Path, table: str) -> List[str]:
    try:
        with sqlite3.connect(path) as conn:
            cursor = conn.execute(f"PRAGMA table_info({table})")
            return [row[1] for row in cursor.fetchall()]
    except Exception:
        return []


def _sqlite_query(path: Path, query: str, limit: int = 200) -> List[Dict[str, Any]]:
    try:
        with sqlite3.connect(path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query + f" LIMIT {int(limit)}")
            return [dict(row) for row in cursor.fetchall()]
    except Exception:
        return []


def _parse_sms(db_path: Path, limit: int = 200) -> Dict[str, Any]:
    rows = _sqlite_query(
        db_path,
        """
        SELECT message.rowid as id,
               message.date as date,
               message.text as text,
               message.is_from_me as is_from_me,
               handle.id as handle_id
        FROM message
        LEFT JOIN handle ON message.handle_id = handle.rowid
        ORDER BY message.date DESC
        """,
        limit=limit,
    )
    for row in rows:
        row["date_iso"] = _apple_time_to_iso(row.get("date"))
    return {"count": len(rows), "messages": rows}


def _parse_safari_history(db_path: Path, limit: int = 200) -> Dict[str, Any]:
    rows = _sqlite_query(
        db_path,
        """
        SELECT history_items.id as id,
               history_items.url as url,
               history_items.title as title,
               history_visits.visit_time as visit_time
        FROM history_items
        LEFT JOIN history_visits ON history_items.id = history_visits.history_item
        ORDER BY history_visits.visit_time DESC
        """,
        limit=limit,
    )
    for row in rows:
        row["visit_time_iso"] = _apple_time_to_iso(row.get("visit_time"))
    return {"count": len(rows), "visits": rows}


def _parse_contacts(db_path: Path, limit: int = 200) -> Dict[str, Any]:
    tables = _sqlite_tables(db_path)
    if "ABPerson" in tables:
        columns = _sqlite_columns(db_path, "ABPerson")
        wanted = [col for col in columns if col.lower() in {"first", "last", "organization"}]
        select_cols = ", ".join(wanted) if wanted else "*"
        rows = _sqlite_query(db_path, f"SELECT {select_cols} FROM ABPerson", limit=limit)
        return {"count": len(rows), "contacts": rows, "table": "ABPerson"}
    if "ZABCDCONTACTINDEX" in tables:
        rows = _sqlite_query(db_path, "SELECT ZDISPLAYNAME FROM ZABCDCONTACTINDEX", limit=limit)
        return {"count": len(rows), "contacts": rows, "table": "ZABCDCONTACTINDEX"}
    return {"count": 0, "contacts": [], "table": None}


def _parse_calls(db_path: Path, limit: int = 200) -> Dict[str, Any]:
    tables = _sqlite_tables(db_path)
    if "ZCALLRECORD" in tables:
        columns = _sqlite_columns(db_path, "ZCALLRECORD")
        wanted = []
        for col in ["ZDATE", "ZANSWERED", "ZCALLTYPE", "ZDURATION", "ZORIGINATOR", "ZDISCONNECTEDCAUSE"]:
            if col in columns:
                wanted.append(col)
        select_cols = ", ".join(wanted) if wanted else "*"
        rows = _sqlite_query(db_path, f"SELECT {select_cols} FROM ZCALLRECORD ORDER BY ZDATE DESC", limit=limit)
        for row in rows:
            if "ZDATE" in row:
                row["date_iso"] = _apple_time_to_iso(row.get("ZDATE"))
        return {"count": len(rows), "calls": rows, "table": "ZCALLRECORD"}
    return {"count": 0, "calls": [], "table": None}


def _parse_notes(db_path: Path, limit: int = 200) -> Dict[str, Any]:
    tables = _sqlite_tables(db_path)
    if "ZNOTE" in tables:
        columns = _sqlite_columns(db_path, "ZNOTE")
        wanted = []
        for col in ["ZDATECREATED", "ZDATEEDITED", "ZTITLE1", "ZSNIPPET"]:
            if col in columns:
                wanted.append(col)
        select_cols = ", ".join(wanted) if wanted else "*"
        rows = _sqlite_query(db_path, f"SELECT {select_cols} FROM ZNOTE ORDER BY ZDATEEDITED DESC", limit=limit)
        for row in rows:
            if "ZDATECREATED" in row:
                row["created_iso"] = _apple_time_to_iso(row.get("ZDATECREATED"))
            if "ZDATEEDITED" in row:
                row["edited_iso"] = _apple_time_to_iso(row.get("ZDATEEDITED"))
        return {"count": len(rows), "notes": rows, "table": "ZNOTE"}
    return {"count": 0, "notes": [], "table": None}


def _parse_calendar(db_path: Path, limit: int = 200) -> Dict[str, Any]:
    tables = _sqlite_tables(db_path)
    if "CalendarItem" in tables:
        columns = _sqlite_columns(db_path, "CalendarItem")
        wanted = []
        for col in ["summary", "start_date", "end_date", "location", "description"]:
            if col in columns:
                wanted.append(col)
        select_cols = ", ".join(wanted) if wanted else "*"
        rows = _sqlite_query(db_path, f"SELECT {select_cols} FROM CalendarItem ORDER BY start_date DESC", limit=limit)
        for row in rows:
            if "start_date" in row:
                row["start_iso"] = _apple_time_to_iso(row.get("start_date"))
            if "end_date" in row:
                row["end_iso"] = _apple_time_to_iso(row.get("end_date"))
        return {"count": len(rows), "events": rows, "table": "CalendarItem"}
    return {"count": 0, "events": [], "table": None}


def _parse_photos(db_path: Path, limit: int = 200) -> Dict[str, Any]:
    tables = _sqlite_tables(db_path)
    if "ZASSET" in tables:
        columns = _sqlite_columns(db_path, "ZASSET")
        wanted = []
        for col in ["ZDATECREATED", "ZADDEDDATE", "ZFILENAME", "ZLATITUDE", "ZLONGITUDE"]:
            if col in columns:
                wanted.append(col)
        select_cols = ", ".join(wanted) if wanted else "*"
        rows = _sqlite_query(db_path, f"SELECT {select_cols} FROM ZASSET ORDER BY ZDATECREATED DESC", limit=limit)
        for row in rows:
            if "ZDATECREATED" in row:
                row["created_iso"] = _apple_time_to_iso(row.get("ZDATECREATED"))
            if "ZADDEDDATE" in row:
                row["added_iso"] = _apple_time_to_iso(row.get("ZADDEDDATE"))
        return {"count": len(rows), "assets": rows, "table": "ZASSET"}
    return {"count": 0, "assets": [], "table": None}


def _parse_plist(path: Path) -> Dict[str, Any]:
    data = _safe_plist_load(path) or {}
    return {"count": len(data) if isinstance(data, dict) else 0, "data": data}


@dataclass
class ArtifactSpec:
    name: str
    domain: str
    relative_path: str
    parser: Optional[Any] = None
    raw_only: bool = False


ARTIFACTS: List[ArtifactSpec] = [
    ArtifactSpec(
        name="sms",
        domain="HomeDomain",
        relative_path="Library/SMS/sms.db",
        parser=_parse_sms,
    ),
    ArtifactSpec(
        name="safari_history",
        domain="HomeDomain",
        relative_path="Library/Safari/History.db",
        parser=_parse_safari_history,
    ),
    ArtifactSpec(
        name="contacts",
        domain="HomeDomain",
        relative_path="Library/AddressBook/AddressBook.sqlitedb",
        parser=_parse_contacts,
    ),
    ArtifactSpec(
        name="call_history",
        domain="WirelessDomain",
        relative_path="Library/CallHistoryDB/CallHistory.storedata",
        parser=_parse_calls,
    ),
    ArtifactSpec(
        name="photos",
        domain="MediaDomain",
        relative_path="PhotoData/Photos.sqlite",
        parser=_parse_photos,
    ),
    ArtifactSpec(
        name="notes",
        domain="HomeDomain",
        relative_path="Library/Notes/NoteStore.sqlite",
        parser=_parse_notes,
    ),
    ArtifactSpec(
        name="calendar",
        domain="HomeDomain",
        relative_path="Library/Calendar/Calendar.sqlitedb",
        parser=_parse_calendar,
    ),
    ArtifactSpec(
        name="wifi_plist",
        domain="SystemConfigurationDomain",
        relative_path="SystemConfiguration/com.apple.wifi.plist",
        parser=_parse_plist,
    ),
    ArtifactSpec(
        name="app_installation_plist",
        domain="HomeDomain",
        relative_path="Library/Caches/com.apple.mobile.installation.plist",
        parser=_parse_plist,
    ),
]


class CaseBuilder:
    def __init__(self, backup_dir: Path):
        self.backup_dir = Path(backup_dir)
        self.catalog = BackupCatalog(self.backup_dir)

    def _load_backup_metadata(self) -> Dict[str, Any]:
        info = _safe_plist_load(self.backup_dir / "Info.plist") or {}
        manifest = _safe_plist_load(self.backup_dir / "Manifest.plist") or {}
        status = _safe_plist_load(self.backup_dir / "Status.plist") or {}
        return {
            "info_plist": info,
            "manifest_plist": manifest,
            "status_plist": status,
        }

    def _parse_artifact(self, spec: ArtifactSpec, record: BackupFileRecord) -> Dict[str, Any]:
        source_path = self.catalog.get_file_path(record)
        if spec.raw_only or not spec.parser:
            return {"present": True, "raw_only": True}
        try:
            data = spec.parser(source_path)
            return {"present": True, "raw_only": False, "data": data}
        except Exception as exc:
            return {"present": True, "raw_only": False, "error": str(exc)}

    def build(self) -> Dict[str, Any]:
        case = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "backup_dir": str(self.backup_dir),
            "metadata": self._load_backup_metadata(),
            "artifacts": {},
        }

        for spec in ARTIFACTS:
            record = self.catalog.find_record(spec.domain, spec.relative_path)
            if not record:
                case["artifacts"][spec.name] = {"present": False}
                continue
            case["artifacts"][spec.name] = {
                "domain": spec.domain,
                "relative_path": spec.relative_path,
                **self._parse_artifact(spec, record),
            }

        return case

    def save(self, output_path: Path) -> Path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        case = self.build()
        output_path.write_text(json.dumps(case, indent=2, default=str))
        return output_path


def load_case(path: Path) -> Dict[str, Any]:
    return json.loads(Path(path).read_text())


def build_timeline(case: Dict[str, Any], limit: int = 500) -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []
    artifacts = case.get("artifacts", {})

    sms = artifacts.get("sms", {}).get("data", {})
    for item in sms.get("messages", []):
        iso = item.get("date_iso")
        if iso:
            events.append({
                "type": "sms",
                "timestamp": iso,
                "details": {
                    "from_me": item.get("is_from_me"),
                    "handle": item.get("handle_id"),
                    "text": item.get("text"),
                },
            })

    safari = artifacts.get("safari_history", {}).get("data", {})
    for item in safari.get("visits", []):
        iso = item.get("visit_time_iso")
        if iso:
            events.append({
                "type": "safari_visit",
                "timestamp": iso,
                "details": {
                    "url": item.get("url"),
                    "title": item.get("title"),
                },
            })

    calls = artifacts.get("call_history", {}).get("data", {})
    for item in calls.get("calls", []):
        iso = item.get("date_iso")
        if iso:
            events.append({
                "type": "call",
                "timestamp": iso,
                "details": item,
            })

    notes = artifacts.get("notes", {}).get("data", {})
    for item in notes.get("notes", []):
        iso = item.get("edited_iso") or item.get("created_iso")
        if iso:
            events.append({
                "type": "note",
                "timestamp": iso,
                "details": item,
            })

    calendar = artifacts.get("calendar", {}).get("data", {})
    for item in calendar.get("events", []):
        iso = item.get("start_iso")
        if iso:
            events.append({
                "type": "calendar",
                "timestamp": iso,
                "details": item,
            })

    photos = artifacts.get("photos", {}).get("data", {})
    for item in photos.get("assets", []):
        iso = item.get("created_iso") or item.get("added_iso")
        if iso:
            events.append({
                "type": "photo",
                "timestamp": iso,
                "details": item,
            })

    events.sort(key=lambda ev: ev.get("timestamp") or "")
    if limit:
        return events[-limit:]
    return events


def search_case(case: Dict[str, Any], query: str, limit: int = 50) -> List[Dict[str, Any]]:
    if not query:
        return []
    needle = query.lower()
    results: List[Dict[str, Any]] = []
    artifacts = case.get("artifacts", {})
    for name, payload in artifacts.items():
        data = payload.get("data")
        if data is None:
            continue
        text = json.dumps(data, default=str).lower()
        if needle in text:
            snippet_index = text.find(needle)
            snippet = text[max(0, snippet_index - 80):snippet_index + 80]
            results.append({
                "artifact": name,
                "match_snippet": snippet,
            })
        if len(results) >= limit:
            break
    return results


def build_case_report(case: Dict[str, Any]) -> Dict[str, Any]:
    artifacts = case.get("artifacts", {})
    counts = {}
    for name, payload in artifacts.items():
        data = payload.get("data", {})
        if isinstance(data, dict) and "count" in data:
            counts[name] = data.get("count")
    timeline = build_timeline(case, limit=200)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "backup_dir": case.get("backup_dir"),
        "artifact_counts": counts,
        "timeline_preview": timeline,
    }


def export_case_report(case: Dict[str, Any], output_path: Path, report_format: str) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report = build_case_report(case)

    if report_format == "json":
        output_path.write_text(json.dumps(report, indent=2, default=str))
        return output_path

    if report_format == "csv":
        import csv
        with output_path.open("w", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["artifact", "count"])
            for name, count in report.get("artifact_counts", {}).items():
                writer.writerow([name, count])
        return output_path

    if report_format == "html":
        rows = []
        for name, count in report.get("artifact_counts", {}).items():
            rows.append(f"<tr><td>{name}</td><td>{count}</td></tr>")
        timeline_rows = []
        for item in report.get("timeline_preview", []):
            timeline_rows.append(
                f"<tr><td>{item.get('timestamp')}</td><td>{item.get('type')}</td><td>{json.dumps(item.get('details', {}))}</td></tr>"
            )
        html = f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>iSpy Case Report</title>
    <style>
      body {{ font-family: Arial, sans-serif; margin: 24px; }}
      table {{ border-collapse: collapse; width: 100%; margin-bottom: 24px; }}
      th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
      th {{ background: #f4f4f4; }}
    </style>
  </head>
  <body>
    <h1>iSpy Case Report</h1>
    <p><strong>Backup:</strong> {report.get("backup_dir")}</p>
    <h2>Artifact Counts</h2>
    <table>
      <tr><th>Artifact</th><th>Count</th></tr>
      {''.join(rows)}
    </table>
    <h2>Timeline Preview</h2>
    <table>
      <tr><th>Timestamp</th><th>Type</th><th>Details</th></tr>
      {''.join(timeline_rows)}
    </table>
  </body>
</html>"""
        output_path.write_text(html)
        return output_path

    raise ValueError(f"Unsupported report format: {report_format}")

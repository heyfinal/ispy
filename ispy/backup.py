"""
iSpy Backup Utilities - Acquisition and Backup Catalog
"""

from __future__ import annotations

import shutil
import sqlite3
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional


def _ensure_idevicebackup2():
    if shutil.which("idevicebackup2") is None:
        raise RuntimeError("idevicebackup2 not found. Install libimobiledevice via brew.")


@dataclass
class BackupFileRecord:
    file_id: str
    domain: str
    relative_path: str


class BackupManager:
    """Wrapper around idevicebackup2 for acquisition tasks."""

    def __init__(self, udid: Optional[str] = None, network: bool = False, interactive: bool = False):
        self.udid = udid
        self.network = network
        self.interactive = interactive

    def _base_cmd(self) -> List[str]:
        cmd = ["idevicebackup2"]
        if self.udid:
            cmd += ["-u", self.udid]
        if self.network:
            cmd.append("-n")
        if self.interactive:
            cmd.append("-i")
        return cmd

    def _run(self, args: List[str], backup_dir: Path) -> subprocess.CompletedProcess:
        _ensure_idevicebackup2()
        cmd = self._base_cmd() + args + [str(backup_dir)]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or "Backup command failed.")
        return proc

    def backup(self, backup_dir: Path, full: bool = False) -> subprocess.CompletedProcess:
        args = ["backup"]
        if full:
            args.append("--full")
        backup_dir.mkdir(parents=True, exist_ok=True)
        return self._run(args, backup_dir)

    def info(self, backup_dir: Path) -> subprocess.CompletedProcess:
        return self._run(["info"], backup_dir)

    def list_files(self, backup_dir: Path) -> subprocess.CompletedProcess:
        return self._run(["list"], backup_dir)

    def unback(self, backup_dir: Path) -> subprocess.CompletedProcess:
        return self._run(["unback"], backup_dir)

    def set_encryption(self, backup_dir: Path, enabled: bool, password: Optional[str] = None) -> subprocess.CompletedProcess:
        args = ["encryption", "on" if enabled else "off"]
        if password:
            args.append(password)
        return self._run(args, backup_dir)

    def change_password(self, backup_dir: Path, old: Optional[str], new: Optional[str]) -> subprocess.CompletedProcess:
        args = ["changepw"]
        if old:
            args.append(old)
        if new:
            args.append(new)
        return self._run(args, backup_dir)


class BackupCatalog:
    """Manifest.db reader for iOS backups."""

    def __init__(self, backup_dir: Path):
        self.backup_dir = Path(backup_dir)
        self.manifest_db = self.backup_dir / "Manifest.db"
        if not self.manifest_db.exists():
            raise FileNotFoundError(f"Manifest.db not found in {self.backup_dir}")
        self._columns = self._load_columns()

    def _load_columns(self) -> Dict[str, str]:
        with sqlite3.connect(self.manifest_db) as conn:
            cursor = conn.execute("PRAGMA table_info(Files)")
            columns = [row[1] for row in cursor.fetchall()]
        return {col.lower(): col for col in columns}

    def _col(self, name: str) -> str:
        column = self._columns.get(name.lower())
        if not column:
            raise KeyError(f"Missing column {name} in Manifest.db Files table")
        return column

    def _resolve_backup_path(self, file_id: str) -> Path:
        direct = self.backup_dir / file_id
        if direct.exists():
            return direct
        sharded = self.backup_dir / file_id[:2] / file_id
        if sharded.exists():
            return sharded
        return direct

    def list_records(
        self,
        domain: Optional[str] = None,
        contains: Optional[str] = None,
        limit: Optional[int] = 500
    ) -> List[BackupFileRecord]:
        file_id_col = self._col("fileID")
        domain_col = self._col("domain")
        path_col = self._col("relativePath")

        filters = []
        params: List[str] = []
        if domain:
            filters.append(f"{domain_col} = ?")
            params.append(domain)
        if contains:
            filters.append(f"{path_col} LIKE ?")
            params.append(f"%{contains}%")

        where = f"WHERE {' AND '.join(filters)}" if filters else ""
        limit_clause = f"LIMIT {int(limit)}" if limit else ""

        query = f"SELECT {file_id_col}, {domain_col}, {path_col} FROM Files {where} {limit_clause}"
        with sqlite3.connect(self.manifest_db) as conn:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()

        return [
            BackupFileRecord(file_id=row[0], domain=row[1] or "", relative_path=row[2] or "")
            for row in rows
        ]

    def find_record(self, domain: str, relative_path: str) -> Optional[BackupFileRecord]:
        file_id_col = self._col("fileID")
        domain_col = self._col("domain")
        path_col = self._col("relativePath")

        query = f"SELECT {file_id_col}, {domain_col}, {path_col} FROM Files WHERE {domain_col} = ? AND {path_col} = ?"
        with sqlite3.connect(self.manifest_db) as conn:
            cursor = conn.execute(query, (domain, relative_path))
            row = cursor.fetchone()
        if not row:
            return None
        return BackupFileRecord(file_id=row[0], domain=row[1] or "", relative_path=row[2] or "")

    def read_file_bytes(self, record: BackupFileRecord) -> bytes:
        path = self._resolve_backup_path(record.file_id)
        return path.read_bytes()

    def get_file_path(self, record: BackupFileRecord) -> Path:
        return self._resolve_backup_path(record.file_id)

    def extract_file(self, record: BackupFileRecord, output_path: Path) -> Path:
        output_path = Path(output_path)
        if output_path.is_dir():
            output_path = output_path / Path(record.relative_path).name
        output_path.parent.mkdir(parents=True, exist_ok=True)
        source = self._resolve_backup_path(record.file_id)
        output_path.write_bytes(source.read_bytes())
        return output_path

    def extract_domain(self, domain: str, output_dir: Path) -> int:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        count = 0
        for record in self.list_records(domain=domain, limit=None):
            relative = Path(record.relative_path)
            if not relative:
                continue
            destination = output_dir / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            source = self._resolve_backup_path(record.file_id)
            if source.exists():
                destination.write_bytes(source.read_bytes())
                count += 1
        return count

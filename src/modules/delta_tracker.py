"""Delta Tracker — Incremental/delta migration change detection."""
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from src.utils.helpers import setup_logger
from src.utils.config import SNAPSHOTS_DIR

logger = setup_logger("delta_tracker")


class DeltaTracker:
    """Track data changes for incremental/delta migration."""

    def __init__(self, project_name: str = "default"):
        self.project_name = project_name
        self.snapshot_dir = SNAPSHOTS_DIR / project_name
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def compute_row_hash(row: pd.Series) -> str:
        """Compute an MD5 hash for a single row."""
        row_str = "|".join(str(v) for v in row.values)
        return hashlib.md5(row_str.encode("utf-8")).hexdigest()

    def compute_hashes(self, df: pd.DataFrame) -> pd.Series:
        """Compute hashes for all rows in a DataFrame."""
        return df.apply(self.compute_row_hash, axis=1)

    def get_changed_records(self, df: pd.DataFrame, table_name: str,
                            id_column: str = None) -> Dict[str, Any]:
        """Compare current data against the last snapshot, return change summary.

        Returns:
            dict with keys: 'new', 'modified', 'deleted', 'unchanged',
                            'new_df', 'modified_df', 'all_changes_df', 'stats'
        """
        current_hashes = self.compute_hashes(df)

        # Load previous snapshot
        prev_snapshot = self._load_snapshot(table_name)

        if prev_snapshot is None:
            # No previous snapshot — everything is new
            return {
                "new": list(range(len(df))),
                "modified": [],
                "deleted": [],
                "unchanged": [],
                "new_df": df.copy(),
                "modified_df": pd.DataFrame(),
                "all_changes_df": df.copy(),
                "stats": {
                    "total_current": len(df),
                    "new_count": len(df),
                    "modified_count": 0,
                    "deleted_count": 0,
                    "unchanged_count": 0,
                    "change_percentage": 100.0
                }
            }

        prev_hashes = prev_snapshot.get("hashes", {})
        prev_id_map = prev_snapshot.get("id_map", {})

        # Build current ID map
        if id_column and id_column in df.columns:
            current_id_map = {str(row[id_column]): idx for idx, row in df.iterrows()}
        else:
            current_id_map = {str(idx): idx for idx in range(len(df))}

        new_indices = []
        modified_indices = []
        unchanged_indices = []
        deleted_keys = []

        current_hash_map = {}
        for key, idx in current_id_map.items():
            h = current_hashes.iloc[idx] if idx < len(current_hashes) else ""
            current_hash_map[key] = h

            if key not in prev_id_map:
                new_indices.append(idx)
            elif prev_hashes.get(prev_id_map[key], "") != h:
                modified_indices.append(idx)
            else:
                unchanged_indices.append(idx)

        # Detect deleted records
        for key in prev_id_map:
            if key not in current_id_map:
                deleted_keys.append(key)

        new_df = df.iloc[new_indices] if new_indices else pd.DataFrame(columns=df.columns)
        modified_df = df.iloc[modified_indices] if modified_indices else pd.DataFrame(columns=df.columns)
        changes_indices = new_indices + modified_indices
        all_changes_df = df.iloc[changes_indices] if changes_indices else pd.DataFrame(columns=df.columns)

        total = len(df)
        change_count = len(new_indices) + len(modified_indices)

        return {
            "new": new_indices,
            "modified": modified_indices,
            "deleted": deleted_keys,
            "unchanged": unchanged_indices,
            "new_df": new_df,
            "modified_df": modified_df,
            "all_changes_df": all_changes_df,
            "stats": {
                "total_current": total,
                "new_count": len(new_indices),
                "modified_count": len(modified_indices),
                "deleted_count": len(deleted_keys),
                "unchanged_count": len(unchanged_indices),
                "change_percentage": round((change_count / total * 100) if total > 0 else 0, 2)
            }
        }

    def save_snapshot(self, df: pd.DataFrame, table_name: str,
                      id_column: str = None):
        """Save current data state as a snapshot for future comparison."""
        hashes = self.compute_hashes(df)

        if id_column and id_column in df.columns:
            id_map = {str(row[id_column]): str(idx) for idx, row in df.iterrows()}
        else:
            id_map = {str(idx): str(idx) for idx in range(len(df))}

        hash_map = {}
        for key, idx_str in id_map.items():
            idx = int(idx_str)
            if idx < len(hashes):
                hash_map[idx_str] = hashes.iloc[idx]

        snapshot = {
            "table_name": table_name,
            "timestamp": datetime.now().isoformat(),
            "row_count": len(df),
            "columns": list(df.columns),
            "id_column": id_column,
            "id_map": id_map,
            "hashes": hash_map,
        }

        filepath = self.snapshot_dir / f"{table_name}_snapshot.json"
        with open(filepath, 'w') as f:
            json.dump(snapshot, f, indent=2)

        logger.info(f"Snapshot saved for {table_name}: {len(df)} rows")

    def _load_snapshot(self, table_name: str) -> Optional[Dict[str, Any]]:
        """Load a previous snapshot for comparison."""
        filepath = self.snapshot_dir / f"{table_name}_snapshot.json"
        if filepath.exists():
            with open(filepath, 'r') as f:
                return json.load(f)
        return None

    def has_snapshot(self, table_name: str) -> bool:
        """Check if a snapshot exists for the given table."""
        filepath = self.snapshot_dir / f"{table_name}_snapshot.json"
        return filepath.exists()

    def get_snapshot_info(self, table_name: str) -> Optional[Dict[str, Any]]:
        """Get metadata about the last snapshot."""
        snapshot = self._load_snapshot(table_name)
        if snapshot:
            return {
                "table_name": snapshot["table_name"],
                "timestamp": snapshot["timestamp"],
                "row_count": snapshot["row_count"],
                "columns": snapshot["columns"],
            }
        return None

    def clear_snapshots(self):
        """Clear all snapshots for this project."""
        for filepath in self.snapshot_dir.glob("*_snapshot.json"):
            filepath.unlink()
        logger.info(f"Cleared all snapshots for project: {self.project_name}")

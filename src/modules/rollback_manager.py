"""Rollback Manager — Checkpoint-based migration rollback mechanism."""
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from src.utils.helpers import setup_logger
from src.utils.config import HISTORY_DIR

logger = setup_logger("rollback_manager")


class RollbackManager:
    """Manages migration checkpoints and rollback operations for MongoDB."""

    def __init__(self, mongo_uri: str = "", database_name: str = "migrion"):
        self.mongo_uri = mongo_uri
        self.database_name = database_name
        self.checkpoints: List[Dict[str, Any]] = []
        self.checkpoint_dir = HISTORY_DIR / "checkpoints"
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def create_checkpoint(self, collection_name: str, metadata: Dict[str, Any] = None) -> str:
        """Create a checkpoint before a batch operation.

        Returns checkpoint_id for future rollback reference.
        """
        checkpoint_id = f"ckpt_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        checkpoint = {
            "checkpoint_id": checkpoint_id,
            "timestamp": datetime.now().isoformat(),
            "collection_name": collection_name,
            "database_name": self.database_name,
            "status": "created",
            "metadata": metadata or {},
            "inserted_ids": [],
            "pre_count": 0,
        }

        # Get current collection count
        try:
            from pymongo import MongoClient
            client = MongoClient(self.mongo_uri)
            db = client[self.database_name]
            checkpoint["pre_count"] = db[collection_name].count_documents({})
            client.close()
        except Exception as e:
            logger.warning(f"Could not get pre-count: {e}")

        self.checkpoints.append(checkpoint)
        self._save_checkpoint(checkpoint)

        logger.info(f"Checkpoint created: {checkpoint_id} for {collection_name}")
        return checkpoint_id

    def record_inserted_ids(self, checkpoint_id: str, inserted_ids: List):
        """Record the IDs of documents inserted in this checkpoint's batch."""
        for ckpt in self.checkpoints:
            if ckpt["checkpoint_id"] == checkpoint_id:
                ckpt["inserted_ids"].extend([str(id_) for id_ in inserted_ids])
                ckpt["status"] = "active"
                self._save_checkpoint(ckpt)
                break

    def rollback(self, checkpoint_id: str) -> Dict[str, Any]:
        """Rollback to a specific checkpoint by removing inserted documents.

        Returns a summary of the rollback operation.
        """
        result = {
            "checkpoint_id": checkpoint_id,
            "status": "failed",
            "records_removed": 0,
            "message": ""
        }

        # Find the checkpoint
        checkpoint = None
        for ckpt in self.checkpoints:
            if ckpt["checkpoint_id"] == checkpoint_id:
                checkpoint = ckpt
                break

        if checkpoint is None:
            # Try loading from disk
            checkpoint = self._load_checkpoint(checkpoint_id)

        if checkpoint is None:
            result["message"] = f"Checkpoint {checkpoint_id} not found"
            return result

        try:
            from pymongo import MongoClient
            from bson import ObjectId

            client = MongoClient(self.mongo_uri)
            db = client[self.database_name]
            collection = db[checkpoint["collection_name"]]

            if checkpoint["inserted_ids"]:
                # Remove the specific documents inserted after checkpoint
                object_ids = []
                for id_str in checkpoint["inserted_ids"]:
                    try:
                        object_ids.append(ObjectId(id_str))
                    except Exception:
                        pass

                if object_ids:
                    delete_result = collection.delete_many({"_id": {"$in": object_ids}})
                    result["records_removed"] = delete_result.deleted_count
                else:
                    # Fallback: remove records added after checkpoint pre_count
                    current_count = collection.count_documents({})
                    records_to_remove = current_count - checkpoint["pre_count"]
                    if records_to_remove > 0:
                        # Remove the last N records
                        cursor = collection.find().sort("_id", -1).limit(records_to_remove)
                        ids_to_remove = [doc["_id"] for doc in cursor]
                        delete_result = collection.delete_many({"_id": {"$in": ids_to_remove}})
                        result["records_removed"] = delete_result.deleted_count
            else:
                # No inserted_ids tracked, use count-based rollback
                current_count = collection.count_documents({})
                records_to_remove = current_count - checkpoint["pre_count"]
                if records_to_remove > 0:
                    cursor = collection.find().sort("_id", -1).limit(records_to_remove)
                    ids_to_remove = [doc["_id"] for doc in cursor]
                    delete_result = collection.delete_many({"_id": {"$in": ids_to_remove}})
                    result["records_removed"] = delete_result.deleted_count

            client.close()

            # Update checkpoint status
            checkpoint["status"] = "rolled_back"
            self._save_checkpoint(checkpoint)

            result["status"] = "success"
            result["message"] = f"Rolled back {result['records_removed']} records from {checkpoint['collection_name']}"

            logger.info(result["message"])

        except Exception as e:
            result["message"] = f"Rollback failed: {str(e)}"
            logger.error(result["message"])

        return result

    def rollback_all(self) -> List[Dict[str, Any]]:
        """Rollback all checkpoints in reverse order."""
        results = []
        for checkpoint in reversed(self.checkpoints):
            if checkpoint["status"] == "active":
                result = self.rollback(checkpoint["checkpoint_id"])
                results.append(result)
        return results

    def get_checkpoints(self) -> List[Dict[str, Any]]:
        """Get all checkpoints."""
        # Merge in-memory and disk checkpoints
        disk_checkpoints = self._load_all_checkpoints()
        all_ids = {c["checkpoint_id"] for c in self.checkpoints}
        for dc in disk_checkpoints:
            if dc["checkpoint_id"] not in all_ids:
                self.checkpoints.append(dc)
        return sorted(self.checkpoints, key=lambda x: x["timestamp"], reverse=True)

    def _save_checkpoint(self, checkpoint: Dict[str, Any]):
        """Save checkpoint to disk."""
        filepath = self.checkpoint_dir / f"{checkpoint['checkpoint_id']}.json"
        with open(filepath, 'w') as f:
            json.dump(checkpoint, f, indent=2, default=str)

    def _load_checkpoint(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """Load a checkpoint from disk."""
        filepath = self.checkpoint_dir / f"{checkpoint_id}.json"
        if filepath.exists():
            with open(filepath, 'r') as f:
                return json.load(f)
        return None

    def _load_all_checkpoints(self) -> List[Dict[str, Any]]:
        """Load all checkpoints from disk."""
        checkpoints = []
        for filepath in self.checkpoint_dir.glob("ckpt_*.json"):
            try:
                with open(filepath, 'r') as f:
                    checkpoints.append(json.load(f))
            except Exception:
                continue
        return checkpoints

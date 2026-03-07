"""ML Schema Matcher — Embedding-based semantic field matching."""
import numpy as np
from typing import Any, Dict, List, Optional, Tuple
from src.utils.helpers import setup_logger

logger = setup_logger("ml_schema_matcher")


class MLSchemaMatcher:
    """Match source and target schema fields using semantic embeddings."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None

    def _load_model(self):
        """Lazy-load the sentence transformer model."""
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(self.model_name)
                logger.info(f"Loaded embedding model: {self.model_name}")
            except ImportError:
                logger.error("sentence-transformers not installed. Run: pip install sentence-transformers")
                raise ImportError("sentence-transformers is required for ML schema matching")

    def _field_to_text(self, field: Dict[str, Any]) -> str:
        """Convert a schema field to a descriptive text string for embedding."""
        name = field.get("name", "")
        # Convert snake_case/camelCase to readable text
        readable = name.replace("_", " ").replace("-", " ")
        # Add type info if available
        dtype = field.get("type", "")
        if dtype:
            readable += f" ({dtype})"
        return readable

    def compute_embeddings(self, fields: List[Dict[str, Any]]) -> np.ndarray:
        """Compute embeddings for a list of schema fields."""
        self._load_model()
        texts = [self._field_to_text(f) for f in fields]
        embeddings = self.model.encode(texts, show_progress_bar=False)
        return embeddings

    def match_fields(self, source_fields: List[Dict[str, Any]],
                     target_fields: List[Dict[str, Any]],
                     threshold: float = 0.3) -> Dict[str, Any]:
        """Match source fields to target fields using cosine similarity.

        Returns a mapping result with confidence scores.
        """
        self._load_model()

        source_texts = [self._field_to_text(f) for f in source_fields]
        target_texts = [self._field_to_text(f) for f in target_fields]

        source_embeddings = self.model.encode(source_texts, show_progress_bar=False)
        target_embeddings = self.model.encode(target_texts, show_progress_bar=False)

        # Compute cosine similarity matrix
        from numpy.linalg import norm
        similarity_matrix = np.zeros((len(source_fields), len(target_fields)))
        for i, se in enumerate(source_embeddings):
            for j, te in enumerate(target_embeddings):
                cos_sim = np.dot(se, te) / (norm(se) * norm(te) + 1e-8)
                similarity_matrix[i][j] = cos_sim

        # Greedy best-match assignment
        mappings = []
        unmapped_source = []
        unmapped_target = list(range(len(target_fields)))

        # Sort by max similarity (descending) to assign best matches first
        source_order = sorted(
            range(len(source_fields)),
            key=lambda i: max(similarity_matrix[i]) if len(target_fields) > 0 else 0,
            reverse=True
        )

        used_targets = set()
        for src_idx in source_order:
            best_target_idx = -1
            best_score = -1

            for tgt_idx in range(len(target_fields)):
                if tgt_idx not in used_targets and similarity_matrix[src_idx][tgt_idx] > best_score:
                    best_score = similarity_matrix[src_idx][tgt_idx]
                    best_target_idx = tgt_idx

            if best_target_idx >= 0 and best_score >= threshold:
                used_targets.add(best_target_idx)
                mappings.append({
                    "source_field": source_fields[src_idx].get("name", ""),
                    "target_field": target_fields[best_target_idx].get("name", ""),
                    "confidence": round(float(best_score), 4),
                    "method": "ML-Embedding",
                    "data_type_source": source_fields[src_idx].get("type", ""),
                    "data_type_target": target_fields[best_target_idx].get("type", ""),
                })
            else:
                unmapped_source.append(source_fields[src_idx].get("name", ""))

        unmapped_target = [
            target_fields[j].get("name", "")
            for j in range(len(target_fields))
            if j not in used_targets
        ]

        # Sort mappings by confidence descending
        mappings.sort(key=lambda m: m["confidence"], reverse=True)

        return {
            "mappings": mappings,
            "unmapped_source_fields": unmapped_source,
            "unmapped_target_fields": unmapped_target,
            "similarity_matrix": similarity_matrix.tolist(),
            "source_fields": [f.get("name", "") for f in source_fields],
            "target_fields": [f.get("name", "") for f in target_fields],
        }

    @staticmethod
    def compare_with_llm(llm_mappings: Dict[str, Any],
                         ml_mappings: Dict[str, Any]) -> Dict[str, Any]:
        """Compare LLM and ML mapping results."""
        llm_map = {}
        for m in llm_mappings.get("mappings", []):
            llm_map[m.get("source_field", "")] = {
                "target": m.get("target_field", ""),
                "confidence": m.get("confidence", 0)
            }

        ml_map = {}
        for m in ml_mappings.get("mappings", []):
            ml_map[m.get("source_field", "")] = {
                "target": m.get("target_field", ""),
                "confidence": m.get("confidence", 0)
            }

        all_sources = set(list(llm_map.keys()) + list(ml_map.keys()))

        comparisons = []
        agreements = 0
        disagreements = 0
        llm_only = 0
        ml_only = 0

        for source in sorted(all_sources):
            llm_entry = llm_map.get(source, {})
            ml_entry = ml_map.get(source, {})

            llm_target = llm_entry.get("target", "—")
            ml_target = ml_entry.get("target", "—")

            if llm_target != "—" and ml_target != "—":
                if llm_target == ml_target:
                    status = "✅ Agree"
                    agreements += 1
                else:
                    status = "⚠️ Disagree"
                    disagreements += 1
            elif llm_target != "—":
                status = "LLM only"
                llm_only += 1
            else:
                status = "ML only"
                ml_only += 1

            comparisons.append({
                "source_field": source,
                "llm_target": llm_target,
                "llm_confidence": round(llm_entry.get("confidence", 0), 3),
                "ml_target": ml_target,
                "ml_confidence": round(ml_entry.get("confidence", 0), 3),
                "status": status,
            })

        total_comparable = agreements + disagreements
        agreement_rate = (agreements / total_comparable * 100) if total_comparable > 0 else 0

        return {
            "comparisons": comparisons,
            "summary": {
                "total_fields": len(all_sources),
                "agreements": agreements,
                "disagreements": disagreements,
                "llm_only": llm_only,
                "ml_only": ml_only,
                "agreement_rate": round(agreement_rate, 1),
            }
        }

import os
import json
import numpy as np
from typing import List, Dict, Any

from .embedder import RouteMasterEmbedder

from src.path_utils import resolve_path

class EmbeddingPipeline:
    """
    Orchestrates text representation construction, model execution,
    shape validation, and serialization of dense embeddings.
    """
    def __init__(self, processed_dir="data/processed", model_dir="model", model_name="BAAI/bge-small-en-v1.5"):
        self.processed_dir = str(resolve_path(processed_dir))
        self.model_dir = str(resolve_path(model_dir))
        self.embeddings_dir = os.path.join(self.model_dir, "embeddings")
        self.model_name = model_name
        
        # Safe directory initialization
        os.makedirs(self.embeddings_dir, exist_ok=True)
        
    def run(self, batch_size: int = 32):
        """
        Runs the complete text extraction and embedding generation loop.
        """
        print(f"STARTING EMBEDDING GENERATION PIPELINE USING '{self.model_name}'...")
        embedder = RouteMasterEmbedder(model_name=self.model_name)
        
        # Load core files
        print("Loading datasets...")
        skills = self._load_json("skills.json")
        careers = self._load_json("careers.json")
        courses = self._load_json("courses.json")
        projects = self._load_json("projects.json")
        
        career_skills = self._load_json("career_skills.json")
        career_trans = self._load_json("career_transferable_skills.json")
        career_interests = self._load_json("career_interests.json")

        # Create quick index mappings
        skills_dict = {s["skill_id"]: s for s in skills}
        
        # Match lists for career links
        cs_dict = {}
        for cs in career_skills:
            cs_dict.setdefault(cs["career_id"], []).append(cs)
            
        ct_dict = {}
        for ct in career_trans:
            ct_dict.setdefault(ct["career_id"], []).append(ct)
            
        ci_dict = {}
        for ci in career_interests:
            ci_dict.setdefault(ci["career_id"], []).append(ci)

        # ── 1. Embed Skills ──────────────────────────────────────────────────────────
        print("Generating Skill embeddings...")
        skill_texts = []
        skill_ids = []
        for s in skills:
            text = f"{s['skill_name']} | Category: {s['skill_category']} | Type: {s['skill_type']}"
            skill_texts.append(text)
            skill_ids.append(s["skill_id"])
            
        self._embed_and_save(embedder, skill_texts, skill_ids, "skills", batch_size)

        # ── 2. Embed Careers ─────────────────────────────────────────────────────────
        print("Generating Career embeddings...")
        career_texts = []
        career_ids = []
        for c in careers:
            cid = c["career_id"]
            title = c["career_title"]
            domain = c["career_domain"]
            desc = c["career_description"]
            
            # Sub-components
            tech_skills = cs_dict.get(cid, [])
            tech_names = ", ".join([skills_dict[ts["skill_id"]]["skill_name"] for ts in tech_skills if ts["skill_id"] in skills_dict])
            
            soft_skills = ct_dict.get(cid, [])
            soft_names = ", ".join([skills_dict[ss["skill_id"]]["skill_name"] for ss in soft_skills if ss["skill_id"] in skills_dict])
            
            interests = ci_dict.get(cid, [])
            interest_desc = ", ".join([f"{i['interest_type']} ({i.get('interest_score', 'N/A')})" for i in interests])
            
            text = f"{title} | Domain: {domain} | Description: {desc}"
            if tech_names:
                text += f" | Technical Skills: {tech_names}"
            if soft_names:
                text += f" | Soft Skills: {soft_names}"
            if interest_desc:
                text += f" | Interests: {interest_desc}"
                
            career_texts.append(text)
            career_ids.append(cid)
            
        self._embed_and_save(embedder, career_texts, career_ids, "careers", batch_size)

        # ── 3. Embed Courses ─────────────────────────────────────────────────────────
        print("Generating Course embeddings...")
        course_texts = []
        course_ids = []
        for crs in courses:
            c_name = crs["course_name"]
            org = crs.get("organization", "Unknown Provider")
            diff = crs.get("difficulty", "Intermediate")
            desc = crs.get("description", "")
            
            # Lookup skills
            mapped_skills = crs.get("skills", [])
            skills_joined = ", ".join([skills_dict[sid]["skill_name"] for sid in mapped_skills if sid in skills_dict])
            if not skills_joined:
                skills_joined = crs.get("skills_raw", "None")
                
            text = f"{c_name} | Difficulty: {diff} | Provider: {org} | Description: {desc} | Skills: {skills_joined}"
            course_texts.append(text)
            course_ids.append(crs["course_id"])
            
        self._embed_and_save(embedder, course_texts, course_ids, "courses", batch_size)

        # ── 4. Embed Projects ────────────────────────────────────────────────────────
        print("Generating Project embeddings...")
        project_texts = []
        project_ids = []
        for p in projects:
            p_name = p["project_name"]
            dom = p.get("domain", "General Engineering")
            diff = p.get("difficulty", "Intermediate")
            desc = p.get("description", "")
            
            stack_list = p.get("tech_stack", [])
            stack = ", ".join(stack_list) if isinstance(stack_list, list) else str(stack_list)
            
            mapped_skills = p.get("skills", [])
            skills_joined = ", ".join([skills_dict[sid]["skill_name"] for sid in mapped_skills if sid in skills_dict])
            if not skills_joined:
                skills_joined = p.get("skills_raw", "None")
                
            text = f"{p_name} | Domain: {dom} | Difficulty: {diff} | Description: {desc} | Tech Stack: {stack} | Skills: {skills_joined}"
            project_texts.append(text)
            project_ids.append(p["project_id"])
            
        self._embed_and_save(embedder, project_texts, project_ids, "projects", batch_size)
        
        print("SUCCESS: EMBEDDING GENERATION PIPELINE COMPLETED SUCCESSFULLY.")

    def _embed_and_save(self, embedder: RouteMasterEmbedder, texts: List[str], ids: List[str], entity: str, batch_size: int):
        """Helper to batch encode, validate shapes, and persist arrays."""
        if not texts:
            print(f"WARNING: No text mappings found for entity '{entity}'. Skipping.")
            return
            
        # 1. Encode
        embeddings = embedder.encode(texts, batch_size=batch_size, show_progress_bar=True)
        
        # 2. Validate
        expected_shape = (len(texts), embedder.dimension)
        assert embeddings.shape == expected_shape, \
            f"Shape validation failed for '{entity}': expected {expected_shape}, got {embeddings.shape}"
            
        # 3. Persist NPY
        npy_path = os.path.join(self.embeddings_dir, f"{entity}_embeddings.npy")
        np.save(npy_path, embeddings)
        
        # 4. Persist ID index map
        id_map = {id_val: idx for idx, id_val in enumerate(ids)}
        json_path = os.path.join(self.embeddings_dir, f"{entity}_ids.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(id_map, f, indent=2)
            
        print(f"SAVED: '{npy_path}' ({embeddings.shape}) and '{json_path}' ({len(id_map)} indices)")

    def _load_json(self, filename: str) -> List[Dict[str, Any]]:
        path = os.path.join(self.processed_dir, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing required dataset: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

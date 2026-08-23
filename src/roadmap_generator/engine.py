import os
import json
import networkx as nx
from typing import List, Dict, Any, Optional, Set, Tuple

from .schemas import (
    RoadmapRequest, RoadmapResponse, CareerBrief, RoadmapSummary,
    RoadmapNode, RoadmapEdge, CompactCourse, CompactProject, ReactFlowData
)
from src.gap_engine.gap_engine import SkillGapEngine
from src.gap_engine.schemas import SkillGapRequest
from src.hybrid_recommender.engine import HybridRecommender
from src.project_recommender.engine import ProjectRecommender
from src.path_utils import resolve_path

# Cached singleton
_global_roadmap_generator = None


class RoadmapGenerator:
    """
    Personalized roadmap generation engine.
    Applies graph theory, career-domain prerequisite filtering, skill normalization,
    DAG validation/cycle resolution, weighted course/project matching, and React Flow output.
    """
    # Canonical skill aliases for normalization
    CANONICAL_ALIASES = {
        "llm": "SK_00255",
        "llms": "SK_00255",
        "large language models": "SK_00255",
        "ml": "SK_00264",
        "machine learning": "SK_00264",
        "dl": "SK_00132",
        "deep learning": "SK_00132",
        "nlp": "SK_00316",
        "natural language processing": "SK_00316",
        "aws": "SK_00046",
        "amazon web services": "SK_00046",
        "js": "SK_00240",
        "javascript": "SK_00240",
        "py": "SK_00360",
        "python": "SK_00360",
        "sql": "SK_00435",
        "git": "SK_00189",
        "docker": "SK_00145",
        "pytorch": "SK_00361",
        "tensorflow": "SK_00457",
        "generative ai": "SK_00188",
        "genai": "SK_00188",
        "rest apis": "SK_00382",
        "rest api": "SK_00382",
        "api": "SK_00382",
        "math": "SK_00270",
        "mathematics": "SK_00270",
        "statistics": "SK_00443",
        "flask": "SK_00179",
        "fastapi": "SK_00174",
    }

    # Out-of-domain skills to filter out when target career is non-web (e.g., AI Engineer)
    WEB_DEV_ONLY_SKILLS = {
        "SK_00212",  # HTML
        "SK_00106",  # CSS
        "SK_00240",  # JavaScript
        "SK_00314",  # Node.js
        "SK_00173",  # Express.js
        "SK_00369",  # React
        "SK_00492",  # Vue.js
        "SK_00019",  # Angular
        "SK_00213",  # HTML/CSS
    }

    MIN_COURSE_RELEVANCE = 0.70
    MIN_PROJECT_RELEVANCE = 0.60

    def __init__(self, processed_dir="data/processed", model_dir="model"):
        self.processed_dir = str(resolve_path(processed_dir))
        self.model_dir = str(resolve_path(model_dir))

        self._load_datasets()

        self.gap_engine = SkillGapEngine(processed_dir=self.processed_dir)
        self.course_recommender = HybridRecommender(processed_dir=self.processed_dir, model_dir=self.model_dir)
        self.project_recommender = ProjectRecommender(processed_dir=self.processed_dir, model_dir=self.model_dir)

        self.G_req = self.gap_engine.resolver.G

    def _load_datasets(self):
        """Loads local registries for dataset lookups."""
        with open(os.path.join(self.processed_dir, "skills.json"), "r", encoding="utf-8") as f:
            skills = json.load(f)
        self.skills_dict = {s["skill_id"]: s for s in skills}
        self.skill_name_to_id = {s["skill_name"].lower().strip(): s["skill_id"] for s in skills}

        with open(os.path.join(self.processed_dir, "careers.json"), "r", encoding="utf-8") as f:
            self.careers_list = json.load(f)
        self.career_lookup = {}
        for c in self.careers_list:
            self.career_lookup[c["career_id"]] = c
            self.career_lookup[c["career_title"].lower().strip()] = c

        with open(os.path.join(self.processed_dir, "courses.json"), "r", encoding="utf-8") as f:
            self.courses_list = json.load(f)

        with open(os.path.join(self.processed_dir, "projects.json"), "r", encoding="utf-8") as f:
            self.projects_list = json.load(f)

        with open(os.path.join(self.processed_dir, "career_skills.json"), "r", encoding="utf-8") as f:
            self.career_skills_list = json.load(f)

        with open(os.path.join(self.processed_dir, "skill_dependencies.json"), "r", encoding="utf-8") as f:
            self.dependencies_list = json.load(f)

    def normalize_skill(self, raw_skill: str) -> Optional[str]:
        """Normalizes a raw skill string or ID into a canonical skill ID."""
        clean = raw_skill.lower().strip()
        if not clean:
            return None

        # Check raw skill ID (e.g. 'SK_00360')
        if clean.upper() in self.skills_dict:
            return clean.upper()

        # Check canonical aliases
        if clean in self.CANONICAL_ALIASES:
            return self.CANONICAL_ALIASES[clean]

        # Check exact skill name lookup
        if clean in self.skill_name_to_id:
            return self.skill_name_to_id[clean]

        # Partial matching fallback
        for name, sid in self.skill_name_to_id.items():
            if clean in name or name in clean:
                return sid

        return None

    def normalize_user_skills(self, skills: List[str]) -> Set[str]:
        """Returns a set of canonical skill IDs for user skills."""
        user_ids = set()
        for s in skills:
            sid = self.normalize_skill(s)
            if sid:
                user_ids.add(sid)
        return user_ids

    def generate_roadmap(self, request: RoadmapRequest) -> RoadmapResponse:
        """Assembles a React Flow-compatible learning roadmap sequence."""
        warnings: List[str] = []

        # 1. Resolve Target Career
        target_input = (request.target_role or "AI Engineer").strip()
        career_obj = self.career_lookup.get(target_input) or self.career_lookup.get(target_input.lower())

        if not career_obj:
            # Fallback search
            for c in self.careers_list:
                if target_input.lower() in c["career_title"].lower():
                    career_obj = c
                    break

        if not career_obj:
            career_obj = {"career_id": "CAR_003", "career_title": "AI Engineer"}
            warnings.append(f"Target career '{target_input}' not found in registry. Defaulted to AI Engineer.")

        career_id = career_obj["career_id"]
        career_title = career_obj["career_title"]

        # 2. Extract Required Career Skills
        career_skills_map = {}
        for cs in self.career_skills_list:
            if cs["career_id"] == career_id:
                career_skills_map[cs["skill_id"]] = cs.get("importance", "Medium")

        if not career_skills_map:
            warnings.append(f"No explicit skill mappings found for career '{career_title}' ({career_id}).")

        # 3. User Skills Normalization
        raw_user_skills = request.skills
        user_skill_ids = self.normalize_user_skills(raw_user_skills)

        # 4. Induce Subgraph with Career & Prerequisite Closure Filtering
        subgraph_nodes = set(career_skills_map.keys())

        # Is web development explicitly part of this career?
        is_web_career = any(sid in self.WEB_DEV_ONLY_SKILLS for sid in career_skills_map)

        # Expand prerequisite closures for required career skills
        prereq_added = set()
        for sid in list(subgraph_nodes):
            if sid in self.skills_dict:
                closures = self.gap_engine.resolver.get_all_prerequisites(sid)
                for req in closures.get("required", []):
                    req_id = req["skill_id"]
                    # Skip web-dev branch if career is non-web and web skill wasn't explicitly required
                    if not is_web_career and req_id in self.WEB_DEV_ONLY_SKILLS and req_id not in career_skills_map:
                        continue
                    subgraph_nodes.add(req_id)
                    prereq_added.add(req_id)

        # Include user's completed skills if they belong to subgraph or prerequisites
        subgraph_nodes.update(user_skill_ids.intersection(self.skills_dict.keys()))

        # Build Graph Edges
        required_edges = []
        for u, v, attrs in self.G_req.edges(data=True):
            if u in subgraph_nodes and v in subgraph_nodes:
                rel = attrs.get("relationship", "prerequisite")
                if rel in ["prerequisite", "strong_prerequisite"]:
                    # Filter out out-of-domain edges (e.g. Express.js -> REST APIs for AI Engineer)
                    if not is_web_career and u in self.WEB_DEV_ONLY_SKILLS and u not in career_skills_map:
                        continue
                    required_edges.append((u, v))

        G_sub = nx.DiGraph()
        G_sub.add_nodes_from(subgraph_nodes)
        G_sub.add_edges_from(required_edges)

        # Validate node existence
        valid_nodes = set(n for n in G_sub.nodes if n in self.skills_dict)
        G_sub = G_sub.subgraph(valid_nodes).copy()

        # 5. Cycle Detection & Breakage
        if not nx.is_directed_acyclic_graph(G_sub):
            cycles = list(nx.simple_cycles(G_sub))
            for cycle in cycles:
                cycle_str = " -> ".join([self.skills_dict.get(n, {}).get("skill_name", n) for n in cycle])
                warnings.append(f"Cycle detected in prerequisite graph: {cycle_str}. Resolving by removing feedback edge.")
                if len(cycle) >= 2:
                    u, v = cycle[0], cycle[1]
                    if G_sub.has_edge(u, v):
                        G_sub.remove_edge(u, v)

        # 6. Topological Sort & Sequence Ranking
        try:
            topo_order = list(nx.topological_sort(G_sub))
        except Exception as e:
            topo_order = sorted(list(G_sub.nodes))
            warnings.append(f"Topological sort fallback used ({e}).")

        # 7. Priority and Unlock Calculations
        unlock_scores = {}
        for sid in G_sub.nodes:
            descendants = nx.descendants(G_sub, sid)
            unlock_scores[sid] = len(descendants)

        skill_priorities = {}
        for sid in G_sub.nodes:
            if sid in career_skills_map:
                skill_priorities[sid] = career_skills_map[sid]
            elif unlock_scores.get(sid, 0) >= 2:
                skill_priorities[sid] = "Critical"
            elif unlock_scores.get(sid, 0) >= 1:
                skill_priorities[sid] = "High"
            else:
                skill_priorities[sid] = "Medium"

        # 8. Node Statuses & Learning Frontier
        completed_courses_clean = {c.lower().strip() for c in request.completed_courses}
        nodes: List[RoadmapNode] = []
        completed_count = 0
        remaining_count = 0
        critical_remaining = 0

        # Determine node statuses
        node_status_map = {}
        next_eligible_candidates = []

        for sid in topo_order:
            if sid in user_skill_ids:
                node_status_map[sid] = "completed"
            else:
                predecessors = list(G_sub.predecessors(sid))
                if all(p in user_skill_ids for p in predecessors):
                    next_eligible_candidates.append(sid)
                    node_status_map[sid] = "next"
                else:
                    node_status_map[sid] = "locked"

        # Refine frontier: prioritize immediate next skills
        priority_weight = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
        next_eligible_candidates.sort(
            key=lambda x: (priority_weight.get(skill_priorities.get(x, "Medium"), 2), unlock_scores.get(x, 0)),
            reverse=True
        )

        for idx, sid in enumerate(topo_order, 1):
            s_name = self.skills_dict.get(sid, {}).get("skill_name", "Unknown Skill")
            priority = skill_priorities.get(sid, "Medium")
            status = node_status_map.get(sid, "locked")

            if status == "completed":
                completed_count += 1
            else:
                remaining_count += 1
                if priority == "Critical":
                    critical_remaining += 1

            predecessor_ids = list(G_sub.predecessors(sid))

            compact_courses: List[CompactCourse] = []
            compact_projects: List[CompactProject] = []
            learning_action = "learn_only"
            reason = ""

            if status != "completed":
                # Course Matching with Weighted Quality Filter
                attached_courses = self._get_relevant_courses_weighted(
                    sid, career_title, request.difficulty, completed_courses_clean
                )
                compact_courses = attached_courses[:request.courses_per_skill]

                # Project Matching
                attached_projects = self._get_relevant_projects_weighted(
                    sid, career_title, request.difficulty
                )
                compact_projects = attached_projects[:request.projects_per_skill]

                if compact_courses and compact_projects:
                    learning_action = "learn_and_practice"
                elif compact_projects:
                    learning_action = "practice_only"
                else:
                    learning_action = "learn_only"

                if status == "next":
                    reason = (
                        f"{s_name} is required for {career_title} and all prerequisites are met. "
                        f"It is currently your highest-priority recommended learning step."
                    )
                else:
                    locked_prereqs = [
                        self.skills_dict.get(p, {}).get("skill_name", p)
                        for p in predecessor_ids if p not in user_skill_ids
                    ]
                    reason = (
                        f"{s_name} is locked because the following prerequisite(s) are incomplete: "
                        f"{', '.join(locked_prereqs)}."
                    )
            else:
                reason = f"{s_name} is already present in your current skill profile."
                learning_action = "none"

            flow_data = ReactFlowData(
                label=s_name,
                status=status,
                priority=priority,
                reason=reason,
                learning_action=learning_action
            )

            node = RoadmapNode(
                id=f"skill-{sid}",
                skill_id=sid,
                skill_name=s_name,
                status=status,
                priority=priority,
                sequence=idx,
                prerequisites=predecessor_ids,
                courses=compact_courses,
                projects=compact_projects,
                data=flow_data
            )
            nodes.append(node)

        # 9. React Flow Edges
        edges: List[RoadmapEdge] = []
        for u, v in G_sub.edges():
            edges.append(RoadmapEdge(
                id=f"edge-{u}-{v}",
                source=f"skill-{u}",
                target=f"skill-{v}",
                relationship="prerequisite"
            ))

        # 10. Summary Metrics & Career Readiness Score
        total_skills = len(topo_order)
        required_career_count = len(career_skills_map) if career_skills_map else total_skills
        completed_required = sum(1 for sid in career_skills_map if sid in user_skill_ids)

        critical_career_skills = [sid for sid, imp in career_skills_map.items() if imp == "Critical"]
        completed_critical = sum(1 for sid in critical_career_skills if sid in user_skill_ids)

        prereq_skills = [sid for sid in topo_order if sid not in career_skills_map]
        completed_prereqs = sum(1 for sid in prereq_skills if sid in user_skill_ids)

        req_ratio = (completed_required / required_career_count) if required_career_count > 0 else 1.0
        crit_ratio = (completed_critical / len(critical_career_skills)) if critical_career_skills else req_ratio
        prereq_ratio = (completed_prereqs / len(prereq_skills)) if prereq_skills else 1.0

        # Documented Readiness Formula: 0.60 * req + 0.25 * crit + 0.15 * prereq
        readiness_score = min(100.0, max(0.0, (0.60 * req_ratio + 0.25 * crit_ratio + 0.15 * prereq_ratio) * 100.0))
        progress_percentage = (completed_count / total_skills * 100.0) if total_skills > 0 else 100.0

        summary = RoadmapSummary(
            total_required_skills=total_skills,
            completed_skills=completed_count,
            remaining_skills=remaining_count,
            progress_percentage=round(progress_percentage, 1),
            critical_skills_remaining=critical_remaining,
            career_readiness_score=round(readiness_score, 1)
        )

        return RoadmapResponse(
            career=CareerBrief(
                career_id=career_id,
                career_title=career_title
            ),
            summary=summary,
            nodes=nodes,
            edges=edges,
            warnings=warnings
        )

    def _get_relevant_courses_weighted(
        self, skill_id: str, career_title: str, difficulty_pref: str, completed_clean: Set[str]
    ) -> List[CompactCourse]:
        """Calculates multi-factored weighted course relevance score and applies quality threshold."""
        skill_info = self.skills_dict.get(skill_id, {})
        target_skill_name = skill_info.get("skill_name", "").lower()

        relevant: List[CompactCourse] = []

        for crs in self.courses_list:
            crs_skills = crs.get("skills") or []
            if skill_id not in crs_skills:
                continue

            c_name = crs.get("course_name", "")
            if c_name.lower().strip() in completed_clean:
                continue

            c_desc = (crs.get("description") or "").lower()
            c_diff = crs.get("difficulty") or "Intermediate"
            rating = float(crs.get("rating") or 0.0)

            # 1. Skill Similarity (0 - 1.0)
            skill_sim = 1.0 if target_skill_name in c_name.lower() or target_skill_name in c_desc else 0.70

            # 2. Career Relevance (0 - 1.0)
            career_rel = 1.0 if career_title.lower() in c_name.lower() or career_title.lower() in c_desc else 0.80

            # 3. Difficulty Match (0 - 1.0)
            if difficulty_pref.lower() == "any level" or c_diff.lower() == difficulty_pref.lower():
                diff_match = 1.0
            else:
                diff_match = 0.70

            # 4. Topic Match (0 - 1.0)
            topic_match = 0.90 if any(k in c_name.lower() for k in target_skill_name.split()) else 0.60

            # 5. Rating Score (0 - 1.0)
            rating_score = min(1.0, rating / 5.0) if rating > 0 else 0.70

            # 6. Prerequisite Alignment (0 - 1.0)
            prereq_align = 0.85

            # Weighted Formula:
            # course_score = 0.35 * skill_sim + 0.20 * career_rel + 0.15 * diff_match + 0.15 * topic_match + 0.10 * rating_score + 0.05 * prereq_align
            course_score = (
                0.35 * skill_sim +
                0.20 * career_rel +
                0.15 * diff_match +
                0.15 * topic_match +
                0.10 * rating_score +
                0.05 * prereq_align
            )

            # Minimum quality threshold: MIN_COURSE_RELEVANCE = 0.70
            if course_score < self.MIN_COURSE_RELEVANCE:
                continue

            compact = CompactCourse(
                course_id=crs["course_id"],
                course_name=c_name,
                organization=crs.get("organization") or "Coursera Provider",
                difficulty=c_diff,
                rating=round(rating, 1),
                url=crs.get("url") or "#",
                relevance_score=round(course_score, 4)
            )
            relevant.append(compact)

        relevant.sort(key=lambda x: -x.relevance_score)
        return relevant

    def _get_relevant_projects_weighted(
        self, skill_id: str, career_title: str, difficulty_pref: str
    ) -> List[CompactProject]:
        """Calculates project relevance score based on skill alignment, difficulty, and developed skills."""
        skill_info = self.skills_dict.get(skill_id, {})
        target_skill_name = skill_info.get("skill_name", "").lower()

        relevant: List[CompactProject] = []

        for proj in self.projects_list:
            proj_skills = proj.get("skills") or []
            if skill_id not in proj_skills:
                continue

            p_name = proj.get("project_name", "")
            p_diff = proj.get("difficulty") or "Intermediate"

            diff_score = 1.0 if (difficulty_pref.lower() == "any level" or p_diff.lower() == difficulty_pref.lower()) else 0.70
            skill_align = 1.0 if target_skill_name in p_name.lower() else 0.80

            relevance = 0.50 * diff_score + 0.50 * skill_align

            if relevance < self.MIN_PROJECT_RELEVANCE:
                continue

            skills_developed_names = []
            for sid in proj_skills:
                if sid in self.skills_dict:
                    skills_developed_names.append(self.skills_dict[sid]["skill_name"])

            compact = CompactProject(
                project_id=proj["project_id"],
                project_name=p_name,
                difficulty=p_diff,
                github_url=proj.get("github_url") or "#",
                relevance_score=round(relevance, 4),
                skills_to_develop=skills_developed_names
            )
            relevant.append(compact)

        relevant.sort(key=lambda x: -x.relevance_score)
        return relevant


def generate_roadmap_api(request_data: Dict[str, Any], processed_dir="data/processed", model_dir="model") -> Dict[str, Any]:
    """Helper wrapper API caching a singleton orchestrator."""
    global _global_roadmap_generator
    if _global_roadmap_generator is None:
        _global_roadmap_generator = RoadmapGenerator(processed_dir=processed_dir, model_dir=model_dir)

    req = RoadmapRequest(**request_data)
    res = _global_roadmap_generator.generate_roadmap(req)
    return res.model_dump()

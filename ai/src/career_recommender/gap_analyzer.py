import os

class GapAnalyzer:
    """
    Performs skill gap analysis for a career path, integrating Phase 2
    dependency graph traversal to identify prerequisite gaps.
    """
    def __init__(self, prerequisite_resolver):
        self.resolver = prerequisite_resolver

    def analyze_gaps(self, user_skill_ids, matched_tech, missing_tech):
        """
        Calculates transitive prerequisite gaps for directly missing required skills.
        Returns a dict:
          - 'prerequisite_gaps': list of transitively missing prerequisite skills
          - 'complete_roadmap_path': topological learning order of all missing skills (direct + indirect)
        """
        prereq_gaps_set = set()
        user_set = set(user_skill_ids)
        direct_missing_set = {s["skill_id"] for s in missing_tech}
        
        # 1. Trace required transitive prerequisites for all directly missing technical skills
        if self.resolver is not None:
            for s in missing_tech:
                sid = s["skill_id"]
                # Get transitive required prerequisites
                closures = self.resolver.get_all_prerequisites(sid)
                req_prereqs = [p["skill_id"] for p in closures.get("required", [])]
                
                for p_id in req_prereqs:
                    # If user is missing this prerequisite and it's not a direct required skill itself
                    if p_id not in user_set and p_id not in direct_missing_set:
                        prereq_gaps_set.add(p_id)

        # Build list of prerequisite gap details
        prereq_gaps = []
        for pid in sorted(prereq_gaps_set):
            skill_name = "Unknown Skill"
            if self.resolver and self.resolver.skills:
                skill_name = self.resolver.skills.get(pid, {}).get("skill_name", "Unknown Skill")
            prereq_gaps.append({
                "skill_id": pid,
                "skill_name": skill_name
            })

        # 2. Compute unified topological order of all missing skills (direct + indirect gaps)
        complete_roadmap = []
        if self.resolver is not None:
            all_missing = direct_missing_set.union(prereq_gaps_set)
            # Use resolver to order them topologically
            ordered_missing = self.resolver.resolve_skill_gap(current_skills=list(user_set), target_skills=list(all_missing))
            complete_roadmap = ordered_missing
        else:
            # Fallback direct missing list if resolver is not available
            complete_roadmap = [
                {"skill_id": s["skill_id"], "skill_name": s["skill_name"]} for s in missing_tech
            ]

        return {
            "prerequisite_gaps": prereq_gaps,
            "complete_roadmap_path": complete_roadmap
        }

class ExplanationGenerator:
    """
    Generates structured, evidence-based natural language explanations
    explaining why a career matches the student profile and outlining gaps.
    """
    @staticmethod
    def generate_explanation(career_title, match_score, component_scores,
                             matched_tech, missing_tech, matched_trans, prereqs):
        """
        Produce a cohesive explanation string summarizing technical match,
        interest alignment, and prerequisite gaps.
        """
        # Determine overall fit level
        if match_score >= 85:
            fit_level = "strong"
        elif match_score >= 60:
            fit_level = "good"
        else:
            fit_level = "moderate"

        explanation_parts = []
        
        # 1. Opening summary sentence
        explanation_parts.append(
            f"'{career_title}' is a {fit_level} match ({match_score}%) for your profile."
        )

        # 2. Interest compatibility explanation
        interest_score = component_scores.get("interest", 0.0)
        if interest_score >= 80.0:
            explanation_parts.append(
                f"Your interests align very strongly with this career path."
            )
        elif interest_score >= 50.0:
            explanation_parts.append(
                f"Your interests show moderate alignment with this field."
            )

        # 3. Technical skills explanation
        tech_score = component_scores.get("technical", 0.0)
        if matched_tech:
            matched_names = [s["skill_name"] for s in matched_tech[:3]]
            matched_str = ", ".join(matched_names)
            if len(matched_tech) > 3:
                matched_str += f", and {len(matched_tech) - 3} others"
            explanation_parts.append(
                f"Your existing skills in {matched_str} satisfy key technical requirements (Tech score: {tech_score:.0f}%)."
            )
        else:
            explanation_parts.append(
                "You do not possess any of the direct technical skills currently required for this career."
            )

        # 4. Transferable skills explanation
        if matched_trans:
            matched_t_names = [t["skill_name"] for t in matched_trans[:3]]
            matched_t_str = ", ".join(matched_t_names)
            explanation_parts.append(
                f"You also demonstrate valuable transferable strengths like {matched_t_str}."
            )

        # 5. Gaps explanation
        if missing_tech:
            # Gather critical missing skills
            critical_missing = [s["skill_name"] for s in missing_tech if s["importance"].lower() == "critical"]
            if critical_missing:
                crit_str = ", ".join(critical_missing[:3])
                explanation_parts.append(
                    f"To succeed in this role, your primary learning focus should be on critical missing skills: {crit_str}."
                )
            else:
                missing_names = [s["skill_name"] for s in missing_tech[:3]]
                explanation_parts.append(
                    f"Key technical skills to develop include: {', '.join(missing_names)}."
                )

        # 6. Prerequisite gaps explanation
        if prereqs:
            prereq_names = [p["skill_name"] for p in prereqs[:3]]
            prereq_str = ", ".join(prereq_names)
            if len(prereqs) > 3:
                prereq_str += f", and {len(prereqs) - 3} other foundation skills"
            explanation_parts.append(
                f"Additionally, you have foundational prerequisite gaps to address first, including {prereq_str}."
            )

        return " ".join(explanation_parts)

"""
FastAPI dependency injectors — pull service singletons from app.state.
"""
from fastapi import Request
from app.services.career_service import CareerService
from app.services.skill_gap_service import SkillGapService
from app.services.course_service import CourseService
from app.services.project_service import ProjectService
from app.services.roadmap_service import RoadmapService
from app.services.recommendation_service import RecommendationService


def get_career_service(request: Request) -> CareerService:
    return request.app.state.career_service


def get_gap_service(request: Request) -> SkillGapService:
    return request.app.state.gap_service


def get_course_service(request: Request) -> CourseService:
    return request.app.state.course_service


def get_project_service(request: Request) -> ProjectService:
    return request.app.state.project_service


def get_roadmap_service(request: Request) -> RoadmapService:
    return request.app.state.roadmap_service


def get_recommendation_service(request: Request) -> RecommendationService:
    return request.app.state.recommendation_service

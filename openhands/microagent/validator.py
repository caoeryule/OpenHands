"""Validator for runtime skills creation and updates.

This module provides validation logic for runtime skills to ensure:
- Valid naming conventions
- Appropriate content length
- Correct type-specific requirements
- No malicious content
- No conflicts with existing skills
"""

import re
from typing import Literal

from openhands.core.logger import openhands_logger as logger
from openhands.microagent.types import MicroagentType

# Validation constants
MIN_SKILL_CONTENT_LENGTH = 10  # 10 bytes minimum
MAX_SKILL_CONTENT_LENGTH = 51200  # 50KB maximum
SKILL_NAME_PATTERN = r'^[a-zA-Z0-9_-]+$'

# Potentially dangerous patterns to check in skill content
DANGEROUS_PATTERNS = [
    r'rm\s+-rf',  # Dangerous file deletion
    r'sudo\s+',  # Sudo commands
    r'eval\(',  # Code evaluation
    r'exec\(',  # Code execution
    r'__import__',  # Dynamic imports
    r'subprocess\.',  # Direct subprocess calls in skill content
]


class SkillValidationError(Exception):
    """Exception raised when skill validation fails."""
    
    def __init__(self, message: str, field: str | None = None):
        self.message = message
        self.field = field
        super().__init__(self.message)


class SkillValidator:
    """Validator for runtime skills."""
    
    @staticmethod
    def validate_skill_name(name: str) -> None:
        """Validate skill name follows naming conventions.
        
        Args:
            name: The skill name to validate
            
        Raises:
            SkillValidationError: If name is invalid
        """
        if not name:
            raise SkillValidationError("Skill name cannot be empty", field="name")
        
        if len(name) < 2:
            raise SkillValidationError(
                "Skill name must be at least 2 characters long", field="name"
            )
        
        if len(name) > 100:
            raise SkillValidationError(
                "Skill name cannot exceed 100 characters", field="name"
            )
        
        if not re.match(SKILL_NAME_PATTERN, name):
            raise SkillValidationError(
                "Skill name must contain only letters, numbers, hyphens, and underscores",
                field="name"
            )
        
        # Reserved names check
        reserved_names = ['repo', 'repo_legacy', 'cursorrules', 'agents']
        if name.lower() in reserved_names:
            raise SkillValidationError(
                f"Skill name '{name}' is reserved and cannot be used",
                field="name"
            )
    
    @staticmethod
    def validate_content(content: str) -> None:
        """Validate skill content length and safety.
        
        Args:
            content: The skill content to validate
            
        Raises:
            SkillValidationError: If content is invalid or unsafe
        """
        if not content:
            raise SkillValidationError("Skill content cannot be empty", field="content")
        
        content_length = len(content.encode('utf-8'))
        
        if content_length < MIN_SKILL_CONTENT_LENGTH:
            raise SkillValidationError(
                f"Skill content is too short (minimum {MIN_SKILL_CONTENT_LENGTH} bytes)",
                field="content"
            )
        
        if content_length > MAX_SKILL_CONTENT_LENGTH:
            raise SkillValidationError(
                f"Skill content is too large (maximum {MAX_SKILL_CONTENT_LENGTH} bytes, {MAX_SKILL_CONTENT_LENGTH // 1024}KB)",
                field="content"
            )
        
        # Check for dangerous patterns
        SkillValidator._check_dangerous_content(content)
    
    @staticmethod
    def _check_dangerous_content(content: str) -> None:
        """Check for potentially dangerous patterns in skill content.
        
        Args:
            content: The content to check
            
        Raises:
            SkillValidationError: If dangerous patterns are found
        """
        content_lower = content.lower()
        
        for pattern in DANGEROUS_PATTERNS:
            if re.search(pattern, content_lower, re.IGNORECASE):
                logger.warning(f"Potentially dangerous pattern detected in skill content: {pattern}")
                # Don't block, but warn
                # In production, you might want to be more strict
    
    @staticmethod
    def validate_triggers(
        triggers: list[str],
        skill_type: Literal['knowledge', 'repo', 'task']
    ) -> None:
        """Validate trigger keywords for knowledge and task skills.
        
        Args:
            triggers: List of trigger keywords
            skill_type: Type of the skill
            
        Raises:
            SkillValidationError: If triggers are invalid for the skill type
        """
        if skill_type == 'repo':
            # Repository skills should not have triggers
            if triggers:
                raise SkillValidationError(
                    "Repository skills cannot have triggers",
                    field="triggers"
                )
            return
        
        if skill_type in ['knowledge', 'task']:
            # Knowledge and task skills must have at least one trigger
            if not triggers or len(triggers) == 0:
                raise SkillValidationError(
                    f"{skill_type.capitalize()} skills must have at least one trigger",
                    field="triggers"
                )
            
            # Validate each trigger
            for trigger in triggers:
                if not trigger or not trigger.strip():
                    raise SkillValidationError(
                        "Trigger keyword cannot be empty",
                        field="triggers"
                    )
                
                if len(trigger) > 100:
                    raise SkillValidationError(
                        f"Trigger keyword '{trigger}' is too long (max 100 characters)",
                        field="triggers"
                    )
            
            # For task skills, check trigger format
            if skill_type == 'task':
                # At least one trigger should start with /
                has_command_trigger = any(t.startswith('/') for t in triggers)
                if not has_command_trigger:
                    # Automatically add / to the first trigger if not present
                    logger.info(f"Task skill triggers should start with /. Adding / to first trigger.")
    
    @staticmethod
    def validate_skill_type(skill_type: str) -> Literal['knowledge', 'repo', 'task']:
        """Validate and normalize skill type.
        
        Args:
            skill_type: The skill type to validate
            
        Returns:
            Normalized skill type
            
        Raises:
            SkillValidationError: If skill type is invalid
        """
        valid_types = ['knowledge', 'repo', 'task']
        
        if not skill_type:
            raise SkillValidationError("Skill type cannot be empty", field="type")
        
        normalized_type = skill_type.lower()
        
        if normalized_type not in valid_types:
            raise SkillValidationError(
                f"Invalid skill type '{skill_type}'. Must be one of: {', '.join(valid_types)}",
                field="type"
            )
        
        return normalized_type  # type: ignore
    
    @staticmethod
    def check_name_conflict(
        name: str,
        existing_skills: dict[str, tuple[object, str]]
    ) -> None:
        """Check if a skill name conflicts with existing skills.
        
        Args:
            name: The skill name to check
            existing_skills: Dictionary of existing skills with their sources
            
        Raises:
            SkillValidationError: If there's a conflict with an existing skill
        """
        if name in existing_skills:
            skill, source = existing_skills[name]
            if source == 'runtime':
                raise SkillValidationError(
                    f"A runtime skill named '{name}' already exists",
                    field="name"
                )
            else:
                # Allow overriding non-runtime skills
                logger.info(
                    f"Runtime skill '{name}' will override existing {source} skill"
                )
    
    @staticmethod
    def validate_skill(
        name: str,
        content: str,
        skill_type: str,
        triggers: list[str] | None = None,
        existing_skills: dict[str, tuple[object, str]] | None = None,
    ) -> tuple[str, Literal['knowledge', 'repo', 'task'], list[str]]:
        """Validate all aspects of a skill.
        
        Args:
            name: Skill name
            content: Skill content
            skill_type: Type of skill
            triggers: Trigger keywords (optional)
            existing_skills: Dictionary of existing skills (optional)
            
        Returns:
            Tuple of (validated_name, validated_type, validated_triggers)
            
        Raises:
            SkillValidationError: If validation fails
        """
        # Validate individual components
        SkillValidator.validate_skill_name(name)
        SkillValidator.validate_content(content)
        validated_type = SkillValidator.validate_skill_type(skill_type)
        
        # Normalize triggers
        validated_triggers = triggers if triggers else []
        SkillValidator.validate_triggers(validated_triggers, validated_type)
        
        # Check for conflicts if existing skills provided
        if existing_skills is not None:
            SkillValidator.check_name_conflict(name, existing_skills)
        
        logger.info(f"Skill validation passed for '{name}' (type: {validated_type})")
        
        return name, validated_type, validated_triggers

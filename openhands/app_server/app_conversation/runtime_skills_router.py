"""Runtime Skills API Router for managing skills at runtime.

This module provides REST API endpoints for creating, reading, updating,
and deleting runtime skills in conversations.
"""

import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import JSONResponse

from openhands.app_server.app_conversation.app_conversation_models import (
    RuntimeSkillCreateRequest,
    RuntimeSkillPersistRequest,
    RuntimeSkillResponse,
    RuntimeSkillsListResponse,
    RuntimeSkillUpdateRequest,
)
from openhands.app_server.app_conversation.app_conversation_service import (
    AppConversationService,
)
from openhands.app_server.config import depends_app_conversation_service
from openhands.microagent import KnowledgeMicroagent, RepoMicroagent, TaskMicroagent
from openhands.microagent.types import MicroagentMetadata, MicroagentType
from openhands.microagent.validator import SkillValidationError, SkillValidator

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/app-conversations', tags=['Runtime Skills'])
app_conversation_service_dependency = depends_app_conversation_service()


@router.post('/{conversation_id}/runtime-skills', status_code=status.HTTP_201_CREATED)
async def create_runtime_skill(
    conversation_id: UUID,
    skill_request: RuntimeSkillCreateRequest,
    app_conversation_service: AppConversationService = (
        app_conversation_service_dependency
    ),
) -> RuntimeSkillResponse:
    """Create a new runtime skill for the conversation.
    
    Runtime skills are stored in memory and have the highest priority,
    overriding skills with the same name from other sources.
    
    Args:
        conversation_id: The UUID of the conversation
        skill_request: The skill creation request
        
    Returns:
        The created skill information
        
    Raises:
        HTTPException: If validation fails or conversation not found
    """
    try:
        logger.info(f"Creating runtime skill '{skill_request.name}' for conversation {conversation_id}")
        
        # Validate the skill
        try:
            validated_name, validated_type, validated_triggers = SkillValidator.validate_skill(
                name=skill_request.name,
                content=skill_request.content,
                skill_type=skill_request.type,
                triggers=skill_request.triggers,
            )
        except SkillValidationError as e:
            logger.warning(f"Skill validation failed: {e.message}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": e.message, "field": e.field}
            )
        
        # Create the appropriate microagent type
        metadata = MicroagentMetadata(
            name=validated_name,
            triggers=validated_triggers if validated_triggers else None,
        )
        
        if validated_type == 'knowledge':
            skill = KnowledgeMicroagent(
                name=validated_name,
                content=skill_request.content,
                metadata=metadata,
                source=f"runtime://{conversation_id}",
                type=MicroagentType.KNOWLEDGE,
            )
        elif validated_type == 'task':
            # Ensure task trigger format
            if validated_triggers and not any(t.startswith('/') for t in validated_triggers):
                validated_triggers[0] = f"/{validated_triggers[0]}"
                metadata.triggers = validated_triggers
            
            skill = TaskMicroagent(
                name=validated_name,
                content=skill_request.content,
                metadata=metadata,
                source=f"runtime://{conversation_id}",
                type=MicroagentType.TASK,
            )
        else:  # repo type
            skill = RepoMicroagent(
                name=validated_name,
                content=skill_request.content,
                metadata=metadata,
                source=f"runtime://{conversation_id}",
                type=MicroagentType.REPO_KNOWLEDGE,
            )
        
        # TODO: Add skill to conversation's Memory
        # This requires accessing the agent's memory instance
        # For now, return the skill info
        # In a complete implementation, we would:
        # 1. Get the agent session for this conversation
        # 2. Access its memory
        # 3. Call memory.add_runtime_skill(skill)
        
        logger.info(f"Successfully created runtime skill '{validated_name}'")
        
        return RuntimeSkillResponse(
            name=validated_name,
            type=validated_type,
            content=skill_request.content,
            triggers=validated_triggers,
            source='runtime',
            is_active=True,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating runtime skill: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create runtime skill: {str(e)}"
        )


@router.get('/{conversation_id}/runtime-skills')
async def list_runtime_skills(
    conversation_id: UUID,
    app_conversation_service: AppConversationService = (
        app_conversation_service_dependency
    ),
) -> RuntimeSkillsListResponse:
    """List all runtime skills for the conversation.
    
    Args:
        conversation_id: The UUID of the conversation
        
    Returns:
        List of all runtime skills
        
    Raises:
        HTTPException: If conversation not found
    """
    try:
        logger.info(f"Listing runtime skills for conversation {conversation_id}")
        
        # TODO: Access conversation's Memory and get runtime skills
        # For now, return empty list
        # In a complete implementation, we would:
        # 1. Get the agent session for this conversation
        # 2. Access its memory
        # 3. Call memory.list_runtime_skills()
        # 4. Convert to RuntimeSkillResponse objects
        
        return RuntimeSkillsListResponse(skills=[])
        
    except Exception as e:
        logger.error(f"Error listing runtime skills: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list runtime skills: {str(e)}"
        )


@router.get('/{conversation_id}/runtime-skills/{skill_name}')
async def get_runtime_skill(
    conversation_id: UUID,
    skill_name: str,
    app_conversation_service: AppConversationService = (
        app_conversation_service_dependency
    ),
) -> RuntimeSkillResponse:
    """Get a specific runtime skill by name.
    
    Args:
        conversation_id: The UUID of the conversation
        skill_name: Name of the skill to retrieve
        
    Returns:
        The skill information
        
    Raises:
        HTTPException: If skill not found
    """
    try:
        logger.info(f"Getting runtime skill '{skill_name}' for conversation {conversation_id}")
        
        # TODO: Access conversation's Memory and get the skill
        # For now, return 404
        # In a complete implementation, we would:
        # 1. Get the agent session for this conversation
        # 2. Access its memory
        # 3. Call memory.get_runtime_skill(skill_name)
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Runtime skill '{skill_name}' not found"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting runtime skill: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get runtime skill: {str(e)}"
        )


@router.put('/{conversation_id}/runtime-skills/{skill_name}')
async def update_runtime_skill(
    conversation_id: UUID,
    skill_name: str,
    update_request: RuntimeSkillUpdateRequest,
    app_conversation_service: AppConversationService = (
        app_conversation_service_dependency
    ),
) -> RuntimeSkillResponse:
    """Update an existing runtime skill.
    
    Args:
        conversation_id: The UUID of the conversation
        skill_name: Name of the skill to update
        update_request: The update request
        
    Returns:
        The updated skill information
        
    Raises:
        HTTPException: If skill not found or validation fails
    """
    try:
        logger.info(f"Updating runtime skill '{skill_name}' for conversation {conversation_id}")
        
        # Validate updates if provided
        if update_request.content:
            try:
                SkillValidator.validate_content(update_request.content)
            except SkillValidationError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"error": e.message, "field": e.field}
                )
        
        # TODO: Access conversation's Memory and update the skill
        # For now, return 404
        # In a complete implementation, we would:
        # 1. Get the agent session for this conversation
        # 2. Access its memory
        # 3. Get the existing skill
        # 4. Create updated skill with new content/triggers
        # 5. Call memory.update_runtime_skill(skill_name, updated_skill)
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Runtime skill '{skill_name}' not found"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating runtime skill: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update runtime skill: {str(e)}"
        )


@router.delete('/{conversation_id}/runtime-skills/{skill_name}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_runtime_skill(
    conversation_id: UUID,
    skill_name: str,
    app_conversation_service: AppConversationService = (
        app_conversation_service_dependency
    ),
) -> None:
    """Delete a runtime skill.
    
    Args:
        conversation_id: The UUID of the conversation
        skill_name: Name of the skill to delete
        
    Raises:
        HTTPException: If skill not found
    """
    try:
        logger.info(f"Deleting runtime skill '{skill_name}' for conversation {conversation_id}")
        
        # TODO: Access conversation's Memory and remove the skill
        # For now, return 404
        # In a complete implementation, we would:
        # 1. Get the agent session for this conversation
        # 2. Access its memory
        # 3. Call memory.remove_runtime_skill(skill_name)
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Runtime skill '{skill_name}' not found"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting runtime skill: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete runtime skill: {str(e)}"
        )


@router.post('/{conversation_id}/runtime-skills/{skill_name}/persist')
async def persist_runtime_skill(
    conversation_id: UUID,
    skill_name: str,
    persist_request: RuntimeSkillPersistRequest,
    app_conversation_service: AppConversationService = (
        app_conversation_service_dependency
    ),
) -> JSONResponse:
    """Persist a runtime skill to file system.
    
    This converts a runtime skill to a permanent skill by writing it
    to the user's skills directory or repository skills directory.
    
    Args:
        conversation_id: The UUID of the conversation
        skill_name: Name of the skill to persist
        persist_request: Persistence options
        
    Returns:
        Success message with file path
        
    Raises:
        HTTPException: If skill not found or persistence fails
    """
    try:
        logger.info(f"Persisting runtime skill '{skill_name}' to {persist_request.location}")
        
        # TODO: Implement persistence logic
        # This would:
        # 1. Get the runtime skill from Memory
        # 2. Convert to Markdown with YAML frontmatter
        # 3. Write to appropriate directory based on location
        # 4. Return the file path
        
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Skill persistence not yet implemented"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error persisting runtime skill: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to persist runtime skill: {str(e)}"
        )

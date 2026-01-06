"""Unit tests for skill validator."""

import pytest

from openhands.microagent.validator import SkillValidationError, SkillValidator


class TestSkillNameValidation:
    """Tests for skill name validation."""
    
    def test_valid_skill_name(self):
        """Test validation of valid skill names."""
        # These should not raise exceptions
        SkillValidator.validate_skill_name('valid-name')
        SkillValidator.validate_skill_name('valid_name')
        SkillValidator.validate_skill_name('valid123')
        SkillValidator.validate_skill_name('ValidName')
    
    def test_empty_name(self):
        """Test that empty names are rejected."""
        with pytest.raises(SkillValidationError) as exc_info:
            SkillValidator.validate_skill_name('')
        assert 'cannot be empty' in str(exc_info.value)
    
    def test_name_too_short(self):
        """Test that names too short are rejected."""
        with pytest.raises(SkillValidationError) as exc_info:
            SkillValidator.validate_skill_name('a')
        assert 'at least 2 characters' in str(exc_info.value)
    
    def test_name_too_long(self):
        """Test that names too long are rejected."""
        long_name = 'a' * 101
        with pytest.raises(SkillValidationError) as exc_info:
            SkillValidator.validate_skill_name(long_name)
        assert 'cannot exceed 100 characters' in str(exc_info.value)
    
    def test_invalid_characters(self):
        """Test that invalid characters are rejected."""
        with pytest.raises(SkillValidationError) as exc_info:
            SkillValidator.validate_skill_name('invalid name!')
        assert 'letters, numbers, hyphens, and underscores' in str(exc_info.value)
        
        with pytest.raises(SkillValidationError):
            SkillValidator.validate_skill_name('invalid@name')
        
        with pytest.raises(SkillValidationError):
            SkillValidator.validate_skill_name('invalid.name')
    
    def test_reserved_names(self):
        """Test that reserved names are rejected."""
        reserved = ['repo', 'repo_legacy', 'cursorrules', 'agents']
        for name in reserved:
            with pytest.raises(SkillValidationError) as exc_info:
                SkillValidator.validate_skill_name(name)
            assert 'reserved' in str(exc_info.value)
        
        # Test case-insensitive
        with pytest.raises(SkillValidationError):
            SkillValidator.validate_skill_name('REPO')


class TestContentValidation:
    """Tests for skill content validation."""
    
    def test_valid_content(self):
        """Test validation of valid content."""
        content = 'This is valid skill content with enough characters.'
        SkillValidator.validate_content(content)
    
    def test_empty_content(self):
        """Test that empty content is rejected."""
        with pytest.raises(SkillValidationError) as exc_info:
            SkillValidator.validate_content('')
        assert 'cannot be empty' in str(exc_info.value)
    
    def test_content_too_short(self):
        """Test that content too short is rejected."""
        with pytest.raises(SkillValidationError) as exc_info:
            SkillValidator.validate_content('short')
        assert 'too short' in str(exc_info.value)
    
    def test_content_too_large(self):
        """Test that content too large is rejected."""
        # Create content larger than 50KB
        large_content = 'a' * (51 * 1024)
        with pytest.raises(SkillValidationError) as exc_info:
            SkillValidator.validate_content(large_content)
        assert 'too large' in str(exc_info.value)
    
    def test_dangerous_patterns_warning(self):
        """Test that dangerous patterns trigger warnings but don't block."""
        # These should not raise exceptions (only warnings)
        content_with_rm = 'Never use rm -rf / in production'
        SkillValidator.validate_content(content_with_rm)
        
        content_with_sudo = 'Use sudo carefully in scripts'
        SkillValidator.validate_content(content_with_sudo)


class TestTriggersValidation:
    """Tests for trigger keywords validation."""
    
    def test_knowledge_skill_needs_triggers(self):
        """Test that knowledge skills must have triggers."""
        with pytest.raises(SkillValidationError) as exc_info:
            SkillValidator.validate_triggers([], 'knowledge')
        assert 'must have at least one trigger' in str(exc_info.value)
    
    def test_task_skill_needs_triggers(self):
        """Test that task skills must have triggers."""
        with pytest.raises(SkillValidationError) as exc_info:
            SkillValidator.validate_triggers([], 'task')
        assert 'must have at least one trigger' in str(exc_info.value)
    
    def test_repo_skill_no_triggers(self):
        """Test that repo skills cannot have triggers."""
        with pytest.raises(SkillValidationError) as exc_info:
            SkillValidator.validate_triggers(['trigger'], 'repo')
        assert 'cannot have triggers' in str(exc_info.value)
    
    def test_valid_triggers(self):
        """Test validation of valid triggers."""
        triggers = ['python', 'best practices', 'coding']
        SkillValidator.validate_triggers(triggers, 'knowledge')
    
    def test_empty_trigger_string(self):
        """Test that empty trigger strings are rejected."""
        with pytest.raises(SkillValidationError) as exc_info:
            SkillValidator.validate_triggers(['valid', '', 'another'], 'knowledge')
        assert 'cannot be empty' in str(exc_info.value)
    
    def test_trigger_too_long(self):
        """Test that triggers too long are rejected."""
        long_trigger = 'a' * 101
        with pytest.raises(SkillValidationError) as exc_info:
            SkillValidator.validate_triggers([long_trigger], 'knowledge')
        assert 'too long' in str(exc_info.value)


class TestSkillTypeValidation:
    """Tests for skill type validation."""
    
    def test_valid_types(self):
        """Test validation of valid skill types."""
        assert SkillValidator.validate_skill_type('knowledge') == 'knowledge'
        assert SkillValidator.validate_skill_type('repo') == 'repo'
        assert SkillValidator.validate_skill_type('task') == 'task'
    
    def test_case_insensitive(self):
        """Test that type validation is case-insensitive."""
        assert SkillValidator.validate_skill_type('KNOWLEDGE') == 'knowledge'
        assert SkillValidator.validate_skill_type('Repo') == 'repo'
        assert SkillValidator.validate_skill_type('TaSk') == 'task'
    
    def test_invalid_type(self):
        """Test that invalid types are rejected."""
        with pytest.raises(SkillValidationError) as exc_info:
            SkillValidator.validate_skill_type('invalid')
        assert 'Invalid skill type' in str(exc_info.value)
    
    def test_empty_type(self):
        """Test that empty type is rejected."""
        with pytest.raises(SkillValidationError) as exc_info:
            SkillValidator.validate_skill_type('')
        assert 'cannot be empty' in str(exc_info.value)


class TestConflictCheck:
    """Tests for skill name conflict checking."""
    
    def test_no_conflict(self):
        """Test that non-conflicting names pass."""
        existing = {
            'existing-skill': (object(), 'global')
        }
        # Should not raise
        SkillValidator.check_name_conflict('new-skill', existing)
    
    def test_conflict_with_runtime_skill(self):
        """Test that conflicts with runtime skills are rejected."""
        existing = {
            'existing-skill': (object(), 'runtime')
        }
        with pytest.raises(SkillValidationError) as exc_info:
            SkillValidator.check_name_conflict('existing-skill', existing)
        assert 'already exists' in str(exc_info.value)
    
    def test_override_non_runtime_skill(self):
        """Test that non-runtime skills can be overridden."""
        existing = {
            'existing-skill': (object(), 'global')
        }
        # Should not raise, just log info
        SkillValidator.check_name_conflict('existing-skill', existing)


class TestCompleteSkillValidation:
    """Tests for complete skill validation."""
    
    def test_valid_knowledge_skill(self):
        """Test validation of a complete valid knowledge skill."""
        name, skill_type, triggers = SkillValidator.validate_skill(
            name='python-best-practices',
            content='Here are some Python best practices for writing clean code...',
            skill_type='knowledge',
            triggers=['python', 'best practices', 'pep8']
        )
        
        assert name == 'python-best-practices'
        assert skill_type == 'knowledge'
        assert triggers == ['python', 'best practices', 'pep8']
    
    def test_valid_repo_skill(self):
        """Test validation of a complete valid repo skill."""
        name, skill_type, triggers = SkillValidator.validate_skill(
            name='repo-guidelines',
            content='This repository follows specific coding guidelines...',
            skill_type='repo',
            triggers=[]
        )
        
        assert name == 'repo-guidelines'
        assert skill_type == 'repo'
        assert triggers == []
    
    def test_valid_task_skill(self):
        """Test validation of a complete valid task skill."""
        name, skill_type, triggers = SkillValidator.validate_skill(
            name='code-review',
            content='Perform a code review on the specified file...',
            skill_type='task',
            triggers=['/code-review', '/review']
        )
        
        assert name == 'code-review'
        assert skill_type == 'task'
        assert '/code-review' in triggers
    
    def test_invalid_name_fails_complete_validation(self):
        """Test that invalid name fails complete validation."""
        with pytest.raises(SkillValidationError):
            SkillValidator.validate_skill(
                name='invalid name!',
                content='Valid content here...',
                skill_type='knowledge',
                triggers=['test']
            )
    
    def test_invalid_content_fails_complete_validation(self):
        """Test that invalid content fails complete validation."""
        with pytest.raises(SkillValidationError):
            SkillValidator.validate_skill(
                name='valid-name',
                content='short',
                skill_type='knowledge',
                triggers=['test']
            )
    
    def test_invalid_type_fails_complete_validation(self):
        """Test that invalid type fails complete validation."""
        with pytest.raises(SkillValidationError):
            SkillValidator.validate_skill(
                name='valid-name',
                content='Valid content here...',
                skill_type='invalid',
                triggers=['test']
            )
    
    def test_missing_triggers_fails_for_knowledge_skill(self):
        """Test that missing triggers fails for knowledge skills."""
        with pytest.raises(SkillValidationError):
            SkillValidator.validate_skill(
                name='valid-name',
                content='Valid content here...',
                skill_type='knowledge',
                triggers=[]
            )
    
    def test_triggers_fail_for_repo_skill(self):
        """Test that triggers fail for repo skills."""
        with pytest.raises(SkillValidationError):
            SkillValidator.validate_skill(
                name='valid-name',
                content='Valid content here...',
                skill_type='repo',
                triggers=['invalid']
            )

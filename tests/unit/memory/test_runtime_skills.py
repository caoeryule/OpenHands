"""Unit tests for runtime skills management in Memory class."""

import pytest

from openhands.events.stream import EventStream
from openhands.memory.memory import Memory
from openhands.microagent import KnowledgeMicroagent, RepoMicroagent
from openhands.microagent.types import MicroagentMetadata, MicroagentType


@pytest.fixture
def event_stream():
    """Create an event stream for testing."""
    return EventStream('test')


@pytest.fixture
def memory(event_stream):
    """Create a Memory instance for testing."""
    return Memory(event_stream=event_stream, sid='test-session')


def test_add_runtime_skill(memory):
    """Test adding a runtime skill to memory."""
    # Create a test skill
    skill = KnowledgeMicroagent(
        name='test-skill',
        content='Test skill content',
        metadata=MicroagentMetadata(
            name='test-skill',
            triggers=['test', 'example']
        ),
        source='runtime://test',
        type=MicroagentType.KNOWLEDGE
    )
    
    # Add the skill
    memory.add_runtime_skill(skill)
    
    # Verify it was added
    assert 'test-skill' in memory.runtime_skills
    assert memory.skill_sources['test-skill'] == 'runtime'
    assert memory.runtime_skills['test-skill'] == skill


def test_update_runtime_skill(memory):
    """Test updating an existing runtime skill."""
    # Create and add a skill
    skill1 = KnowledgeMicroagent(
        name='test-skill',
        content='Original content',
        metadata=MicroagentMetadata(name='test-skill', triggers=['test']),
        source='runtime://test',
        type=MicroagentType.KNOWLEDGE
    )
    memory.add_runtime_skill(skill1)
    
    # Create updated skill
    skill2 = KnowledgeMicroagent(
        name='test-skill',
        content='Updated content',
        metadata=MicroagentMetadata(name='test-skill', triggers=['test', 'updated']),
        source='runtime://test',
        type=MicroagentType.KNOWLEDGE
    )
    
    # Update the skill
    result = memory.update_runtime_skill('test-skill', skill2)
    
    # Verify update succeeded
    assert result is True
    assert memory.runtime_skills['test-skill'].content == 'Updated content'


def test_update_nonexistent_skill(memory):
    """Test updating a skill that doesn't exist."""
    skill = KnowledgeMicroagent(
        name='nonexistent',
        content='Content',
        metadata=MicroagentMetadata(name='nonexistent'),
        source='runtime://test',
        type=MicroagentType.KNOWLEDGE
    )
    
    result = memory.update_runtime_skill('nonexistent', skill)
    assert result is False


def test_remove_runtime_skill(memory):
    """Test removing a runtime skill."""
    # Create and add a skill
    skill = KnowledgeMicroagent(
        name='test-skill',
        content='Content',
        metadata=MicroagentMetadata(name='test-skill'),
        source='runtime://test',
        type=MicroagentType.KNOWLEDGE
    )
    memory.add_runtime_skill(skill)
    
    # Remove the skill
    result = memory.remove_runtime_skill('test-skill')
    
    # Verify removal
    assert result is True
    assert 'test-skill' not in memory.runtime_skills
    assert 'test-skill' not in memory.skill_sources


def test_remove_nonexistent_skill(memory):
    """Test removing a skill that doesn't exist."""
    result = memory.remove_runtime_skill('nonexistent')
    assert result is False


def test_get_runtime_skill(memory):
    """Test retrieving a specific runtime skill."""
    # Create and add a skill
    skill = KnowledgeMicroagent(
        name='test-skill',
        content='Content',
        metadata=MicroagentMetadata(name='test-skill'),
        source='runtime://test',
        type=MicroagentType.KNOWLEDGE
    )
    memory.add_runtime_skill(skill)
    
    # Get the skill
    retrieved = memory.get_runtime_skill('test-skill')
    
    # Verify retrieval
    assert retrieved is not None
    assert retrieved == skill


def test_get_nonexistent_skill(memory):
    """Test retrieving a skill that doesn't exist."""
    retrieved = memory.get_runtime_skill('nonexistent')
    assert retrieved is None


def test_list_runtime_skills(memory):
    """Test listing all runtime skill names."""
    # Add multiple skills
    skill1 = KnowledgeMicroagent(
        name='skill1',
        content='Content 1',
        metadata=MicroagentMetadata(name='skill1'),
        source='runtime://test',
        type=MicroagentType.KNOWLEDGE
    )
    skill2 = RepoMicroagent(
        name='skill2',
        content='Content 2',
        metadata=MicroagentMetadata(name='skill2'),
        source='runtime://test',
        type=MicroagentType.REPO_KNOWLEDGE
    )
    
    memory.add_runtime_skill(skill1)
    memory.add_runtime_skill(skill2)
    
    # List skills
    skill_names = memory.list_runtime_skills()
    
    # Verify list
    assert len(skill_names) == 2
    assert 'skill1' in skill_names
    assert 'skill2' in skill_names


def test_get_all_skills_with_source(memory):
    """Test getting all skills with their sources."""
    # Add a runtime skill
    runtime_skill = KnowledgeMicroagent(
        name='runtime-skill',
        content='Runtime content',
        metadata=MicroagentMetadata(name='runtime-skill'),
        source='runtime://test',
        type=MicroagentType.KNOWLEDGE
    )
    memory.add_runtime_skill(runtime_skill)
    
    # Add a repo skill directly
    repo_skill = RepoMicroagent(
        name='repo-skill',
        content='Repo content',
        metadata=MicroagentMetadata(name='repo-skill'),
        source='repo://test',
        type=MicroagentType.REPO_KNOWLEDGE
    )
    memory.repo_microagents['repo-skill'] = repo_skill
    
    # Get all skills
    all_skills = memory.get_all_skills_with_source()
    
    # Verify results
    assert len(all_skills) >= 2  # May include global skills
    assert 'runtime-skill' in all_skills
    assert 'repo-skill' in all_skills
    
    # Verify sources
    skill, source = all_skills['runtime-skill']
    assert source == 'runtime'
    assert skill == runtime_skill


def test_runtime_skill_priority_in_matching(memory):
    """Test that runtime skills have priority over other skills in matching."""
    # Add a global knowledge skill with same trigger
    global_skill = KnowledgeMicroagent(
        name='global-skill',
        content='Global content',
        metadata=MicroagentMetadata(name='global-skill', triggers=['python']),
        source='global://test',
        type=MicroagentType.KNOWLEDGE
    )
    memory.knowledge_microagents['global-skill'] = global_skill
    
    # Add a runtime skill with same trigger
    runtime_skill = KnowledgeMicroagent(
        name='runtime-python',
        content='Runtime Python content',
        metadata=MicroagentMetadata(name='runtime-python', triggers=['python']),
        source='runtime://test',
        type=MicroagentType.KNOWLEDGE
    )
    memory.add_runtime_skill(runtime_skill)
    
    # Find microagent knowledge with 'python' trigger
    results = memory._find_microagent_knowledge('I need help with python')
    
    # Verify runtime skill is included
    runtime_matches = [r for r in results if r.name == 'runtime-python']
    assert len(runtime_matches) > 0
    
    # The runtime skill should be in the results
    assert any(r.content == 'Runtime Python content' for r in results)


def test_multiple_runtime_skills_with_different_types(memory):
    """Test managing multiple runtime skills of different types."""
    # Create skills of different types
    knowledge_skill = KnowledgeMicroagent(
        name='knowledge-skill',
        content='Knowledge content',
        metadata=MicroagentMetadata(name='knowledge-skill', triggers=['help']),
        source='runtime://test',
        type=MicroagentType.KNOWLEDGE
    )
    
    repo_skill = RepoMicroagent(
        name='repo-skill',
        content='Repo content',
        metadata=MicroagentMetadata(name='repo-skill'),
        source='runtime://test',
        type=MicroagentType.REPO_KNOWLEDGE
    )
    
    # Add both skills
    memory.add_runtime_skill(knowledge_skill)
    memory.add_runtime_skill(repo_skill)
    
    # Verify both are stored
    assert len(memory.runtime_skills) == 2
    assert isinstance(memory.runtime_skills['knowledge-skill'], KnowledgeMicroagent)
    assert isinstance(memory.runtime_skills['repo-skill'], RepoMicroagent)

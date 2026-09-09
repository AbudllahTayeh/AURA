from memory.short_term.redis_store import ShortTermMemoryManager

def test_redis_short_term_store():
    memory = ShortTermMemoryManager()
    mock_state = {"query": "Compare Vector DBs", "status": "in_progress"}
    
    memory.save_session_state("test_session_1", mock_state)
    retrieved = memory.get_session_state("test_session_1")
    
    assert retrieved["query"] == "Compare Vector DBs"
    assert retrieved["status"] == "in_progress"

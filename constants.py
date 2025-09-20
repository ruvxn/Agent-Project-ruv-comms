from types import SimpleNamespace

SYSTEM_MESSAGE_LIST = SimpleNamespace(
    top_k_kb_found_prompt=(
        "User is asking for the question that {user_input}, "
        "based on the knowledge base as below, answer user's question. "
        "kb:{top_k_kb}"
    ),
    top_k_kb_not_found_prompt=("There is no knowledge base available,"
                               "reply user 'No KB Found'"),
    should_use_rag_prompt=("Based on user_input, decide whether should use rag_retrieval",
                           "user_input: {user_input}.Return 'TRUE' if decide to use rag, else return 'FALSE'.",
                           " Answer only 'TRUE' or 'FALSE'")
)

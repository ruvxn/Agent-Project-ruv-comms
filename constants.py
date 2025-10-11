from types import SimpleNamespace

SYSTEM_MESSAGE_LIST = SimpleNamespace(
    top_k_kb_found_prompt=(
        "User asked: {user_input}. Using the knowledge below, "
        "please provide an exact answer if available. "
        "Knowledge: {top_k_kb}"
    ),
    top_k_kb_not_found_prompt=("There is no knowledge base available,"
                               "reply user 'No KB Found'"),

)


SYSTEM_LOG_LIST = SimpleNamespace(
    rag_router_log_template=SimpleNamespace(
        get_collection_exception=(
            "[rag_router] go to chat_agent. get_or_create_summary_collection error: {e}"),
        empty_collection_error=(
            "[rag_router] PDF_SUMMARY_COLLECTION is empty, go to [chat_agent]"),
        rag_retrieval_exception=(
            "[rag_router] [get_embedding] [rag_retrieval_node] error: {e}"),
        no_user_input_error=("[rag_router] No user_input, go to [chat_aget]"),
        successful_log=(
            "[rag_router] go to[rag_agent] top_score: {top_score}; rag_threshold: {RAG_THRESHOLD}"),
        no_kb_log=(
            "[rag_router] There is no revelant kb. Go to [no_answer_agent],top_score: {top_score}; rag_threshold: {RAG_THRESHOLD}"),
        chat_agent_log=(
            "[rag_router] top_score: {top_score} <= 0, go to chat_agent ")
    )
)

SYSTEM_PROMPT_LIST = SimpleNamespace(
    tool_router_prompt=(
        "You are a Tool Router.\n"
        "Available tools: {tool_names}\n"
        "Decide which tool to use based on the user input.\n"
        "Use the tool by calling it directly; do not just return JSON.\n"
        "If no tool is needed, respond naturally to the user.\n"
        "- Respond ONLY with a valid JSON object in this exact format:\n"
        "  {{'tool_name': '<tool_name>', 'args': {{}}}}\n"
        "- Do not include any extra text or explanation.\n"
        "- JSON must be parseable.\n"
    )
)

# In residential care,how many resident deaths in 2022–23
# how many First Nations people using home support were aged under 65
# what is home care

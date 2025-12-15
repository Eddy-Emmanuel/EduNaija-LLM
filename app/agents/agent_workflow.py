from typing import TypedDict

class AgentWorkFlow(TypedDict):
    query:str
    is_question_answered:bool
    final_answer:str
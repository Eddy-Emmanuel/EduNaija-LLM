import os
from langchain_openai import ChatOpenAI
from app.agents.agent_workflow import AgentWorkFlow
from app.model.schema import ResponseVerificationSchema
from app.configurations.accesskeys import accesskeys_config
from app.agents.prompts import main_agent_prompt, verify_agent_prompt

os.environ["OPENAI_API_KEY"] = accesskeys_config.OPENAI_API_KEY

llm_1 = ChatOpenAI(model_name="gpt-5-mini")
llm_2 = ChatOpenAI(model_name="gpt-5-mini")

llm_1_chain = main_agent_prompt | llm_1
llm_2_chain = verify_agent_prompt | llm_2
def EduNaijaAgent(state:AgentWorkFlow):
    response = llm_1_chain.invoke({"USER_INPUT": state["query"]}).content
    


import os
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from app.agents.prompts import main_agent_prompt
from app.configurations.accesskeys import accesskeys_config
from langchain_community.utilities import GoogleSerperAPIWrapper

os.environ["OPENAI_API_KEY"] = accesskeys_config.OPENAI_API_KEY
os.environ["SERPER_API_KEY"] = accesskeys_config.SERPAPI_API_KEY

model = ChatOpenAI(model="gpt-5", temperature=0)
serp_search = GoogleSerperAPIWrapper()
custom_serp_tool = Tool(
    name="web_search",
    description="Search the web for information",
    func=serp_search.run,
)
agent = create_agent(model=model, 
                     tools=[custom_serp_tool], 
                     system_prompt=main_agent_prompt)

# print(agent.invoke(
#     {"messages": [{"role": "user", "content": "whats the current time is lagos?"}]}
# ))

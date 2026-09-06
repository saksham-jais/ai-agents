from langchain_groq import ChatGroq
from dotenv import load_dotenv
import sys
sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

from langchain_community.tools import DuckDuckGoSearchRun
search_tool = DuckDuckGoSearchRun()
results = search_tool.invoke('ipl news')
print(results)




# llm = ChatGroq(model="openai/gpt-oss-20b")

# result = llm.invoke("Write a 5 Line Poem on Cricket")

# print(result.content)
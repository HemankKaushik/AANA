from langgraph.graph import StateGraph
from typing import TypedDict

class State(TypedDict):
    message: str

def hello_node(state: State):
    print("LangGraph is working!")
    return state

graph = StateGraph(State)
graph.add_node("hello", hello_node)
graph.set_entry_point("hello")
graph.set_finish_point("hello")

app = graph.compile()
app.invoke({"message": "test"})

from pydantic import BaseModel
from typing import List, Optional, Dict

class Node(BaseModel):
    id: str
    type: str
    config: Dict

class Edge(BaseModel):
    source: str
    target: str
    condition: Optional[str] = None

class Workflow(BaseModel):
    id: str
    nodes: List[Node]
    edges: List[Edge]

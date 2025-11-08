from fastapi import FastAPI, File, UploadFile
from typing_extensions import Annotated
import uvicorn
from utils import *
from dijkstra import dijkstra
import json
from graph import Graph
from node import Node

# create FastAPI app
app = FastAPI()

# global variable for active graph
active_graph = None

@app.get("/")
async def root():
    return {"message": "Welcome to the Shortest Path Solver!"}


@app.post("/upload_graph_json/")
async def create_upload_file(file: UploadFile):
    global active_graph
    try:
        active_graph = await create_graph_from_json(file)
        return {"Upload Success": file.filename}
    except Exception as e:
        return {"Upload Error": f"Invalid JSON file: {str(e)}"}


@app.get("/solve_shortest_path/start_node_id={start_node_id}&end_node_id={end_node_id}")
async def get_shortest_path(start_node_id: str, end_node_id: str):
    global active_graph
    if not active_graph:
        return {"error": "No graph loaded. Please upload a graph first."}
    
    try:
        # Get the start and end nodes
        if start_node_id not in active_graph.nodes or end_node_id not in active_graph.nodes:
            return {"error": "Invalid start or end node ID."}
            
        start_node = active_graph.nodes[start_node_id]
        
        # Run Dijkstra's algorithm
        graph_result = dijkstra(active_graph, start_node)
        end_node = graph_result.nodes[end_node_id]
        
        # Extract the path from end to start
        if end_node.dist == float('inf'):
            return {"error": f"No path found between {start_node_id} and {end_node_id}"}
            
        # Reconstruct the path
        path = []
        current = end_node
        while current is not None:
            path.append(current.id)
            current = current.prev
            
        # Reverse the path to get it from start to end
        path.reverse()
        
        return {
            "path": path,
            "total_distance": end_node.dist
        }
        
    except Exception as e:
        return {"error": f"Error calculating path: {str(e)}"}

if __name__ == "__main__":
    print("Server is running at http://localhost:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)
    
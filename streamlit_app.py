import math
import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt

warehouse_locations = {
    "receiving_area": (0, 0),
    "storage_a": (2, 1),
    "storage_b": (1, 4),
    "sorting_area": (4, 2),
    "inspection_area": (5, 5),
    "packing_station": (7, 6)
}

warehouse_graph = {
    "receiving_area": {"storage_a": 2.2, "storage_b": 4.1},
    "storage_a": {"sorting_area": 2.2},
    "storage_b": {"inspection_area": 5.0, "sorting_area": 6.0},
    "sorting_area": {"inspection_area": 3.2, "packing_station": 5.0},
    "inspection_area": {"packing_station": 2.2},
    "packing_station": {}
}

airport_locations = {
    "baggage_area": (0, 0),
    "security": (2, 1),
    "checkpoint": (1, 4),
    "food_court": (4, 2),
    "terminal_hall": (5, 5),
    "departure_gate": (8, 6)
}

airport_graph = {
    "baggage_area": {"security": 2.2, "checkpoint": 4.1},
    "security": {"food_court": 2.2},
    "checkpoint": {"terminal_hall": 5.0},
    "food_court": {"terminal_hall": 3.2, "departure_gate": 6.0},
    "terminal_hall": {"departure_gate": 3.2},
    "departure_gate": {}
}


def heuristic(locations, node, goal):
    x1, y1 = locations[node]
    x2, y2 = locations[goal]
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def gbfs(graph, locations, start, goal):
    frontier = [start]
    parent = {start: None}
    visited = []

    while len(frontier) > 0:
        best = frontier[0]
        for node in frontier:
            if heuristic(locations, node, goal) < heuristic(locations, best, goal):
                best = node
        frontier.remove(best)
        visited.append(best)

        if best == goal:
            break

        for neighbor in graph[best]:
            if neighbor not in visited and neighbor not in frontier:
                frontier.append(neighbor)
                parent[neighbor] = best

    if goal not in parent:
        return None, None, visited

    path = []
    node = goal
    while node is not None:
        path.append(node)
        node = parent[node]
    path.reverse()

    cost = 0
    for i in range(len(path) - 1):
        cost = cost + graph[path[i]][path[i + 1]]

    return path, cost, visited


def draw(graph, locations, path, start, goal, visited, title):
    g = nx.DiGraph()
    for node in graph:
        g.add_node(node)
        for neighbor in graph[node]:
            g.add_edge(node, neighbor, weight=graph[node][neighbor])

    path_edges = []
    for i in range(len(path) - 1):
        path_edges.append((path[i], path[i + 1]))

    colors = []
    for node in g.nodes():
        if node == start:
            colors.append("red")
        elif node == goal:
            colors.append("green")
        elif node in visited:
            colors.append("yellow")
        else:
            colors.append("lightblue")

    fig, ax = plt.subplots(figsize=(10, 6))
    nx.draw(g, locations, ax=ax, with_labels=True, node_color=colors, node_size=1800, font_size=8, edge_color="gray")
    nx.draw_networkx_edges(g, locations, ax=ax, edgelist=path_edges, edge_color="red", width=3)
    nx.draw_networkx_edge_labels(g, locations, ax=ax, edge_labels=nx.get_edge_attributes(g, "weight"), font_size=7)
    ax.set_title(title)
    return fig


st.set_page_config(page_title="ai lab 6", layout="wide")
st.title("ai lab 6")
st.write("name: ibrahim ahmed | roll number: 3093")

task = st.radio("select task", ["task 1: warehouse heuristic", "task 2: airport gbfs"])

if task == "task 1: warehouse heuristic":
    st.header("task 1: designing a heuristic for a warehouse robot")
    nodes = list(warehouse_graph.keys())
    goal = st.selectbox("goal node", nodes, index=nodes.index("packing_station"))

    rows = []
    for node in warehouse_locations:
        rows.append({"node": node, "h(n)": round(heuristic(warehouse_locations, node, goal), 2)})
    st.subheader("heuristic values")
    st.table(rows)

    checks = []
    for node in warehouse_graph:
        for neighbor in warehouse_graph[node]:
            hn = heuristic(warehouse_locations, node, goal)
            right = warehouse_graph[node][neighbor] + heuristic(warehouse_locations, neighbor, goal)
            if hn <= right + 0.000001:
                status = "satisfied"
            else:
                status = "violated"
            checks.append({"edge": node + " -> " + neighbor, "h(n)": round(hn, 2), "cost + h(m)": round(right, 2), "status": status})
    st.subheader("condition h(n) <= cost(n, m) + h(m)")
    st.table(checks)

    g = nx.DiGraph()
    for node in warehouse_graph:
        for neighbor in warehouse_graph[node]:
            g.add_edge(node, neighbor, weight=warehouse_graph[node][neighbor])

    if goal == "receiving_area" or not nx.has_path(g, "receiving_area", goal):
        st.warning("no path from receiving_area to " + goal)
    else:
        path = nx.shortest_path(g, "receiving_area", goal, weight="weight")
        cost = nx.shortest_path_length(g, "receiving_area", goal, weight="weight")
        st.write("minimum cost path: " + " -> ".join(path))
        st.write("total cost: " + str(round(cost, 2)))
        st.pyplot(draw(warehouse_graph, warehouse_locations, path, "receiving_area", goal, [], "warehouse robot (red = minimum cost path)"))

else:
    st.header("task 2: greedy best first search for airport baggage handling")
    nodes = list(airport_graph.keys())
    col1, col2 = st.columns(2)
    start = col1.selectbox("start node", nodes, index=nodes.index("baggage_area"))
    goal = col2.selectbox("goal node", nodes, index=nodes.index("departure_gate"))

    if st.button("run gbfs"):
        if start == goal:
            st.warning("start and goal are the same")
        else:
            path, cost, visited = gbfs(airport_graph, airport_locations, start, goal)
            st.write("expansion order: " + " -> ".join(visited))
            if path is None:
                st.error("no path found from " + start + " to " + goal)
            else:
                st.write("solution path: " + " -> ".join(path))
                st.write("total path cost: " + str(round(cost, 2)))
                st.pyplot(draw(airport_graph, airport_locations, path, start, goal, visited, "airport baggage handling - gbfs (red = solution path)"))

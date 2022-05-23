import math
import os
import json

from typing import Optional, List, Tuple

import typer
import networkx as nx

from pyvis.network import Network


app = typer.Typer()


def graph_files(path_to_file):
    folder = os.path.dirname(path_to_file)
    result = set()
    for file in os.listdir(folder):
        if file.endswith(".json"):
            json_file = file[: -5:]
            result.add(json_file)
    return result


def get_path_to_file(graph_name: str):
    path_to_folder = os.path.dirname(os.path.abspath(__file__))
    new_file = ".".join([graph_name, "json"])
    path_to_file = os.path.join(path_to_folder, "graphs", new_file)
    return path_to_file


# @app.command()
def create_file(graph_name: str):
    path_to_file = get_path_to_file(graph_name)
    graphs = graph_files(path_to_file)
    if graph_name not in graphs:
        with open(path_to_file, 'w') as file:
            json.dump({}, file)
            return path_to_file, True
    else:
        return path_to_file, False


def add_data_to_json(path_to_file, data):
    with open(path_to_file, 'w') as file:
        json.dump(data, file, indent=4)


def create_directed(graph_name: str):
    # g = DirectedGraph(graph_name)
    upload_data = {
        "name": graph_name,
        "directed": True,
        "nodes": [],
        "edges": []
    }
    path_to_file, is_created = create_file(graph_name)
    if is_created:
        add_data_to_json(path_to_file, upload_data)


def create_undirected(graph_name: str):
    upload_data = {
        "name": graph_name,
        "directed": False,
        "nodes": [],
        "edges": []
    }
    path_to_file, is_created = create_file(graph_name)
    if is_created:
        add_data_to_json(path_to_file, upload_data)


def return_json_graph(graph_name: str):
    g = read_graph_from_json(graph_name)

    nodes = g['nodes']
    edges = g['edges']

    if g['directed']:
        nx_g = nx.DiGraph()
    else:
        nx_g = nx.Graph()

    nx_g.add_nodes_from(nodes)
    nx_g.add_edges_from(edges)

    return g['name'], nx_g


@app.command()
def add_graph(graph_name: str, directed_graph: Optional[bool] =
                  typer.Option(
                      None,
                      "--directed",
                      "-d",
                      help="Create directed graph"
                  ), undirected_graph: Optional[bool] =
                  typer.Option(
                      None,
                      "--undirected",
                      "-u",
                      help="Create undirected graph"
                  )):
    if directed_graph:
        create_directed(graph_name)
    elif undirected_graph:
        create_undirected(graph_name)
    else:
        typer.echo("error")


def read_graph_from_json(graph_name: str):
    path_to_file = get_path_to_file(graph_name)
    with open(path_to_file) as file:
        graph_dict = json.load(file)
    return graph_dict


@app.command()
def add_node(graph_name: str, node: str):
    graph = read_graph_from_json(graph_name)
    graph["nodes"].append(node)
    path_to_file = get_path_to_file(graph_name)
    add_data_to_json(path_to_file, graph)


@app.command()
def add_edge(graph_name: str, source: str, to: str):
    graph = read_graph_from_json(graph_name)
    graph["edges"].append((source, to))
    path_to_file = get_path_to_file(graph_name)
    add_data_to_json(path_to_file, graph)


def update_graph(name: str, directed: bool, nodes, edges):
    data = {
        "name": name,
        "directed": directed,
        "nodes": list(nodes),
        "edges": list(edges)
    }
    return data


@app.command()
def delete_node(graph_name: str, node: str):
    name, nx_g = return_json_graph(graph_name)

    try:
        nx_g.remove_node(node)

        new_graph = update_graph(name, isinstance(nx_g, nx.DiGraph), nx_g.nodes, nx_g.edges)
        path_to_file = get_path_to_file(graph_name)
        add_data_to_json(path_to_file, new_graph)
    except nx.exception.NetworkXError:
        typer.echo(f"Graph {name} does not contain node {node}")


@app.command()
def delete_edge(graph_name: str, source: str, to: str):
    name, nx_g = return_json_graph(graph_name)

    try:
        nx_g.remove_edge(source, to)

        new_graph = update_graph(name, isinstance(nx_g, nx.DiGraph), nx_g.nodes, nx_g.edges)
        path_to_file = get_path_to_file(graph_name)
        add_data_to_json(path_to_file, new_graph)
    except nx.exception.NetworkXError:
        typer.echo(f"Graph {name} does not contain edge ({source}, {to})")

# hamilton cycle

@app.command()
def relabel_node(graph_name: str, old_name: str, new_name: str):
    name, nx_g = return_json_graph(graph_name)

    mapping = {old_name: new_name}
    nx_g = nx.relabel_nodes(nx_g, mapping)

    new_graph = update_graph(name, isinstance(nx_g, nx.DiGraph), nx_g.nodes, nx_g.edges)
    path_to_file = get_path_to_file(graph_name)
    add_data_to_json(path_to_file, new_graph)


@app.command()
def nodes_amount(graph_name: str):
    g = read_graph_from_json(graph_name)
    typer.echo(f"Graph {g['name']} has {len(g['nodes'])} nodes")


@app.command()
def edges_amount(graph_name: str):
    g = read_graph_from_json(graph_name)
    typer.echo(f"Graph {g['name']} has {len(g['edges'])} edges")


@app.command()
def node_degree(graph_name: str, node: str):
    name, nx_g = return_json_graph(graph_name)

    try:
        typer.echo(f"Node {node} has degree {nx_g.degree[node]}")
    except KeyError:
        typer.echo(f"There is no node {node}")


@app.command()
def graph_degree(graph_name: str):
    name, nx_g = return_json_graph(graph_name)

    graph_degree = 0
    degrees = nx_g.degree
    for node, degree in degrees:
        graph_degree += degree

    typer.echo(f"Graph {name} has degree {graph_degree}")


@app.command()
def is_eulerian(graph_name: str):
    name, nx_g = return_json_graph(graph_name)
    answer = "Yes" if nx.is_eulerian(nx_g) else "No"
    typer.echo(f"Is graph {name} eulerian? --- {answer}")


@app.command()
def hamiltonian_cycle(graph_name: str):
    name, nx_g = return_json_graph(graph_name)
    graph = adjacency_list(nx_g.nodes, nx_g.edges)
    paths = []
    for node in nx_g.nodes:
        path = hamilton(graph, node)
        if path:
            if nx_g.has_edge(path[0], path[-1]):
                typer.echo(path)
                paths.append(path)
    if not paths:
        typer.echo(f'Graph {name} has no hamiltonian cycle')


def hamilton(graph, start):
    size = len(graph)
    to_visit = [None, start]
    path = []
    while to_visit:
        v = to_visit.pop()
        if v:
            path.append(v)
            if len(path) == size:
                break
            for x in set(graph[v]) - set(path):
                to_visit.append(None)
                to_visit.append(x)
        else:
            path.pop()
    return path


@app.command()
def diameter(graph_name: str):
    name, nx_g = return_json_graph(graph_name)
    try:
        d = nx.diameter(nx_g)
        typer.echo(f"Graph {name} has diameter {d}")
    except nx.exception.NetworkXError:
        typer.echo("Can not find graph diameter")


@app.command()
def radius(graph_name: str):
    name, nx_g = return_json_graph(graph_name)
    try:
        r = nx.radius(nx_g)
        typer.echo(f"Graph {name} has radius {r}")
    except nx.exception.NetworkXError:
        typer.echo("Can not find graph radius")


@app.command()
def center(graph_name: str):
    name, nx_g = return_json_graph(graph_name)
    try:
        c = nx.center(nx_g)
        for current_center in c:
            typer.echo(f"Graph {name} has center {current_center}")
    except nx.exception.NetworkXError:
        typer.echo("Can not find graph center")


def make_nodes_names(nodes_list):
    nodes = []
    for node_pair in nodes_list:
        node_name = ",".join([node_pair[0], node_pair[1]])
        nodes.append(node_name)
    return nodes


def make_edges_names(edges_list):
    edges = []
    for edge_list in edges_list:
        source = ",".join([edge_list[0][0], edge_list[0][1]])
        to = ",".join([edge_list[1][0], edge_list[1][1]])
        edges.append([source, to])
    return edges


@app.command()
def cartesian_product(graph1: str, graph2: str, product_name: str):
    name1, nx_g1 = return_json_graph(graph1)
    name2, nx_g2 = return_json_graph(graph2)
    g1_g2 = nx.cartesian_product(nx_g1, nx_g2)

    path_to_file, is_creates = create_file(product_name)
    nodes = make_nodes_names(g1_g2.nodes)
    edges = make_edges_names(g1_g2.edges)

    data = update_graph(product_name, isinstance(g1_g2, nx.DiGraph), nodes, edges)
    add_data_to_json(path_to_file, data)


@app.command()
def tensor_product(graph1: str, graph2: str, product_name: str):
    name1, nx_g1 = return_json_graph(graph1)
    name2, nx_g2 = return_json_graph(graph2)
    g1_g2 = nx.tensor_product(nx_g1, nx_g2)

    path_to_file, is_creates = create_file(product_name)
    nodes = make_nodes_names(g1_g2.nodes)
    edges = make_edges_names(g1_g2.edges)

    data = update_graph(product_name, isinstance(g1_g2, nx.DiGraph), nodes, edges)
    add_data_to_json(path_to_file, data)


@app.command()
def tree(graph_name: str):
    name, nx_g = return_json_graph(graph_name)
    adj_list = adjacency_list(nx_g.nodes, nx_g.edges)
    result = {node: set() for node in adj_list.keys()}
    visited = set()

    tree_name = "-".join([graph_name, "tree"])
    bin_tree = make_tree(adj_list, list(result.items())[0][0], visited, result)

    nodes, edges = nodes_and_values(bin_tree)

    new_graph = update_graph(tree_name, isinstance(nx_g, nx.DiGraph), nodes, edges)
    path_to_file = get_path_to_file(tree_name)
    add_data_to_json(path_to_file, new_graph)


def adjacency_list(nodes, edges):
    edges = sorted(edges)
    result = {node: set() for node in nodes}
    frequency = []
    for edge in edges:
        frequency.extend(list(edge))

    for edge in edges:
        result[edge[0]].add(edge[1])
        result[edge[1]].add(edge[0])

    for key in result.keys():
        result[key] = sorted(list(result[key]), key=frequency.count)

    return result


@app.command()
def binary_tree(graph_name: str):
    name, nx_g = return_json_graph(graph_name)
    adj_list = adjacency_list(nx_g.nodes, nx_g.edges)

    result = {node: set() for node in adj_list.keys()}
    visited = set()

    tree_name = "-".join([graph_name, "binary"])
    bin_tree = make_tree(adj_list, list(result.items())[0][0], visited, result, binary=2)

    nodes, edges = nodes_and_values(bin_tree)
    new_graph = update_graph(tree_name, isinstance(nx_g, nx.DiGraph), nodes, edges)
    path_to_file = get_path_to_file(tree_name)
    add_data_to_json(path_to_file, new_graph)


def nodes_and_values(bin_tree):
    nodes = []
    edges = []

    for key, values in bin_tree.items():
        nodes.append(key)
        for value in values:
            edges.append([key, value])

    return nodes, edges


def make_tree(adj_list, source, visited, result, binary=math.inf):
    for to in adj_list[source]:
        if to not in visited:
            if len(result[source]) < binary:
                result[source].add(to)
                visited.add(source)
                visited.add(to)

    for node in result[source]:
        make_tree(adj_list, node, visited, result, binary=binary)

    return result


def get_html_path(html_name: str):
    path_to_file = os.path.join("", "htmls", html_name)
    return path_to_file


@app.command()
def subgraph(graph_name, nodes: List[str]):
    name, nx_g = return_json_graph(graph_name)
    sub = nx_g.subgraph(nodes)

    sub_name = "-".join([name, "sub"])

    new_graph = update_graph(sub_name, isinstance(nx_g, nx.DiGraph), sub.nodes, sub.edges)
    path_to_file = get_path_to_file(sub_name)
    add_data_to_json(path_to_file, new_graph)


@app.command()
def show_subgraph(graph: str,
                  subgraph: str,
                  html_name: str,
                  subgraph_color: str = 'red',
                  nodes_color: str = 'cyan',
                  edges_color: str = 'blue',
                  stay_this_tab: Optional[bool] = typer.Option(False,
                                                               "-o",
                                                               "--open-new-tab",
                                                               help='Open new tab')
                  ):
    graph_dict = read_graph_from_json(graph)
    subgraph_dict = read_graph_from_json(subgraph)
    nt = Network(height='550xp',
                 width='550xp',
                 directed=graph_dict["directed"],
                 bgcolor='#222222',
                 font_color='white',
                 notebook=not stay_this_tab)
    for node in graph_dict['nodes']:
        if node in subgraph_dict['nodes']:
            nt.add_node(node, color=subgraph_color)
        else:
            nt.add_node(node, color=nodes_color)
    for edge in graph_dict['edges']:
        if edge in subgraph_dict['edges']:
            nt.add_edge(edge[0], edge[1], color=subgraph_color)
        else:
            nt.add_edge(edge[0], edge[1], color=edges_color)
    html_file = get_html_path(html_name)
    # nt.toggle_physics(status=False)
    nt.show(html_file)
    return nt


@app.command()
def change_nodes_color(graph: str,
                  html_name: str,
                  colored_nodes: List[str],
                  node_color: str = 'red',
                  nodes_color: str = 'cyan',
                  edges_color: str = 'blue',
                  stay_this_tab: Optional[bool] = typer.Option(False,
                                                               "-o",
                                                               "--open-new-tab",
                                                               help='Open new tab')
                  ):
    graph_dict = read_graph_from_json(graph)
    nt = Network(height='550xp',
                 width='550xp',
                 directed=graph_dict["directed"],
                 bgcolor='#222222',
                 font_color='white',
                 notebook=not stay_this_tab)
    for node in graph_dict['nodes']:
        if node in colored_nodes:
            nt.add_node(node, color=node_color)
        else:
            nt.add_node(node, color=nodes_color)
    for edge in graph_dict['edges']:
        nt.add_edge(edge[0], edge[1], color=edges_color)
    html_file = get_html_path(html_name)
    # nt.toggle_physics(status=False)
    nt.show(html_file)
    return nt


@app.command()
def change_edges_color(graph: str,
                  html_name: str,
                  colored_edges: List[str],
                  edge_color: str = 'red',
                  nodes_color: str = 'cyan',
                  edges_color: str = 'blue',
                  stay_this_tab: Optional[bool] = typer.Option(False,
                                                               "-o",
                                                               "--open-new-tab",
                                                               help='Open new tab')
                  ):
    source = [colored_edges[i] for i in range(len(colored_edges)) if i % 2 == 0]
    to = [colored_edges[i] for i in range(len(colored_edges)) if i % 2 == 1]
    graph_dict = read_graph_from_json(graph)
    nt = Network(height='550xp',
                 width='550xp',
                 directed=graph_dict["directed"],
                 bgcolor='#222222',
                 font_color='white',
                 notebook=not stay_this_tab)
    for node in graph_dict['nodes']:
        nt.add_node(node, color=nodes_color)
    for edge in graph_dict['edges']:
        if (edge[0], edge[1]) in zip(source, to):
            nt.add_edge(edge[0], edge[1], color=edge_color)
        else:
            nt.add_edge(edge[0], edge[1], color=edges_color)
    html_file = get_html_path(html_name)
    # nt.toggle_physics(status=False)
    nt.show(html_file)
    return nt


@app.command()
def show(graph_name: str,
         html_name: str,
         nodes_color: str = 'cyan',
         edges_color: str = 'blue',
         stay_this_tab: Optional[bool] = typer.Option(False,
                                       "-o",
                                       "--open-new-tab",
                                       help='Open new tab')):
    graph_dict = read_graph_from_json(graph_name)
    nt = Network(height='550xp',
                 width='550xp',
                 directed=graph_dict["directed"],
                 bgcolor='#222222',
                 font_color='white',
                 notebook=not stay_this_tab)
    for node in graph_dict["nodes"]:
        nt.add_node(node, color=nodes_color)
    for edge in graph_dict["edges"]:
        nt.add_edge(edge[0], edge[1], color=edges_color)
    html_file = get_html_path(html_name)
    # nt.toggle_physics(status=False)
    nt.show(html_file)
    return nt


if __name__ == "__main__":
    app()
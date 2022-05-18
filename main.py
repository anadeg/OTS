import os
import json

from typing import Optional

import typer
import networkx as nx

from pyvis.network import Network

from directed_graph_class import DirectedGraph
from undirected_graph_class import UndirectedGraph


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


@app.command()
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
        json.dump(data, file)


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
    # g = UndirectedGraph(graph_name)
    upload_data = {
        "name": graph_name,
        "directed": False,
        "nodes": [],
        "edges": []
    }
    path_to_file, is_created = create_file(graph_name)
    if is_created:
        add_data_to_json(path_to_file, upload_data)


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
    old_graph = read_graph_from_json(graph_name)

    name, is_directed, nodes, edges = list(old_graph.values())
    nx_g = nx.Graph()
    nx_g.add_nodes_from(nodes)
    nx_g.add_edges_from(edges)

    nx_g.remove_node(node)

    new_graph = update_graph(name, is_directed, nx_g.nodes, nx_g.edges)
    path_to_file = get_path_to_file(graph_name)
    add_data_to_json(path_to_file, new_graph)


def get_html_path(html_name: str):
    path_to_file = os.path.join("", "htmls", html_name)
    return path_to_file


@app.command()
def show(graph_name: str,
         html_name: str,
         stay_this_tab: Optional[bool] = typer.Option(False,
                                       "-f",
                                       "--false",
                                       help='Stay on current tab - default (or open new)')):
    graph_dict = read_graph_from_json(graph_name)
    nt = Network(directed=graph_dict["directed"],
                 bgcolor='#222222',
                 font_color='white',
                 notebook=not stay_this_tab)
    nt.add_nodes(graph_dict["nodes"])
    nt.add_edges(graph_dict["edges"])
    html_file = get_html_path(html_name)
    nt.show(html_file)
    return nt


if __name__ == "__main__":
    app()

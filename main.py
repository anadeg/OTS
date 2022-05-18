import glob, os
import json

from typing import Optional

import pyvis
import networkx as nx
import typer

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


@app.command()
def create_file(graph_name: str):
    path_to_folder = os.path.dirname(os.path.abspath(__file__))
    new_file = ".".join([graph_name, "json"])
    path_to_file = os.path.join(path_to_folder, "graphs", new_file)
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
    g = DirectedGraph(graph_name)
    upload_data = {
        "name": g.name,
        "directed": True,
        "nodes": list(g.graph.nodes),
        "edges": list(g.graph.edges)
    }
    path_to_file, is_created = create_file(graph_name)
    if is_created:
        add_data_to_json(path_to_file, upload_data)


def create_undirected(graph_name: str):
    g = UndirectedGraph(graph_name)
    upload_data = {
        "name": g.name,
        "directed": False,
        "nodes": list(g.graph.nodes),
        "edges": list(g.graph.edges)
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


if __name__ == "__main__":
    app()

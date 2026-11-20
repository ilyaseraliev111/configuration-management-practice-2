"""Преобразование готового графа в Mermaid и ASCII-дерево."""


def mermaid_lines(graph):
    """Возвращает flowchart: один узел на версию, все рёбра графа."""
    ids = {key: f"n{index}" for index, key in enumerate(graph.order)}
    yield "flowchart TD"
    for key in graph.order:
        yield f'    {ids[key]}["{key}"]'
    for parent in graph.order:
        for child in graph.edges[parent]:
            yield f"    {ids[parent]} --> {ids[child]}"


def branches(graph, parent):
    """Отмечает последнее ребро для отрисовки вертикальных линий."""
    children = graph.edges[parent]
    last = len(children) - 1
    for index, child in enumerate(children):
        yield child, index == last


def ascii_lines(graph):
    """Обходит граф стеком; повторные узлы показывает как ссылки."""
    yield graph.root
    shown = {graph.root}
    active = {graph.root}
    stack = [(graph.root, "", iter(branches(graph, graph.root)))]
    while stack:
        parent, prefix, children = stack[-1]
        branch = next(children, None)
        if branch is None:
            stack.pop()
            active.remove(parent)
            continue
        child, last = branch
        connector = "`-- " if last else "|-- "
        line = prefix + connector + child
        if child in shown:
            suffix = " [cycle]" if child in active else " [shared]"
            yield line + suffix
            continue
        yield line
        shown.add(child)
        active.add(child)
        indent = "    " if last else "|   "
        stack.append((child, prefix + indent, iter(branches(graph, child))))


def print_visualization(graph, ascii_mode=False):
    """Печатает Mermaid либо ASCII-дерево того же графа."""
    lines = ascii_lines(graph) if ascii_mode else mermaid_lines(graph)
    for line in lines:
        print(line)

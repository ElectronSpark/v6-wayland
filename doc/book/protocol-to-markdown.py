#!/usr/bin/env python3

import sys
from xml.dom import Node
from xml.dom.minidom import parse

if len(sys.argv) != 2:
    print("usage: protocol-to-markdown.py <xml>")
    sys.exit(1)
filename = sys.argv[1]

doc = parse(filename)
assert doc.documentElement.tagName == "protocol"

def parse_protocol(node):
    protocol = {
        "copyright": None,
        "summary": None,
        "description": None,
        "interfaces": [],
    }
    for child in filter(is_element, node.childNodes):
        match child.tagName:
            case "copyright":
                protocol["copyright"] = parse_text(child)
            case "description":
                protocol |= parse_description(child)
            case "interface":
                protocol["interfaces"].append(parse_interface(child))
    return protocol

def parse_interface(node):
    interface = {
        "name": node.getAttribute("name"),
        "version": node.getAttribute("version"),
        "frozen": node.getAttribute("frozen") == "true",
        "summary": None,
        "description": None,
        "requests": [],
        "events": [],
        "enums": [],
    }
    for child in filter(is_element, node.childNodes):
        match child.tagName:
            case "description":
                interface |= parse_description(child)
            case "request":
                interface["requests"].append(parse_message(child))
            case "event":
                interface["events"].append(parse_message(child))
            case "enum":
                interface["enums"].append(parse_enum(child))
    return interface

def parse_message(node):
    message = {
        "name": node.getAttribute("name"),
        "type": node.getAttribute("type"),
        "since": node.getAttribute("since"),
        "deprecated-since": node.getAttribute("deprecated-since"),
        "summary": None,
        "description": None,
        "args": [],
    }
    for child in filter(is_element, node.childNodes):
        match child.tagName:
            case "description":
                message |= parse_description(child)
            case "arg":
                message["args"].append(parse_arg(child))
    return message

def parse_arg(node):
    arg = {
        "name": node.getAttribute("name"),
        "type": node.getAttribute("type"),
        "summary": node.getAttribute("summary"),
        "description": None,
        "interface": node.getAttribute("interface"),
        "allow-null": node.getAttribute("allow-null") == "true",
        "enum": node.getAttribute("enum"),
    }
    for child in filter(is_element, node.childNodes):
        if child.tagName == "description":
            arg |= parse_description(child)
    return arg

def parse_enum(node):
    enum = {
        "name": node.getAttribute("name"),
        "since": node.getAttribute("since"),
        "bitfield": node.getAttribute("bitfield") == "true",
        "summary": None,
        "description": None,
        "entries": [],
    }
    for child in filter(is_element, node.childNodes):
        match child.tagName:
            case "description":
                enum |= parse_description(child)
            case "entry":
                enum["entries"].append(parse_entry(child))
    return enum

def parse_entry(node):
    entry = {
        "name": node.getAttribute("name"),
        "value": node.getAttribute("value"),
        "summary": node.getAttribute("summary"),
        "since": node.getAttribute("since"),
        "deprecated-since": node.getAttribute("deprecated-since"),
    }
    for child in filter(is_element, node.childNodes):
        if child.tagName == "description":
            entry |= parse_description(child)
    return entry

def parse_description(node):
    return {
        "summary": node.getAttribute("summary"),
        "description": parse_text(node),
    }

def parse_text(node):
    raw = "".join([child.data for child in node.childNodes])
    raw = raw.lstrip("\n")

    start = len(raw) - len(raw.lstrip())
    indent = raw[:start]

    lines = [l.removeprefix(indent) for l in raw.split("\n")]
    return "\n".join(lines).strip()

def is_element(node):
    return node.nodeType == Node.ELEMENT_NODE

def render_protocol(protocol):
    if protocol["copyright"]:
        print("```")
        print(protocol["copyright"])
        print("```")

    if protocol["description"]:
        print(protocol["description"])

    for interface in protocol["interfaces"]:
        render_interface(interface)

def render_interface(interface):
    render_header("##", interface)

    for request in interface["requests"]:
        render_message(request)
    for event in interface["events"]:
        render_message(event)
    for enum in interface["enums"]:
        render_enum(enum)

def render_message(message):
    render_header("###", message)

    for arg in message["args"]:
        print(f"`{arg["name"]}`")
        print(f"  : `{arg["type"]}` — {arg["summary"]}")
        print("")

def render_enum(enum):
    render_header("###", enum)

    for entry in enum["entries"]:
        print(f"`{entry["name"]}`")
        print(f"  : `{entry["value"]}` — {entry["summary"]}")
        print("")

def render_header(heading, element):
    print("")
    print(f"{heading} `{element["name"]}`", end="")
    if element["summary"]:
        print(f" — {element["summary"]}")
    else:
        print("")
    print("")
    if element["description"]:
        print(element["description"])
        print("")

protocol = parse_protocol(doc.documentElement)
render_protocol(protocol)

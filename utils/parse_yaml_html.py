#!/usr/bin/env python3
import yaml
import sys
import graphviz
import os
import shutil

# if there's an argument, we assume it's going to be the output directory to create,
# overwriting anything that's there (yeah yeah argparse etc)
# the script prints svg of the relationships on stdout

outdir = None

if len(sys.argv) > 1:
    outdir = sys.argv[1]
    shutil.rmtree(outdir, ignore_errors = True)
    os.mkdir(outdir)
else:
    print("Usage: ... | parse_html_yaml.py <output_directory>")
    print("Expects yaml input with top-level entries for transform name")
    print("WARNING: replaces <output_directory> if it exists without warning")
    exit(1)

nodes = yaml.safe_load(sys.stdin)

dot = graphviz.Digraph(format='svg', 
                       node_attr={'shape': 'rect', 
                                  'style': 'rounded,filled',
                                  'fontname': 'Arial',
                                  'colorscheme': 'set39',
                                  'fillcolor': '5',
                                  'margin': '0.3,0.0',
                                  'penwidth': '0'})


for nodename in nodes:
    # dictionary w/ keys for transform names
    node = nodes[nodename]
    
    # the label is the filename to write and the node label in the map
    label = nodename
    ext = ''
    if 'ext' in node:
        label = nodename + '.' + node['ext']
        ext = node['ext']


    # should be a code block, if not put something there
    if 'code' not in node:
        node['code'] = "No code provided?"

    # if they didn't provide a description, use the label
    if 'desc' not in node:
        node['desc'] = label
    
    # the attr entry should be a key/value map,
    # used to pass graphviz node attributes
    # if not used, use an empty dictionary
    attr = {}
    if 'attr' in node:
        attr = node['attr']

    # if there's an extension set and the user hasn't
    # used the fillcolor attribute, let's color the node
    # by the extension
    if 'fillcolor' not in attr and ext != "":
        colormap = {'sql': '1', 'py': '3', 'R': '6'}
        attr['fillcolor'] = colormap[ext]


    # create the node in the graph, named by the transform name
    # but labeled with the desired extension, and pass through defined attributes
    dot.node(nodename, 
             label, 
             tooltip = node['desc'], 
             URL = label,
             target = "_blank",
             **attr)

    # get the inputs and create edges
    if "inputs" in node:
        inputs = node["inputs"]
        for input in inputs:
            dot.edge(input, nodename)

    # write the code for this node to a file in the outdir
    if outdir:
        meta = node.copy()
        meta.pop('code')
        meta = {nodename: meta}
        meta_yaml_lines = yaml.dump(meta).split(os.linesep)
        if ext in ['py', 'R', 'r', 'sql', 'SQL']:
            if ext in ['py', 'R', 'r']:
                meta_yaml_lines = ["#* " + line for line in meta_yaml_lines]
            elif ext in ['sql', 'SQL']:
                meta_yaml_lines = ["--* " + line for line in meta_yaml_lines]

            node['code'] = os.linesep.join(meta_yaml_lines + [node['code']])

        source_fh = open(os.path.join(outdir, label), 'w')
        source_fh.write(node['code'])
        source_fh.close()

# now write to the output dir an html file with svg version of the graph
with open(os.path.join(outdir, "index.html"), "w") as html_handle:
    html_handle.write("<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\" /></head><body>\n")
    html_handle.write(str(dot.pipe(format = 'svg', encoding = 'ascii')) + "\n")
    html_handle.write("</body></html>")

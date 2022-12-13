
N3C Workbook Parser
=================

This small utility is developed for [N3C](https://covid.cd2h.org), to help 
researchers publish code from Code Workbooks to git repositories in more browsable way.


Table of Contents
=================

* [Overview](#overview)
   * [Features](#features)
   * [Requirements](#requirements)
   * [Known Issues](#known-issues)
   * [Future Ideas](#future-ideas)
* [Example Usage](#example-usage)
   * [Add Metadata to Workbook Transforms](#add-metadata-to-workbook-transforms)
      * [Metadata Fields](#metadata-fields)
   * [Initial Project Setup and Publishing](#initial-project-setup-and-publishing)
   * [Pulling and Pushing Updates](#pulling-and-pushing-updates)
   * [Using Branches](#using-branches)

<!-- Created by https://github.com/ekalinin/github-markdown-toc -->


# Overview

## Features

* Export each transform node as an independent code file
* Creates an SVG-based browsable graph of the transform nodes with customization options
* Supports multiple code workbooks

Browse example output at [https://oneilsh.github.io/n3c_example_project_public/](https://oneilsh.github.io/n3c_example_project_public/). Notice that
there are both hover text descriptions, and nodes are clickable to browse the code.

[![graph](./docs_images/graph.png)](https://oneilsh.github.io/n3c_example_project_public/)

## Requirements

To make this utility work, you will need the following:

* [Graphviz](https://graphviz.org/)
* GNU tools: `awk`, `sed`, and `bash`
* python3, and the following python packages:
  * [graphviz](https://pypi.org/project/graphviz/)
  * [pyyaml](https://pypi.org/project/PyYAML/)

## Known Issues

* The code could be more robust to non-conforming inputs
* Requires a Unix-like environment with `sed`, `awk`, and `bash`
* Each transform should be annotated by the user as python, R, or sql, when this could be derived automatically
* For pipelines spanning multiple workbooks, information on which workbook each transform derives from is dropped

All of the above could be solved by migrating all of the logic entirely to python -- pull requests welcome :)

## Future Ideas

Additional metadata fields could be parsed and added to the visualization or outputs. Ideas include
metadata on inputs, for example subfields of each input that describe the columns expected and their types,
and/or integrated metadata on transform output. 

Support for parsing Code Repo exports would allow the use of parsed Repos and Workbooks in a single project.

It would also be nice to use github actions to re-build the parsed output and host it via github pages 
on push. Early work on this exists in `utils/github`. This would also remove the dependency on `graphviz` et al. 


# Example Usage

## Add Metadata to Workbook Transforms

To start, you will need to add metadata to transforms in Code Workbooks you wish to parse and publish. 
Here are two workbooks we'll use as examples: [workbook1](https://unite.nih.gov/workspace/vector/view/ri.vector.main.workbook.dde3a2a4-7f3c-4c51-99dc-50dcff82fbe9?branch=master) and [workbook2](https://unite.nih.gov/workspace/vector/view/ri.vector.main.workbook.a0526ea9-8d77-43bd-94b3-9f589e307129?branch=master) (N3C enclave access required).

Here's a screenshot from `workbook1`, illustrating the minimal suggested metadata requirement for an `sql` node:

![input_concept_set_members](./docs_images/input_concept_set_members.png)

Notice that the first section of the transform is a set of special comment lines, each beginning with `--* ` (two hyphens, a star, and a space). This 
block defines the metadata for the transform using SQL comments (`--`). For R and Python nodes, the metadata blocks
begin with `#* `. The R node in `workbook1` illustrates this with more options set.

![plot_person](./docs_images/plot_person.png)

**Note**: Don't get fancy with the formatting of this metadata block. In the current implementation the block should:

* Be the first lines of the transform (lines prior will be ignored)
* Be contiguous (not contain any empty lines)
* Be valid [YAML](https://en.wikipedia.org/wiki/YAML) after the special comment characters and space

**Note 2**: All transforms in your code workbook(s) should have metadata blocks. Missing some will result in lack
of output for those nodes and unconnected parts of the pipeline visualization.

### Metadata Fields

The following fields are supported and illustrated in the second screenshot above:

* **Node name (e.g. `plot_person:` above)** *Required.* Metadata must live under a heading defining the name of the node. 
  This can be anything you like, but note that it must be a valid YAML field name (no spaces), and it will
  be the name used to refer to this node as an input to other nodes. We recommend 
  using `snake_case` names for your transforms, both in the name of the saved dataset 
  and in-workbook transform name (`plot_person` as `plot_person` in the screenshot above).

* **`inputs:`** *Required* (unless you have a transform with no inputs for some reason...). It should
  be a YAML list of node names that are inputs to this node.

* **`desc:`** *Recommended.* This should be a short description for the node, and will be used as hoverover text in
  the output visualization. To conform to YAML standard you may need to wrap it in quotes (as above). You could also
  use YAML multi-line strings, for example:

  ```
  #* some_transform:
  #*   desc: |
  #*     This is a multiline
  #*     string in YAML. 
  #*   inputs:
  #*     - ...
  ```

  Note that when using multi-line strings your line breaks will be preserved, but additional line breaks may
  also be added by the browsers hover-text.

* **`ext:`** *Recommended.* This should be one of `py`, `R`, or `sql` to alert the parser to what kind
  of transform is being parsed. This is used to set the filename in the per-transform code output, and 
  the color of the node in the visualization.

* **`attr:`** *Optional.* This field can be used to specify additional visualization settings for 
  the node as `attribute: value` pairs referring to graphviz [node attributes](https://graphviz.org/docs/nodes/). 
  All attributes should be supported, with the exception of `tooltip` which is instead specified by `desc` above. 
  For example, to change the node to use a hexagon shape, blue fill, and font size of 20:

  ```
  #* some_transform:
  #*   attr:
  #*     fillcolor: blue
  #*     shape: hexagon
  #*     fontsize: "20"
  #*   inputs:
  #*     - ...
  ```

  Note that numeric values (like font size) should be specified as strings enclosed in quotes. You can use
  RGB values by enclosing them in quotes as well, e.g. `"#25EF34"`. The standard color scheme uses the
  Colorbrewer [set3, 9 class](https://colorbrewer2.org/#type=qualitative&scheme=Set3&n=9) palette, so you can also 
  use e.g. `fillcolor: "7"` to use the 7th color in this colorscheme. 


## Initial Project Setup and Publishing

For this section we'll assume you are somewhat familiar with working with GitHub and a Unix-based command-line
environment. 

First, we're goin to need a local project folder to work it, which will contain several git repositories.

```
mkdir n3c_example_project_local
cd n3c_example_project_local
```

Next, create a [new repository](https://docs.github.com/en/get-started/quickstart/create-a-repo) on GitHub to represent 
the public-facing view of your project, with or without a README.md, and clone it to your
local machine. I've called mine `n3c_example_project_public`:

```
git clone https://github.com/oneilsh/n3c_example_project_public.git
```

Now we need to clone the Code Workbooks from the Enclave. For each
workbook, select the "gear" icon near the top, and then "Export git repository". 
This will open a new browser tab, with a command to run to clone the workbook. Use
the commands provided to clone the workbook repositories from the Enclave.

```
git clone <long URL provided for workbook1>
git clone <long URL provided for workbook2>
``` 

Finally we are going to need this `workbook_parser` tooling:

```
git clone https://github.com/oneilsh/n3c_workbook_parser.git
```

Now we can run the workbook parser. The two arguments are the directory to look for workbook files in (`.` for the current
project directory), and the output folder to place results in (`n3c_example_project_public/docs` in this case):

```
n3c_workbook_parser/parse_workbooks . n3c_example_project_public/docs
```

At this point we have a variety of subfolders: the two workbook folders `workbook1` and `workbook2`, the `n3c_workbook_parser`
utility folder, and the public-facing repo with the `docs` output folder with individual code files for each transform and an `index.html` that you can 
open to browse the transforms. Note that the individual tranform files end in `.txt` - this is to make them more easily viewable in a web browser.

```
n3c_example_project_local
├── n3c_example_project_public
│   ├── README.md
│   └── docs
│       ├── index.html
│       ├── input_concept_set_members.sql.txt
│       ├── plot_person.R.txt
│       ├── pneumonia_concept_set.sql.txt
│       ├── pneumonia_conditions.sql.txt
│       └── pneumonia_expired_demographics.py.txt
├── n3c_workbook_parser
│   ├── README.md
│   ├── docs_images
│   │   ├── gh_pages.png
│   │   ├── input_concept_set_members.png
│   │   └── plot_person.png
│   ├── parse_workbooks
│   └── utils
│       ├── github
│       │   ├── README.md
│       │   └── workflows
│       │       └── runparser.yml
│       ├── meta2yaml.sh
│       ├── parse_yaml_html.py
│       └── strip_extraneous.awk
├── workbook1
│   ├── pipeline.R
│   ├── pipeline.py
│   ├── pipeline.sql
│   └── workbook.yml
└── workbook2
    ├── pipeline.R
    ├── pipeline.py
    ├── pipeline.sql
    └── workbook.yml

9 directories, 25 files
```

Now that we have our public-facing repo built, we can push it up to GitHub.

```
cd n3c_example_project_public
git add -A
git commit -m "Pushing parsed results"
git push
```

On GitHub, we can configure the repo pages under Settings -> Pages, 
and select the `main` branch `docs` subfolder.

![gh_pages](./docs_images/gh_pages.png)

Once it has built (you can see the build progress on the Actions tab),
the page will be browsable at the URL indicated in the Pages settings tab.
The page for this example is at [https://oneilsh.github.io/n3c_example_project_public/](https://oneilsh.github.io/n3c_example_project_public/).

## Pulling and Pushing Updates

As you work on your project you will likely make changes to your workbooks and possibly add new workbooks. Updating the public repository is 
fairly easy: you just need to re-pull the workbook repositories from the enclave, re-run the parser, and re-push the public repo. 

**NOTE! In order for updates to Code Workbooks to be saved so that they can be pulled down, just making text edits won't do it. You need to either run a 
transform in the workbook, or create a new transform in the workbook.**

So, supposing I've made a change to `workbook2` and-rerun a transform, I start by making sure I'm in the local project folder:

```
cd n3c_example_project_public 
```

Then do the requisite pull/build/push steps (using `-C` to pull and push the repositories without needing to move into them).
Because the parsing step overwrites the output directory contents, you will be prompted to ensure this is what you want. 

```
git -C workbook2 pull
n3c_workbook_parser/parse_workbooks . n3c_example_project_public/docs
git -C n3c_example_project_public add -A
git -C n3c_example_project_public commit -m "Updates in workbook2"
git -C n3c_example_project_public push
```

The GitHub pages version will automatically re-deploy and be available in a couple of minutes.


## Using Branches

Code workbooks support branches, and these may be checked out for use in parsing. Note that
if you want to use branches on your published repository, those will need to be created separately 
(and GitHub pages will need to be configured to use the branch you'd like to publish).

Supposing I've created a new `example_branch` on `workbook1` in the enclave, and run a transform to 
commit that branch in the enclave, we just need to `git fetch` and `git switch` to the new branch.

```
cd workbook1
git fetch
git switch example_branch
```

From there the parsing script can be re-run to pick up the changes made in the new branch.






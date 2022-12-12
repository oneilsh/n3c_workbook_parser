#!/usr/bin/env sh
# this script should read input on stdin and assumes a specific 
# set of yaml-encoded comments describing code blocks,
# e.g. the output of cat pipeline.* | strip_extraneous.awk
# all it does really is remove the comment parts of the magic 
# comments (--* and #* at the beginnning on lines),
# and indent all other lines under the code: block to produce valid yaml

# treat lines that start with #* or --* as defining yaml; 
# leave these alone for now (first condition)
# other lines we need to pad in so that they can be treated as a multiline 
# string in the yaml
# then we strip off those leading characters
awk '/^(#\*)|(--\*)/ {print $0} !/^(#\*)|(--\*)/ {print "     "$0}' \
| sed 's/^--\* //' \
| sed 's/^#\* //' 


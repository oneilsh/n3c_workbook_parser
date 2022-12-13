#!/usr/bin/env -S awk -f

# this script should read on stdin one or more pipeline.* files
# e.g. cat pipeline.* | ./strip_extraneous.awk
#
# it removes lines starting with @transform_pandas up until the first magic 
# comment; this means transforms not metadata-commented will be removed (buyer beware)

BEGIN {new_transform = 0; printing = 0; in_meta_block = 0}
/@transform_pandas/ {new_transform = 1; printing = 0; in_meta_block = 0}
new_transform && /^(--\*)|(#\*) / {printing = 1; new_transform = 0; in_meta_block = 1} 
in_meta_block && !/^(--\*)|(#\*)/ {print "#*   code: |"; in_meta_block = 0}
printing && !/@transform_pandas/ {print $0}

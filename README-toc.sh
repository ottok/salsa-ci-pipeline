#!/bin/bash
# Copyright salsa-ci-team and others
# SPDX-License-Identifier: FSFAP
# Copying and distribution of this file, with or without modification, are
# permitted in any medium without royalty provided the copyright notice and
# this notice are preserved. This file is offered as-is, without any warranty.

#
# This script generates a Markdown table-of-contents from a README.html file,
# in order to update the README.md documentation source file.
#
# Generating a README.html is out of scope for this script. Use your code editor
# or the GitLab UI to render the HTML version from the Markdown source.
#
# Note that only headers on level 1-3 are included in the table-of-contents
# for the sake of brevity. Also note that for a header to be included, the `sed`
# rule expects the HTML tag format to be uniform.
#
# Running this script needs human oversight as it is not perfect, but good
# enough for the mostly on-off job.

# Check if a filename is provided
if [ -z "$1" ]
then
  echo "Usage: $0 <filename.html>"
  exit 1
fi

# Extract links, text, and header level using sed and awk
sed -n 's/.*<a id="user-content-[^"]*" class="anchor" aria-hidden="true" href="#\([^"]*\)"><\/a>\(.*\)<\/h\([1-3]\)>/\2\t\1\t\3/p' "$1" | \
awk -F'\t' '{
  # Escape special markdown characters
  text = $1
  gsub(/\[/,"\\[", text)
  gsub(/\]/,"\\]", text)
  gsub(/\(/,"\\(", text)
  gsub(/\)/,"\\)", text)
  link = $2
  gsub(/\[/,"\\[", link)
  gsub(/\]/,"\\]", link)
  gsub(/\(/,"\\(", link)
  gsub(/\)/,"\\)", link)

  # Calculate indentation based on header level
  indent = ""
  for (i = 1; i < $3; i++) {
    indent = indent "  "
  }

  printf "%s* [%s](#%s)\n", indent, text, link
}'

exit 0

#!/bin/bash

# Create a new post with today's date and prompt for the title.

# Config
editor="e"
format="md"

# Get layout via getopts (-l)
# --
# http://wiki.bash-hackers.org/howto/getopts_tutorial

while getopts ":l:" opt; do
    case $opt in
        l)
            layout=$OPTARG
            ;;
        :) echo "$opt requires an argument" >&2
            exit 1
            ;;
    esac
done

# Set default config values
# --
# http://www.cyberciti.biz/tips/howto-setting-default-values-for-shell-variables.html

: "${layout:="post"}"

echo "---"
echo "Creating a new ${layout} for" `date +%A", "%B" "%e", "%Y`"."
echo ""
read -p "Enter the title: " title 
read -p "Enter a category?: " category

# Turn spaces into dashes
for word in $title
do
    dashedTitle=${dashedTitle}-${word}
done

# Convert title to lowercase
dashedTitle="`echo ${dashedTitle} | tr '[A-Z]' '[a-z]'`"

# Create a filename with the date, dashed title, and format 
filename="`date +%Y-%m-%d`${dashedTitle}.${format}"

# Make the filename w/ the category
# filename="${category}/`date +%Y-%m-%d`${dashedTitle}.${format}"
# Make the category directory here if it doesnt exist.
# mkdir -p ${category}

echo $filename

touch $filename

# Add initial YAML to the top of the new bit
echo "---" >> $filename
echo "layout: ${layout}" >> $filename
echo "title: \"${title}\"" >> $filename
echo "<!--- modified: `date +%Y-%m-%d` -->" >> $filename
echo "category: ${category}" >> $filename
echo "tags:" >> $filename
echo "description: \"${title}\"" >> $filename
echo "image:" >> $filename
echo "  feature: feat/ralph-stover.jpg" >> $filename
echo "  credit: " >> $filename
echo "  creditlink: " >> $filename
echo "---" >> $filename
echo "" >> $filename

# open $editor
#${editor} + $filename

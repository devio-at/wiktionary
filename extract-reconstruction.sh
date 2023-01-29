grep '>Reconstruction:' enwiktionary-20220120-pages-meta-current.xml  | sed 's/ *<title>Reconstruction://g' | sed 's/\/.*//g' | sort | uniq -c | sed -r 's/ +([0-9]+) (.+)/\2,\1/'

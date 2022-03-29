# Uusage: 
#    awk -f transform.awk halocode.py > python.code-snippets
#
#    then copy  'python.code-snippets' to '.vscode/' of project root
#

function ltrim(s) { 
    sub(/^[ \t\r\n]+/, "", s); return s
}

function rtrim(s) { 
    sub(/[ \t\r\n]+$/, "", s); return s
}

function trim(s) { 
    return rtrim(ltrim(s)); 
}

function escape(s) {
    gsub( "\"", "'", s)
    return s
}

function prep(s) {
    return escape(trim(s))
}

function print_desc(s) {
    s = prep(s)
    if (s != "") {
        print "            \""s, "\""
    }
}

BEGIN {
    # '("' or ' \n' or '"),'
    FS="[(][\"]|[ ][\\\\][n]|[\"][)][,]"
    print "{"
}

{
    $2 = prep($2)
    if ($2 != "") {
        print "    \""$2"\" : {"
        print "        \"prefix\": \""$2"\","
        print "        \"body\": \""$2"\","
        print "        \"description\": ["
        print_desc($3)
        print_desc($4)
        print_desc($5)
        print "        ]"
        print "    },"
    }
}

END {
    print "}"
}

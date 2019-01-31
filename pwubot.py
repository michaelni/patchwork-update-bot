#!/usr/bin/python
#Michael Niedermayer
#GPL 2+

import os
import pickle
import re
import subprocess
import sys

# This may be needed to be applied to pwclient for it to not crash
#@@ -165,7 +172,7 @@
#                 # naive way to strip < and > from message-id
#                 val = string.strip(str(patch["msgid"]), "<>")
#             else:
#+                val = unicode(patch[fieldname]).encode('utf-8')
#-                val = str(patch[fieldname])
#
#             return val

pwclient = "pwclient"

def cached_call( command ):
    if not command in cache :
        cache[command] = os.popen(command).read()
    return cache[command]

def isint(value):
    try:
        int(value)
        return True
    except:
        return False

id_list = []
status_list = []
subject_list = []
date_list = []
delegate_list = []
submitter_list = []
patch_list = []

git_author_list = []
git_subject_list = []

applied_status_subject_list = []
not_applicable_status_subject_list = []

def get_patch_list( ):
    proc = subprocess.Popen([pwclient, 'list', '-f', '%{id}@#SEP%{state}@#SEP%{name}@#SEP%{date}@#SEP%{delegate}@#SEP%{submitter}'],stdout=subprocess.PIPE)
    sys.stderr.write("loading: ")

    subject_clean = re.compile('\[[^]]*\]')

    for line in proc.stdout:
        tmp = line.strip().split('@#SEP')
        if isint(tmp[0]) :
            id_list             .append(tmp[0])
            status_list         .append(tmp[1])
            subject_list        .append(subject_clean.sub('', tmp[2], count=1).strip())
            date_list           .append(tmp[3])
            delegate_list       .append(tmp[4])
            submitter_list      .append(tmp[5])

            sys.stderr.write(tmp[0] + ", ")
            patch_list          .append(cached_call(pwclient +' view ' + tmp[0]))

    sys.stderr.write("\n")
    return True

def get_git_list( ):
    proc = subprocess.Popen(['git', 'log', '--pretty=short', '--first-parent', '-1000', 'origin/master'],stdout=subprocess.PIPE)
    sys.stderr.write("giting: ")
    for line in proc.stdout:
        if line.startswith('Author: ') :
            git_author_list.append(line[8:].strip())
            sys.stderr.write(".")
        elif line.startswith('    ') :
            git_subject_list.append(line[4:].strip())
            sys.stderr.write(":")

    sys.stderr.write("\n")
    return True

cache = {}
try :
    f = open("pwubot.cache", 'rb')
    cache = pickle.load(f)
    f.close()
except : IOError

get_patch_list()
get_git_list()

# Find non applicable (fate failure type patches) which havnt been marked correctly
ids = ""
for i, item in enumerate(patch_list):
    if item.find("+++ tests/data/fate/") >= 0 and status_list[i] != "Not Applicable":
        sys.stderr.write("Fate patch: " + id_list[i] + " " + status_list[i] + " " + date_list[i] + " " + submitter_list[i] + " " + subject_list[i] + "\n")
        ids += " " + id_list[i]
if ids != "" :
    sys.stderr.write(pwclient + " update " + ids + " -s 'Not Applicable'\n")


#Find Accepted / NA patches
for i, item in enumerate(subject_list):
    if status_list[i] == "Applied":
        applied_status_subject_list.append(item)
    if status_list[i] == "Not Applicable":
        not_applicable_status_subject_list.append(item)

#Find superseeded patches by subject and submitter
ids = ""
p = re.compile('[vV]\d+')
subject_index = sorted((p.sub('v#',e),submitter_list[i],i) for i,e in enumerate(subject_list))
last_index = -1
for i, item in enumerate(subject_index):
    j = item[2]
    if last_index >= 0 and subject_index[i][0] == subject_index[last_i][0] and submitter_list[last_index] == submitter_list[j] :
        older = last_index
        if int(id_list[j]) < int(id_list[last_index]) :
            older = j
        if status_list[older] == "New":
            sys.stderr.write("DUP: " + id_list[older] + " " + status_list[older] + " " + date_list[older] + " " + submitter_list[older] + " " + subject_list[older] + "\n")
            ids += " " + id_list[older]
    last_index = j
    last_i = i;
if ids != "" :
    sys.stderr.write(pwclient + " update " + ids + " -s 'Superseded'\n")


ids = ""
for i, item in enumerate(subject_list):
    if item in git_subject_list and status_list[i] == "New" and not item in applied_status_subject_list:
        sys.stderr.write("Applied: " + id_list[i] + " " + status_list[i] + " " + date_list[i] + " " + submitter_list[i] + " " + subject_list[i] + "\n")
        ids += " " + id_list[i]
if ids != "" :
    sys.stderr.write(pwclient + " update " + ids + " -s 'Accepted'\n")

applied_stat = superseeded_stat = new_stat = 0
for i, item in enumerate(subject_list):
    if status_list[i] == "Accepted":
        applied_stat+=1
    elif status_list[i] == "Superseded":
        superseeded_stat+=1
    elif status_list[i] == "New":
        new_stat+=1

sys.stderr.write("Accepted: " + str(applied_stat) + " Superseded: " + str(superseeded_stat) + " New: " + str(new_stat) + "\n")

f = open("pwubot.cache", 'wb')
pickle.dump(cache, f)
f.close()
from setup import *

# This script calls each individual section in sequence

print("\nStarting Google Tasks + Notion sync!\n")

print("----------------------------------------------------------------------\n")
import apiConnections

if SYNC_DELETED_TASKS:
    print("----------------------------------------------------------------------\n")
    import syncDeletions

print("----------------------------------------------------------------------\n")
import importToGTasks

print("----------------------------------------------------------------------\n")
import importToNotion

print("----------------------------------------------------------------------\n")
import updateGTasks

print("----------------------------------------------------------------------\n")
import updateNotion

print("----------------------------------------------------------------------\n")
print("Finished Google Tasks + Notion sync!\n")
exit()

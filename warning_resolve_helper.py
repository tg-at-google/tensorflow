'''
The goal of this module is to 
make warning resolution much faster by leverage the commonalities
structure of each of the warnings. 

Algorithm:
0* Initialize files_commited_count=0, files_per_commit_threshold=16, load batch_number from info.json
1* Use bazel to build the file assoicated with the warning being fixed; Reproduce the warning;
	* Assume the build file is in the cwd and run elif (not_found_error):
		* Lookup the path for the build file 
	* Confirm warning reproduced
2* Open gedit and make  and save fix, then close gedit
3* Build and Confirm no_error_present and build_success else goto 2* 
4* Add file to the current commit 
5* if (files_commited_count==files_per_commit_threshold): make a commit and push commmit 
	* create a pull request for commit
	* set files_commited_count=0,
	* increment batch_number and update info.json	
	* create and checkout a new branch, sign-compare-warning-fixes-batch-{}

Repeat until done.
'''

import os, json

# -- init ---
files_commited_count=None
batch_number=None
files_per_commit_threshold=16
warning_producing_files=None

with open("indexed_warning_files.json",'r') as filenames:
	warning_producing_files=json.loads(filenames)

if not os.path.isfile('info.json'):
	files_commited_count=0	
	batch_number=1
	with open('info.json', 'w') as info_file:
		info_file.write(json.dumps({
			"files_commited_count": files_commited_count,
			"batch_number": batch_number
		})
else:
	with open('info.json', 'r') as info_file:
		info = json.loads('info.json')
		files_commited_count=info['files_commited_count']
		batch_number=info['batch_number']

# -- building from python, reproduce the warning ---
def can_convert_to_int(obj):
	try:
		int(obj)
	except:
		return False
	return True
	
warning_id = None

while (warning_id not in warning_producing_files):
	_warning_id = None
	while not can_convert_to_int(_warning_id):
		_warning_id = input("Enter the id of the warning you would like to resolve: ")
	warning_id=int(_warning_id)

print(warning_producing_files[warning_id])

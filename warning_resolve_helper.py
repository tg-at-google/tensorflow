import os, json
import subprocess


def can_convert_to_int(obj):
	try:
		int(obj)
	except:
		return False
	return True

def directory_of(filepath):
	# returns as a string
	# the directory of the filepath passed
	directory_path=filepath
	i=len(directory_path)-1
	while (directory_path[i] != "/"):
		i-=1
	return directory_path[:i+1]

def get_filename(filepath):
    # give a filepath
    # return only the filename
    i=len(filepath)-1
    while (filepath[i] != "/"):
        i-=1
    return filepath[i+1:]

# class SignCompareWarning():
# 	def __init__(self, warning_id):
# 		self.id = warning_id
# 		self.build_file_directory =
# 		self.build_file



# forgive poorly named method
class WarningResolveHelper:
	def __init__(self):
		# restore the below variable from 'info.json'
		self.files_commited_count=None
		self.batch_number=None
		self.files_per_commit_threshold=16
		self.warning_producing_files=None
		self.terminal_flag=False
		self.active_warning = {}

		#load indexed warining producing filenames
		with open("indexed_warning_files.json",'r') as filenames:
			self.warning_producing_files=json.load(filenames)
			self.warning_producing_files={ int(key): self.warning_producing_files[key] for key in self.warning_producing_files }

		# load git commit state from 'info.json'
		if (not os.path.isfile('info.json')):
			self.files_commited_count=0
			self.batch_number=1
			with open('info.json', 'w') as info_file:
				info_file.write(json.dumps({
					"files_commited_count": self.files_commited_count,
					"batch_number": self.batch_number
					})
				)
		else:
			with open('info.json', 'r') as info_file:
				info = json.load(info_file)
				self.files_commited_count=info['files_commited_count']
				self.batch_number=info['batch_number']

		return None

	def get_warning_id_from_user(self):
		warning_id = None
		#! should also check if warning is already resolved and loop back in, in that case
		while (warning_id not in self.warning_producing_files):
			_warning_id = None
			while not can_convert_to_int(_warning_id):
				_warning_id = input("Enter the id of the warning you would like to resolve: ")
			warning_id=int(_warning_id)
		self.active_warning["warning_id"]= warning_id
		return None

	def lookup_relevant_build_info(self, filepath):
		print("You are seeing this message becuase the because the default build arguments did not succeed in producing the relevant build.")
		print("The associated file is:\n{}".format(filepath))
		build_file_directory= input('Enter the directory of the BUILD for the above file: ')
		build_alias = input('Enter the build alias of the relevant build: ')

		bazel_build_info_object = {
			"build_file_directory": build_file_directory,
			"bazel_build_argument": '//'+ build_file_directory + ":" + build_alias
		}

		return bazel_build_info_object

	def reproduce_warning(self):
		warning_reproduced=False

		# of the warning producing file
		filepath = self.warning_producing_files[self.active_warning["warning_id"]]
		file_directory = directory_of(filepath)
		filename = get_filename(filepath)

		build_file_directory = file_directory
		bazel_build_argument = None

		while (not warning_reproduced):
			if (bazel_build_argument==None):
				# we haven't tried using the default arugment
				bazel_build_argument = '//'+ build_file_directory[:-1] + ":" + filename[:-3]
			else:
				# we've tried using the default argument and it failed
				# lookup the correct build arguments
				bazel_build_info = self.lookup_relevant_build_info(filepath)
				build_file_directory= bazel_build_info['build_file_directory']
				bazel_build_argument= bazel_build_info['bazel_build_argument']
				# but for now this is not implemented so just terminate instead


			# sph is short for subprocess helper
			clear_cache_sph= subprocess.run(['rm','-rf', 'bazel-bin/'+ build_file_directory], capture_output=True)
			print("build running, please await it's completion ( it may take a few seconds to a minute. )")
			reproduce_warning_sph= subprocess.run(['bazel','build', bazel_build_argument], capture_output=True)

			# sph_outstream= reproduce_warning_sph.stdout.decode('utf-8')
			sph_errstream= reproduce_warning_sph.stderr.decode('utf-8')
			print( sph_errstream )

			if (reproduce_warning_sph.returncode == 0):
				warning_reproduced= ("[-Wsign-compare]" in sph_errstream) #or ("[-Wsign-compare]" in sph_outstream)

		self.active_warning["build_file_directory"]=build_file_directory
		self.active_warning["bazel_build_argument"]=bazel_build_argument
		self.active_warning["resolution_attempts"]=0
		return None

	def warning_resolved(self):
		# run build again and confirm build success AND no "[-Wsign-compare]" flags
		# present

		print("build running, please await it's completion ( it may take a few seconds to a minute. )")
		clear_cache_sph= subprocess.run(['rm','-rf', 'bazel-bin/'+ self.active_warning["build_file_directory"]], capture_output=True)
		confirm_resolution_sph= subprocess.run(['bazel','build', self.active_warning["bazel_build_argument"]], capture_output=True)

		sph_errstream= confirm_resolution_sph.stderr.decode('utf-8')
		print( sph_errstream )

		warning_resolved = False

		if (confirm_resolution_sph.returncode == 0):
			warning_resolved= ("[-Wsign-compare]" not in sph_errstream)

		return warning_resolved

	def prompt_user_resolution_action(self):
		filepath = self.warning_producing_files[self.active_warning["warning_id"]]
		print("!!! {}".format(filepath))
		fix_warning_sph= subprocess.run(['gedit', filepath])
		input("Press enter when done editing:")
		return None

	def update_git_state(self):
		filepath = self.warning_producing_files[self.active_warning['warning_id']]
		subprocess.run(['git','add', filepath], capture_output=True)

		self.files_commited_count+=1
		if (self.files_commited_count==self.files_per_commit_threshold):
			commit_message='[Wsign-compare] resolution, batch {}'.format(batch_number)
			subprocess.run(['git','commit', '-m', ], capture_output=True)
			subprocess.run(['git','push'], capture_output=True) # will break
			#confirm success

			self.batch_number+=1
			new_branch_name = 'sign-compare-warning-fixes-batch-{}'.format(self.batch_number)
			subprocess.run(['git','checkout' '-b', new_branch_name], capture_output=True)

		self.update_file_state()
		return None

	def interaction_loop(self):
		self.get_warning_id_from_user()
		# warning_id being referenced is an unresolved reference
		self.reproduce_warning()
		while (not self.warning_resolved()):
			self.prompt_user_resolution_action()
		self.update_git_state()
		self.prompt_termination_option()
		#! handlier
		return None

	def update_file_state(self):
		with open('info.json', 'w') as info_file:
			info_file.write(json.dumps({
				"files_commited_count": self.files_commited_count,
				"batch_number": self.batch_number
				})
			)
		return None

	def prompt_termination_option(self):
		if ( input("Terminate Session? [Y/.]") == 'Y' ):
			self.terminal_flag = True
		return None

	def terminal_state(self):
		return self.terminal_flag

if __name__ == "__main__":
	helper = WarningResolveHelper()

	while ( not helper.terminal_state() ):
		helper.interaction_loop()

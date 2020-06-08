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

# forgive poorly named method
class WarningResolveHelper:
	def __init__(self):
		# restore the below variable from 'info.json'
		self.files_commited_count=None
		self.batch_number=None
		self.files_per_commit_threshold=16
		self.warning_producing_files=None

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
		return warning_id

	def lookup_relevant_build_info(self):
		pass

	def reproduce_warning(self, warning_id):
		warning_reproduced=False
		default_build_argument_used=False

		# of the warning producing file
		filepath = self.warning_producing_files[warning_id]
		file_directory = directory_of(filepath)
		filename = get_filename(filepath)

		build_file_directory = file_directory
		bazel_build_argument = None

		while (not warning_reproduced):
			if (bazel_build_argument==None):
				# we haven't tried using the default arugment
				bazel_build_argument = '//'+ file_directory[:-1] + ":" + filename[:-3]
				bazel
			else:
				# we've tried using the default argument and it failed
				# lookup the correct build arguments
				bazel_build_info = self.lookup_relevant_build_info()

				# but for now this is not implemented so just terminate instead
				pass

			# sph is short for subprocess helper
			clear_cache_sph= subprocess.run(['rm','-rf', 'bazel-bin/'+ file_directory], capture_output=True)
			reproduce_warning_sph= subprocess.run(['bazel','build', bazel_build_default_argument], capture_output=True)

			if (reproduce_warning_sph.return_code == 0):
				build_log= reproduce_warning_sph.stderr.decode('utf-8')
				print( build_log )
				warning_reproduced= "[-Wsign-compare]" in build_log
		return None

	def warning_resolved(self):
		# run build again and confirm build success AND no "[-Wsign-compare]" flags
		# present
		clear_cache_sph= subprocess.run(['rm','-rf', 'bazel-bin/'+ file_directory], capture_output=True)
		confirm_resolution_sph= subprocess.run(['bazel','build', bazel_build_default_argument], capture_output=True)
		build_log =
		if (
		(confirm_resolution_sph.return_code != 0) or
		("[-Wsign-compare]" in build_log)
		):
		#go back
		return None

	def prompt_user_resolution_action(self, warning_id):
		filepath = self.warning_producing_files[warning_id]
		fix_warning_sph= subprocess.run(['gedit', filepath])
		input("Press enter when done editing:")
		return None

	def interaction_loop(self):
		warning_id = self.get_warning_id_from_user()
		# warning_id being referenced is an unresolved reference
		self.reproduce_warning(warning_id)
		while (not self.warning_resolved(warning_id):
			self.prompt_user_resolution_action(warning_id)
		return None

	def update_git_state(self):
		return None



if __name__ == "__main__":
	helper = WarningResolveHelper()

	while ( helper.terminal_state() ):
		helper.interaction_loop()

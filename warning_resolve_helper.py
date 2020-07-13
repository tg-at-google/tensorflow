import os, json
import subprocess, webbrowser

#this file is a hack, it is not well engineered
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
		self.terminal_flag=False
		self.warning_producing_files = None
		self.active_warning = {}

		#load indexed warining producing filenames
		self.load_warning_producing_filenames()

		return None

	def load_warning_producing_filenames(self):
		with open("indexed_warning_files.json",'r') as filenames:
			self.warning_producing_files=json.load(filenames)
			self.warning_producing_files={ int(key): self.warning_producing_files[key] for key in self.warning_producing_files }
		return None

	def interaction_loop(self):
		self.get_warning_id_from_user()
		self.reproduce_warning()

		# warning_id being referenced is an unresolved reference
		while (not self.warning_resolved()):
			self.prompt_user_resolution_action()

		self.prompt_termination_option()
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

	def reproduce_warning(self):
		filepath = self.warning_producing_files[self.active_warning["warning_id"]]
		file_directory = directory_of(filepath)
		filename = get_filename(filepath)

		self.active_warning["warning_reproduction_attempts"] = 0
		build_file_directory = file_directory
		bazel_build_argument = None
		warning_reproduced=False

		while (not warning_reproduced):
			if (self.active_warning["warning_reproduction_attempts"] == 0):
				# we haven't tried using the default arugment
				bazel_build_argument = '//'+ build_file_directory[:-1] + ":" + filename[:-3]
			elif (self.active_warning["warning_reproduction_attempts"] == 1):
				build_file_directory = directory_of(build_file_directory[-1]) # check if build file is located in parent directory, as commonly true
				bazel_build_argument = '//'+ build_file_directory[:-1] + ":" + filename[:-3]
			else:
				# we've tried using the default argument and it failed
				# prompt user for correct build info
				bazel_build_info = self.prompt_user_for_build_info(filepath)
				build_file_directory= bazel_build_info['build_file_directory']
				bazel_build_argument= bazel_build_info['bazel_build_argument']


			# sph is short for subprocess helper
			clear_cache_sph= subprocess.run(['rm','-rf', 'bazel-bin/'+ build_file_directory], capture_output=True)
			print("build running, please await it's completion ( it may take a few seconds to a minute. )")
			reproduce_warning_sph= subprocess.run(['bazel','build', bazel_build_argument], capture_output=True)
			self.active_warning["warning_reproduction_attempts"] += 1

			# sph_outstream= reproduce_warning_sph.stdout.decode('utf-8')
			sph_errstream= reproduce_warning_sph.stderr.decode('utf-8')
			print( sph_errstream )

			if (reproduce_warning_sph.returncode == 0):
				warning_reproduced= ("[-Wsign-compare]" in sph_errstream) #or ("[-Wsign-compare]" in sph_outstream)

		self.active_warning["build_file_directory"]=build_file_directory
		self.active_warning["bazel_build_argument"]=bazel_build_argument
		self.active_warning["resolution_attempts"] = 0
		return None

	def warning_resolved(self):
		warning_resolved = False

		# run build again and confirm build success AND no "[-Wsign-compare]" flags
		if ( self.active_warning["resolution_attempts"] > 0 ):
			print("Build running, please await it's completion ( it may take a few seconds to a minute.")
			[ print("-"*10) for i in range(5)]
			clear_cache_sph= subprocess.run(['rm','-rf', 'bazel-bin/'+ self.active_warning["build_file_directory"]], capture_output=True)
			confirm_resolution_sph= subprocess.run(['bazel','build', self.active_warning["bazel_build_argument"]], capture_output=True)

			sph_errstream= confirm_resolution_sph.stderr.decode('utf-8')
			print( sph_errstream )

			if (confirm_resolution_sph.returncode == 0):
				warning_resolved= ("[-Wsign-compare]" not in sph_errstream)

		return warning_resolved

	def prompt_user_resolution_action(self):
		self.active_warning["resolution_attempts"] += 1
		filepath = self.warning_producing_files[self.active_warning["warning_id"]]
		print("!!! {}".format(filepath))
		fix_warning_sph= subprocess.run(['gedit', filepath])
		input("Press enter when done editing:")
		return None

	def prompt_user_for_build_info(self, filepath):
		print("You are seeing this message becuase the because the default build arguments did not succeed in producing the relevant build.")
		print("The associated file is:\n{}".format(filepath))
		filename = get_filename(filepath)

		help_page_url = "https://cs.opensource.google/search?q=" + filename + "%20&ss=tensorflow%2Ftensorflow"
		webbrowser.open(help_page_url)
		build_file_directory= input('Enter the directory of the BUILD for the above file: ')

		if ( (build_file_directory == "") or (build_file_directory == "s") ):
			build_file_directory = directory_of(filepath)[:-1]
		elif ( (build_file_directory == " ") or (build_file_directory == "p") ):
			build_file_directory = directory_of( directory_of(filepath)[-1] )[:-1]

		build_alias = input('Enter the build alias of the relevant build: ')

		bazel_build_info_object = {
			"build_file_directory": build_file_directory,
			"bazel_build_argument": '//'+ build_file_directory + ":" + build_alias
		}

		return bazel_build_info_object

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

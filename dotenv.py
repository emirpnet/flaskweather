# load_dotenv.py
# Version: 0.2 (2020-11-14)
# Author: Jochen Peters

import sys, os


def print_os_environ():
	for k, v in os.environ.items():
		print("'", k, "'=", "'", v, "'", sep='')


def remove_enclosing_quotes(s):
	if (s[0]=='"' and s[-1]=='"') or (s[0]=="'" and s[-1]=="'"):
		return s[1:-1]
	else:
		return s


def load_dotenv(filename='.env'):
	try:
		with open(filename, 'r') as f:
			lines = f.readlines()
	except IOError:
		print('WARNING ' , load_dotenv.__name__, ': could not read file "', filename, '"', sep='', file=sys.stderr)
		return

	if lines:
		dotenv_dict = parse_dotenv(lines)
		add_to_environment_variables(dotenv_dict)


def parse_dotenv(lines):
	dotenv_dict = {}
	for line_number, s in enumerate(lines):
		# ignore stuff
		s = s.strip()
		if s[0] == '#': # ignore comment lines
			continue
		if s.count('=') != 1: # ignore lines with no or more than one equal sign
			print('WARNING ' , parse_dotenv.__name__, ': ignoring line ', line_number, ' (invalid)', sep='', file=sys.stderr)
			continue
		if s.startswith('export '): # ignore export statement
			s = s.replace('export ', '', 1)

		# split up key / value
		key, value = s.split('=')
		key = remove_enclosing_quotes(key.strip())
		value = remove_enclosing_quotes(value.strip())

		# add to dict
		if key in dotenv_dict:
			print('WARNING ' , parse_dotenv.__name__, ': ignoring line ', line_number, ' (key "', key, '" already defined)', sep='', file=sys.stderr)
			continue
		dotenv_dict[str(key)] = str(value)

	return dotenv_dict


def add_to_environment_variables(env_dict, override_existing=False):
	if env_dict:
		for k, v in env_dict.items():
			if k in os.environ and not override_existing:
				continue
			if v is not None:
				os.environ[str(k)] = str(v)



if __name__ == '__main__':

	if len(sys.argv) >= 2:
		load_dotenv(os.path.basename(sys.argv[1]))
	else:
		load_dotenv()

	print_os_environ()

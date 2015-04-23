import argparse

parser = argparse.ArgumentParser(description="A simple photo organizer")
parser.add_argument("src_dir", help="photo directory")
parser.add_argument("dest_dir", help="target directory")
parser.add_argument("-r", "--recursive", action="store_true", dest="recursive", default=True, help="process folders recursively")
parser.add_argument("-v", "--verbose", help="increase verbosity", action="store_true")
parser.add_argument("-d", "--dry", dest="dry", action="store_true", help="dry run")
args = parser.parse_args()

print "source folder = ", args.src_dir
print "target folder = ", args.dest_dir
print "is recursive = ", args.recursive
print "is verbose = ", args.verbose
print "is dry run = ", args.dry

import sys
import os
import argparse

def parse_arguments():
    argparser = argparse.ArgumentParser(prog="Tiny", description="Parser and type system for the Tiny language")
    argparser.add_argument(
        "src_file",
        metavar="SOURCE_FILE",
        help="path to source file that contains tiny code"
    )
    return argparser.parse_args()

def cli():
    args = parse_arguments()

    abs_src = os.path.abspath(args.src_file)
    if not os.path.exists(abs_src):
        print("Specified source file path " + abs_src + " is invalid or doesn't exist.\nPlease try again with a valid source.")
        sys.exit()
    l = len(abs_src)
    if abs_src[l-4:] != 'tiny':
        print("Source file path " + abs_src + " should be of type .tiny")
        sys.exit()
    src = abs_src

    return src
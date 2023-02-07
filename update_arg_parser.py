import os
import argparse


def _dir_path(path: str) -> str:
    path = str(path)
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"Dir: {path} is not a valid path")


def _setup_list_version_parser(parser: argparse.ArgumentParser):
    parser.add_argument("-p", "--product", help="Product name", required=True, type=str, dest="product")


def _setup_add_version_parser(parser: argparse.ArgumentParser):
    parser.add_argument("-p", "--product", help="Product name", required=True, type=str, dest="product")
    parser.add_argument("-i", "--info", help="Version info json", required=True, type=argparse.FileType("r"), dest="version_info")


def _setup_replace_version_parser(parser: argparse.ArgumentParser):
    parser.add_argument("-p", "--product", help="Product name", required=True, type=str)
    parser.add_argument("-i", "--info", help="Version info json", required=True, type=argparse.FileType("r"), dest="version_info")


def _setup_delete_version_parser(parser: argparse.ArgumentParser):
    parser.add_argument("-p", "--product", help="Product name", required=True, type=str, dest="product")
    parser.add_argument("-c", "--code", help="Version code", required=True, type=int, dest="version_code")


def _setup_refresh_parser(parser: argparse.ArgumentParser):
    parser.add_argument("-p", "--product", help="Product name", required=True, type=str, dest="product")


def _setup_new_output_parser(parser: argparse.ArgumentParser):
    parser.add_argument("-n", "--name", help="Name", required=True, type=str, dest="name")
    parser.add_argument("-d", "--dest", help="Output dir", required=False, default=".", type=_dir_path, dest="dest")


def _setup_create_parser(parser: argparse.ArgumentParser):
    sub_parsers = parser.add_subparsers(dest="create", help="Create types", required=True)

    _setup_new_output_parser(sub_parsers.add_parser("version", help="New version info"))
    _setup_new_output_parser(sub_parsers.add_parser("product", help="New product"))


def get_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Update generator command controller")

    sub_parsers = parser.add_subparsers(title="Commands", dest="command", required=True)

    sub_parsers.add_parser("launch", help="Launch interactive UI")

    _setup_create_parser(sub_parsers.add_parser("create", help="Create file or folder"))

    _setup_list_version_parser(sub_parsers.add_parser("list", help="List versions"))
    _setup_add_version_parser(sub_parsers.add_parser("add", help="Add version"))
    _setup_replace_version_parser(sub_parsers.add_parser("replace", help="Replace version"))
    _setup_delete_version_parser(sub_parsers.add_parser("delete", help="Delete version"))
    _setup_refresh_parser(sub_parsers.add_parser("refresh", help="Refresh version index and latest info"))

    return parser

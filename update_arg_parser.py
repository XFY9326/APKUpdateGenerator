import os
import argparse


def _dir_path(path: str) -> str:
    path = str(path)
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"Dir: {path} is not a valid path")


def _file_path(path: str) -> str:
    path = str(path)
    if os.path.isfile(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"File: {path} is not a valid path")


def _parse_product(parser: argparse.ArgumentParser):
    parser.add_argument("-p", "--product", help="Product name", required=True, type=str, dest="product")


def _parse_product_version(parser: argparse.ArgumentParser):
    _parse_product(parser)
    parser.add_argument("-i", "--info", help="Version info json", required=True, type=_file_path, dest="version_info")


def _parse_new_output(parser: argparse.ArgumentParser):
    parser.add_argument("-n", "--name", help="Name", required=True, type=str, dest="name")
    parser.add_argument("-d", "--dest", help="Output dir", required=False, default=".", type=_dir_path, dest="dest")


def _setup_delete_version_parser(parser: argparse.ArgumentParser):
    _parse_product(parser)
    parser.add_argument("-c", "--code", help="Version code", required=True, type=int, dest="version_code")


def _setup_show_parser(parser: argparse.ArgumentParser):
    sub_parsers = parser.add_subparsers(title="Show", dest="show", required=True, metavar="<type>")

    sub_parsers.add_parser("products", help="Show products")
    _parse_product(sub_parsers.add_parser("versions", help="Show versions"))


def _setup_refresh_parser(parser: argparse.ArgumentParser):
    sub_parsers = parser.add_subparsers(title="Refresh types", dest="refresh", required=True, metavar="<type>")

    _parse_product(sub_parsers.add_parser("all", help="Refresh all"))
    _parse_product(sub_parsers.add_parser("index", help="Refresh version index"))
    _parse_product(sub_parsers.add_parser("latest", help="Refresh latest version"))


def _setup_create_parser(parser: argparse.ArgumentParser):
    sub_parsers = parser.add_subparsers(title="Create types", dest="create", required=True, metavar="<type>")

    _parse_new_output(sub_parsers.add_parser("version", help="New version info"))
    _parse_new_output(sub_parsers.add_parser("product", help="New product"))


def parse_args(args: list[str]) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Update generator command controller")

    sub_parsers = parser.add_subparsers(title="Commands", dest="command", required=True, metavar="<command>")

    _setup_create_parser(sub_parsers.add_parser("create", help="Create file or folder"))
    _setup_show_parser(sub_parsers.add_parser("show", help="Show versions"))
    _parse_product_version(sub_parsers.add_parser("add", help="Add version"))
    _parse_product_version(sub_parsers.add_parser("replace", help="Replace version"))
    _setup_delete_version_parser(sub_parsers.add_parser("delete", help="Delete version"))
    _setup_refresh_parser(sub_parsers.add_parser("refresh", help="Refresh version index and latest info"))

    return parser.parse_args(args)

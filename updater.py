import os
import sys
import argparse
from update_arg_parser import parse_args
from update_controller import UpdateCommandController, UpdateInteractiveController

WORK_DIR = os.path.realpath(os.path.dirname(__file__))
SOURCE_ROOT = os.path.join(WORK_DIR, "Updates")
NEW_VERSIONS_ROOT = os.path.join(WORK_DIR, "NewVersions")
RECENT_INDEX_LENGTH = 15


def interactive_start_menu():
    UpdateInteractiveController.show_banner()
    product = UpdateInteractiveController.get_product(SOURCE_ROOT)
    if product is not None:
        controller = UpdateInteractiveController(product, SOURCE_ROOT, RECENT_INDEX_LENGTH, NEW_VERSIONS_ROOT)
        controller.launch_interactive_menu()


def command_control_handler(args: argparse.Namespace):
    controller = UpdateCommandController(SOURCE_ROOT, RECENT_INDEX_LENGTH)
    controller.execute_commands(args)


def main():
    if len(sys.argv) > 1:
        args = parse_args(sys.argv[1:])
        command_control_handler(args)
    else:
        interactive_start_menu()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExit")

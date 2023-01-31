import os
from update_controller import UpdateController

WORK_DIR = os.path.realpath(os.path.dirname(__file__))
SOURCE_ROOT = os.path.join(WORK_DIR, "Updates")
NEW_VERSIONS_ROOT = os.path.join(WORK_DIR, "NewVersions")
RECENT_INDEX_LENGTH = 15


__author__ = "XFY9326"
__version__ = "0.1"
__website__ = "https://github.com/XFY9326/APKUpdateGenerator"


def show_title():
    print("Update generator\n")
    print(f"Made by {__author__}")
    print(f"Version: {__version__}")
    print(f"Website: {__website__}")
    print()


def launch_update_generator():
    product = UpdateController.get_product(SOURCE_ROOT)
    if product is not None:
        controller = UpdateController(product, SOURCE_ROOT, NEW_VERSIONS_ROOT, RECENT_INDEX_LENGTH)
        controller.launch_product_functions()


def main():
    show_title()
    launch_update_generator()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExit")

import os
from update_controller import UpdateController

WORK_DIR = os.path.realpath(os.path.dirname(__file__))
SOURCE_ROOT = os.path.join(WORK_DIR, "Updates")
NEW_VERSIONS_ROOT = os.path.join(WORK_DIR, "NewVersions")
RECENT_INDEX_LENGTH = 15


def main():
    product = UpdateController.get_product(SOURCE_ROOT)
    if product is not None:
        controller = UpdateController(product, SOURCE_ROOT, NEW_VERSIONS_ROOT, RECENT_INDEX_LENGTH)
        controller.launch_product_functions()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nExit")

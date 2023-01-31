from typing import Union, Optional, Callable


def print_divider(c: str = "-", n: int = 50):
    print(c * n + "\n")


class UpdateViewMenus:
    @staticmethod
    def _choose_ui(title: str, sections: list[str], otherwise: Optional[str] = "<Exit>") -> Optional[int]:
        print_divider()
        print(title)
        num_len = len(str(len(sections)))
        for i, section in enumerate(sections):
            print(f"{i + 1:{num_len}d} -> {section}")
        if otherwise is not None:
            print(f"{0:{num_len}d} -> {otherwise}")
        print()
        result: Union[bool, int, None] = True
        while result is True:
            try:
                result = int(input("Input: ").strip())
                if 0 <= result <= len(sections):
                    if result == 0:
                        if otherwise is None:
                            print("Unknown otherwise input!")
                        else:
                            result = None
                    else:
                        result = result - 1
                else:
                    print("Unknown input!")
            except ValueError:
                print("Invalid input!")
        print()
        return result

    @staticmethod
    def product_functions_menu(
        product: str,
        on_list_versions: Callable[[], None],
        on_add_version: Callable[[], None],
        on_replace_version: Callable[[], None],
        on_delete_version: Callable[[], None],
    ):
        sections = ["List versions", "Add version", "Replace version", "Delete version"]
        actions = [on_list_versions, on_add_version, on_replace_version, on_delete_version]
        while True:
            choice = UpdateViewMenus._choose_ui(f"Current Product: {product}", sections)
            if choice is not None:
                actions[choice]()
            else:
                break

    @staticmethod
    def choose_version_template_menu(new_versions: list[str]) -> Optional[str]:
        choice = UpdateViewMenus._choose_ui("Choose version template file", new_versions, "<New version file>")
        return new_versions[choice] if choice is not None else None

    @staticmethod
    def choose_product_menu(products: list[str]) -> Optional[str]:
        choice = UpdateViewMenus._choose_ui("Choose new product", products, "<New product>")
        return products[choice] if choice is not None else None


class UpdateViewInputs:
    _INVALID_FILE_NAME_SYMBOLS = ["/", "\\", "?", "*", ":", "<", ">", '"', "|"]

    @staticmethod
    def _new_file_name(title: str, validator: Callable[[str], bool]) -> Optional[str]:
        print(title)
        result = input("Input: ").strip()
        if result.isspace() or len(result) == 0:
            print("Empty name!")
        else:
            for i in result:
                if i in UpdateViewInputs._INVALID_FILE_NAME_SYMBOLS:
                    print(f"Invalid symbols '{i}' in name '{result}'!")
                    return None
            if validator(result):
                return result
        return None

    @staticmethod
    def _get_version_code(title: str, validator: Callable[[int], bool]) -> Optional[int]:
        print(title)
        result = input("Input version code: ").strip()
        if result.isdigit():
            result = int(result)
            if result < 0:
                print("Invalid version code")
            elif validator(result):
                return result
        else:
            print("Version code must be digit!")
        return None

    @staticmethod
    def _yes_or_no(msg: str, default: Optional[bool] = None) -> bool:
        if default is None:
            hint = "(y/n)"
        elif default:
            hint = "(Y/n)"
        else:
            hint = "(y/N)"
        while True:
            result = input(f"{msg} {hint}: ").strip().lower()
            if (result is None or result.isspace() or len(result) == 0) and default is not None:
                return default
            elif result == "y" or result == "yes":
                return True
            elif result == "n" or result == "no":
                return False
            else:
                print("Unknown input! Input should be 'y, yes, n or no'!")

    @staticmethod
    def create_new_version_template(validator: Callable[[str], bool]) -> Optional[str]:
        return UpdateViewInputs._new_file_name("Please enter a new version template name (without .json)", validator)

    @staticmethod
    def create_new_product(validator: Callable[[str], bool]) -> Optional[str]:
        return UpdateViewInputs._new_file_name("Please enter a new product name", validator)

    @staticmethod
    def get_delete_version_code(validator: Callable[[int], bool]) -> Optional[int]:
        return UpdateViewInputs._get_version_code("Please enter a version code to delete", validator)

    @staticmethod
    def validate_delete_version(version_code: int, version_name: str) -> bool:
        return UpdateViewInputs._yes_or_no(f"Are you sure to delete {version_name} ({version_code})", False)

    @staticmethod
    def validate_replace_version(version_code_new: int, version_name_new: str, version_code: int, version_name: str) -> bool:
        return UpdateViewInputs._yes_or_no(
            f"Are you sure to replace {version_name} ({version_code}) with {version_name_new} ({version_code_new})", False
        )


class UpdateViewOutputs:
    @staticmethod
    def list_versions(versions: list[int], show_cols: int = 10):
        if len(versions) == 0:
            print("No versions available!")
        else:
            num_length = len(str(max(versions)))
            print("Versions:")
            for i in range(0, len(versions), show_cols):
                print("\t".join([f"{versions[i + o]:{num_length}d}" for o in range(show_cols) if i + o < len(versions)]))

    @staticmethod
    def new_version_template_created(path: str):
        print(f"New version template created in '{path}'. Edit it before using!")

    @staticmethod
    def file_name_exist(name: str, path: str):
        print(f"File or folder '{name}' exists in '{path}'!")

    @staticmethod
    def new_product_created(name: str):
        print(f"New product '{name}' created")

    @staticmethod
    def unknown_version_code(version_code: int):
        print(f"Unknown version code {version_code}!")

    @staticmethod
    def same_version_code_exists(version_code: int):
        print(f"Same version code {version_code} exists!")

    @staticmethod
    def new_version_added(version_code: int, version_name: str):
        print(f"New version {version_name} ({version_code}) added!")

    @staticmethod
    def new_version_replaced(version_code: int, version_name: str):
        print(f"New version {version_name} ({version_code}) replaced!")

    @staticmethod
    def version_deleted(version_code: int, version_name: str):
        print(f"Version {version_name} ({version_code}) deleted!")

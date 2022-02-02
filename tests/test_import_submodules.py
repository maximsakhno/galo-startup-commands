from galo_startup_commands import import_submodules


def test_module_with_nested_modules() -> None:
    import tests.test_module
    import tests.test_module.test_submodule1
    import tests.test_module.test_submodule1.test_subsubmodule
    import tests.test_module.test_submodule2

    expected_result = {
        tests.test_module,
        tests.test_module.test_submodule1,
        tests.test_module.test_submodule1.test_subsubmodule,
        tests.test_module.test_submodule2,
    }

    assert set(import_submodules(tests.test_module)) == expected_result


def test_module_without_nested_modules() -> None:
    import tests.test_module.test_submodule2

    expected_result = {
        tests.test_module.test_submodule2,
    }

    assert set(import_submodules(tests.test_module.test_submodule2)) == expected_result

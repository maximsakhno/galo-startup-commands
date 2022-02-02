from galo_startup_commands import fetch_startup_commands


def test_fetch_startup_commands() -> None:
    import tests.test_module.test_submodule1.test_subsubmodule

    expected_result = {
        getattr(tests.test_module.test_submodule1.test_subsubmodule.startup1, "startup_command"),
        getattr(tests.test_module.test_submodule1.test_subsubmodule.startup2, "startup_command"),
    }

    assert (
        set(fetch_startup_commands(tests.test_module.test_submodule1.test_subsubmodule))
        == expected_result
    )

def pytest_addoption(parser):
    parser.addoption("--exe", action="store", default="py.exe",
                     help="Path to the py.exe program.")

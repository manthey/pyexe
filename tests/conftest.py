def pytest_addoption(parser):
    parser.addoption('--exe', action='store', default='py.exe',
                     help='Path to the py.exe program.')


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        'pyexe: the test only applies to the stand-alone executable.')

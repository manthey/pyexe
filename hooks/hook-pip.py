from PyInstaller.utils.hooks import collect_data_files, copy_metadata

datas = collect_data_files('pip')  # codespell:ignore datas
datas += copy_metadata('pip')  # codespell:ignore datas
datas += copy_metadata('setuptools')  # codespell:ignore datas

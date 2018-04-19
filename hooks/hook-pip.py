from PyInstaller.utils.hooks import collect_data_files, copy_metadata
datas = collect_data_files('pip')
datas += copy_metadata('pip')
datas += copy_metadata('setuptools')

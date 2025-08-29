c = get_config()

c.ServerApp.ip = '0.0.0.0'
c.ServerApp.port = 8888
c.ServerApp.open_browser = False
c.ServerApp.allow_root = True
c.ServerApp.notebook_dir = '/workspace/notebooks'

c.NotebookApp.iopub_data_rate_limit = 10000000
c.NotebookApp.rate_limit_window = 3.0

c.ContentsManager.allow_hidden = True
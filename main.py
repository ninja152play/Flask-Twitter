import os
from app.app import create_app

app = create_app()

if __name__ == '__main__':
    app.run()
    # dist_path = os.path.join(os.path.dirname(__file__), 'dist')
    # app.run(extra_files=[os.path.join(dist_path, 'index.html')])
    #To prod remove debug=True
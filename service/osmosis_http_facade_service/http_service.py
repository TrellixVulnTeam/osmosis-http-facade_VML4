#!/usr/bin/env python
import os
import tempfile
import shutil
import logging
import osmosis_http_facade_service.data_store as data_store
from flask import Flask, render_template, request, Response, redirect, url_for, send_file
from werkzeug import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = "/tmp/osmosis_facade/cache"
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['tar.gz', "gz"])


logger = logging.getLogger(__name__)

def mkdir_p(pathname):
    try:
        (destination) = os.makedirs( pathname, exist_ok=True )
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


class Service(object):
    def __init__(self, address):
        self.address = address
        self.data_store = data_store.OsmosisDataStore(address="osmosis.dc1:1010")

    def run(self):
        ip, port = self.address.split(':')
        app.run(host=ip, port=int(port), debug=True, use_reloader=True)

    # For a given file, return whether it's an allowed type or not
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']
    
    @app.route('/labels/<string:label>', methods=['DELETE'])
    def delete_label(label):
        try:
            self.data_store.remove(label)
            return Response(response={"status": "deleted"},
                            status=200,
                            mimetype="application/json")
        except:
            error = {"message": "Error in osmosis server.", "command": command}
            return Response(response=error,
                            status=400,
                            mimetype="application/json")
    
    @app.route('/labels/<string:label>', methods=['GET'])
    def download_file(label):
        archive = self.data_store.remove(label)
        res = send_file(archive)
        os.remove(archive)
        return res
    
    
    @app.route('/labels/<string:label>', methods=['POST'])
    def upload_file(label):
        f = request.files['file']
        if f and allowed_file(f.filename):
            try:
                filename = secure_filename(f.filename)
                temp_dir = tempfile.mkdtemp(prefix='osmosis_facade_')
                #archive=os.path.join(app.config['UPLOAD_FOLDER'], filename)
                archive=os.path.join(temp_dir, filename)
                f.save(archive)
                self.data_store(label, archive)
            finally:
                shutil.rmtree(temp_dir)
            # cleanup
            return Response(response=filename,
                            status=202,
                            mimetype="application/json")

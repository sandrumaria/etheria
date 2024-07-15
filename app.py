from flask import Flask, request, redirect, url_for, flash
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.secret_key = 'supersecretkey'

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file multiple>
      <input type=submit value=Upload>
    </form>
    '''

@app.route('/', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    files = request.files.getlist('file')
    for file in files:
        if file and allowed_file(file.filename):
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            send_to_vm(file_path, filename)
            flash(f'File {filename} uploaded and sent to VM')
    return redirect(url_for('index'))

def send_to_vm(local_path, filename):
    # Replace these with your VM details
    vm_ip = "108.142.172.30"
    vm_username = "azureuser"
    ssh_key_path = "C:/Users/mariasandru/.ssh/id_rsa"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(vm_ip, username=vm_username, key_filename=ssh_key_path)

    sftp = ssh.open_sftp()
    remote_path = f'/path/on/vm/{filename}'
    sftp.put(local_path, remote_path)
    sftp.close()
    ssh.close()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
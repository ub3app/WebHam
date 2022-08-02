from flask import Flask, render_template, request
app = Flask(__name__)

#from .rigctlproxy import RigctlProxy

@app.route("/hello")
def hello():
    return "Hello World!"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    username = request.args.get('username')
    password = request.args.get('password')
    return "username = " + str(username or '') + ", password = " + str(password or '')

if __name__ == "__main__":
    #rp = RigctlProxy()
    #rp.greet()
    app.run(host='0.0.0.0', port=5000)

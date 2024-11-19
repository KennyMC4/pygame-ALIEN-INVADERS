from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Tu proyecto Pygame está funcionando en Render, pero los gráficos no pueden mostrarse aquí."

if __name__ == '__main__':
    app.run(debug=True, port=5000)

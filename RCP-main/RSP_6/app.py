from flask import Flask, render_template, jsonify
import logging
import os
from time import time
from functools import wraps

app = Flask(__name__)

# Путь к директории логов
log_directory = 'logs'
# Создание директории, если она не существует
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_directory, 'flask_log.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/hello', methods=['GET'])
def say_hello():
    logger.info("Received request to /hello")
    return jsonify(message="Hello, World!"), 200

@app.route('/testError', methods=['GET'])
def generate_error():
    logger.warning("Simulated error requested")
    # Изменение сообщения на более психотерапевтическое
    return jsonify(error="Что-то пошло не так!", message="Это всего лишь имитация ошибки. Попробуйте еще раз."), 500

def log_execution_time(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        start_time = time()
        result = fn(*args, **kwargs)
        execution_time = time() - start_time
        logger.info("Executed %s in %.2f ms", fn.__name__, execution_time * 1000)
        return result
    return wrapper

@app.route('/time', methods=['GET'])
@log_execution_time
def execution_time():
    time.sleep(0.5)
    # Изменение сообщения по завершению
    return jsonify(message="Время выполнения метода составило 500 миллисекунд."), 200

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error("An error occurred: %s", str(e), exc_info=True)
    return jsonify(error="Внутренняя ошибка сервера", message=str(e)), 500

if __name__ == "__main__":
    app.run(debug=True)

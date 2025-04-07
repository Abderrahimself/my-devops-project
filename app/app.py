import os
import json
import logging
import uuid
from datetime import datetime
from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(_name_)

# Custom JSON formatter for logs
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        # Add request info if available
        if hasattr(record, 'request_id'):
            log_record["request_id"] = record.request_id
        if hasattr(record, 'user_agent'):
            log_record["user_agent"] = record.user_agent
        if hasattr(record, 'ip'):
            log_record["ip"] = record.ip
        
        return json.dumps(log_record)

# Add a JSON file handler
json_handler = logging.FileHandler("logs/app.json")
json_handler.setFormatter(JsonFormatter())
logger.addHandler(json_handler)

app = Flask(_name_)

# Database connection function
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'postgres'),
            database=os.getenv('DB_NAME', 'taskdb'),
            user=os.getenv('DB_USER', 'devops'),
            password=os.getenv('DB_PASSWORD', 'devops_password'),
            cursor_factory=RealDictCursor
        )
        conn.autocommit = True
        logger.info("Database connection established")
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        return None

# Initialize database table
def init_db():
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS tasks (
                        id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        description TEXT,
                        completed BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP
                    )
                ''')
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization error: {str(e)}")
        finally:
            conn.close()

# Request middleware to add request info to logs
@app.before_request
def before_request():
    request.request_id = str(uuid.uuid4())
    
    # Add request context to log records
    old_factory = logging.getLogRecordFactory()
    def record_factory(*args, **kwargs):
        record = old_factory(*args, **kwargs)
        record.request_id = request.request_id
        record.ip = request.remote_addr
        record.user_agent = request.headers.get('User-Agent', '')
        return record
    
    logging.setLogRecordFactory(record_factory)
    
    # Log the request
    logger.info(f"Request: {request.method} {request.path}")

@app.route('/health', methods=['GET'])
def health_check():
    logger.info("Health check endpoint called")
    
    # Check database connection
    conn = get_db_connection()
    db_status = "connected" if conn else "disconnected"
    if conn:
        conn.close()
    
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": db_status
    })

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    conn = get_db_connection()
    if not conn:
        logger.error("Failed to connect to database")
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM tasks ORDER BY created_at DESC")
            tasks = cur.fetchall()
        logger.info(f"Retrieved {len(tasks)} tasks")
        return jsonify(list(tasks))
    except Exception as e:
        logger.error(f"Error retrieving tasks: {str(e)}")
        return jsonify({"error": "Failed to retrieve tasks"}), 500
    finally:
        conn.close()

@app.route('/api/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    conn = get_db_connection()
    if not conn:
        logger.error("Failed to connect to database")
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
            task = cur.fetchone()
            
        if task:
            logger.info(f"Retrieved task with ID: {task_id}")
            return jsonify(task)
        else:
            logger.warning(f"Task with ID {task_id} not found")
            return jsonify({"error": "Task not found"}), 404
    except Exception as e:
        logger.error(f"Error retrieving task: {str(e)}")
        return jsonify({"error": "Failed to retrieve task"}), 500
    finally:
        conn.close()

@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    if not data or 'title' not in data:
        logger.error("Invalid task data provided")
        return jsonify({"error": "Invalid task data"}), 400
    
    task_id = str(uuid.uuid4())
    now = datetime.now()
    
    conn = get_db_connection()
    if not conn:
        logger.error("Failed to connect to database")
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO tasks (id, title, description, created_at) VALUES (%s, %s, %s, %s) RETURNING *",
                (task_id, data['title'], data.get('description', ''), now)
            )
            task = cur.fetchone()
        
        logger.info(f"Created new task with ID: {task_id}")
        return jsonify(task), 201
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        return jsonify({"error": "Failed to create task"}), 500
    finally:
        conn.close()

@app.route('/api/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    if not data:
        logger.error("Invalid update data provided")
        return jsonify({"error": "Invalid data"}), 400
    
    conn = get_db_connection()
    if not conn:
        logger.error("Failed to connect to database")
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        # First check if task exists
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
            task = cur.fetchone()
            
        if not task:
            logger.warning(f"Attempted to update non-existent task with ID: {task_id}")
            return jsonify({"error": "Task not found"}), 404
        
        # Build the update query
        update_fields = []
        params = []
        
        if 'title' in data:
            update_fields.append("title = %s")
            params.append(data['title'])
            
        if 'description' in data:
            update_fields.append("description = %s")
            params.append(data['description'])
            
        if 'completed' in data:
            update_fields.append("completed = %s")
            params.append(data['completed'])
            
        update_fields.append("updated_at = %s")
        params.append(datetime.now())
        
        # Add task_id as the last parameter
        params.append(task_id)
        
        # Execute the update
        with conn.cursor() as cur:
            query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = %s RETURNING *"
            cur.execute(query, params)
            updated_task = cur.fetchone()
        
        logger.info(f"Updated task with ID: {task_id}")
        return jsonify(updated_task)
    except Exception as e:
        logger.error(f"Error updating task: {str(e)}")
        return jsonify({"error": "Failed to update task"}), 500
    finally:
        conn.close()

@app.route('/api/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    conn = get_db_connection()
    if not conn:
        logger.error("Failed to connect to database")
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        # First check if task exists
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
            task = cur.fetchone()
            
        if not task:
            logger.warning(f"Attempted to delete non-existent task with ID: {task_id}")
            return jsonify({"error": "Task not found"}), 404
        
        # Delete the task
        with conn.cursor() as cur:
            cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        
        logger.info(f"Deleted task with ID: {task_id}")
        return jsonify({"message": "Task deleted successfully"})
    except Exception as e:
        logger.error(f"Error deleting task: {str(e)}")
        return jsonify({"error": "Failed to delete task"}), 500
    finally:
        conn.close()

# Generate some logs periodically for testing
@app.route('/api/generate-logs', methods=['POST'])
def generate_logs():
    count = request.json.get('count', 10)
    logger.info(f"Generating {count} test log entries")
    
    for i in range(count):
        level = "INFO" if i % 5 != 0 else ("WARNING" if i % 10 != 0 else "ERROR")
        if level == "INFO":
            logger.info(f"Test log entry #{i+1}: This is a sample log message for testing")
        elif level == "WARNING":
            logger.warning(f"Test log entry #{i+1}: This is a warning log message for testing")
        else:
            logger.error(f"Test log entry #{i+1}: This is an error log message for testing")
    
    return jsonify({"message": f"Generated {count} log entries"}), 201

if _name_ == '_main_':
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Initialize database
    init_db()
    
    # Start the application
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting application on port {port}")
    app.run(host='0.0.0.0', port=port)
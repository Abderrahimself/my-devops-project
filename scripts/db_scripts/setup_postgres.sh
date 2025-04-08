# #!/bin/bash

# echo "Setting up PostgreSQL for log storage..."

# # Create logs table in PostgreSQL
# docker exec postgres-db psql -U devops -d taskdb -c "
# CREATE TABLE IF NOT EXISTS logs (
#     id SERIAL PRIMARY KEY,
#     timestamp TIMESTAMP WITH TIME ZONE,
#     level TEXT,
#     message TEXT,
#     module TEXT,
#     function TEXT,
#     line INTEGER,
#     request_id TEXT,
#     user_agent TEXT,
#     ip TEXT,
#     raw_log JSONB,
#     created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
# );

# CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp);
# CREATE INDEX IF NOT EXISTS idx_logs_level ON logs(level);
# CREATE INDEX IF NOT EXISTS idx_logs_request_id ON logs(request_id);
# "

# echo "PostgreSQL setup completed!"

#!/bin/bash

echo "Setting up PostgreSQL for log storage..."

# Get the container ID of the postgres container
POSTGRES_CONTAINER=$(docker ps --filter "name=postgres" -q | head -n 1)

if [ -z "$POSTGRES_CONTAINER" ]; then
    echo "Error: PostgreSQL container not found. Skipping setup."
    exit 0
fi

# Create logs table in PostgreSQL
docker exec $POSTGRES_CONTAINER psql -U devops -d taskdb -c "
CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE,
    level TEXT,
    message TEXT,
    module TEXT,
    function TEXT,
    line INTEGER,
    request_id TEXT,
    user_agent TEXT,
    ip TEXT,
    raw_log JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_logs_level ON logs(level);
CREATE INDEX IF NOT EXISTS idx_logs_request_id ON logs(request_id);
"

echo "PostgreSQL setup completed!"
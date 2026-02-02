# Dockerfile for PostgreSQL Database - Production
FROM postgres:15-alpine

# Set environment variables
ENV POSTGRES_DB=todo_app
ENV POSTGRES_USER=todo_user
ENV POSTGRES_PASSWORD=password

# Copy initialization scripts
COPY database/init-scripts/ /docker-entrypoint-initdb.d/

# Expose port
EXPOSE 5432

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}

# Start PostgreSQL
CMD ["postgres"]
#!/bin/bash
# Docker management script for Notion Report Generator

CONTAINER_NAME="notion-report-generator"

case "$1" in
    "start")
        echo "🚀 Starting Notion Report Generator container..."
        docker start $CONTAINER_NAME
        echo "   Web interface: http://localhost:8080"
        ;;
    "stop")
        echo "🛑 Stopping Notion Report Generator container..."
        docker stop $CONTAINER_NAME
        ;;
    "restart")
        echo "🔄 Restarting Notion Report Generator container..."
        docker restart $CONTAINER_NAME
        echo "   Web interface: http://localhost:8080"
        ;;
    "logs")
        echo "📋 Showing logs for Notion Report Generator container..."
        docker logs -f $CONTAINER_NAME
        ;;
    "status")
        echo "📊 Container status:"
        docker ps -a --filter name=$CONTAINER_NAME
        ;;
    "remove")
        echo "🗑️  Removing Notion Report Generator container..."
        docker rm -f $CONTAINER_NAME
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|logs|status|remove}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the container"
        echo "  stop    - Stop the container"
        echo "  restart - Restart the container"
        echo "  logs    - Show container logs"
        echo "  status  - Show container status"
        echo "  remove  - Remove the container"
        exit 1
        ;;
esac

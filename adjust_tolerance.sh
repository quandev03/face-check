#!/bin/bash

# Script to adjust face recognition tolerance

echo "🎯 Face Recognition Tolerance Adjuster"
echo "======================================"

# Function to test current tolerance
test_tolerance() {
    echo "📊 Current tolerance: $1"
    echo "Testing recognition with tolerance $1..."
    
    # Update docker-compose.yml
    sed -i.bak "s/FACE_RECOGNITION_TOLERANCE=.*/FACE_RECOGNITION_TOLERANCE=$1/" docker-compose.yml
    
    # Restart container
    echo "🔄 Restarting container with new tolerance..."
    docker-compose up -d
    
    # Wait for container to start
    sleep 5
    
    # Test health
    if curl -s http://localhost:5555/health > /dev/null; then
        echo "✅ Container restarted successfully"
        echo "🧪 Ready for testing with tolerance: $1"
    else
        echo "❌ Container failed to start"
        return 1
    fi
}

# Function to show recommendations
show_recommendations() {
    echo ""
    echo "📋 Tolerance Recommendations:"
    echo "============================="
    echo "0.3  - Very strict (fewer false positives, more false negatives)"
    echo "0.35 - Strict (good for high security)"
    echo "0.4  - Balanced (current setting)"
    echo "0.5  - Moderate (good for general use)"
    echo "0.6  - Lenient (more false positives)"
    echo ""
    echo "💡 Tips:"
    echo "- Start with 0.4 and adjust based on results"
    echo "- Lower tolerance = more strict = fewer false positives"
    echo "- Higher tolerance = more lenient = more false positives"
    echo "- Test with real images to find optimal value"
}

# Main menu
while true; do
    echo ""
    echo "Choose an option:"
    echo "1) Set tolerance to 0.3 (Very strict)"
    echo "2) Set tolerance to 0.35 (Strict)"
    echo "3) Set tolerance to 0.4 (Balanced - current)"
    echo "4) Set tolerance to 0.5 (Moderate)"
    echo "5) Set tolerance to 0.6 (Lenient)"
    echo "6) Show recommendations"
    echo "7) Test current API"
    echo "8) Exit"
    echo ""
    read -p "Enter your choice (1-8): " choice
    
    case $choice in
        1) test_tolerance 0.3 ;;
        2) test_tolerance 0.35 ;;
        3) test_tolerance 0.4 ;;
        4) test_tolerance 0.5 ;;
        5) test_tolerance 0.6 ;;
        6) show_recommendations ;;
        7) 
            echo "🧪 Testing current API..."
            curl -X GET http://localhost:5555/health
            echo ""
            curl -X GET http://localhost:5555/api/employees
            ;;
        8) 
            echo "👋 Goodbye!"
            break
            ;;
        *) echo "❌ Invalid choice. Please try again." ;;
    esac
done

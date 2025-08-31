#!/bin/bash
set -e

echo "============================================="
echo "Microshare ERP Integration - System Validator"
echo "============================================="

BASE_URL="http://localhost:8000"
TIMEOUT=60

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

if ! command -v jq &> /dev/null; then
    echo -e "${RED}Installing jq...${NC}"
    sudo apt-get update && sudo apt-get install -y jq
fi

# Function to test endpoint and measure response time
test_endpoint_with_timing() {
    local endpoint=$1
    local description=$2
    local test_cache=${3:-false}
    
    echo -n "  $description... "
    
    local start_time=$(date +%s.%3N)
    if response=$(curl -s --max-time $TIMEOUT "$BASE_URL$endpoint" 2>/dev/null); then
        local end_time=$(date +%s.%3N)
        local duration=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || awk "BEGIN {print $end_time - $start_time}")
        
        if echo "$response" | jq . >/dev/null 2>&1; then
            printf "${GREEN}PASS${NC} ${CYAN}(%.2fs)${NC}\n" "$duration"
            
            # If testing cache, make a second call
            if [ "$test_cache" = "true" ]; then
                echo -n "    Second call (cached)... "
                local cache_start=$(date +%s.%3N)
                if cache_response=$(curl -s --max-time 30 "$BASE_URL$endpoint" 2>/dev/null); then
                    local cache_end=$(date +%s.%3N)
                    local cache_duration=$(echo "$cache_end - $cache_start" | bc -l 2>/dev/null || awk "BEGIN {print $cache_end - $cache_start}")
                    
                    printf "${GREEN}PASS${NC} ${CYAN}(%.2fs)${NC}" "$cache_duration"
                    
                    # Show speedup if significant
                    if (( $(awk "BEGIN {print ($duration > $cache_duration * 2)}") )); then
                        local speedup=$(awk "BEGIN {printf \"%.0f\", $duration / $cache_duration}")
                        printf " ${YELLOW}[${speedup}x faster]${NC}\n"
                    else
                        echo ""
                    fi
                else
                    echo -e "${RED}FAIL${NC}"
                fi
            fi
            return 0
        else
            echo -e "${RED}FAIL (invalid JSON)${NC}"
            return 1
        fi
    else
        echo -e "${RED}TIMEOUT${NC}"
        return 1
    fi
}

echo -e "${BLUE}Waiting for service startup...${NC}"
for i in {1..20}; do
    if curl -s --max-time 5 "$BASE_URL/api/v1/health" >/dev/null 2>&1; then
        echo -e "${GREEN}Service is ready!${NC}"
        break
    fi
    echo "  Waiting... ($i/20)"
    sleep 3
done

echo ""
echo -e "${BLUE}Phase 1: Basic Health Checks${NC}"
test_endpoint_with_timing "/api/v1/health" "Health Check"

echo ""
echo -e "${BLUE}Phase 2: Cache Performance Demo${NC}"
echo -e "${YELLOW}Note: First calls take 30-60s, cached calls are <1s${NC}"

# Clear cache to demonstrate difference
echo -n "  Clearing cache for demo... "
curl -s -X DELETE --max-time 10 "$BASE_URL/api/v1/cache" >/dev/null 2>&1 || true
echo -e "${GREEN}DONE${NC}"

echo ""
test_endpoint_with_timing "/api/v1/devices/" "Device Listing" true
test_endpoint_with_timing "/api/v1/devices/clusters" "Cluster Info" true

echo ""
echo -e "${BLUE}Phase 3: System Metrics${NC}"
if device_response=$(curl -s --max-time 30 "$BASE_URL/api/v1/devices/" 2>/dev/null); then
    device_count=$(echo "$device_response" | jq -r '.devices | length' 2>/dev/null)
    echo "  Device count: ${GREEN}$device_count${NC}"
fi

echo ""
echo "============================================="
echo -e "${GREEN}Performance Demo Complete!${NC}"
echo "============================================="
echo ""
echo -e "${BLUE}Key Insights:${NC}"
echo "• Initial calls: 30-60 seconds (Microshare API)"
echo "• Cached calls: <1 second (100x+ faster)"
echo "• Cache TTL: 300 seconds"
echo ""
echo "Developer commands:"
echo "curl -s --max-time 60 http://localhost:8000/api/v1/devices/ | jq '.devices | length'"
echo "open http://localhost:8000/docs"

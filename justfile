# repo-autopilot generated justfile
# Ports: qdrant=6333

set dotenv-load

qdrant_port := "6333"

# 도움말 출력
default:
    @just --list

# --- Development ---

# Qdrant 개발 서버 실행 (port: 6333)
dev:
    docker run -p {{qdrant_port}}:6333 qdrant/qdrant:latest

# --- Build ---

build:
    @echo "⚠️  Build not applicable for this project."

# --- Test ---

test:
    @echo "⚠️  Test not configured. Add test commands as needed."

# --- Database (Vector DB) ---

qdrant-up:
    docker run -d -p {{qdrant_port}}:6333 --name qdrant qdrant/qdrant:latest
qdrant-down:
    docker stop qdrant && docker rm qdrant
qdrant-logs:
    docker logs -f qdrant

# --- Utility ---

check-env:
    @test -n "$OPENROUTER_API_KEY" || (echo "❌ OPENROUTER_API_KEY not set" && exit 1)
    @test -n "$GH_TOKEN" || (echo "❌ GH_TOKEN not set" && exit 1)
    @echo "✅ All env vars OK"

clean:
    docker system prune -f

# --- Deploy ---

deploy:
    @echo "⚠️  Deploy not configured. Edit this recipe for your deployment target."

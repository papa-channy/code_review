# repo-autopilot generated justfile
# Ports: qdrant=6333

set dotenv-load

qdrant_port := "6333"

# 도움말 출력
default:
    @just --list

# --- Development ---

# Qdrant 벡터 DB 개발 서버 실행 (port: 6333)
dev-qdrant:
    docker run -p {{qdrant_port}}:6333 qdrant/qdrant:latest

# 전체 개발 서버 실행 (현재 프로젝트는 벡터 DB만 포함)
dev: dev-qdrant

# --- Build ---

build:
    @echo "⚠️  Build not configured. This project appears to be a code review visualization setup."

# --- Test ---

test:
    @echo "⚠️  Test not configured. This project appears to be a code review visualization setup."

# --- Database (Vector DB) ---

qdrant-up:
    docker run -d --name qdrant -p {{qdrant_port}}:6333 qdrant/qdrant:latest
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
    docker system prune -a -f --volumes

# --- Deploy ---

deploy:
    @echo "⚠️  Deploy not configured. Edit this recipe for your deployment target."

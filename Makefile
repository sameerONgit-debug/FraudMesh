# FraudMesh Makefile
# Quick commands for development and demo

.PHONY: setup seed demo test reset clean install train db-up api-up web-up dev

# Install dependencies
install:
	pip install -r requirements.txt
	cd apps/web && npm install

# Setup databases (Docker)
db-up:
	docker-compose up -d postgres neo4j redis

# Train ML model
train:
	cd services/ml-training && python -c "from risk_engine import train_model, get_model; m = train_model(10000); get_model().save_model('apps/api/app/ml/model.pkl')"

# Seed demo data
seed:
	PYTHONPATH=/workspace python scripts/seed_demo.py

# Run full demo scenario
demo: db-up train seed
	@echo "========================================"
	@echo "FraudMesh Demo Ready!"
	@echo "========================================"
	@echo "API Docs: http://localhost:8000/docs"
	@echo "Web UI:   http://localhost:3000"
	@echo ""
	@echo "Demo scenario seeded:"
	@echo "  - Transaction: ₹85,000 (A-101 → B-781)"
	@echo "  - Case: FM-DEMO-001"
	@echo "  - Risk progression: calculated by ML"

# Run tests
test:
	pytest apps/api/tests -v

# Reset everything
reset:
	docker compose down -v
	rm -rf apps/api/app/ml/model.pkl
	rm -f /tmp/fraudmesh.db
	@echo "Reset complete. Run 'make setup' to start fresh."

# Clean build artifacts
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".DS_Store" -delete

# Full setup
setup: install db-up train seed
	@echo "========================================"
	@echo "FraudMesh Setup Complete!"
	@echo "========================================"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Start API:  cd apps/api && uvicorn app.main:app --reload"
	@echo "  2. Start Web:  cd apps/web && npm run dev"
	@echo "  3. Open:       http://localhost:8000/docs (API)"
	@echo "                 http://localhost:3000 (UI)"

# Start API server
api-up:
	cd apps/api && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Start web frontend
web-up:
	cd apps/web && npm run dev

# Development mode (all services)
dev:
	@echo "Starting FraudMesh in development mode..."
	@echo "Press Ctrl+C to stop all services"
	docker compose up -d postgres neo4j redis
	cd services/ml-training && python -c "from risk_engine import train_model, get_model; train_model(5000); get_model().save_model('apps/api/app/ml/model.pkl')" 2>/dev/null || true
	PYTHONPATH=/workspace python scripts/seed_demo.py 2>/dev/null || true
	@echo ""
	@echo "Services started:"
	@echo "  - PostgreSQL: localhost:5432"
	@echo "  - Neo4j:      localhost:7687 (browser: localhost:7474)"
	@echo "  - Redis:      localhost:6379"
	@echo ""
	@echo "Now start API and Web in separate terminals:"
	@echo "  make api-up"
	@echo "  make web-up"

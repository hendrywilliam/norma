# Makefile untuk Kubernetes Deployment Norma Parser

NAMESPACE=norma-parser
REGISTRY=registry.example.com
IMAGE_NAME=norma-parser
IMAGE_TAG=latest

.PHONY: help build push deploy delete logs status shell

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build Docker image
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

push: ## Push Docker image to registry
	docker tag $(IMAGE_NAME):$(IMAGE_TAG) $(REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)
	docker push $(REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)

create-namespace: ## Create namespace
	kubectl create namespace $(NAMESPACE) --dry-run=client -o yaml | kubectl apply -f -

create-secret: ## Create secret for database password
	@echo "Masukkan database password:"
	@read -s password; \
	kubectl create secret generic parser-secrets \
		--from-literal=DB_PASSWORD=$$password \
		-n $(NAMESPACE) --dry-run=client -o yaml | kubectl apply -f -

deploy-all: ## Deploy all resources
	kubectl apply -f namespace.yaml
	kubectl apply -f configmap.yaml -n $(NAMESPACE)
	kubectl apply -f secret.yaml -n $(NAMESPACE) || true
	kubectl apply -f pvc.yaml -n $(NAMESPACE)
	kubectl apply -f postgres-statefulset.yaml -n $(NAMESPACE)
	kubectl apply -f postgres-service.yaml -n $(NAMESPACE)
	kubectl apply -f parser-deployment.yaml -n $(NAMESPACE)
	kubectl apply -f parser-service.yaml -n $(NAMESPACE)
	kubectl apply -f ingress.yaml -n $(NAMESPACE)
	kubectl apply -f hpa.yaml -n $(NAMESPACE)

deploy: build push deploy-all ## Full deployment: build, push, and deploy

deploy-config: ## Update ConfigMap only
	kubectl apply -f configmap.yaml -n $(NAMESPACE)

deploy-parser: ## Deploy Parser API only
	kubectl apply -f parser-deployment.yaml -n $(NAMESPACE)
	kubectl rollout status deployment/parser-api -n $(NAMESPACE)

deploy-postgres: ## Deploy PostgreSQL only
	kubectl apply -f postgres-statefulset.yaml -n $(NAMESPACE)
	kubectl rollout status statefulset/postgres -n $(NAMESPACE)

delete-all: ## Delete all resources
	kubectl delete namespace $(NAMESPACE)

delete-parser: ## Delete Parser API only
	kubectl delete deployment/parser-api -n $(NAMESPACE)

delete-postgres: ## Delete PostgreSQL only
	kubectl delete statefulset/postgres -n $(NAMESPACE)
	kubectl delete pvc postgres-pvc -n $(NAMESPACE)

logs-parser: ## Show Parser API logs
	kubectl logs -f deployment/parser-api -n $(NAMESPACE)

logs-postgres: ## Show PostgreSQL logs
	kubectl logs -f statefulset/postgres -n $(NAMESPACE)

status: ## Show all resources status
	@echo "=== Pods ===="
	kubectl get pods -n $(NAMESPACE)
	@echo ""
	@echo "=== Services ===="
	kubectl get svc -n $(NAMESPACE)
	@echo ""
	@echo "=== Deployments ===="
	kubectl get deployments -n $(NAMESPACE)
	@echo ""
	@echo "=== StatefulSets ===="
	kubectl get statefulsets -n $(NAMESPACE)
	@echo ""
	@echo "=== PVC ===="
	kubectl get pvc -n $(NAMESPACE)
	@echo ""
	@echo "=== HPA ===="
	kubectl get hpa -n $(NAMESPACE)

shell-parser: ## Open shell in Parser pod
	kubectl exec -it $$(kubectl get pods -n $(NAMESPACE) -l app=parser-api -o jsonpath='{.items[0].metadata.name}') -- /bin/sh

shell-postgres: ## Open psql in PostgreSQL pod
	kubectl exec -it postgres-0 -n $(NAMESPACE) -- psql -U postgres -d peraturan_db

port-forward-api: ## Port forward Parser API to localhost:8000
	kubectl port-forward service/parser-api-service 8000:8000 -n $(NAMESPACE)

port-forward-postgres: ## Port forward PostgreSQL to localhost:5432
	kubectl port-forward service/postgres-service 5432:5432 -n $(NAMESPACE)

scale: ## Scale Parser API (usage: make scale REPLICAS=3)
	kubectl scale deployment/parser-api --replicas=$(REPLICAS) -n $(NAMESPACE)

restart-parser: ## Restart Parser API
	kubectl rollout restart deployment/parser-api -n $(NAMESPACE)

restart-postgres: ## Restart PostgreSQL
	kubectl rollout restart statefulset/postgres -n $(NAMESPACE)

backup-db: ## Backup database
	kubectl exec postgres-0 -n $(NAMESPACE) -- pg_dump -U postgres peraturan_db > backup_$$(date +%Y%m%d_%H%M%S).sql

describe-parser: ## Describe Parser deployment
	kubectl describe deployment/parser-api -n $(NAMESPACE)

describe-postgres: ## Describe PostgreSQL statefulset
	kubectl describe statefulset/postgres -n $(NAMESPACE)

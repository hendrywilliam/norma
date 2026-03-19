# Kubernetes Deployment untuk Norma Parser API

Deployments untuk Parser API dan PostgreSQL database di Kubernetes.

## Struktur Direktori

```
kubernetes/
├── namespace.yaml              # Namespace untuk semua resources
├── configmap.yaml            # Environment variables
├── secret.yaml               # Sensitive data (passwords)
├── pvc.yaml                  # Persistent Volume Claim untuk PostgreSQL
├── postgres-statefulset.yaml   # PostgreSQL StatefulSet
├── postgres-service.yaml       # PostgreSQL Service
├── parser-deployment.yaml      # Parser API Deployment
├── parser-service.yaml        # Parser API Service
├── ingress.yaml              # Ingress untuk external access
└── hpa.yaml                 # Horizontal Pod Autoscaler
```

## Prasyarat

1. Cluster Kubernetes yang sudah berjalan
2. `kubectl` sudah terinstall dan terkonfigurasi
3. Docker image `norma-parser:latest` sudah dibuat dan di-push ke registry

## Build Docker Image

```bash
# Dari root directory parser
cd /home/hendri/norma/apps/parser

# Build Docker image
docker build -t norma-parser:latest .

# Atau push ke container registry
# docker tag norma-parser:latest registry.example.com/norma-parser:latest
# docker push registry.example.com/norma-parser:latest
```

## Deployment

### 1. Buat Database Password Secret

PENTING: Ganti password default dengan password yang aman!

```bash
# Method 1: Dengan kubectl create secret command (recommended)
kubectl create secret generic parser-secrets \
  --from-literal=DB_PASSWORD=your_secure_password \
  -n norma-parser

# Method 2: Dengan apply file (edit secret.yaml dulu)
kubectl apply -f kubernetes/secret.yaml -n norma-parser
```

### 2. Apply Semua Resources

```bash
# Apply namespace dulu
kubectl apply -f kubernetes/namespace.yaml

# Apply semua resources
kubectl apply -f kubernetes/configmap.yaml -n norma-parser
kubectl apply -f kubernetes/pvc.yaml -n norma-parser
kubectl apply -f kubernetes/postgres-statefulset.yaml -n norma-parser
kubectl apply -f kubernetes/postgres-service.yaml -n norma-parser
kubectl apply -f kubernetes/parser-deployment.yaml -n norma-parser
kubectl apply -f kubernetes/parser-service.yaml -n norma-parser
kubectl apply -f kubernetes/ingress.yaml -n norma-parser
kubectl apply -f kubernetes/hpa.yaml -n norma-parser
```

Atau apply semua sekaligus:

```bash
kubectl apply -f kubernetes/ -n norma-parser
```

### 3. Cek Deployment Status

```bash
# Cek semua resources di namespace
kubectl get all -n norma-parser

# Cek pods
kubectl get pods -n norma-parser

# Cek logs
kubectl logs -f deployment/parser-api -n norma-parser

# Cek database pod
kubectl logs -f statefulset/postgres -n norma-parser
```

## Database Initialization

Setelah PostgreSQL berjalan, jalankan migrasi SQL:

```bash
# Copy SQL schema file ke pod
kubectl cp DATABASE_SCHEMA.md postgres-0:/tmp/schema.md -n norma-parser

# Atau connect langsung ke database
kubectl exec -it postgres-0 -n norma-parser -- psql -U postgres -d peraturan_db

# Jalankan migration SQL (jika ada file migrasi)
kubectl exec -it postgres-0 -n norma-parser -- psql -U postgres -d peraturan_db -f /migrations/init.sql
```

## Access API

### Port Forward (untuk testing lokal)

```bash
# Forward port API
kubectl port-forward service/parser-api-service 8000:8000 -n norma-parser

# Forward port Database (opsional)
kubectl port-forward service/postgres-service 5432:5432 -n norma-parser
```

### Via Ingress

Jika ingress sudah dikonfigurasi dengan domain:

```bash
# Access via: http://parser.norma.local
# atau HTTPS jika TLS dikonfigurasi: https://parser.norma.local

# Cek API health
curl http://parser.norma.local/api/health
curl http://parser.norma.local/api/status
```

### LoadBalancer Service (alternatif)

Jika cluster mendukung LoadBalancer, ubah `type: ClusterIP` ke `type: LoadBalancer` di `parser-service.yaml`:

```yaml
spec:
  type: LoadBalancer
  ports:
  - port: 8000
    ...
```

## Scale Application

### Manual Scaling

```bash
# Scale deployment
kubectl scale deployment parser-api --replicas=3 -n norma-parser
```

### Auto Scaling (HPA)

HorizontalPodAutoscaler sudah dikonfigurasi:
- Min replicas: 1
- Max replicas: 5
- Scale up ketika CPU > 70% atau Memory > 80%

Untuk mengubah konfigurasi HPA, edit file `hpa.yaml` lalu apply ulang:

```bash
kubectl apply -f kubernetes/hpa.yaml -n norma-parser
```

Cek status HPA:

```bash
kubectl get hpa -n norma-parser
```

## Database Backup

```bash
# Backup database dari pod
kubectl exec postgres-0 -n norma-parser -- pg_dump -U postgres peraturan_db > backup.sql

# Restore database
kubectl exec -i postgres-0 -n norma-parser -- psql -U postgres peraturan_db < backup.sql
```

## Troubleshooting

### Check Pod Issues

```bash
# Pod status
kubectl describe pod <pod-name> -n norma-parser

# Pod logs
kubectl logs <pod-name> -n norma-parser --previous

# Masuk ke pod untuk debugging
kubectl exec -it <pod-name> -n norma-parser -- /bin/sh
```

### Database Connection Issues

```bash
# Cek database pod status
kubectl get pods -l app=postgres -n norma-parser

# Cek database logs
kubectl logs postgres-0 -n norma-parser

# Test database connection dari parser pod
kubectl exec -it deployment/parser-api -n norma-parser -- python -c "
import asyncpg
async def test():
    conn = await asyncpg.connect('postgresql://postgres:password@postgres-service:5432/peraturan_db')
    print('Connected successfully!')
    await conn.close()
import asyncio
asyncio.run(test())
"
```

### Reset Deployment

```bash
# Delete semua resources
kubectl delete -f kubernetes/ -n norma-parser

# Delete namespace dan semua resources
kubectl delete namespace norma-parser

# Apply ulang
kubectl apply -f kubernetes/ -n norma-parser
```

## Configuration Variables

### ConfigMap Variables

| Variable | Default | Description |
|----------|----------|-------------|
| DB_HOST | postgres-service | Database hostname |
| DB_PORT | 5432 | Database port |
| DB_NAME | peraturan_db | Database name |
| DB_USER | postgres | Database user |
| DB_MIN_CONNECTIONS | 1 | Min database connections |
| DB_MAX_CONNECTIONS | 10 | Max database connections |
| HOST | 0.0.0.0.0 | API host |
| PORT | 8000 | API port |
| LOG_LEVEL | info | Logging level |
| RELOAD | false | Enable hot reload (dev only) |
| REQUEST_DELAY | 1 | Delay antar requests (detik) |

### Secret Variables

| Variable | Description |
|----------|-------------|
| DB_PASSWORD | Database password (GANTI!) |

## Resource Limits

### Parser API Pod
- Memory: 256Mi - 512Mi
- CPU: 200m - 500m

### PostgreSQL Pod
- Memory: 512Mi - 1Gi
- CPU: 250m - 500m
- Storage: 10Gi PersistentVolume

## Monitoring

### Health Checks

```bash
# Parser API Health
curl http://localhost:8000/api/health

# Parser API Status
curl http://localhost:8000/api/status

# List Peraturan
curl http://localhost:8000/api/peraturan
```

### Metrics

Untuk monitoring lebih lanjut, install Prometheus Operator atau ekspor metrics ke existing monitoring system.

This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Tech Stack

- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4
- **UI Components**: shadcn/ui
- **Package Manager**: Bun

## Getting Started

First, run the development server:

```bash
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Building for Production

```bash
# Install dependencies
bun install

# Build for production
bun run build

# Start production server
bun start
```

## Kubernetes Deployment

Web frontend dapat di-deploy ke Kubernetes cluster menggunakan manifest files di folder `kubernetes/`.

### Struktur Kubernetes

```
kubernetes/
├── web-deployment.yaml    # Deployment config
├── web-service.yaml       # Service config (ClusterIP)
└── web-ingress.yaml       # Ingress config
```

### Deploy ke Kubernetes

```bash
# Build Docker image
docker build -t norma-web:latest .

# Deploy ke cluster
kubectl apply -f kubernetes/

# Atau apply satu per satu
kubectl apply -f kubernetes/web-deployment.yaml
kubectl apply -f kubernetes/web-service.yaml
kubectl apply -f kubernetes/web-ingress.yaml

# Check status
kubectl get pods -n norma
kubectl get services -n norma
kubectl get ingress -n norma

# View logs
kubectl logs -f deployment/web -n norma

# Port forward untuk local testing
kubectl port-forward svc/web-service 3000:3000 -n norma
```

### Konfigurasi

Deployment menggunakan:
- **Namespace**: `norma`
- **Port**: 3000
- **Replicas**: 1
- **Resources**: 256Mi-512Mi memory, 100m-500m CPU
- **Health Check**: `/` endpoint

Environment variables:
- `NODE_ENV=production`
- `API_URL` - dari Secret `norma-secrets` (server-side only, tidak di-expose ke client)

**Arsitektur API**:
- Client mengakses backend melalui internal API routes (`/api/peraturan/*`, `/api/health`)
- API routes mengambil `API_URL` dari environment (server-side) dan melakukan fetch ke backend
- `API_URL` tidak pernah di-expose ke client-side code

### Ingress Access

Web dapat diakses melalui ingress dengan host `web.norma.local`:

```bash
# Add entry to /etc/hosts
echo "127.0.0.1 web.norma.local" | sudo tee -a /etc/hosts

# Access via browser
# http://web.norma.local
```

### Prerequisites

1. Namespace `norma` sudah dibuat:
   ```bash
   kubectl apply -f apps/kubernetes/namespace.yaml
   ```

2. NGINX Ingress Controller terinstall di cluster:
   ```bash
   kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml
   ```

3. REST API service running di namespace `norma`

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.

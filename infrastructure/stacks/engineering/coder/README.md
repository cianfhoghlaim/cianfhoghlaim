# Coder Stack - Self-Hosted Cloud IDE

This stack deploys **Coder**, an open-source platform that turns your infrastructure into a self-hosted cloud IDE. It allows you to create remote development environments (Workspaces) on your own servers, providing full parity between development and production.

## 🚀 Key Benefits

### 1. Environment Parity
Stop "works on my machine" issues by defining your development environment in code (via Dockerfiles or Terraform). Every developer on the project uses the exact same toolchain, libraries, and OS.

### 2. High-Performance Remote Dev
By hosting Coder on the **48GB MacBook M4 Max**, you can access a massive amount of RAM and CPU for compilation and testing from any low-powered device (like a tablet or an old laptop) without any lag.

### 3. Secure Access (Pangolin Integrated)
Coder is routed through **Pangolin**, providing a secure, encrypted tunnel to your workspaces. You can code from anywhere in the world without exposing SSH ports to the public internet.

### 4. Persistence & Speed
Workspaces keep their state. If you lose your connection or switch devices, your terminal, open files, and running processes are exactly where you left them.

### 5. Automated Secrets (Locket)
Locket automatically injects necessary API keys (like GitHub tokens or database credentials) into your workspaces, so you don't have to manually manage `.env` files in your IDE.

## 🛠 Usage in Cianfhoghlaim

- **Primary Host**: MacBook M4 Max (`bunchloch`)
- **Access URL**: `coder.cianfhoghlaim.ie`
- **Deployment**: Managed by **Komodo** for easy lifecycle management.

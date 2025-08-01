# 📋 CyberBlue Installation Guide

This comprehensive guide will walk you through installing and configuring CyberBlue on your system.

---

## 📋 Pre-Installation Checklist

### ✅ **System Requirements**

#### Minimum Requirements
- **Operating System**: Linux (Ubuntu 20.04+, CentOS 8+, Debian 11+)
- **CPU**: 4 cores minimum
- **RAM**: 8GB minimum
- **Storage**: 50GB free disk space
- **Network**: Internet connection for Docker image downloads

#### Recommended Requirements
- **Operating System**: Ubuntu 22.04 LTS or CentOS Stream 9
- **CPU**: 8+ cores (Intel i7/AMD Ryzen 7 or better)
- **RAM**: 16GB+ (32GB for production)
- **Storage**: 100GB+ SSD with high IOPS
- **Network**: Gigabit Ethernet

#### Supported Platforms
- ✅ **Linux**: Ubuntu, CentOS, RHEL, Debian, Fedora
- ✅ **macOS**: Intel and Apple Silicon (M1/M2)
- ✅ **Windows**: Via WSL2 (Windows Subsystem for Linux)

---

## 🐳 Docker & Docker Compose Installation

### Ubuntu/Debian Installation

```bash
# Update package index
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Enable Docker to start on boot
sudo systemctl enable docker
sudo systemctl start docker

# Verify installation
docker --version
docker compose version
```

### CentOS/RHEL Installation

```bash
# Install required packages
sudo dnf install -y dnf-utils

# Add Docker repository
sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# Install Docker Engine
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker --version
docker compose version
```

### macOS Installation

1. Download Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop)
2. Install the `.dmg` file
3. Start Docker Desktop
4. Verify installation in terminal:
   ```bash
   docker --version
   docker compose version
   ```

---

## 📥 Downloading CyberBlue

### Method 1: Git Clone (Recommended)

```bash
# Clone the repository
git clone https://github.com/m7siri/cyber-blue-project.git

# Navigate to directory
cd cyber-blue-project

# Verify files
ls -la
```

### Method 2: Download ZIP

```bash
# Download and extract
wget https://github.com/m7siri/cyber-blue-project/archive/main.zip
unzip main.zip
cd cyber-blue-project-main
```

---

## ⚙️ Configuration

### 1. Environment Configuration

```bash
# Copy environment template
cp .env.template .env

# Edit configuration file
nano .env
```

### 2. Environment Variables

Configure the following variables in `.env`:

```bash
# =================================
# NETWORK CONFIGURATION
# =================================
HOST_IP=10.0.0.40                    # Your server's IP address
NETWORK_SUBNET=172.18.0.0/16         # Docker internal network
PORTAL_PORT=5500                     # CyberBlue portal port

# =================================
# SECURITY CONFIGURATION
# =================================
WAZUH_ADMIN_PASSWORD=SecurePass123!
OPENSEARCH_ADMIN_PASSWORD=SecurePass123!
MISP_ADMIN_EMAIL=admin@cyberblue.local
MISP_ADMIN_PASSWORD=SecurePass123!

# =================================
# DATABASE CONFIGURATION
# =================================
POSTGRES_PASSWORD=SecurePass123!
MYSQL_ROOT_PASSWORD=SecurePass123!
ELASTICSEARCH_PASSWORD=SecurePass123!

# =================================
# SSL CONFIGURATION
# =================================
SSL_CERT_PATH=./ssl/cert.pem
SSL_KEY_PATH=./ssl/key.pem
```

### 3. System Optimization

```bash
# Increase virtual memory for Elasticsearch
echo 'vm.max_map_count=262144' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# Increase file descriptor limits
echo '* soft nofile 65536' | sudo tee -a /etc/security/limits.conf
echo '* hard nofile 65536' | sudo tee -a /etc/security/limits.conf

# Optimize Docker daemon
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2"
}
EOF

sudo systemctl restart docker
```

---

## 🚀 Deployment

### Quick Start Deployment

```bash
# Make scripts executable
chmod +x quick-start.sh
chmod +x cyberblue_init.sh

# Run quick start script
./quick-start.sh
```

### Manual Deployment

```bash
# 1. Initialize system
./cyberblue_init.sh

# 2. Start all services
docker compose up -d

# 3. Monitor deployment
docker compose logs -f
```

### Step-by-Step Deployment

```bash
# 1. Pull all images (optional, for faster startup)
docker compose pull

# 2. Create networks
docker network create cyberblue-network

# 3. Start core services first
docker compose up -d opensearch wazuh-indexer

# 4. Wait for core services (30 seconds)
sleep 30

# 5. Start remaining services
docker compose up -d

# 6. Verify all containers are running
docker compose ps
```

---

## ✅ Verification & Testing

### 1. Container Health Check

```bash
# Check all containers
docker compose ps

# Expected output: All services should show "running" status
# If any service shows "unhealthy" or "exited", check logs:
docker compose logs [service-name]
```

### 2. Service Accessibility Test

```bash
# Test portal accessibility
curl -f http://localhost:5500 || echo "Portal not accessible"

# Test individual services
curl -k -f https://localhost:7000 || echo "Velociraptor not accessible"
curl -k -f https://localhost:7001 || echo "Wazuh not accessible"
curl -f http://localhost:7004 || echo "CyberChef not accessible"
```

### 3. Port Verification

```bash
# Check open ports
netstat -tulpn | grep -E "(5500|700[0-9]|9443)"

# Or using ss command
ss -tulpn | grep -E "(5500|700[0-9]|9443)"
```

---

## 🔧 First-Time Service Setup

### 1. Wazuh Dashboard Setup

1. Access: `https://YOUR_IP:7001`
2. Login: `admin` / `SecurePass123!` (from your .env)
3. Complete initial setup wizard
4. Configure agents as needed

### 2. MISP Setup

1. Access: `https://YOUR_IP:7003`
2. Login: `admin@cyberblue.local` / `SecurePass123!`
3. Complete organization setup
4. Configure feeds and taxonomies

### 3. Velociraptor Setup

1. Access: `https://YOUR_IP:7000`
2. Create admin user on first login
3. Configure client endpoints
4. Set up artifact collection

### 4. Shuffle Setup

1. Access: `https://YOUR_IP:7002`
2. Create initial admin account
3. Configure app integrations
4. Build your first workflow

---

## 📊 Advanced Configuration

### Custom Domain Setup

```bash
# Add to /etc/hosts or configure DNS
echo "YOUR_IP cyberblue.local" | sudo tee -a /etc/hosts
echo "YOUR_IP wazuh.cyberblue.local" | sudo tee -a /etc/hosts
echo "YOUR_IP misp.cyberblue.local" | sudo tee -a /etc/hosts
```

### SSL Certificate Configuration

```bash
# Generate self-signed certificates
mkdir -p ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem \
  -out ssl/cert.pem \
  -subj "/C=US/ST=State/L=City/O=CyberBlue/CN=cyberblue.local"

# Or use Let's Encrypt for production
# certbot certonly --standalone -d your-domain.com
```

### Resource Optimization

```bash
# For systems with limited resources, edit docker-compose.yml:
# Reduce memory limits for services
# Disable unnecessary services

# Example: Disable some services
docker compose stop wireshark evebox
```

---

## 🔍 Troubleshooting

### Common Installation Issues

#### Docker Permission Denied
```bash
# Fix: Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

#### Out of Memory Errors
```bash
# Increase virtual memory
sudo sysctl -w vm.max_map_count=262144
echo 'vm.max_map_count=262144' | sudo tee -a /etc/sysctl.conf
```

#### Port Already in Use
```bash
# Find process using port
sudo netstat -tulpn | grep :7001
# Kill process
sudo kill -9 [PID]
```

#### Container Fails to Start
```bash
# Check logs
docker compose logs [service-name]

# Restart specific service
docker compose restart [service-name]

# Rebuild container
docker compose up -d --force-recreate [service-name]
```

### Service-Specific Issues

#### Elasticsearch/OpenSearch Issues
```bash
# Check cluster health
curl -X GET "localhost:9200/_cluster/health?pretty"

# Reset passwords
docker compose exec opensearch /usr/share/opensearch/plugins/opensearch-security/tools/securityadmin.sh -cd /usr/share/opensearch/plugins/opensearch-security/securityconfig/ -icl -nhnv -cacert /usr/share/opensearch/config/certificates/root-ca.pem -cert /usr/share/opensearch/config/certificates/admin.pem -key /usr/share/opensearch/config/certificates/admin.key
```

#### Database Connection Issues
```bash
# Test database connectivity
docker compose exec postgres psql -U postgres -c "\l"
docker compose exec mysql mysql -u root -p -e "SHOW DATABASES;"
```

### Performance Monitoring

```bash
# Monitor resource usage
docker stats

# Check disk usage
docker system df

# Clean up unused resources
docker system prune -a
```

---

## 🔄 Maintenance Tasks

### Regular Updates

```bash
# Update images
docker compose pull

# Restart with new images
docker compose up -d --force-recreate
```

### Backup Procedures

```bash
# Backup configurations
tar -czf cyberblue-backup-$(date +%Y%m%d).tar.gz \
  .env docker-compose.yml configs/ ssl/

# Backup databases
docker compose exec postgres pg_dumpall -U postgres > postgres-backup.sql
docker compose exec mysql mysqldump -u root -p --all-databases > mysql-backup.sql
```

### Log Management

```bash
# View logs
docker compose logs -f --tail=100

# Clean old logs
docker system prune --volumes
```

---

## 📚 Next Steps

After successful installation:

1. **📖 Read the User Guide**: Learn how to use each tool effectively
2. **🔒 Review Security Guide**: Implement security best practices
3. **🎯 Configure Use Cases**: Set up specific detection scenarios
4. **📊 Set Up Monitoring**: Configure alerting and dashboards
5. **🤝 Join Community**: Participate in discussions and contribute

---

## 🆘 Getting Help

If you encounter issues:

1. **Check Logs**: `docker compose logs [service-name]`
2. **Review Troubleshooting**: Common issues above
3. **Search Issues**: [GitHub Issues](https://github.com/m7siri/cyber-blue-project/issues)
4. **Ask Community**: [GitHub Discussions](https://github.com/m7siri/cyber-blue-project/discussions)
5. **Report Bug**: Create detailed issue report

---

## 📋 Summary

Congratulations! You've successfully installed CyberBlue. Your cybersecurity lab is now ready with:

- ✅ **15+ Security Tools** fully configured
- ✅ **CyberBlue Portal** for centralized management
- ✅ **Production-ready** configurations
- ✅ **Monitoring & Logging** enabled
- ✅ **Security Hardening** applied

**Next**: Access your CyberBlue Portal at `http://YOUR_IP:5500` and start exploring your security tools!

---

*Need help? Check our [Documentation](README.md) or [Support Channels](https://github.com/m7siri/cyber-blue-project/discussions)* 
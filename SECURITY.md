# 🔒 CyberBlue Security Guide

This guide provides comprehensive security hardening and best practices for CyberBlue deployments.

---

## 🎯 Security Overview

CyberBlue is designed with security in mind, but proper configuration and hardening are essential for production deployments. This guide covers:

- **🔐 Password Security**
- **🛡️ SSL/TLS Configuration** 
- **🌐 Network Security**
- **👤 User Management**
- **📊 Data Protection**
- **🔍 Security Verification**
- **⚡ Production Recommendations**

---

## 🔐 Password Security

### 1. Change Default Passwords

**CRITICAL**: Never use default passwords in production!

   ```bash
# Edit .env file with strong passwords
nano .env
```

### 2. Password Requirements

Use passwords that meet these criteria:
- **Minimum 12 characters**
- **Mix of uppercase, lowercase, numbers, symbols**
- **No dictionary words**
- **Unique for each service**

### 3. Recommended Password Generation

   ```bash
# Generate strong passwords
   openssl rand -base64 32
   
# Or use password manager tools
# Examples: 1Password, Bitwarden, LastPass
```

### 4. Service-Specific Passwords

Update these passwords in `.env`:

```bash
# Core Services
WAZUH_ADMIN_PASSWORD='V3ry$tr0ng!P@ssw0rd123'
OPENSEARCH_ADMIN_PASSWORD='An0th3r$tr0ng!P@ss456'
MISP_ADMIN_PASSWORD='M1SP$ecur3!P@ssw0rd789'

# Databases
POSTGRES_PASSWORD='P0stgr3$!Secur3P@ss012'
MYSQL_ROOT_PASSWORD='MyS3cur3!R00tP@ss345'
ELASTICSEARCH_PASSWORD='El@st1c$3arch!P@ss678'

# Additional Services
THEHIVE_ADMIN_PASSWORD='Th3H1v3!Adm1nP@ss901'
CORTEX_API_KEY='C0rt3x!AP1K3y$234567890'
   ```

---

## 🛡️ SSL/TLS Configuration

### 1. Generate SSL Certificates

#### Self-Signed Certificates (Development)

```bash
# Create SSL directory
mkdir -p ssl

# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:4096 \
  -keyout ssl/key.pem \
  -out ssl/cert.pem \
  -subj "/C=US/ST=State/L=City/O=CyberBlue/CN=cyberblue.local" \
  -config <(
    echo '[dn]'
    echo 'CN=cyberblue.local'
    echo '[req]'
    echo 'distinguished_name = dn'
    echo '[extensions]'
    echo 'subjectAltName=DNS:cyberblue.local,DNS:*.cyberblue.local,IP:10.0.0.40'
    echo 'keyUsage=keyEncipherment,dataEncipherment'
    echo 'extendedKeyUsage=serverAuth'
  ) \
  -extensions extensions

# Set proper permissions
chmod 600 ssl/key.pem
chmod 644 ssl/cert.pem
```

#### Production Certificates (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot

# Generate certificate for your domain
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates to CyberBlue
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/key.pem
sudo chown $USER:$USER ssl/*.pem
```

### 2. Configure SSL in Docker Compose

Update `docker-compose.yml` for SSL-enabled services:

```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./ssl:/etc/nginx/ssl:ro
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - portal
```

### 3. SSL Best Practices

- **Use TLS 1.2+** minimum
- **Disable weak ciphers**
- **Enable HSTS headers**
- **Use strong key exchange**
- **Regular certificate renewal**

---

## 🌐 Network Security

### 1. Firewall Configuration

#### UFW (Ubuntu Firewall)

```bash
# Enable UFW
sudo ufw enable

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (adjust port as needed)
sudo ufw allow 22/tcp

# Allow CyberBlue services
sudo ufw allow 5500/tcp  # Portal
sudo ufw allow 7000:7099/tcp  # Security tools
sudo ufw allow 9443/tcp  # Portainer

# Check status
sudo ufw status verbose
```

#### Firewalld (CentOS/RHEL)

```bash
# Enable firewalld
sudo systemctl enable firewalld
sudo systemctl start firewalld

# Create custom service
sudo firewall-cmd --permanent --new-service=cyberblue
sudo firewall-cmd --permanent --service=cyberblue --add-port=5500/tcp
sudo firewall-cmd --permanent --service=cyberblue --add-port=7000-7099/tcp
sudo firewall-cmd --permanent --service=cyberblue --add-port=9443/tcp

# Enable service
sudo firewall-cmd --permanent --add-service=cyberblue
sudo firewall-cmd --reload
```

### 2. Docker Network Security

#### Create Isolated Networks

```bash
# Create custom networks
docker network create \
  --driver bridge \
  --subnet=172.20.0.0/16 \
  --opt encrypted=true \
  cyberblue-frontend

docker network create \
  --driver bridge \
  --subnet=172.21.0.0/16 \
  --opt encrypted=true \
  cyberblue-backend
```

#### Network Segmentation

```yaml
# docker-compose.yml network configuration
networks:
  frontend:
    external: true
    name: cyberblue-frontend
  backend:
    external: true
    name: cyberblue-backend
  database:
    internal: true
    driver: bridge
```

### 3. Restrict External Access

```bash
# Bind services to localhost only (for proxy setup)
# Edit docker-compose.yml
ports:
  - "127.0.0.1:7001:7001"  # Only localhost access
```

### 4. VPN Access (Recommended)

Set up VPN for remote access:

```bash
# WireGuard example
sudo apt install wireguard

# Generate keys
wg genkey | tee privatekey | wg pubkey > publickey

# Configure server
sudo nano /etc/wireguard/wg0.conf
```

---

## 👤 User Management

### 1. Service Account Security

#### Wazuh User Management

```bash
# Access Wazuh container
docker compose exec wazuh.dashboard bash

# Create read-only user
/usr/share/wazuh-dashboard/bin/wazuh-passwords-tool.sh -u wazuh-readonly -p 'ReadOnlyPass123!'

# Create analyst user with limited permissions
/usr/share/wazuh-dashboard/bin/wazuh-passwords-tool.sh -u wazuh-analyst -p 'AnalystPass123!'
```

#### MISP User Roles

1. **Admin**: Full system access
2. **Org Admin**: Organization management
3. **User**: Basic event management
4. **Read Only**: View-only access

### 2. Multi-Factor Authentication

#### Enable MFA for Critical Services

```bash
# Install TOTP for SSH
sudo apt install libpam-google-authenticator

# Configure for user
google-authenticator

# Edit SSH config
sudo nano /etc/pam.d/sshd
# Add: auth required pam_google_authenticator.so
```

### 3. Access Control Lists

#### Implement IP-based restrictions:

```bash
# nginx configuration
location /admin/ {
    allow 10.0.0.0/8;
    allow 192.168.0.0/16;
    deny all;
}
```

---

## 📊 Data Protection

### 1. Encryption at Rest

#### Database Encryption

```yaml
# PostgreSQL with encryption
postgres:
  image: postgres:15
  environment:
    POSTGRES_INITDB_ARGS: "--auth-host=scram-sha-256"
  volumes:
    - postgres_data:/var/lib/postgresql/data
```

#### Volume Encryption

```bash
# Encrypt Docker volumes using LUKS
sudo cryptsetup luksFormat /dev/sdb
sudo cryptsetup luksOpen /dev/sdb encrypted_volume
sudo mkfs.ext4 /dev/mapper/encrypted_volume
```

### 2. Backup Security

```bash
# Encrypted backups
tar -czf - /path/to/data | gpg --cipher-algo AES256 --compress-algo 1 --s2k-mode 3 --s2k-digest-algo SHA512 --s2k-count 65536 --symmetric --output backup.tar.gz.gpg

# Restore encrypted backup
gpg --decrypt backup.tar.gz.gpg | tar -xzf -
```

### 3. Log Security

#### Secure log storage:

```yaml
# Centralized logging with encryption
logging:
  driver: "syslog"
  options:
    syslog-address: "tls://log-server:6514"
    syslog-format: "rfc5424micro"
```

### 4. Secrets Management

```bash
# Use Docker secrets instead of environment variables
echo "my_secret_password" | docker secret create db_password -

# Reference in docker-compose.yml
secrets:
  - db_password
```

---

## 🔍 Security Verification

### 1. Security Scanning

#### Container Security Scan

```bash
# Scan containers for vulnerabilities
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  -v $HOME/Library/Caches:/root/.cache/ \
  aquasec/trivy image cyberblue:latest
```

#### Network Vulnerability Scan

```bash
# Nmap security scan
nmap -sS -O -v your-server-ip

# OpenVAS scan (if available)
openvas-cli -T localhost -p 9390 -u admin -w admin_password --xml="<create_target><name>CyberBlue</name><hosts>your-server-ip</hosts></create_target>"
```

### 2. Access Testing

```bash
# Test authentication
curl -k -u admin:wrong_password https://your-server:7001
# Should return 401 Unauthorized

# Test SSL configuration
nmap --script ssl-enum-ciphers -p 7001 your-server-ip
```

### 3. Compliance Verification

#### Security Checklist

- [ ] **Default passwords changed**
- [ ] **SSL/TLS enabled for all services**
- [ ] **Firewall properly configured**
- [ ] **Regular security updates applied**
- [ ] **Backup encryption enabled**
- [ ] **Access logs monitored**
- [ ] **MFA enabled for critical accounts**
- [ ] **Network segmentation implemented**
- [ ] **Vulnerability scanning scheduled**
- [ ] **Incident response plan documented**

---

## ⚡ Production Recommendations

### 1. Infrastructure Security

#### Hardened Operating System

```bash
# Disable unnecessary services
sudo systemctl disable bluetooth
sudo systemctl disable avahi-daemon

# Enable automatic security updates
sudo apt install unattended-upgrades
sudo dpkg-reconfigure unattended-upgrades

# Configure fail2ban
sudo apt install fail2ban
sudo systemctl enable fail2ban
```

#### Kernel Hardening

```bash
# Add to /etc/sysctl.conf
net.ipv4.ip_forward=0
net.ipv4.conf.all.send_redirects=0
net.ipv4.conf.default.send_redirects=0
net.ipv4.conf.all.accept_redirects=0
net.ipv4.conf.default.accept_redirects=0
kernel.dmesg_restrict=1
```

### 2. Monitoring and Alerting

#### Security Event Monitoring

```yaml
# Add security monitoring container
security-monitor:
  image: elastic/filebeat:8.5.0
  volumes:
    - /var/log:/var/log:ro
    - ./filebeat.yml:/usr/share/filebeat/filebeat.yml:ro
  environment:
    - ELASTICSEARCH_HOST=opensearch:9200
```

#### Log Monitoring

```bash
# Monitor authentication failures
sudo tail -f /var/log/auth.log | grep "Failed password"

# Monitor Docker events
docker events --filter event=start --filter event=stop
```

### 3. Disaster Recovery

#### Backup Strategy

```bash
#!/bin/bash
# automated-backup.sh

BACKUP_DIR="/secure/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Stop services
docker compose stop

# Create encrypted backup
tar -czf - . | gpg --cipher-algo AES256 --symmetric --output "$BACKUP_DIR/cyberblue_$DATE.tar.gz.gpg"

# Start services
docker compose start

# Rotate old backups (keep 30 days)
find $BACKUP_DIR -name "cyberblue_*.tar.gz.gpg" -mtime +30 -delete
```

#### Recovery Testing

```bash
# Test backup integrity monthly
gpg --decrypt backup.tar.gz.gpg | tar -tzf - > /dev/null
echo "Backup integrity: $?"
```

### 4. Security Policies

#### Password Policy

```bash
# Enforce strong passwords
sudo apt install libpam-pwquality
echo "password requisite pam_pwquality.so retry=3 minlen=12 difok=3 ucredit=-1 lcredit=-1 dcredit=-1 ocredit=-1" >> /etc/pam.d/common-password
```

#### Session Management

```bash
# Configure session timeouts
echo "ClientAliveInterval 300" >> /etc/ssh/sshd_config
echo "ClientAliveCountMax 2" >> /etc/ssh/sshd_config
```

---

## 🚨 Incident Response

### 1. Security Incident Procedures

#### Immediate Response

1. **Isolate affected systems**
2. **Preserve evidence**
3. **Assess scope of breach**
4. **Implement containment**
5. **Begin recovery process**

#### Investigation Commands

```bash
# Check for unauthorized access
sudo last -n 50
sudo grep "Failed password" /var/log/auth.log

# Monitor network connections
sudo netstat -tulpn
sudo ss -tulpn

# Check running processes
ps aux --forest
docker ps -a
```

### 2. Forensic Data Collection

```bash
# Create forensic image
sudo dd if=/dev/sda of=/forensics/system-image.dd bs=4M status=progress

# Collect memory dump
sudo dd if=/dev/mem of=/forensics/memory-dump.dd bs=1M

# Container forensics
docker diff container_name
docker logs container_name > /forensics/container.log
```

### 3. Recovery Procedures

```bash
# Restore from clean backup
gpg --decrypt clean_backup.tar.gz.gpg | tar -xzf -

# Rebuild compromised containers
docker compose down
docker compose build --no-cache
docker compose up -d
```

---

## 📋 Security Maintenance

### 1. Regular Tasks

#### Daily
- [ ] Review authentication logs
- [ ] Check service availability
- [ ] Monitor resource usage

#### Weekly
- [ ] Apply security updates
- [ ] Review user access
- [ ] Test backups

#### Monthly
- [ ] Vulnerability scanning
- [ ] Access audit
- [ ] Policy review
- [ ] Incident response drill

### 2. Update Procedures

```bash
# Update CyberBlue
cd /path/to/cyberblue
git pull origin main
docker compose pull
docker compose up -d --force-recreate

# Update system packages
sudo apt update && sudo apt upgrade -y
sudo reboot
```

### 3. Security Metrics

Track these metrics:
- **Failed login attempts**
- **Privilege escalations**
- **Network anomalies**
- **Resource consumption**
- **Certificate expiration**

---

## 🔗 Additional Resources

### Security Standards
- **NIST Cybersecurity Framework**
- **ISO 27001**
- **OWASP Top 10**
- **CIS Critical Security Controls**

### Security Tools Integration
- **OSSEC** for host intrusion detection
- **Fail2Ban** for brute force protection
- **Lynis** for security auditing
- **Chkrootkit** for rootkit detection

### Documentation
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [Linux Security Hardening](https://www.cisecurity.org/cis-benchmarks/)
- [Container Security Standards](https://www.nist.gov/publications/application-container-security-guide)

---

## 📞 Security Support

For security-related questions or incident reporting:

- **Security Issues**: Use private vulnerability disclosure
- **General Questions**: [GitHub Discussions](https://github.com/m7siri/cyber-blue-project/discussions)
- **Documentation**: [Security Wiki](https://github.com/m7siri/cyber-blue-project/wiki/Security)

---

## ⚠️ Security Notice

**Remember**: Security is an ongoing process, not a one-time setup. Regularly review and update your security measures based on:

- **New threat intelligence**
- **Updated security standards**
- **Lessons learned from incidents**
- **Changes in your environment**

---

*Last updated: [Current Date] | Version: 1.0* 
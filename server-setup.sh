#!/bin/bash

# 🖥️ Server Setup Script for Sitemap to LLMS.txt
# This script helps prepare your server for deployment

set -e  # Exit on any error

echo "🖥️ Server Setup for Sitemap to LLMS.txt..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
else
    print_error "Could not detect OS"
    exit 1
fi

print_status "Detected OS: $OS $VER"

# Function to install Docker on Ubuntu/Debian
install_docker_ubuntu() {
    print_step "Installing Docker on Ubuntu/Debian..."
    
    # Update package list
    sudo apt-get update
    
    # Install prerequisites
    sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
    
    # Add Docker's official GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Add Docker repository
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Update package list again
    sudo apt-get update
    
    # Install Docker
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io
    
    # Install Docker Compose
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    print_status "Docker installed successfully"
}

# Function to install Docker on CentOS/RHEL
install_docker_centos() {
    print_step "Installing Docker on CentOS/RHEL..."
    
    # Install prerequisites
    sudo yum install -y yum-utils
    
    # Add Docker repository
    sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    
    # Install Docker
    sudo yum install -y docker-ce docker-ce-cli containerd.io
    
    # Start and enable Docker
    sudo systemctl start docker
    sudo systemctl enable docker
    
    # Install Docker Compose
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    print_status "Docker installed successfully"
}

# Check if Docker is already installed
if command -v docker &> /dev/null; then
    print_status "Docker is already installed"
    docker --version
else
    print_step "Docker not found. Installing..."
    
    case $OS in
        *"Ubuntu"*|*"Debian"*)
            install_docker_ubuntu
            ;;
        *"CentOS"*|*"Red Hat"*|*"Rocky"*|*"AlmaLinux"*)
            install_docker_centos
            ;;
        *)
            print_error "Unsupported OS: $OS"
            print_warning "Please install Docker manually: https://docs.docker.com/get-docker/"
            exit 1
            ;;
    esac
fi

# Check if Docker Compose is installed
if command -v docker-compose &> /dev/null; then
    print_status "Docker Compose is already installed"
    docker-compose --version
else
    print_error "Docker Compose not found. Please install it manually."
    exit 1
fi

# Add user to docker group
if ! groups $USER | grep -q docker; then
    print_step "Adding user to docker group..."
    sudo usermod -aG docker $USER
    print_warning "User added to docker group. You may need to log out and back in for changes to take effect."
else
    print_status "User already in docker group"
fi

# Check if ports are available
print_step "Checking port availability..."

if sudo netstat -tlnp | grep :80 > /dev/null; then
    print_warning "Port 80 is already in use:"
    sudo netstat -tlnp | grep :80
    print_warning "You may need to stop the service using port 80 or change the port in docker-compose.prod.yml"
else
    print_status "Port 80 is available"
fi

if sudo netstat -tlnp | grep :443 > /dev/null; then
    print_warning "Port 443 is already in use:"
    sudo netstat -tlnp | grep :443
    print_warning "You may need to stop the service using port 443 or change the port in docker-compose.prod.yml"
else
    print_status "Port 443 is available"
fi

# Configure firewall (Ubuntu/Debian)
if command -v ufw &> /dev/null; then
    print_step "Configuring UFW firewall..."
    
    # Allow SSH (if not already allowed)
    sudo ufw allow ssh
    
    # Allow HTTP and HTTPS
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    
    # Enable firewall
    echo "y" | sudo ufw enable
    
    print_status "Firewall configured and enabled"
fi

# Configure firewall (CentOS/RHEL)
if command -v firewall-cmd &> /dev/null; then
    print_step "Configuring firewalld..."
    
    # Allow HTTP and HTTPS
    sudo firewall-cmd --permanent --add-service=http
    sudo firewall-cmd --permanent --add-service=https
    
    # Reload firewall
    sudo firewall-cmd --reload
    
    print_status "Firewall configured"
fi

# Check system resources
print_step "Checking system resources..."

# Check RAM
TOTAL_RAM=$(free -m | awk 'NR==2{printf "%.0f", $2/1024}')
if [ $TOTAL_RAM -lt 2 ]; then
    print_warning "System has ${TOTAL_RAM}GB RAM. Recommended minimum is 2GB for production use."
else
    print_status "RAM: ${TOTAL_RAM}GB (sufficient)"
fi

# Check disk space
DISK_SPACE=$(df -BG / | awk 'NR==2{print $4}' | sed 's/G//')
if [ $DISK_SPACE -lt 10 ]; then
    print_warning "System has ${DISK_SPACE}GB free space. Recommended minimum is 10GB."
else
    print_status "Disk space: ${DISK_SPACE}GB (sufficient)"
fi

# Create deployment directory
print_step "Setting up deployment directory..."
DEPLOY_DIR="/opt/sitemap-to-llmstxt"

if [ ! -d "$DEPLOY_DIR" ]; then
    sudo mkdir -p "$DEPLOY_DIR"
    sudo chown $USER:$USER "$DEPLOY_DIR"
    print_status "Created deployment directory: $DEPLOY_DIR"
else
    print_status "Deployment directory already exists: $DEPLOY_DIR"
fi

echo ""
echo "🎉 Server setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Clone your repository to the server:"
echo "   git clone <your-repo-url> $DEPLOY_DIR"
echo ""
echo "2. Navigate to the project directory:"
echo "   cd $DEPLOY_DIR"
echo ""
echo "3. Make scripts executable:"
echo "   chmod +x deploy.sh build-frontend.sh"
echo ""
echo "4. Run the deployment script:"
echo "   ./deploy.sh"
echo ""
echo "🔧 Useful commands:"
echo "   Check Docker status: sudo systemctl status docker"
echo "   View Docker logs: sudo journalctl -u docker"
echo "   Check firewall status: sudo ufw status (Ubuntu) or sudo firewall-cmd --list-all (CentOS)"
echo ""
echo "📚 For more information, see DEPLOYMENT.md"

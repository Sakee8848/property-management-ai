#!/bin/bash

echo "======================================"
echo "物业管理AI系统 - 一键启动脚本"
echo "======================================"
echo ""

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: 未安装 Docker"
    echo "请先安装 Docker Desktop: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# 检查 Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ 错误: 未安装 Docker Compose"
    exit 1
fi

echo "✅ Docker 环境检查通过"
echo ""

# 检查环境变量文件
if [ ! -f "backend/.env" ]; then
    echo "📝 创建环境变量文件..."
    cp backend/.env.example backend/.env
    echo ""
    echo "⚠️  重要提示:"
    echo "   请编辑 backend/.env 文件，配置以下必需项:"
    echo "   - OPENAI_API_KEY=your-api-key"
    echo "   - SECRET_KEY=your-secret-key"
    echo ""
    echo "   可以使用以下命令生成SECRET_KEY:"
    echo "   openssl rand -hex 32"
    echo ""
    read -p "配置完成后按回车继续..."
fi

echo "🚀 启动所有服务..."
docker-compose up -d

echo ""
echo "⏳ 等待服务启动..."
sleep 10

echo ""
echo "======================================"
echo "✅ 服务启动完成！"
echo "======================================"
echo ""
echo "📱 访问地址:"
echo "   前端H5: http://localhost:5173"
echo "   后端API: http://localhost:8000/api/docs"
echo "   健康检查: http://localhost:8000/health"
echo ""
echo "📋 查看日志:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 停止服务:"
echo "   docker-compose down"
echo ""

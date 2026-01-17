#!/bin/bash

echo "======================================"
echo "GitHub 推送脚本"
echo "======================================"
echo ""

# 检查是否已设置远程仓库
if git remote get-url origin > /dev/null 2>&1; then
    echo "✅ 远程仓库已配置"
    git remote -v
    echo ""
    read -p "是否要推送到此仓库？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "❌ 还未配置远程仓库"
    echo ""
    echo "请按以下步骤操作："
    echo ""
    echo "1. 访问 https://github.com/new 创建新仓库"
    echo "   - Repository name: property-management-ai"
    echo "   - Description: 智能物业管理AI系统"
    echo "   - Public (公开)"
    echo ""
    echo "2. 创建完成后，复制仓库URL"
    echo "   例如：https://github.com/YOUR_USERNAME/property-management-ai.git"
    echo ""
    read -p "请输入GitHub仓库URL: " REPO_URL
    
    if [ -z "$REPO_URL" ]; then
        echo "❌ URL不能为空"
        exit 1
    fi
    
    echo ""
    echo "添加远程仓库..."
    git remote add origin "$REPO_URL"
    echo "✅ 远程仓库已配置"
fi

echo ""
echo "🚀 开始推送代码到GitHub..."
echo ""

# 确保在main分支
git branch -M main

# 推送到main分支
echo "推送到 main 分支..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 推送成功！"
    echo ""
    echo "======================================"
    echo "代码已备份到GitHub"
    echo "======================================"
    echo ""
    
    # 创建gh-pages分支用于GitHub Pages
    echo "创建 gh-pages 分支用于GitHub Pages..."
    git checkout -b gh-pages 2>/dev/null || git checkout gh-pages
    git push origin gh-pages
    git checkout main
    
    echo ""
    echo "✅ gh-pages 分支已创建"
    echo ""
    echo "======================================"
    echo "下一步：启用GitHub Pages"
    echo "======================================"
    echo ""
    echo "1. 访问仓库页面"
    echo "2. 点击 Settings"
    echo "3. 点击左侧 Pages"
    echo "4. Source 选择：gh-pages 分支"
    echo "5. 点击 Save"
    echo ""
    echo "等待30秒后，你的演示页面将发布到："
    echo "https://YOUR_USERNAME.github.io/property-management-ai/mvp-prototype.html"
    echo ""
else
    echo ""
    echo "❌ 推送失败"
    echo ""
    echo "可能的原因："
    echo "1. GitHub仓库URL不正确"
    echo "2. 没有推送权限（需要先登录GitHub）"
    echo "3. 网络连接问题"
    echo ""
    echo "请检查后重试"
fi

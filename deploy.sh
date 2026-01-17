#!/bin/bash

# 物业管理AI系统 - 自动部署脚本
# 使用方法: ./deploy.sh "你的变更说明"

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的信息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 打印标题
print_header() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║                                                                  ║"
    echo "║              物业管理AI系统 - 自动部署工具                       ║"
    echo "║                                                                  ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo ""
}

# 获取当前时间
get_timestamp() {
    date "+%Y-%m-%d %H:%M:%S"
}

# 获取版本号（基于提交次数）
get_version() {
    local commit_count=$(git rev-list --count HEAD 2>/dev/null || echo "0")
    local major=1
    local minor=$((commit_count / 10))
    local patch=$((commit_count % 10))
    echo "v${major}.${minor}.${patch}"
}

# 检查是否在git仓库中
check_git_repo() {
    if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
        print_error "当前目录不是Git仓库"
        exit 1
    fi
}

# 检查是否有未提交的更改
check_changes() {
    if [[ -z $(git status -s) ]]; then
        print_warning "没有检测到任何更改"
        read -p "是否继续？(y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 0
        fi
        return 1
    fi
    return 0
}

# 获取变更说明
get_commit_message() {
    if [ -n "$1" ]; then
        echo "$1"
    else
        print_info "请输入本次变更说明（留空使用默认说明）："
        read -r message
        if [ -z "$message" ]; then
            echo "更新和优化系统功能"
        else
            echo "$message"
        fi
    fi
}

# 生成变更文件列表
get_changed_files() {
    git status -s | awk '{print $2}' | head -10
}

# 统计代码变更
get_code_stats() {
    local additions=$(git diff --cached --numstat | awk '{s+=$1} END {print s}')
    local deletions=$(git diff --cached --numstat | awk '{s+=$2} END {print s}')
    echo "${additions:-0} additions, ${deletions:-0} deletions"
}

# 生成Release文档
generate_release_doc() {
    local version=$1
    local commit_msg=$2
    local timestamp=$3
    local changed_files=$4
    local stats=$5
    local release_file="RELEASE.md"
    
    # 如果是第一次，创建文件头
    if [ ! -f "$release_file" ]; then
        cat > "$release_file" << 'EOF'
# 📦 Release Notes - 物业管理AI系统

本文档记录了系统的所有版本发布和变更历史。

---

EOF
    fi
    
    # 在文件开头插入新版本信息（保留原有内容）
    local temp_file=$(mktemp)
    cat > "$temp_file" << EOF
## ${version} - ${timestamp}

### 🎯 本次变更
${commit_msg}

### 📊 统计信息
- 变更统计：${stats}
- 提交时间：${timestamp}
- 提交者：$(git config user.name)

### 📝 变更文件
\`\`\`
${changed_files}
\`\`\`

### 🔗 访问地址
- **MVP演示**：https://sakee8848.github.io/property-management-ai/mvp-prototype.html
- **GitHub仓库**：https://github.com/Sakee8848/property-management-ai

---

EOF
    
    # 如果文件存在，追加原有内容（跳过前3行标题）
    if [ -f "$release_file" ]; then
        tail -n +4 "$release_file" >> "$temp_file"
    fi
    
    mv "$temp_file" "$release_file"
    
    print_success "Release文档已更新：$release_file"
}

# 生成部署摘要
generate_deployment_summary() {
    local version=$1
    local commit_msg=$2
    
    cat > "DEPLOYMENT_SUMMARY.txt" << EOF
╔══════════════════════════════════════════════════════════════════╗
║                     部署摘要                                      ║
╚══════════════════════════════════════════════════════════════════╝

版本号：${version}
部署时间：$(get_timestamp)
变更说明：${commit_msg}

部署状态：✅ 成功

访问地址：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📱 MVP演示页面：
https://sakee8848.github.io/property-management-ai/mvp-prototype.html

🔗 GitHub仓库：
https://github.com/Sakee8848/property-management-ai

📚 Release文档：
https://github.com/Sakee8848/property-management-ai/blob/main/RELEASE.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

分享给客户：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
您好！物业管理AI系统已更新 🎉

🆕 本次更新：${commit_msg}

🔗 访问地址：
https://sakee8848.github.io/property-management-ai/mvp-prototype.html

📱 使用方法：
1. 手机浏览器打开链接
2. 输入任意用户名密码登录
3. 体验AI对话等功能

如有任何问题，请随时联系！
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EOF
    
    print_success "部署摘要已生成：DEPLOYMENT_SUMMARY.txt"
}

# 主流程
main() {
    print_header
    
    # 1. 检查Git仓库
    print_info "检查Git仓库..."
    check_git_repo
    print_success "Git仓库检查通过"
    
    # 2. 检查更改
    print_info "检查代码更改..."
    has_changes=true
    check_changes || has_changes=false
    
    if [ "$has_changes" = true ]; then
        local changed_files=$(get_changed_files)
        echo ""
        print_info "检测到以下文件变更："
        echo "$changed_files"
        echo ""
    fi
    
    # 3. 获取变更说明
    local commit_message=$(get_commit_message "$1")
    print_info "变更说明：$commit_message"
    
    # 4. 获取版本号
    local version=$(get_version)
    print_info "当前版本：$version"
    
    # 5. 添加所有更改
    if [ "$has_changes" = true ]; then
        print_info "添加文件到暂存区..."
        git add -A
        print_success "文件已添加"
        
        # 获取统计信息
        local stats=$(get_code_stats)
        print_info "代码统计：$stats"
    else
        local changed_files="无新增文件"
        local stats="0 additions, 0 deletions"
    fi
    
    # 6. 生成Release文档
    print_info "生成Release文档..."
    local timestamp=$(get_timestamp)
    generate_release_doc "$version" "$commit_message" "$timestamp" "$changed_files" "$stats"
    
    # 7. 生成部署摘要
    print_info "生成部署摘要..."
    generate_deployment_summary "$version" "$commit_message"
    
    # 8. 将新生成的文档也加入提交
    git add RELEASE.md DEPLOYMENT_SUMMARY.txt 2>/dev/null || true
    
    # 9. 提交更改
    print_info "提交更改到本地仓库..."
    local full_commit_msg="[$version] $commit_message"
    
    if git diff --cached --quiet; then
        print_warning "没有需要提交的更改"
    else
        git commit -m "$full_commit_msg"
        print_success "代码已提交"
    fi
    
    # 10. 推送到GitHub
    print_info "推送到GitHub..."
    
    # 推送main分支
    if git push origin main; then
        print_success "main分支推送成功"
    else
        print_error "main分支推送失败"
        exit 1
    fi
    
    # 推送gh-pages分支
    print_info "更新gh-pages分支..."
    local current_branch=$(git branch --show-current)
    git push origin main:gh-pages 2>/dev/null || print_warning "gh-pages更新跳过"
    
    # 11. 完成
    echo ""
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║                                                                  ║"
    echo "║                    🎉 部署成功！                                  ║"
    echo "║                                                                  ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo ""
    
    print_success "版本：$version"
    print_success "变更：$commit_message"
    print_success "时间：$timestamp"
    echo ""
    
    print_info "访问地址："
    echo "  📱 https://sakee8848.github.io/property-management-ai/mvp-prototype.html"
    echo ""
    
    print_info "查看详情："
    echo "  📄 cat RELEASE.md"
    echo "  📄 cat DEPLOYMENT_SUMMARY.txt"
    echo ""
    
    # 显示部署摘要
    cat DEPLOYMENT_SUMMARY.txt
}

# 运行主程序
main "$@"

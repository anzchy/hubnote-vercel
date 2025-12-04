#!/bin/bash
# 初始化 Vercel KV 用户白名单

echo "🔧 初始化 Vercel KV 用户白名单..."

# 白名单数据（JSON 格式）
WHITELIST_DATA='{
  "allowed_users": ["anzchy", "hubnote"],
  "admin_users": ["anzchy"]
}'

# 使用 Vercel CLI 设置
echo "📤 上传白名单到 Vercel KV..."
vercel kv set user_whitelist "$WHITELIST_DATA" --yes

echo "✅ 白名单已上传！"
echo ""
echo "验证："
vercel kv get user_whitelist

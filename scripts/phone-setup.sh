#!/bin/sh
# 手机端一键安装 sync/push 命令
mkdir -p ~/bin

cat > ~/bin/sync << 'EOF'
#!/bin/sh
cd ~/storage/shared/Documents/second-brain || exit 1
GIT_SSH_COMMAND="ssh -p 443" git fetch origin
GIT_SSH_COMMAND="ssh -p 443" git reset --hard origin/master
echo "=== 同步完成 ==="
EOF

cat > ~/bin/push << 'EOF'
#!/bin/sh
cd ~/storage/shared/Documents/second-brain || exit 1
GIT_SSH_COMMAND="ssh -p 443" git add -A
git commit -m "phone"
GIT_SSH_COMMAND="ssh -p 443" git push
echo "=== 上传完成 ==="
EOF

chmod +x ~/bin/sync ~/bin/push

grep -q '$HOME/bin' ~/.bashrc 2>/dev/null || echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc

echo "=== 安装完成，以后输入 sync 拉取，push 上传 ==="

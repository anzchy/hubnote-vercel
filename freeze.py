from app import create_app
import os
import shutil

def generate_static_site():
    """手动生成静态网站"""
    app = create_app()
    
    # 清理并创建输出目录
    if os.path.exists('build'):
        shutil.rmtree('build')
    os.makedirs('build')
    
    with app.app_context():
        # 手动生成配置页面
        with app.test_client() as client:
            print("生成配置页面...")
            response = client.get('/config')
            if response.status_code == 200:
                with open('build/config.html', 'w', encoding='utf-8') as f:
                    f.write(response.get_data(as_text=True))
                print("✓ 配置页面生成成功")
            else:
                print(f"✗ 配置页面生成失败: {response.status_code}")
    
    # 复制静态资源
    if os.path.exists('static'):
        shutil.copytree('static', 'build/static', dirs_exist_ok=True)
        print("✓ 静态资源已复制")
    
    # 创建一个简单的index.html重定向到config.html
    index_content = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>HubNote</title>
    <meta http-equiv="refresh" content="0; url=config.html">
</head>
<body>
    <p>正在跳转到配置页面... <a href="config.html">点击这里</a></p>
</body>
</html>'''
    
    with open('build/index.html', 'w', encoding='utf-8') as f:
        f.write(index_content)
    print("✓ 首页重定向文件已创建")
    
    # 创建CNAME文件用于GitHub Pages自定义域名
    with open('build/CNAME', 'w') as f:
        f.write('note.jackcheng.chat')
    print("✓ CNAME文件已创建")
    
    return True

if __name__ == '__main__':
    print("开始生成静态网站...")
    
    try:
        success = generate_static_site()
        
        if success:
            print("\n静态网站生成完成！")
            
            # 列出生成的文件
            print("\n生成的文件:")
            for root, dirs, files in os.walk('build'):
                for file in files:
                    rel_path = os.path.relpath(os.path.join(root, file), 'build')
                    print(f"  {rel_path}")
            
            print("\n接下来的步骤:")
            print("1. 将 build/ 目录的内容推送到 GitHub Pages 仓库")
            print("2. 在域名DNS设置中添加 CNAME 记录指向 <username>.github.io")
            print("3. 在 GitHub Pages 设置中启用自定义域名 note.jackcheng.chat")
        
    except Exception as e:
        print(f"生成静态网站时出错: {e}")
        import traceback
        traceback.print_exc()
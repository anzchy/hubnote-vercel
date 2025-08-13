// Markdown 编辑器功能

document.addEventListener('DOMContentLoaded', function() {
    initMarkdownEditor();
});

function initMarkdownEditor() {
    // 初始化 Issue 编辑功能
    initIssueEditor();
    
    // 初始化评论编辑功能
    initCommentEditor();
    
    // 初始化添加评论功能
    initAddCommentEditor();
    
    // 初始化标签页切换
    initTabSwitching();
    
    // 初始化 Markdown 工具栏
    initMarkdownToolbar();
}

// 初始化 Issue 编辑功能
function initIssueEditor() {
    const editBtn = document.getElementById('edit-issue-btn');
    const editSection = document.getElementById('issue-edit-section');
    const displaySection = document.getElementById('issue-content-display');
    const saveBtn = document.getElementById('save-issue-btn');
    const cancelBtn = document.getElementById('cancel-issue-edit-btn');
    const editor = document.getElementById('issue-editor');
    
    if (!editBtn || !editSection || !displaySection) return;
    
    // 编辑按钮点击事件
    editBtn.addEventListener('click', function() {
        showIssueEditor();
    });
    
    // 保存按钮点击事件
    if (saveBtn) {
        saveBtn.addEventListener('click', function() {
            saveIssueChanges();
        });
    }
    
    // 取消按钮点击事件
    if (cancelBtn) {
        cancelBtn.addEventListener('click', function() {
            hideIssueEditor();
        });
    }
    
    // 编辑器输入事件（实时预览）
    if (editor) {
        editor.addEventListener('input', function() {
            updateIssuePreview();
        });
    }
}

// 初始化评论编辑功能
function initCommentEditor() {
    const editBtns = document.querySelectorAll('.edit-comment-btn');
    
    editBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const commentIndex = this.getAttribute('data-comment-index');
            showCommentEditor(commentIndex);
        });
    });
    
    // 保存和取消按钮事件
    document.addEventListener('click', function(e) {
        if (e.target.id && e.target.id.startsWith('save-comment-btn-')) {
            const commentIndex = e.target.id.replace('save-comment-btn-', '');
            const commentId = e.target.getAttribute('data-comment-id');
            saveCommentChanges(commentIndex, commentId);
        }
        
        if (e.target.id && e.target.id.startsWith('cancel-comment-edit-btn-')) {
            const commentIndex = e.target.id.replace('cancel-comment-edit-btn-', '');
            hideCommentEditor(commentIndex);
        }
    });
    
    // 评论编辑器输入事件
    document.addEventListener('input', function(e) {
        if (e.target.id && e.target.id.startsWith('comment-editor-')) {
            const commentIndex = e.target.id.replace('comment-editor-', '');
            updateCommentPreview(commentIndex);
        }
    });
}

// 初始化添加评论编辑器
function initAddCommentEditor() {
    const textarea = document.getElementById('add-comment-textarea');
    const submitBtn = document.getElementById('submit-comment-btn');
    const writeTab = document.getElementById('add-comment-write-tab');
    const previewTab = document.getElementById('add-comment-preview-tab');
    
    if (!textarea || !submitBtn) return;
    
    // 监听输入变化
    textarea.addEventListener('input', function() {
        // 启用/禁用提交按钮
        submitBtn.disabled = this.value.trim().length === 0;
        
        // 更新预览
        updateAddCommentPreview();
    });
    
    // 标签页切换
    if (writeTab) {
        writeTab.addEventListener('click', function() {
            switchAddCommentTab('write');
        });
    }
    
    if (previewTab) {
        previewTab.addEventListener('click', function() {
            switchAddCommentTab('preview');
            updateAddCommentPreview();
        });
    }
    
    // 提交评论
    submitBtn.addEventListener('click', function() {
        submitNewComment();
    });
    
    // 键盘快捷键
    textarea.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + Enter 提交评论
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            if (!submitBtn.disabled) {
                submitNewComment();
            }
        }
    });
}

// 初始化 Markdown 工具栏
function initMarkdownToolbar() {
    document.addEventListener('click', function(e) {
        if (e.target.closest('.toolbar-btn')) {
            const btn = e.target.closest('.toolbar-btn');
            const action = btn.getAttribute('data-action');
            const textarea = document.getElementById('add-comment-textarea');
            
            if (textarea && action) {
                applyMarkdownFormat(textarea, action);
            }
        }
    });
}

// 初始化标签页切换
function initTabSwitching() {
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('tab-btn')) {
            const tabType = e.target.getAttribute('data-tab');
            const tabContainer = e.target.closest('.issue-edit-section, .comment-edit-section');
            switchTab(tabContainer, tabType);
        }
    });
}

// 显示 Issue 编辑器
function showIssueEditor() {
    const editSection = document.getElementById('issue-edit-section');
    const displaySection = document.getElementById('issue-content-display');
    const editBtn = document.getElementById('edit-issue-btn');
    
    if (editSection && displaySection && editBtn) {
        editSection.style.display = 'block';
        displaySection.style.display = 'none';
        editBtn.style.display = 'none';
        
        // 聚焦到编辑器
        const editor = document.getElementById('issue-editor');
        if (editor) {
            editor.focus();
        }
    }
}

// 隐藏 Issue 编辑器
function hideIssueEditor() {
    const editSection = document.getElementById('issue-edit-section');
    const displaySection = document.getElementById('issue-content-display');
    const editBtn = document.getElementById('edit-issue-btn');
    
    if (editSection && displaySection && editBtn) {
        editSection.style.display = 'none';
        displaySection.style.display = 'block';
        editBtn.style.display = 'inline-block';
    }
}

// 显示评论编辑器
function showCommentEditor(commentIndex) {
    const editSection = document.getElementById(`comment-edit-${commentIndex}`);
    const displaySection = document.getElementById(`comment-content-${commentIndex}`);
    const editBtn = document.querySelector(`[data-comment-index="${commentIndex}"]`);
    
    if (editSection && displaySection && editBtn) {
        editSection.style.display = 'block';
        displaySection.style.display = 'none';
        editBtn.style.display = 'none';
        
        // 聚焦到编辑器
        const editor = document.getElementById(`comment-editor-${commentIndex}`);
        if (editor) {
            editor.focus();
        }
    }
}

// 隐藏评论编辑器
function hideCommentEditor(commentIndex) {
    const editSection = document.getElementById(`comment-edit-${commentIndex}`);
    const displaySection = document.getElementById(`comment-content-${commentIndex}`);
    const editBtn = document.querySelector(`[data-comment-index="${commentIndex}"]`);
    
    if (editSection && displaySection && editBtn) {
        editSection.style.display = 'none';
        displaySection.style.display = 'block';
        editBtn.style.display = 'inline-block';
    }
}

// 切换标签页
function switchTab(container, tabType) {
    if (!container) return;
    
    // 更新标签按钮状态
    const tabBtns = container.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-tab') === tabType) {
            btn.classList.add('active');
        }
    });
    
    // 更新面板显示
    const panels = container.querySelectorAll('.tab-panel');
    panels.forEach(panel => {
        panel.classList.remove('active');
    });
    
    // 显示对应面板
    if (tabType === 'write') {
        const writePanel = container.querySelector('[id*="write-panel"], #write-panel');
        if (writePanel) {
            writePanel.classList.add('active');
        }
    } else if (tabType === 'preview') {
        const previewPanel = container.querySelector('[id*="preview-panel"], #preview-panel');
        if (previewPanel) {
            previewPanel.classList.add('active');
        }
        
        // 更新预览内容
        if (container.id === 'issue-edit-section') {
            updateIssuePreview();
        } else {
            const commentIndex = container.id.replace('comment-edit-', '');
            updateCommentPreview(commentIndex);
        }
    }
}

// 更新 Issue 预览
function updateIssuePreview() {
    const editor = document.getElementById('issue-editor');
    const previewContent = document.getElementById('preview-content');
    
    if (editor && previewContent) {
        const content = editor.value;
        if (content.trim()) {
            // 这里应该调用后端 API 来渲染 Markdown
            // 暂时使用简单的文本显示
            previewContent.innerHTML = `<p>预览功能需要后端支持 Markdown 渲染</p><pre>${escapeHtml(content)}</pre>`;
        } else {
            previewContent.innerHTML = '<p class="no-description">没有内容可预览</p>';
        }
    }
}

// 更新评论预览
function updateCommentPreview(commentIndex) {
    const editor = document.getElementById(`comment-editor-${commentIndex}`);
    const previewContent = document.getElementById(`comment-preview-content-${commentIndex}`);
    
    if (editor && previewContent) {
        const content = editor.value;
        if (content.trim()) {
            // 这里应该调用后端 API 来渲染 Markdown
            // 暂时使用简单的文本显示
            previewContent.innerHTML = `<p>预览功能需要后端支持 Markdown 渲染</p><pre>${escapeHtml(content)}</pre>`;
        } else {
            previewContent.innerHTML = '<p class="no-description">没有内容可预览</p>';
        }
    }
}

// 保存 Issue 更改
function saveIssueChanges() {
    const editor = document.getElementById('issue-editor');
    const saveBtn = document.getElementById('save-issue-btn');
    
    if (!editor || !saveBtn) return;
    
    const content = editor.value.trim();
    
    if (!content) {
        showNotification('内容不能为空', 'error');
        return;
    }
    
    // 显示加载状态
    saveBtn.disabled = true;
    saveBtn.textContent = '保存中...';
    
    // 获取当前页面信息
    const pathParts = window.location.pathname.split('/');
    const owner = pathParts[2];
    const repo = pathParts[3];
    const issueNumber = pathParts[5];
    
    // 发送请求到后端更新 Issue
    fetch(`/api/repos/${owner}/${repo}/issues/${issueNumber}`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            body: content
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 更新显示的内容
            const issueContent = document.querySelector('.issue-content .markdown-content');
            if (issueContent) {
                // 注意：这里应该使用后端渲染的 Markdown，目前只是简单显示文本
                issueContent.innerHTML = escapeHtml(content);
            }
            
            hideIssueEditor();
            showNotification('Issue 已保存并同步到 GitHub');
        } else {
            showNotification(data.error || '保存失败', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('网络错误，请稍后重试', 'error');
    })
    .finally(() => {
        // 重置按钮状态
        saveBtn.disabled = false;
        saveBtn.textContent = '保存更改';
    });
}

// 保存评论更改
function saveCommentChanges(commentIndex, commentId) {
    const editor = document.getElementById(`comment-editor-${commentIndex}`);
    const saveBtn = document.getElementById(`save-comment-btn-${commentIndex}`);
    
    if (!editor || !saveBtn) return;
    
    const content = editor.value.trim();
    
    if (!content) {
        showNotification('评论内容不能为空', 'error');
        return;
    }
    
    // 显示加载状态
    saveBtn.disabled = true;
    saveBtn.textContent = '保存中...';
    
    // 获取当前页面信息
    const pathParts = window.location.pathname.split('/');
    const owner = pathParts[2];
    const repo = pathParts[3];
    const issueNumber = pathParts[5];
    
    // 发送请求到后端更新评论
    fetch(`/api/repos/${owner}/${repo}/comments/${commentId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            body: content
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 更新显示的内容
            const commentContent = document.querySelector(`#comment-content-${commentIndex} .markdown-content`);
            if (commentContent) {
                // 注意：这里应该使用后端渲染的 Markdown，目前只是简单显示文本
                commentContent.innerHTML = escapeHtml(content);
            }
            
            hideCommentEditor(commentIndex);
            showNotification('评论已保存并同步到 GitHub');
        } else {
            showNotification(data.error || '保存评论失败', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('网络错误，请稍后重试', 'error');
    })
    .finally(() => {
        // 重置按钮状态
        saveBtn.disabled = false;
        saveBtn.textContent = '保存更改';
    });
}

// 切换添加评论标签页
function switchAddCommentTab(tabType) {
    const writeTab = document.getElementById('add-comment-write-tab');
    const previewTab = document.getElementById('add-comment-preview-tab');
    const writeContent = document.getElementById('add-comment-write-content');
    const previewContent = document.getElementById('add-comment-preview-content');
    
    if (!writeTab || !previewTab || !writeContent || !previewContent) return;
    
    if (tabType === 'write') {
        writeTab.classList.add('active');
        previewTab.classList.remove('active');
        writeContent.style.display = 'block';
        previewContent.style.display = 'none';
    } else {
        writeTab.classList.remove('active');
        previewTab.classList.add('active');
        writeContent.style.display = 'none';
        previewContent.style.display = 'block';
    }
}

// 更新添加评论预览
function updateAddCommentPreview() {
    const textarea = document.getElementById('add-comment-textarea');
    const previewContent = document.getElementById('add-comment-preview-content');
    
    if (!textarea || !previewContent) return;
    
    const content = textarea.value.trim();
    if (content) {
        // 简单的 Markdown 预览（实际应用中需要后端支持）
        previewContent.innerHTML = `<div class="markdown-preview">${escapeHtml(content)}</div>`;
    } else {
        previewContent.innerHTML = '<div class="preview-placeholder">Nothing to preview</div>';
    }
}

// 应用 Markdown 格式
function applyMarkdownFormat(textarea, action) {
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = textarea.value.substring(start, end);
    let replacement = '';
    let cursorOffset = 0;
    
    switch (action) {
        case 'bold':
            replacement = `**${selectedText || 'bold text'}**`;
            cursorOffset = selectedText ? 0 : -9;
            break;
        case 'italic':
            replacement = `*${selectedText || 'italic text'}*`;
            cursorOffset = selectedText ? 0 : -11;
            break;
        case 'code':
            replacement = `\`${selectedText || 'code'}\``;
            cursorOffset = selectedText ? 0 : -5;
            break;
        case 'link':
            replacement = `[${selectedText || 'link text'}](url)`;
            cursorOffset = selectedText ? -5 : -14;
            break;
        case 'unordered-list':
            replacement = `- ${selectedText || 'list item'}`;
            cursorOffset = selectedText ? 0 : -9;
            break;
        case 'ordered-list':
            replacement = `1. ${selectedText || 'list item'}`;
            cursorOffset = selectedText ? 0 : -9;
            break;
        case 'quote':
            replacement = `> ${selectedText || 'quote'}`;
            cursorOffset = selectedText ? 0 : -5;
            break;
        default:
            return;
    }
    
    // 替换选中文本
    textarea.value = textarea.value.substring(0, start) + replacement + textarea.value.substring(end);
    
    // 设置光标位置
    const newCursorPos = start + replacement.length + cursorOffset;
    textarea.setSelectionRange(newCursorPos, newCursorPos);
    textarea.focus();
    
    // 触发输入事件以更新预览
    textarea.dispatchEvent(new Event('input'));
}

// 提交新评论
function submitNewComment() {
    const textarea = document.getElementById('add-comment-textarea');
    const submitBtn = document.getElementById('submit-comment-btn');
    
    if (!textarea || !submitBtn) return;
    
    const content = textarea.value.trim();
    if (!content) {
        showNotification('请输入评论内容', 'error');
        return;
    }
    
    // 禁用提交按钮
    submitBtn.disabled = true;
    submitBtn.textContent = '提交中...';
    
    // 获取当前页面信息
    const pathParts = window.location.pathname.split('/');
    const owner = pathParts[2];
    const repo = pathParts[3];
    const issueNumber = pathParts[5];
    
    // 发送请求到后端
    fetch(`/api/repos/${owner}/${repo}/issues/${issueNumber}/comments`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            body: content
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('评论已成功添加');
            // 清空输入框
            textarea.value = '';
            // 刷新页面以显示新评论
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showNotification(data.error || '添加评论失败', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('网络错误，请稍后重试', 'error');
    })
    .finally(() => {
        // 恢复提交按钮
        submitBtn.disabled = false;
        submitBtn.textContent = 'Comment';
    });
}

// 显示通知
function showNotification(message, type = 'info') {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // 添加样式
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 6px;
        color: white;
        font-weight: 500;
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
    `;
    
    // 设置背景色
    if (type === 'success') {
        notification.style.backgroundColor = '#28a745';
    } else if (type === 'error') {
        notification.style.backgroundColor = '#dc3545';
    } else {
        notification.style.backgroundColor = '#007bff';
    }
    
    // 添加到页面
    document.body.appendChild(notification);
    
    // 3秒后自动移除
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// 工具函数
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getRepoNameFromUrl() {
    const pathParts = window.location.pathname.split('/');
    if (pathParts.length >= 4 && pathParts[1] === 'repo') {
        return `${pathParts[2]}/${pathParts[3]}`;
    }
    return null;
}

function getIssueNumberFromUrl() {
    const pathParts = window.location.pathname.split('/');
    if (pathParts.length >= 6 && pathParts[4] === 'issue') {
        return parseInt(pathParts[5]);
    }
    return null;
}

// 添加 CSS 动画
if (!document.getElementById('notification-styles')) {
    const style = document.createElement('style');
    style.id = 'notification-styles';
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
}

// 导出函数供其他脚本使用
window.MarkdownEditor = {
    showIssueEditor,
    hideIssueEditor,
    showCommentEditor,
    hideCommentEditor,
    updateIssuePreview,
    updateCommentPreview
};
// Issue 详情和评论页面的 JavaScript 功能

document.addEventListener('DOMContentLoaded', function() {
    initCommentsPage();
});

function initCommentsPage() {
    // 初始化评论交互
    initCommentInteractions();
    
    // 初始化代码高亮
    initCodeHighlight();
    
    // 初始化图片预览
    initImagePreview();
    
    // 初始化链接处理
    initLinkHandling();
    
    // 初始化评论筛选
    initCommentFilters();
    
    // 初始化评论搜索
    initCommentSearch();
    
    // 加载评论统计
    loadCommentStats();
}

// 初始化评论交互
function initCommentInteractions() {
    // 初始化评论展开/折叠
    const commentItems = document.querySelectorAll('.comment-item');
    commentItems.forEach(comment => {
        const body = comment.querySelector('.comment-body');
        if (body && body.scrollHeight > 200) {
            addExpandButton(comment, body);
        }
    });
    
    // 初始化评论操作按钮
    initCommentActions();
    
    // 初始化回复功能
    initReplyFunctionality();
}

// 添加展开按钮
function addExpandButton(comment, body) {
    body.style.maxHeight = '200px';
    body.style.overflow = 'hidden';
    body.style.position = 'relative';
    
    const expandBtn = document.createElement('button');
    expandBtn.className = 'expand-btn';
    expandBtn.textContent = '展开更多';
    expandBtn.style.cssText = `
        position: absolute;
        bottom: 0;
        right: 0;
        background: linear-gradient(to right, transparent, #fff 30%);
        border: none;
        padding: 5px 10px;
        color: #0366d6;
        cursor: pointer;
        font-size: 0.9rem;
    `;
    
    expandBtn.addEventListener('click', function() {
        if (body.style.maxHeight === '200px') {
            body.style.maxHeight = 'none';
            this.textContent = '收起';
        } else {
            body.style.maxHeight = '200px';
            this.textContent = '展开更多';
        }
    });
    
    body.appendChild(expandBtn);
}

// 初始化评论操作
function initCommentActions() {
    // 三点菜单点击事件
    const menuButtons = document.querySelectorAll('.comment-menu-btn');
    menuButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const commentIndex = this.getAttribute('data-comment-index');
            const dropdown = document.getElementById(`comment-menu-${commentIndex}`);
            
            // 关闭其他打开的菜单
            document.querySelectorAll('.comment-menu-dropdown').forEach(menu => {
                if (menu !== dropdown) {
                    menu.style.display = 'none';
                }
            });
            
            // 切换当前菜单显示状态
            dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
        });
    });
    
    // 点击页面其他地方关闭菜单
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.comment-menu')) {
            document.querySelectorAll('.comment-menu-dropdown').forEach(menu => {
                menu.style.display = 'none';
            });
        }
    });
    
    // 删除评论按钮
    const deleteButtons = document.querySelectorAll('.delete-comment-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const commentId = this.getAttribute('data-comment-id');
            const commentIndex = this.getAttribute('data-comment-index');
            
            if (confirm('确定要删除这条评论吗？此操作无法撤销。')) {
                deleteComment(commentId, commentIndex);
            }
            
            // 关闭菜单
            const dropdown = document.getElementById(`comment-menu-${commentIndex}`);
            dropdown.style.display = 'none';
        });
    });
    
    // 复制评论链接
    const copyButtons = document.querySelectorAll('.copy-comment-link');
    copyButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const commentId = this.getAttribute('data-comment-id');
            const currentUrl = window.location.href.split('#')[0];
            const commentUrl = `${currentUrl}#comment-${commentId}`;
            
            window.HubNote.copyToClipboard(commentUrl);
        });
    });
    
    // 引用评论
    const quoteButtons = document.querySelectorAll('.quote-comment');
    quoteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const comment = this.closest('.comment-item');
            const author = comment.querySelector('.comment-author').textContent;
            const body = comment.querySelector('.comment-body').textContent.trim();
            
            const quotedText = `> ${body.split('\n').join('\n> ')}\n\n@${author} `;
            
            // 如果有回复框，填入引用内容
            const replyTextarea = document.querySelector('.reply-textarea');
            if (replyTextarea) {
                replyTextarea.value = quotedText;
                replyTextarea.focus();
            } else {
                window.HubNote.copyToClipboard(quotedText);
        window.HubNote.showNotification('引用内容已复制到剪贴板', 'success');
            }
        });
    });
}

// 初始化回复功能
function initReplyFunctionality() {
    const replyButtons = document.querySelectorAll('.reply-btn');
    replyButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const comment = this.closest('.comment-item');
            const author = comment.querySelector('.comment-author').textContent;
            
            // 显示回复框
            showReplyBox(comment, author);
        });
    });
}

// 显示回复框
function showReplyBox(comment, replyToAuthor) {
    // 移除已存在的回复框
    const existingReplyBox = document.querySelector('.reply-box');
    if (existingReplyBox) {
        existingReplyBox.remove();
    }
    
    const replyBox = document.createElement('div');
    replyBox.className = 'reply-box';
    replyBox.innerHTML = `
        <div class="reply-header">
            <span>回复 @${replyToAuthor}</span>
            <button class="close-reply-btn" type="button">×</button>
        </div>
        <textarea class="reply-textarea" placeholder="写下你的回复..." rows="4"></textarea>
        <div class="reply-actions">
            <button class="btn btn-primary submit-reply-btn" type="button">发送回复</button>
            <button class="btn btn-secondary cancel-reply-btn" type="button">取消</button>
        </div>
    `;
    
    // 插入回复框
    comment.parentNode.insertBefore(replyBox, comment.nextSibling);
    
    // 绑定事件
    const closeBtn = replyBox.querySelector('.close-reply-btn');
    const cancelBtn = replyBox.querySelector('.cancel-reply-btn');
    const submitBtn = replyBox.querySelector('.submit-reply-btn');
    const textarea = replyBox.querySelector('.reply-textarea');
    
    closeBtn.addEventListener('click', () => replyBox.remove());
    cancelBtn.addEventListener('click', () => replyBox.remove());
    
    submitBtn.addEventListener('click', function() {
        const replyText = textarea.value.trim();
        if (!replyText) {
            window.HubNote.showNotification('请输入回复内容', 'error');
            return;
        }
        
        // 这里应该调用 API 发送回复，但由于是只读应用，我们只是显示提示
        window.HubNote.showNotification('此应用为只读模式，无法发送回复。请前往 GitHub 进行回复。', 'info');
    });
    
    // 自动聚焦
    textarea.focus();
}

// 初始化代码高亮
function initCodeHighlight() {
    const codeBlocks = document.querySelectorAll('pre code');
    codeBlocks.forEach(block => {
        // 添加复制按钮
        addCopyButton(block);
        
        // 添加语言标签
        addLanguageLabel(block);
    });
}

// 添加代码复制按钮
function addCopyButton(codeBlock) {
    const pre = codeBlock.parentElement;
    if (pre.tagName !== 'PRE') return;
    
    const copyBtn = document.createElement('button');
    copyBtn.className = 'copy-code-btn';
    copyBtn.textContent = '复制';
    copyBtn.style.cssText = `
        position: absolute;
        top: 8px;
        right: 8px;
        background: #f6f8fa;
        border: 1px solid #d1d5da;
        border-radius: 3px;
        padding: 4px 8px;
        font-size: 12px;
        cursor: pointer;
        opacity: 0;
        transition: opacity 0.2s;
    `;
    
    pre.style.position = 'relative';
    pre.appendChild(copyBtn);
    
    // 悬停显示按钮
    pre.addEventListener('mouseenter', () => {
        copyBtn.style.opacity = '1';
    });
    
    pre.addEventListener('mouseleave', () => {
        copyBtn.style.opacity = '0';
    });
    
    // 复制功能
    copyBtn.addEventListener('click', function() {
        const code = codeBlock.textContent;
        window.HubNote.copyToClipboard(code);
        
        this.textContent = '已复制';
        setTimeout(() => {
            this.textContent = '复制';
        }, 2000);
    });
}

// 添加语言标签
function addLanguageLabel(codeBlock) {
    const className = codeBlock.className;
    const languageMatch = className.match(/language-(\w+)/);
    
    if (languageMatch) {
        const language = languageMatch[1];
        const pre = codeBlock.parentElement;
        
        const langLabel = document.createElement('span');
        langLabel.className = 'code-language';
        langLabel.textContent = language;
        langLabel.style.cssText = `
            position: absolute;
            top: 8px;
            left: 8px;
            background: #0366d6;
            color: white;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 11px;
            font-weight: bold;
            text-transform: uppercase;
        `;
        
        pre.appendChild(langLabel);
    }
}

// 初始化图片预览
function initImagePreview() {
    const images = document.querySelectorAll('.comment-body img');
    images.forEach(img => {
        img.style.cursor = 'pointer';
        img.addEventListener('click', function() {
            showImageModal(this.src, this.alt);
        });
    });
}

// 显示图片模态框
function showImageModal(src, alt) {
    const modal = document.createElement('div');
    modal.className = 'image-modal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.8);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 10000;
        cursor: pointer;
    `;
    
    const img = document.createElement('img');
    img.src = src;
    img.alt = alt;
    img.style.cssText = `
        max-width: 90%;
        max-height: 90%;
        object-fit: contain;
        border-radius: 4px;
    `;
    
    modal.appendChild(img);
    document.body.appendChild(modal);
    
    // 点击关闭
    modal.addEventListener('click', function() {
        this.remove();
    });
    
    // ESC 键关闭
    const handleEsc = function(e) {
        if (e.key === 'Escape') {
            modal.remove();
            document.removeEventListener('keydown', handleEsc);
        }
    };
    document.addEventListener('keydown', handleEsc);
}

// 初始化链接处理
function initLinkHandling() {
    // 处理所有页面中的链接，包括评论和Issue内容中的链接
    const links = document.querySelectorAll('.markdown-content a, .comment-body a, .issue-content a');
    links.forEach(link => {
        // 外部链接在新窗口打开
        if (link.hostname !== window.location.hostname) {
            link.target = '_blank';
            link.rel = 'noopener noreferrer';
            
            // 添加外部链接图标
            if (!link.querySelector('.external-link-icon')) {
                const icon = document.createElement('span');
                icon.className = 'external-link-icon';
                icon.innerHTML = ' ↗';
                icon.style.fontSize = '0.8em';
                icon.style.opacity = '0.7';
                link.appendChild(icon);
            }
        }
    });
    
    // 监听动态添加的内容
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        const newLinks = node.querySelectorAll('.markdown-content a, .comment-body a, .issue-content a');
                        newLinks.forEach(link => {
                            if (link.hostname !== window.location.hostname) {
                                link.target = '_blank';
                                link.rel = 'noopener noreferrer';
                                
                                if (!link.querySelector('.external-link-icon')) {
                                    const icon = document.createElement('span');
                                    icon.className = 'external-link-icon';
                                    icon.innerHTML = ' ↗';
                                    icon.style.fontSize = '0.8em';
                                    icon.style.opacity = '0.7';
                                    link.appendChild(icon);
                                }
                            }
                        });
                    }
                });
            }
        });
    });
    
    // 开始观察DOM变化
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
}

// 初始化评论筛选
function initCommentFilters() {
    const filterSelect = document.getElementById('comment-filter');
    if (!filterSelect) return;
    
    filterSelect.addEventListener('change', function() {
        filterComments(this.value);
    });
}

// 筛选评论
function filterComments(filterType) {
    const comments = document.querySelectorAll('.comment-item');
    
    comments.forEach(comment => {
        let isVisible = true;
        
        switch (filterType) {
            case 'all':
                isVisible = true;
                break;
            case 'author':
                // 只显示作者的评论
                const isAuthor = comment.querySelector('.comment-author').classList.contains('issue-author');
                isVisible = isAuthor;
                break;
            case 'collaborators':
                // 只显示协作者的评论
                const isCollaborator = comment.querySelector('.comment-author').classList.contains('collaborator');
                isVisible = isCollaborator;
                break;
            case 'with-code':
                // 只显示包含代码的评论
                const hasCode = comment.querySelector('.comment-body pre, .comment-body code');
                isVisible = !!hasCode;
                break;
        }
        
        comment.style.display = isVisible ? 'block' : 'none';
    });
}

// 初始化评论搜索
function initCommentSearch() {
    const searchInput = document.getElementById('comment-search');
    if (!searchInput) return;
    
    let searchTimeout;
    
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            searchComments(this.value.trim());
        }, 300);
    });
}

// 搜索评论
function searchComments(searchTerm) {
    const comments = document.querySelectorAll('.comment-item');
    let visibleCount = 0;
    
    comments.forEach(comment => {
        const author = comment.querySelector('.comment-author').textContent.toLowerCase();
        const body = comment.querySelector('.comment-body').textContent.toLowerCase();
        
        const searchLower = searchTerm.toLowerCase();
        const isVisible = !searchTerm || 
            author.includes(searchLower) || 
            body.includes(searchLower);
        
        if (isVisible) {
            comment.style.display = 'block';
            visibleCount++;
        } else {
            comment.style.display = 'none';
        }
    });
    
    updateCommentSearchResults(visibleCount, searchTerm);
}

// 更新评论搜索结果
function updateCommentSearchResults(visibleCount, searchTerm) {
    let resultDiv = document.getElementById('comment-search-results');
    
    if (!resultDiv) {
        resultDiv = document.createElement('div');
        resultDiv.id = 'comment-search-results';
        resultDiv.className = 'search-results';
        
        const commentsList = document.querySelector('.comments-list');
        if (commentsList) {
            commentsList.parentNode.insertBefore(resultDiv, commentsList);
        }
    }
    
    if (searchTerm) {
        resultDiv.textContent = `找到 ${visibleCount} 条匹配的评论`;
        resultDiv.style.display = 'block';
    } else {
        resultDiv.style.display = 'none';
    }
}

// 加载评论统计
function loadCommentStats() {
    const comments = document.querySelectorAll('.comment-item');
    const totalComments = comments.length;
    
    if (totalComments === 0) return;
    
    const authors = {};
    let totalWords = 0;
    let codeBlocks = 0;
    let images = 0;
    
    comments.forEach(comment => {
        // 统计作者
        const author = comment.querySelector('.comment-author').textContent.trim();
        authors[author] = (authors[author] || 0) + 1;
        
        // 统计字数
        const body = comment.querySelector('.comment-body').textContent.trim();
        totalWords += body.split(/\s+/).length;
        
        // 统计代码块
        const codeElements = comment.querySelectorAll('.comment-body pre, .comment-body code');
        codeBlocks += codeElements.length;
        
        // 统计图片
        const imgElements = comment.querySelectorAll('.comment-body img');
        images += imgElements.length;
    });
    
    displayCommentStats({
        totalComments,
        authors,
        totalWords,
        codeBlocks,
        images
    });
}

// 显示评论统计
function displayCommentStats(stats) {
    let statsDiv = document.getElementById('comment-stats');
    
    if (!statsDiv) {
        statsDiv = document.createElement('div');
        statsDiv.id = 'comment-stats';
        statsDiv.className = 'comment-stats';
        
        const issueHeader = document.querySelector('.issue-header');
        if (issueHeader) {
            issueHeader.appendChild(statsDiv);
        }
    }
    
    const topAuthors = Object.entries(stats.authors)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 3)
        .map(([author, count]) => `${author} (${count})`)
        .join(', ');
    
    statsDiv.innerHTML = `
        <div class="stats-summary">
            <span class="stat-item">${stats.totalComments} 条评论</span>
            <span class="stat-item">${stats.totalWords} 字</span>
            ${stats.codeBlocks > 0 ? `<span class="stat-item">${stats.codeBlocks} 代码块</span>` : ''}
            ${stats.images > 0 ? `<span class="stat-item">${stats.images} 图片</span>` : ''}
            ${topAuthors ? `<span class="stat-item">主要参与者: ${topAuthors}</span>` : ''}
        </div>
    `;
}

// 跳转到评论
function scrollToComment(commentId) {
    const comment = document.getElementById(`comment-${commentId}`);
    if (comment) {
        comment.scrollIntoView({ behavior: 'smooth', block: 'center' });
        comment.style.backgroundColor = '#fff3cd';
        setTimeout(() => {
            comment.style.backgroundColor = '';
        }, 2000);
    }
}

// 导出函数供全局使用
window.CommentsManager = {
    filterComments,
    searchComments,
    scrollToComment,
    showImageModal
};

// 处理 URL 中的评论锚点// 删除评论函数
function deleteComment(commentId, commentIndex) {
    const repoFullName = window.location.pathname.match(/\/repo\/([^\/]+\/[^\/]+)/)[1];
    
    fetch(`/api/repos/${repoFullName}/issues/comments/${commentId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 删除成功，移除DOM元素
            const commentElement = document.querySelector(`[data-comment-index="${commentIndex}"]`).closest('.comment-item');
            if (commentElement) {
                commentElement.remove();
            }
            
            // 显示成功消息
            if (window.HubNote && window.HubNote.showNotification) {
            window.HubNote.showNotification('评论删除成功', 'success');
            } else {
                alert('评论删除成功');
            }
            
            // 刷新页面以更新评论计数
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            // 删除失败
            if (window.HubNote && window.HubNote.showNotification) {
            window.HubNote.showNotification(data.message || '删除评论失败', 'error');
            } else {
                alert(data.message || '删除评论失败');
            }
        }
    })
    .catch(error => {
        console.error('删除评论时发生错误:', error);
        if (window.HubNote && window.HubNote.showNotification) {
            window.HubNote.showNotification('删除评论时发生错误', 'error');
        } else {
            alert('删除评论时发生错误');
        }
    });
}

// 如果URL中有评论锚点，滚动到对应评论
if (window.location.hash.startsWith('#comment-')) {
    const commentId = window.location.hash.replace('#comment-', '');
    setTimeout(() => {
        scrollToComment(commentId);
    }, 500);
}
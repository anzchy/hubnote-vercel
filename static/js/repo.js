// 仓库管理页面的 JavaScript 功能

document.addEventListener('DOMContentLoaded', function() {
    initRepoPage();
});

function initRepoPage() {
    // 初始化添加仓库表单
    initAddRepoForm();
    
    // 初始化删除仓库功能
    initDeleteRepo();
    
    // 初始化搜索功能
    initRepoSearch();
    
    // 初始化排序功能
    initRepoSort();
    
    // 加载仓库统计信息
    loadRepoStats();
}

// 初始化添加仓库表单
function initAddRepoForm() {
    const form = document.getElementById('add-repo-form');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(form);
        const repoUrl = formData.get('repo_url').trim();
        
        if (!repoUrl) {
            window.GitNote.showNotification('请输入仓库 URL', 'error');
            return;
        }
        
        if (!isValidRepoUrl(repoUrl)) {
            window.GitNote.showNotification('请输入有效的 GitHub 仓库 URL', 'error');
            return;
        }
        
        addRepository(repoUrl);
    });
}

// 添加仓库
function addRepository(repoUrl) {
    const submitBtn = document.querySelector('#add-repo-form button[type="submit"]');
    const originalText = submitBtn.textContent;
    
    // 显示加载状态
    submitBtn.textContent = '添加中...';
    submitBtn.disabled = true;
    
    // 发送请求
    fetch('/add_repo', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `repo_url=${encodeURIComponent(repoUrl)}`
    })
    .then(response => {
        if (response.ok) {
            window.GitNote.showNotification('仓库添加成功！', 'success');
            // 清空表单
            document.getElementById('add-repo-form').reset();
            // 刷新页面显示新添加的仓库
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            return response.text().then(text => {
                throw new Error(text || '添加仓库失败');
            });
        }
    })
    .catch(error => {
        console.error('添加仓库失败:', error);
        window.GitNote.showNotification(error.message || '添加仓库失败', 'error');
    })
    .finally(() => {
        // 恢复按钮状态
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    });
}

// 初始化删除仓库功能
function initDeleteRepo() {
    const deleteButtons = document.querySelectorAll('.delete-repo-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const repoName = this.getAttribute('data-repo');
            const repoDisplayName = this.getAttribute('data-repo-name') || repoName;
            
            window.GitNote.confirmAction(
                `确定要删除仓库 "${repoDisplayName}" 吗？\n\n注意：这只会从本地列表中移除，不会影响 GitHub 上的仓库。`,
                () => deleteRepository(repoName)
            );
        });
    });
}

// 删除仓库
function deleteRepository(repoName) {
    fetch('/remove_repo', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `repo_name=${encodeURIComponent(repoName)}`
    })
    .then(response => {
        if (response.ok) {
            window.GitNote.showNotification('仓库删除成功！', 'success');
            // 移除对应的仓库卡片
            const repoCard = document.querySelector(`[data-repo="${repoName}"]`).closest('.repo-card');
            if (repoCard) {
                repoCard.style.opacity = '0';
                repoCard.style.transform = 'scale(0.9)';
                setTimeout(() => {
                    repoCard.remove();
                    updateRepoStats();
                }, 300);
            }
        } else {
            return response.text().then(text => {
                throw new Error(text || '删除仓库失败');
            });
        }
    })
    .catch(error => {
        console.error('删除仓库失败:', error);
        window.GitNote.showNotification(error.message || '删除仓库失败', 'error');
    });
}

// 初始化搜索功能
function initRepoSearch() {
    const searchInput = document.getElementById('repo-search');
    if (!searchInput) return;
    
    let searchTimeout;
    
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            filterRepositories(this.value.trim());
        }, 300);
    });
}

// 过滤仓库
function filterRepositories(searchTerm) {
    const repoCards = document.querySelectorAll('.repo-card');
    let visibleCount = 0;
    
    repoCards.forEach(card => {
        const repoName = card.querySelector('.repo-name').textContent.toLowerCase();
        const repoDesc = card.querySelector('.repo-description')?.textContent.toLowerCase() || '';
        const repoLang = card.querySelector('.repo-language')?.textContent.toLowerCase() || '';
        
        const searchLower = searchTerm.toLowerCase();
        const isVisible = !searchTerm || 
            repoName.includes(searchLower) || 
            repoDesc.includes(searchLower) || 
            repoLang.includes(searchLower);
        
        if (isVisible) {
            card.style.display = 'block';
            visibleCount++;
        } else {
            card.style.display = 'none';
        }
    });
    
    // 显示搜索结果统计
    updateSearchResults(visibleCount, repoCards.length, searchTerm);
}

// 更新搜索结果显示
function updateSearchResults(visibleCount, totalCount, searchTerm) {
    let resultDiv = document.getElementById('search-results');
    
    if (!resultDiv) {
        resultDiv = document.createElement('div');
        resultDiv.id = 'search-results';
        resultDiv.className = 'search-results';
        
        const repoGrid = document.querySelector('.repo-grid');
        if (repoGrid) {
            repoGrid.parentNode.insertBefore(resultDiv, repoGrid);
        }
    }
    
    if (searchTerm) {
        resultDiv.textContent = `找到 ${visibleCount} 个匹配的仓库（共 ${totalCount} 个）`;
        resultDiv.style.display = 'block';
    } else {
        resultDiv.style.display = 'none';
    }
}

// 初始化排序功能
function initRepoSort() {
    const sortSelect = document.getElementById('repo-sort');
    if (!sortSelect) return;
    
    sortSelect.addEventListener('change', function() {
        sortRepositories(this.value);
    });
}

// 排序仓库
function sortRepositories(sortBy) {
    const repoGrid = document.querySelector('.repo-grid');
    if (!repoGrid) return;
    
    const repoCards = Array.from(repoGrid.querySelectorAll('.repo-card'));
    
    repoCards.sort((a, b) => {
        switch (sortBy) {
            case 'name':
                const nameA = a.querySelector('.repo-name').textContent.toLowerCase();
                const nameB = b.querySelector('.repo-name').textContent.toLowerCase();
                return nameA.localeCompare(nameB);
                
            case 'stars':
                const starsA = parseInt(a.querySelector('.repo-stars')?.textContent || '0');
                const starsB = parseInt(b.querySelector('.repo-stars')?.textContent || '0');
                return starsB - starsA;
                
            case 'issues':
                const issuesA = parseInt(a.querySelector('.repo-issues')?.textContent || '0');
                const issuesB = parseInt(b.querySelector('.repo-issues')?.textContent || '0');
                return issuesB - issuesA;
                
            case 'updated':
                const dateA = new Date(a.querySelector('.repo-updated')?.getAttribute('data-date') || '1970-01-01');
                const dateB = new Date(b.querySelector('.repo-updated')?.getAttribute('data-date') || '1970-01-01');
                return dateB - dateA;
                
            case 'added':
            default:
                const addedA = new Date(a.querySelector('.repo-added')?.getAttribute('data-date') || '1970-01-01');
                const addedB = new Date(b.querySelector('.repo-added')?.getAttribute('data-date') || '1970-01-01');
                return addedB - addedA;
        }
    });
    
    // 重新排列 DOM 元素
    repoCards.forEach(card => {
        repoGrid.appendChild(card);
    });
}

// 加载仓库统计信息
function loadRepoStats() {
    const repoCards = document.querySelectorAll('.repo-card');
    const totalRepos = repoCards.length;
    
    if (totalRepos === 0) return;
    
    let totalStars = 0;
    let totalIssues = 0;
    let totalForks = 0;
    const languages = {};
    
    repoCards.forEach(card => {
        // 统计星标数
        const stars = parseInt(card.querySelector('.repo-stars')?.textContent || '0');
        totalStars += stars;
        
        // 统计 Issues 数
        const issues = parseInt(card.querySelector('.repo-issues')?.textContent || '0');
        totalIssues += issues;
        
        // 统计 Fork 数
        const forks = parseInt(card.querySelector('.repo-forks')?.textContent || '0');
        totalForks += forks;
        
        // 统计编程语言
        const langElement = card.querySelector('.repo-language');
        if (langElement) {
            const lang = langElement.textContent.trim();
            if (lang) {
                languages[lang] = (languages[lang] || 0) + 1;
            }
        }
    });
    
    // 显示统计信息
    displayRepoStats({
        totalRepos,
        totalStars,
        totalIssues,
        totalForks,
        languages
    });
}

// 显示仓库统计信息
function displayRepoStats(stats) {
    let statsDiv = document.getElementById('repo-stats');
    
    if (!statsDiv) {
        statsDiv = document.createElement('div');
        statsDiv.id = 'repo-stats';
        statsDiv.className = 'repo-stats';
        
        const pageHeader = document.querySelector('.page-header');
        if (pageHeader) {
            pageHeader.appendChild(statsDiv);
        }
    }
    
    const topLanguages = Object.entries(stats.languages)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 3)
        .map(([lang, count]) => `${lang} (${count})`)
        .join(', ');
    
    statsDiv.innerHTML = `
        <div class="stats-grid">
            <div class="stat-item">
                <span class="stat-number">${stats.totalRepos}</span>
                <span class="stat-label">仓库</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">${stats.totalStars}</span>
                <span class="stat-label">星标</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">${stats.totalIssues}</span>
                <span class="stat-label">Issues</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">${stats.totalForks}</span>
                <span class="stat-label">Forks</span>
            </div>
            ${topLanguages ? `
            <div class="stat-item stat-languages">
                <span class="stat-label">主要语言</span>
                <span class="stat-value">${topLanguages}</span>
            </div>
            ` : ''}
        </div>
    `;
}

// 更新统计信息
function updateRepoStats() {
    loadRepoStats();
}

// 验证仓库 URL
function isValidRepoUrl(url) {
    // GitHub URL 格式
    const githubUrlPattern = /^https?:\/\/github\.com\/[\w.-]+\/[\w.-]+\/?$/;
    // owner/repo 格式
    const ownerRepoPattern = /^[\w.-]+\/[\w.-]+$/;
    
    return githubUrlPattern.test(url) || ownerRepoPattern.test(url);
}

// 复制仓库链接
function copyRepoLink(repoName) {
    const repoUrl = `https://github.com/${repoName}`;
    window.GitNote.copyToClipboard(repoUrl);
}

// 导出函数供全局使用
window.RepoManager = {
    addRepository,
    deleteRepository,
    filterRepositories,
    sortRepositories,
    copyRepoLink,
    updateRepoStats
};
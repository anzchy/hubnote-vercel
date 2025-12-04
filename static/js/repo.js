// 仓库管理页面的 JavaScript 功能

document.addEventListener('DOMContentLoaded', function() {
    initRepoPage();
});

function initRepoPage() {
    // 加载仓库列表（Client-Side Rendering）
    loadRepositories();

    // 初始化添加仓库表单
    initAddRepoForm();
    
    // 初始化搜索功能
    initRepoSearch();
    
    // 初始化排序功能
    initRepoSort();
}

// 加载仓库列表
function loadRepositories() {
    const loadingState = document.getElementById('loading-state');
    const reposGrid = document.getElementById('repos-grid');
    const emptyState = document.getElementById('empty-state');
    const repoCountBadge = document.getElementById('repo-count-badge');
    const exportBtn = document.getElementById('exportDataBtn');
    
    if (loadingState) loadingState.style.display = 'block';
    if (reposGrid) reposGrid.style.display = 'none';
    if (emptyState) emptyState.style.display = 'none';
    
    fetch('/api/my_repos')
        .then(response => {
            if (!response.ok) {
                throw new Error('加载仓库列表失败: ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            if (loadingState) loadingState.style.display = 'none';
            
            if (data.success && data.repositories && data.repositories.length > 0) {
                renderRepoList(data.repositories);
                if (reposGrid) reposGrid.style.display = 'grid';
                if (exportBtn) exportBtn.style.display = 'inline-flex';
            } else {
                if (emptyState) emptyState.style.display = 'flex';
                if (exportBtn) exportBtn.style.display = 'none';
            }
            
            // 更新计数
            if (repoCountBadge) {
                const count = data.repositories ? data.repositories.length : 0;
                repoCountBadge.textContent = `(${count})`;
            }
            
            // 加载统计信息
            if (data.repositories) {
                calculateAndDisplayStats(data.repositories);
            }
        })
        .catch(error => {
            console.error('加载仓库失败:', error);
            if (loadingState) loadingState.style.display = 'none';
            window.HubNote.showNotification('加载仓库列表失败，请刷新重试', 'error');
        });
}

// 渲染仓库列表
function renderRepoList(repos) {
    const reposGrid = document.getElementById('repos-grid');
    if (!reposGrid) return;
    
    reposGrid.innerHTML = '';
    
    repos.forEach(repo => {
        const repoCard = createRepoCard(repo);
        reposGrid.appendChild(repoCard);
    });
    
    // 初始化删除按钮事件
    initDeleteButtons();
}

// 创建单个仓库卡片
function createRepoCard(repo) {
    const card = document.createElement('div');
    card.className = 'repo-card';
    
    // 格式化日期
    const addedDate = repo.added_at ? new Date(repo.added_at).toLocaleDateString() : '未知';
    
    card.innerHTML = `
        <div class="repo-header">
            <h3 class="repo-name">
                <a href="${repo.url}" target="_blank">${repo.full_name}</a>
            </h3>
            <div class="repo-actions">
                <a href="/repo/${repo.full_name}/issues" class="btn btn-sm btn-outline">查看 Issues</a>
                <button class="btn btn-sm btn-danger delete-repo-btn" 
                        data-repo="${repo.full_name}" 
                        data-repo-name="${repo.name}">
                    删除
                </button>
            </div>
        </div>
        
        ${repo.description ? `<p class="repo-description">${repo.description}</p>` : ''}
        
        <div class="repo-stats">
            <span class="stat-item">
                <span class="stat-icon">⭐</span>
                ${repo.stars || 0}
            </span>
            <span class="stat-item">
                <span class="stat-icon">🍴</span>
                ${repo.forks || 0}
            </span>
            <span class="stat-item">
                <span class="stat-icon">🐛</span>
                ${repo.open_issues || 0} Issues
            </span>
            ${repo.language ? `
            <span class="stat-item">
                <span class="stat-icon">💻</span>
                ${repo.language}
            </span>` : ''}
        </div>
        
        <div class="repo-meta">
            <small class="text-muted">
                添加于 ${addedDate}
                ${repo.is_default ? '<span class="badge badge-info ml-2">默认</span>' : ''}
            </small>
        </div>
    `;
    
    return card;
}

// 计算并显示统计信息（替代旧的 DOM 读取方式）
function calculateAndDisplayStats(repos) {
    let totalStars = 0;
    let totalIssues = 0;
    let totalForks = 0;
    const languages = {};
    
    repos.forEach(repo => {
        totalStars += (repo.stars || 0);
        totalIssues += (repo.open_issues || 0);
        totalForks += (repo.forks || 0);
        
        if (repo.language) {
            languages[repo.language] = (languages[repo.language] || 0) + 1;
        }
    });
    
    displayRepoStats({
        totalRepos: repos.length,
        totalStars,
        totalIssues,
        totalForks,
        languages
    });
}

// 初始化删除按钮
function initDeleteButtons() {
    const deleteButtons = document.querySelectorAll('.delete-repo-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const repoName = this.getAttribute('data-repo');
            const repoDisplayName = this.getAttribute('data-repo-name') || repoName;
            
            window.HubNote.confirmAction(
                `确定要删除仓库 "${repoDisplayName}" 吗？\n\n注意：这只会从本地列表中移除，不会影响 GitHub 上的仓库。`,
                () => deleteRepository(repoName)
            );
        });
    });
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
            window.HubNote.showNotification('请输入仓库 URL', 'error');
            return;
        }
        
        if (!isValidRepoUrl(repoUrl)) {
            window.HubNote.showNotification('请输入有效的 GitHub 仓库 URL', 'error');
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
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json'
        },
        body: `repo_url=${encodeURIComponent(repoUrl)}`
    })
    .then(response => response.json())
    .then(data => {
        console.log('添加仓库响应:', data);
        if (data.success) {
            window.HubNote.showNotification(data.message || '仓库添加成功！', 'success');
            document.getElementById('add-repo-form').reset();
            
            // 重新加载列表而不是刷新页面（SPA体验）
            loadRepositories();
        } else {
            throw new Error(data.error || '添加仓库失败');
        }
    })
    .catch(error => {
        console.error('添加仓库失败:', error);
        window.HubNote.showNotification(error.message || '添加仓库失败', 'error');
    })
    .finally(() => {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    });
}

// 删除仓库
function deleteRepository(repoName) {
    fetch('/remove_repo/' + repoName, {  // 修正 URL 格式
        method: 'GET', // 注意：原本是GET请求，虽然RESTful应该是DELETE
    })
    .then(response => {
        if (response.redirected || response.ok) {
            window.HubNote.showNotification('仓库删除成功！', 'success');
            // 重新加载列表
            loadRepositories();
        } else {
            throw new Error('删除仓库失败');
        }
    })
    .catch(error => {
        console.error('删除仓库失败:', error);
        window.HubNote.showNotification(error.message || '删除仓库失败', 'error');
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

// 过滤仓库 (前端过滤)
function filterRepositories(searchTerm) {
    const repoCards = document.querySelectorAll('.repo-card');
    let visibleCount = 0;
    
    repoCards.forEach(card => {
        const repoName = card.querySelector('.repo-name').textContent.toLowerCase();
        const repoDesc = card.querySelector('.repo-description')?.textContent.toLowerCase() || '';
        
        const searchLower = searchTerm.toLowerCase();
        const isVisible = !searchTerm || 
            repoName.includes(searchLower) || 
            repoDesc.includes(searchLower);
        
        if (isVisible) {
            card.style.display = 'block';
            visibleCount++;
        } else {
            card.style.display = 'none';
        }
    });
    
    updateSearchResults(visibleCount, repoCards.length, searchTerm);
}

// 更新搜索结果显示
function updateSearchResults(visibleCount, totalCount, searchTerm) {
    let resultDiv = document.getElementById('search-results');
    const reposGrid = document.getElementById('repos-grid');
    
    if (!resultDiv && reposGrid) {
        resultDiv = document.createElement('div');
        resultDiv.id = 'search-results';
        resultDiv.className = 'search-results';
        reposGrid.parentNode.insertBefore(resultDiv, reposGrid);
    }
    
    if (resultDiv) {
        if (searchTerm) {
            resultDiv.textContent = `找到 ${visibleCount} 个匹配的仓库（共 ${totalCount} 个）`;
            resultDiv.style.display = 'block';
        } else {
            resultDiv.style.display = 'none';
        }
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

// 排序仓库 (DOM 排序)
function sortRepositories(sortBy) {
    const reposGrid = document.getElementById('repos-grid');
    if (!reposGrid) return;
    
    const repoCards = Array.from(reposGrid.querySelectorAll('.repo-card'));
    
    repoCards.sort((a, b) => {
        switch (sortBy) {
            case 'name':
                const nameA = a.querySelector('.repo-name').textContent.toLowerCase();
                const nameB = b.querySelector('.repo-name').textContent.toLowerCase();
                return nameA.localeCompare(nameB);
            case 'stars':
                const starsA = parseInt(extractNumber(a.querySelector('.repo-stats .stat-item:nth-child(1)')));
                const starsB = parseInt(extractNumber(b.querySelector('.repo-stats .stat-item:nth-child(1)')));
                return starsB - starsA;
            case 'issues':
                const issuesA = parseInt(extractNumber(a.querySelector('.repo-stats .stat-item:nth-child(3)')));
                const issuesB = parseInt(extractNumber(b.querySelector('.repo-stats .stat-item:nth-child(3)')));
                return issuesB - issuesA;
            default:
                return 0;
        }
    });
    
    repoCards.forEach(card => reposGrid.appendChild(card));
}

function extractNumber(element) {
    return element ? element.textContent.replace(/[^0-9]/g, '') || '0' : '0';
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

// 验证仓库 URL
function isValidRepoUrl(url) {
    const githubUrlPattern = /^https?:\/\/github\.com\/[\w.-]+\/[\w.-]+\/?$/;
    const ownerRepoPattern = /^[\w.-]+\/[\w.-]+$/;
    return githubUrlPattern.test(url) || ownerRepoPattern.test(url);
}

// 复制仓库链接
function copyRepoLink(repoName) {
    const repoUrl = `https://github.com/${repoName}`;
    window.HubNote.copyToClipboard(repoUrl);
}

// 导出函数供全局使用
window.RepoManager = {
    deleteRepository,
    filterRepositories,
    sortRepositories,
    copyRepoLink,
    loadRepositories
};
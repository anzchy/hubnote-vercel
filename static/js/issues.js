// Issues 页面的 JavaScript 功能

document.addEventListener('DOMContentLoaded', function() {
    initIssuesPage();
});

function initIssuesPage() {
    // 初始化筛选器
    initIssueFilters();
    
    // 初始化搜索功能
    initIssueSearch();
    
    // 初始化排序功能
    initIssueSort();
    
    // 初始化分页
    initPagination();
    
    // 初始化 Issue 交互
    initIssueInteractions();
    
    // 加载 Issues 统计信息
    loadIssueStats();
}

// 初始化筛选器
function initIssueFilters() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    filterButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // 更新活跃状态
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            const filterType = this.getAttribute('data-filter');
            filterIssues(filterType);
        });
    });
}

// 筛选 Issues
function filterIssues(filterType) {
    const issueItems = document.querySelectorAll('.issue-item');
    let visibleCount = 0;
    
    issueItems.forEach(item => {
        const issueState = item.getAttribute('data-state');
        let isVisible = false;
        
        switch (filterType) {
            case 'all':
                isVisible = true;
                break;
            case 'open':
                isVisible = issueState === 'open';
                break;
            case 'closed':
                isVisible = issueState === 'closed';
                break;
        }
        
        if (isVisible) {
            item.style.display = 'block';
            visibleCount++;
        } else {
            item.style.display = 'none';
        }
    });
    
    updateFilterResults(visibleCount, filterType);
}

// 更新筛选结果显示
function updateFilterResults(visibleCount, filterType) {
    let resultDiv = document.getElementById('filter-results');
    
    if (!resultDiv) {
        resultDiv = document.createElement('div');
        resultDiv.id = 'filter-results';
        resultDiv.className = 'filter-results';
        
        const issuesList = document.querySelector('.issues-list');
        if (issuesList) {
            issuesList.parentNode.insertBefore(resultDiv, issuesList);
        }
    }
    
    const filterText = {
        'all': '全部',
        'open': '开放',
        'closed': '已关闭'
    }[filterType] || filterType;
    
    resultDiv.textContent = `显示 ${visibleCount} 个${filterText} Issues`;
}

// 初始化搜索功能
function initIssueSearch() {
    const searchInput = document.getElementById('issue-search');
    if (!searchInput) return;
    
    let searchTimeout;
    
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            searchIssues(this.value.trim());
        }, 300);
    });
}

// 搜索 Issues
function searchIssues(searchTerm) {
    const issueItems = document.querySelectorAll('.issue-item');
    let visibleCount = 0;
    
    issueItems.forEach(item => {
        const title = item.querySelector('.issue-title').textContent.toLowerCase();
        const body = item.querySelector('.issue-body')?.textContent.toLowerCase() || '';
        const author = item.querySelector('.issue-author')?.textContent.toLowerCase() || '';
        const labels = Array.from(item.querySelectorAll('.issue-label'))
            .map(label => label.textContent.toLowerCase())
            .join(' ');
        
        const searchLower = searchTerm.toLowerCase();
        const isVisible = !searchTerm || 
            title.includes(searchLower) || 
            body.includes(searchLower) || 
            author.includes(searchLower) || 
            labels.includes(searchLower);
        
        if (isVisible) {
            item.style.display = 'block';
            visibleCount++;
        } else {
            item.style.display = 'none';
        }
    });
    
    updateSearchResults(visibleCount, searchTerm);
}

// 更新搜索结果显示
function updateSearchResults(visibleCount, searchTerm) {
    let resultDiv = document.getElementById('search-results');
    
    if (!resultDiv) {
        resultDiv = document.createElement('div');
        resultDiv.id = 'search-results';
        resultDiv.className = 'search-results';
        
        const issuesList = document.querySelector('.issues-list');
        if (issuesList) {
            issuesList.parentNode.insertBefore(resultDiv, issuesList);
        }
    }
    
    if (searchTerm) {
        resultDiv.textContent = `搜索到 ${visibleCount} 个匹配的 Issues`;
        resultDiv.style.display = 'block';
    } else {
        resultDiv.style.display = 'none';
    }
}

// 初始化排序功能
function initIssueSort() {
    const sortSelect = document.getElementById('issue-sort');
    if (!sortSelect) return;
    
    sortSelect.addEventListener('change', function() {
        sortIssues(this.value);
    });
}

// 排序 Issues
function sortIssues(sortBy) {
    const issuesList = document.querySelector('.issues-list');
    if (!issuesList) return;
    
    const issueItems = Array.from(issuesList.querySelectorAll('.issue-item'));
    
    issueItems.sort((a, b) => {
        switch (sortBy) {
            case 'created':
                const createdA = new Date(a.querySelector('.issue-created')?.getAttribute('data-date') || '1970-01-01');
                const createdB = new Date(b.querySelector('.issue-created')?.getAttribute('data-date') || '1970-01-01');
                return createdB - createdA;
                
            case 'updated':
                const updatedA = new Date(a.querySelector('.issue-updated')?.getAttribute('data-date') || '1970-01-01');
                const updatedB = new Date(b.querySelector('.issue-updated')?.getAttribute('data-date') || '1970-01-01');
                return updatedB - updatedA;
                
            case 'comments':
                const commentsA = parseInt(a.querySelector('.issue-comments')?.textContent || '0');
                const commentsB = parseInt(b.querySelector('.issue-comments')?.textContent || '0');
                return commentsB - commentsA;
                
            case 'title':
                const titleA = a.querySelector('.issue-title').textContent.toLowerCase();
                const titleB = b.querySelector('.issue-title').textContent.toLowerCase();
                return titleA.localeCompare(titleB);
                
            default:
                return 0;
        }
    });
    
    // 重新排列 DOM 元素
    issueItems.forEach(item => {
        issuesList.appendChild(item);
    });
}

// 初始化分页
function initPagination() {
    const paginationLinks = document.querySelectorAll('.pagination a');
    paginationLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const page = this.getAttribute('data-page');
            if (page) {
                loadPage(parseInt(page));
            }
        });
    });
}

// 加载指定页面
function loadPage(page) {
    const currentUrl = new URL(window.location);
    currentUrl.searchParams.set('page', page);
    
    // 显示加载状态
    const issuesList = document.querySelector('.issues-list');
    window.HubNote.showLoading(issuesList);
    
    // 更新 URL 并重新加载
    window.history.pushState({}, '', currentUrl);
    window.location.reload();
}

// 初始化 Issue 交互
function initIssueInteractions() {
    // 初始化 Issue 项点击
    const issueItems = document.querySelectorAll('.issue-item');
    issueItems.forEach(item => {
        item.addEventListener('click', function(e) {
            // 如果点击的是链接，不处理
            if (e.target.tagName === 'A' || e.target.closest('a')) {
                return;
            }
            
            const issueLink = this.querySelector('.issue-title a');
            if (issueLink) {
                window.location.href = issueLink.href;
            }
        });
        
        // 添加悬停效果
        item.addEventListener('mouseenter', function() {
            this.style.backgroundColor = '#f6f8fa';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
        });
    });
    
    // 初始化标签点击
    const labelElements = document.querySelectorAll('.issue-label');
    labelElements.forEach(label => {
        label.addEventListener('click', function(e) {
            e.stopPropagation();
            
            const labelText = this.textContent.trim();
            filterByLabel(labelText);
        });
    });
}

// 按标签筛选
function filterByLabel(labelText) {
    const searchInput = document.getElementById('issue-search');
    if (searchInput) {
        searchInput.value = `label:"${labelText}"`;
        searchIssues(searchInput.value);
    }
}

// 加载 Issues 统计信息
function loadIssueStats() {
    const issueItems = document.querySelectorAll('.issue-item');
    const totalIssues = issueItems.length;
    
    if (totalIssues === 0) return;
    
    let openCount = 0;
    let closedCount = 0;
    let totalComments = 0;
    const labels = {};
    const authors = {};
    
    issueItems.forEach(item => {
        // 统计状态
        const state = item.getAttribute('data-state');
        if (state === 'open') {
            openCount++;
        } else if (state === 'closed') {
            closedCount++;
        }
        
        // 统计评论数
        const comments = parseInt(item.querySelector('.issue-comments')?.textContent || '0');
        totalComments += comments;
        
        // 统计标签
        const labelElements = item.querySelectorAll('.issue-label');
        labelElements.forEach(labelEl => {
            const label = labelEl.textContent.trim();
            if (label) {
                labels[label] = (labels[label] || 0) + 1;
            }
        });
        
        // 统计作者
        const authorEl = item.querySelector('.issue-author');
        if (authorEl) {
            const author = authorEl.textContent.trim();
            if (author) {
                authors[author] = (authors[author] || 0) + 1;
            }
        }
    });
    
    // 显示统计信息
    displayIssueStats({
        totalIssues,
        openCount,
        closedCount,
        totalComments,
        labels,
        authors
    });
}

// 显示 Issues 统计信息
function displayIssueStats(stats) {
    let statsDiv = document.getElementById('issue-stats');
    
    if (!statsDiv) {
        statsDiv = document.createElement('div');
        statsDiv.id = 'issue-stats';
        statsDiv.className = 'issue-stats';
        
        const pageHeader = document.querySelector('.page-header');
        if (pageHeader) {
            pageHeader.appendChild(statsDiv);
        }
    }
    
    const topLabels = Object.entries(stats.labels)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 5)
        .map(([label, count]) => `${label} (${count})`)
        .join(', ');
    
    const topAuthors = Object.entries(stats.authors)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 3)
        .map(([author, count]) => `${author} (${count})`)
        .join(', ');
    
    statsDiv.innerHTML = `
        <div class="stats-grid">
            <div class="stat-item">
                <span class="stat-number">${stats.totalIssues}</span>
                <span class="stat-label">总 Issues</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">${stats.openCount}</span>
                <span class="stat-label">开放</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">${stats.closedCount}</span>
                <span class="stat-label">已关闭</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">${stats.totalComments}</span>
                <span class="stat-label">总评论</span>
            </div>
            ${topLabels ? `
            <div class="stat-item stat-labels">
                <span class="stat-label">热门标签</span>
                <span class="stat-value">${topLabels}</span>
            </div>
            ` : ''}
            ${topAuthors ? `
            <div class="stat-item stat-authors">
                <span class="stat-label">活跃作者</span>
                <span class="stat-value">${topAuthors}</span>
            </div>
            ` : ''}
        </div>
    `;
}

// 复制 Issue 链接
function copyIssueLink(repoName, issueNumber) {
    const issueUrl = `https://github.com/${repoName}/issues/${issueNumber}`;
    window.HubNote.copyToClipboard(issueUrl);
}

// 刷新 Issues
function refreshIssues() {
    window.HubNote.showNotification('正在刷新 Issues...', 'info');
    window.location.reload();
}

// 导出函数供全局使用
window.IssuesManager = {
    filterIssues,
    searchIssues,
    sortIssues,
    loadPage,
    filterByLabel,
    copyIssueLink,
    refreshIssues
};
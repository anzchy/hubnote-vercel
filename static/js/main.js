// 主要的 JavaScript 功能

// DOM 加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 初始化应用
    initApp();
});

function initApp() {
    // 自动关闭 flash 消息
    autoCloseFlashMessages();
    
    // 初始化工具提示
    initTooltips();
    
    // 初始化表单验证
    initFormValidation();
}

// 自动关闭 flash 消息
function autoCloseFlashMessages() {
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        // 5秒后自动关闭
        setTimeout(() => {
            if (message.parentElement) {
                message.style.opacity = '0';
                message.style.transform = 'translateY(-10px)';
                setTimeout(() => {
                    message.remove();
                }, 300);
            }
        }, 5000);
    });
}

// 初始化工具提示
function initTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(event) {
    const element = event.target;
    const tooltipText = element.getAttribute('data-tooltip');
    
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = tooltipText;
    tooltip.style.position = 'absolute';
    tooltip.style.background = '#24292e';
    tooltip.style.color = 'white';
    tooltip.style.padding = '0.5rem';
    tooltip.style.borderRadius = '4px';
    tooltip.style.fontSize = '0.8rem';
    tooltip.style.zIndex = '1000';
    tooltip.style.pointerEvents = 'none';
    
    document.body.appendChild(tooltip);
    
    const rect = element.getBoundingClientRect();
    tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
    tooltip.style.top = rect.top - tooltip.offsetHeight - 5 + 'px';
    
    element._tooltip = tooltip;
}

function hideTooltip(event) {
    const element = event.target;
    if (element._tooltip) {
        element._tooltip.remove();
        delete element._tooltip;
    }
}

// 表单验证
function initFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', validateForm);
    });
}

function validateForm(event) {
    const form = event.target;
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            showFieldError(field, '此字段为必填项');
            isValid = false;
        } else {
            clearFieldError(field);
        }
    });
    
    // 验证仓库 URL 格式
    const repoUrlField = form.querySelector('input[name="repo_url"]');
    if (repoUrlField && repoUrlField.value.trim()) {
        if (!isValidRepoUrl(repoUrlField.value.trim())) {
            showFieldError(repoUrlField, '请输入有效的 GitHub 仓库 URL 或 owner/repo 格式');
            isValid = false;
        }
    }
    
    if (!isValid) {
        event.preventDefault();
    }
}

function isValidRepoUrl(url) {
    // 检查是否为 GitHub URL 格式
    const githubUrlPattern = /^https?:\/\/github\.com\/[\w.-]+\/[\w.-]+\/?$/;
    // 检查是否为 owner/repo 格式
    const ownerRepoPattern = /^[\w.-]+\/[\w.-]+$/;
    
    return githubUrlPattern.test(url) || ownerRepoPattern.test(url);
}

function showFieldError(field, message) {
    clearFieldError(field);
    
    field.style.borderColor = '#d73a49';
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.textContent = message;
    errorDiv.style.color = '#d73a49';
    errorDiv.style.fontSize = '0.8rem';
    errorDiv.style.marginTop = '0.25rem';
    
    field.parentNode.insertBefore(errorDiv, field.nextSibling);
}

function clearFieldError(field) {
    field.style.borderColor = '';
    
    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
}

// 工具函数
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (days > 0) {
        return `${days}天前`;
    } else if (hours > 0) {
        return `${hours}小时前`;
    } else if (minutes > 0) {
        return `${minutes}分钟前`;
    } else {
        return '刚刚';
    }
}

function truncateText(text, maxLength) {
    if (text.length <= maxLength) {
        return text;
    }
    return text.substring(0, maxLength) + '...';
}

// API 调用辅助函数
function apiCall(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    const mergedOptions = { ...defaultOptions, ...options };
    
    return fetch(url, mergedOptions)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .catch(error => {
            console.error('API call failed:', error);
            throw error;
        });
}

// 显示加载状态
function showLoading(element) {
    if (element) {
        element.style.opacity = '0.6';
        element.style.pointerEvents = 'none';
        
        const loader = document.createElement('div');
        loader.className = 'loading-spinner';
        loader.innerHTML = '⏳ 加载中...';
        loader.style.position = 'absolute';
        loader.style.top = '50%';
        loader.style.left = '50%';
        loader.style.transform = 'translate(-50%, -50%)';
        loader.style.background = 'rgba(255, 255, 255, 0.9)';
        loader.style.padding = '1rem';
        loader.style.borderRadius = '4px';
        loader.style.zIndex = '1000';
        
        element.style.position = 'relative';
        element.appendChild(loader);
    }
}

function hideLoading(element) {
    if (element) {
        element.style.opacity = '';
        element.style.pointerEvents = '';
        
        const loader = element.querySelector('.loading-spinner');
        if (loader) {
            loader.remove();
        }
    }
}

// 确认对话框
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// 复制到剪贴板
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('已复制到剪贴板', 'success');
        }).catch(err => {
            console.error('复制失败:', err);
            showNotification('复制失败', 'error');
        });
    } else {
        // 降级方案
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
            showNotification('已复制到剪贴板', 'success');
        } catch (err) {
            console.error('复制失败:', err);
            showNotification('复制失败', 'error');
        }
        document.body.removeChild(textArea);
    }
}

// 显示通知
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.padding = '1rem';
    notification.style.borderRadius = '4px';
    notification.style.zIndex = '10000';
    notification.style.maxWidth = '300px';
    notification.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)';
    
    switch (type) {
        case 'success':
            notification.style.background = '#d4edda';
            notification.style.color = '#155724';
            notification.style.border = '1px solid #c3e6cb';
            break;
        case 'error':
            notification.style.background = '#f8d7da';
            notification.style.color = '#721c24';
            notification.style.border = '1px solid #f5c6cb';
            break;
        default:
            notification.style.background = '#d1ecf1';
            notification.style.color = '#0c5460';
            notification.style.border = '1px solid #bee5eb';
    }
    
    document.body.appendChild(notification);
    
    // 3秒后自动移除
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 300);
    }, 3000);
    
    // 返回通知元素，供外部使用
    return notification;
}

// 导出全局函数
window.HubNote = {
    formatDate,
    truncateText,
    apiCall,
    showLoading,
    hideLoading,
    confirmAction,
    copyToClipboard,
    showNotification
};
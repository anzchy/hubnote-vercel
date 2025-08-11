/**
 * 数据导出功能的前端交互逻辑
 */

class DataExportManager {
    constructor() {
        this.exportModal = document.getElementById('exportModal');
        this.exportProgress = document.getElementById('exportProgress');
        this.repoSelect = document.getElementById('exportRepoSelect');
        this.formatSelect = document.getElementById('exportFormatSelect');
        this.confirmBtn = document.getElementById('confirmExportBtn');
        this.exportInfo = document.getElementById('exportInfo');
        this.repoDescription = document.getElementById('repoDescription');
        this.progressText = document.getElementById('progressText');
        
        this.availableRepos = [];
        this.initEventListeners();
    }

    initEventListeners() {
        // 导出按钮点击事件
        document.getElementById('exportDataBtn').addEventListener('click', () => {
            this.openExportModal();
        });

        // 关闭模态框事件
        document.getElementById('closeExportModal').addEventListener('click', () => {
            this.closeExportModal();
        });

        document.getElementById('cancelExportBtn').addEventListener('click', () => {
            this.closeExportModal();
        });

        // 点击模态框外部关闭
        this.exportModal.addEventListener('click', (e) => {
            if (e.target === this.exportModal) {
                this.closeExportModal();
            }
        });

        // 仓库选择变化事件
        this.repoSelect.addEventListener('change', () => {
            this.onRepoSelectionChange();
        });

        // 确认导出按钮事件
        this.confirmBtn.addEventListener('click', () => {
            this.startExport();
        });

        // ESC 键关闭模态框
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.exportModal.style.display !== 'none') {
                this.closeExportModal();
            }
        });
    }

    async openExportModal() {
        try {
            // 显示模态框
            this.exportModal.style.display = 'flex';
            
            // 加载可导出的仓库列表
            await this.loadAvailableRepos();
            
            // 重置表单
            this.resetForm();
        } catch (error) {
            console.error('打开导出模态框失败:', error);
            this.showError('加载仓库列表失败，请稍后重试');
        }
    }

    closeExportModal() {
        this.exportModal.style.display = 'none';
        this.resetForm();
    }

    async loadAvailableRepos() {
        try {
            const response = await fetch('/api/export/repos');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.availableRepos = data.repos || [];
            
            // 更新仓库选择下拉框
            this.updateRepoSelect();
        } catch (error) {
            console.error('加载仓库列表失败:', error);
            throw error;
        }
    }

    updateRepoSelect() {
        // 清空现有选项
        this.repoSelect.innerHTML = '<option value="">请选择仓库...</option>';
        
        // 添加仓库选项
        this.availableRepos.forEach(repo => {
            const option = document.createElement('option');
            option.value = repo.full_name;
            option.textContent = `${repo.full_name} (${repo.open_issues} Issues)`;
            option.dataset.description = repo.description || '暂无描述';
            this.repoSelect.appendChild(option);
        });
    }

    onRepoSelectionChange() {
        const selectedRepo = this.repoSelect.value;
        
        if (selectedRepo) {
            // 显示仓库信息
            const selectedOption = this.repoSelect.selectedOptions[0];
            const description = selectedOption.dataset.description;
            
            this.repoDescription.textContent = description;
            this.exportInfo.style.display = 'block';
            
            // 启用确认按钮
            this.confirmBtn.disabled = false;
        } else {
            // 隐藏仓库信息
            this.exportInfo.style.display = 'none';
            
            // 禁用确认按钮
            this.confirmBtn.disabled = true;
        }
    }

    async startExport() {
        const selectedRepo = this.repoSelect.value;
        const selectedFormat = this.formatSelect.value;
        
        if (!selectedRepo || !selectedFormat) {
            this.showError('请选择仓库和导出格式');
            return;
        }

        try {
            // 关闭模态框，显示进度
            this.exportModal.style.display = 'none';
            this.showProgress('正在准备导出数据...');
            
            // 发起导出请求
            const response = await fetch(`/api/export/${encodeURIComponent(selectedRepo)}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    format: selectedFormat
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
            }
            
            // 更新进度
            this.updateProgress('正在下载文件...');
            
            // 获取文件内容
            const blob = await response.blob();
            
            // 生成文件名
            const fileName = this.generateFileName(selectedRepo, selectedFormat);
            
            // 下载文件
            this.downloadFile(blob, fileName);
            
            // 隐藏进度，显示成功消息
            this.hideProgress();
            this.showSuccess(`数据导出成功！文件已保存为 ${fileName}`);
            
        } catch (error) {
            console.error('导出失败:', error);
            this.hideProgress();
            this.showError(`导出失败: ${error.message}`);
        }
    }

    generateFileName(repoFullName, format) {
        const repoName = repoFullName.replace('/', '_');
        const timestamp = new Date().toISOString().slice(0, 19).replace(/[:-]/g, '');
        const extension = format === 'json' ? 'json' : 'csv';
        return `${repoName}_export_${timestamp}.${extension}`;
    }

    downloadFile(blob, fileName) {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }

    showProgress(message) {
        this.progressText.textContent = message;
        this.exportProgress.style.display = 'flex';
    }

    updateProgress(message) {
        this.progressText.textContent = message;
    }

    hideProgress() {
        this.exportProgress.style.display = 'none';
    }

    resetForm() {
        this.repoSelect.value = '';
        this.formatSelect.value = 'json';
        this.exportInfo.style.display = 'none';
        this.confirmBtn.disabled = true;
    }

    showError(message) {
        // 创建错误提示
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-error';
        errorDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background-color: #f8d7da;
            color: #721c24;
            padding: 1rem;
            border: 1px solid #f5c6cb;
            border-radius: 6px;
            z-index: 1200;
            max-width: 400px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        `;
        errorDiv.textContent = message;
        
        document.body.appendChild(errorDiv);
        
        // 3秒后自动移除
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.parentNode.removeChild(errorDiv);
            }
        }, 5000);
    }

    showSuccess(message) {
        // 创建成功提示
        const successDiv = document.createElement('div');
        successDiv.className = 'alert alert-success';
        successDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background-color: #d4edda;
            color: #155724;
            padding: 1rem;
            border: 1px solid #c3e6cb;
            border-radius: 6px;
            z-index: 1200;
            max-width: 400px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        `;
        successDiv.textContent = message;
        
        document.body.appendChild(successDiv);
        
        // 4秒后自动移除
        setTimeout(() => {
            if (successDiv.parentNode) {
                successDiv.parentNode.removeChild(successDiv);
            }
        }, 4000);
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    // 检查是否在首页（有导出按钮）
    if (document.getElementById('exportDataBtn')) {
        new DataExportManager();
    }
});
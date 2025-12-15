/**
 * Global News Brief Dashboard - Main Application
 * Handles UI state, bulletin rendering, and user interactions
 */

class NewsApp {
    constructor() {
        this.loader = new BulletinLoader();
        this.currentRegion = 'all';
        this.currentPeriod = 'morning';
        this.currentDate = this.getTodayDate();
        this.allArticles = [];
        this.filteredArticles = [];
        this.searchQuery = '';
        
        this.elements = {};
        this.init();
    }
    
    getTodayDate() {
        return new Date().toISOString().split('T')[0];
    }
    
    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.cacheElements();
            this.attachListeners();
            this.renderDateList();
            this.loadBulletins();
        });
    }
    
    cacheElements() {
        this.elements = {
            articlesContainer: document.getElementById('articles-container'),
            loadingState: document.getElementById('loading-state'),
            errorState: document.getElementById('error-state'),
            errorMessage: document.getElementById('error-message'),
            retryBtn: document.getElementById('retry-btn'),
            displayDate: document.getElementById('display-date'),
            articleCount: document.getElementById('article-count'),
            archiveMonth: document.getElementById('archive-month'),
            dateList: document.getElementById('date-list'),
            prevMonth: document.getElementById('prev-month'),
            nextMonth: document.getElementById('next-month'),
            btnMorning: document.getElementById('btn-morning'),
            btnEvening: document.getElementById('btn-evening'),
            regionFilters: document.getElementById('region-filters'),
            searchInput: document.getElementById('search-input'),
            loadMoreContainer: document.getElementById('load-more-container')
        };
    }
    
    attachListeners() {
        // Period toggle
        this.elements.btnMorning.addEventListener('click', () => this.setPeriod('morning'));
        this.elements.btnEvening.addEventListener('click', () => this.setPeriod('evening'));
        
        // Region filter
        this.elements.regionFilters.querySelectorAll('.region-btn').forEach(btn => {
            btn.addEventListener('click', () => this.setRegion(btn.dataset.region));
        });
        
        // Retry button
        this.elements.retryBtn.addEventListener('click', () => this.loadBulletins());
        
        // Search input
        this.elements.searchInput.addEventListener('input', (e) => {
            this.searchQuery = e.target.value.toLowerCase();
            this.filterAndRenderArticles();
        });
    }
    
    setPeriod(period) {
        if (this.currentPeriod === period) return;
        this.currentPeriod = period;
        this.updatePeriodButtons();
        this.loadBulletins();
    }
    
    updatePeriodButtons() {
        const morningActive = this.currentPeriod === 'morning';
        
        this.elements.btnMorning.className = morningActive
            ? 'period-btn flex items-center gap-2 px-3 py-1.5 rounded-md bg-slate-700/50 shadow-sm text-xs font-bold text-primary transition-all'
            : 'period-btn flex items-center gap-2 px-3 py-1.5 rounded-md text-text-secondary-dark hover:text-text-primary-dark text-xs font-bold transition-all';
        
        this.elements.btnEvening.className = !morningActive
            ? 'period-btn flex items-center gap-2 px-3 py-1.5 rounded-md bg-slate-700/50 shadow-sm text-xs font-bold text-primary transition-all'
            : 'period-btn flex items-center gap-2 px-3 py-1.5 rounded-md text-text-secondary-dark hover:text-text-primary-dark text-xs font-bold transition-all';
    }
    
    setRegion(region) {
        if (this.currentRegion === region) return;
        this.currentRegion = region;
        this.updateRegionButtons();
        this.filterAndRenderArticles();
    }
    
    updateRegionButtons() {
        this.elements.regionFilters.querySelectorAll('.region-btn').forEach(btn => {
            const isActive = btn.dataset.region === this.currentRegion;
            btn.className = isActive
                ? 'region-btn px-3 py-1 rounded-full bg-primary/10 text-primary border border-primary/20 text-xs font-bold'
                : 'region-btn px-3 py-1 rounded-full bg-transparent text-text-secondary-dark border border-border-dark hover:border-slate-600 text-xs font-medium transition-colors';
        });
    }
    
    setDate(date) {
        if (this.currentDate === date) return;
        this.currentDate = date;
        this.renderDateList();
        this.loadBulletins();
    }
    
    renderDateList() {
        const dates = this.getLast7Days();
        const today = this.getTodayDate();
        
        // Update month display
        const currentDateObj = new Date(this.currentDate);
        this.elements.archiveMonth.textContent = currentDateObj.toLocaleDateString('en-US', { 
            month: 'long', 
            year: 'numeric' 
        });
        
        this.elements.dateList.innerHTML = dates.map(date => {
            const dateObj = new Date(date + 'T12:00:00');
            const dayName = dateObj.toLocaleDateString('en-US', { weekday: 'short' });
            const dayNum = dateObj.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            const isToday = date === today;
            const isSelected = date === this.currentDate;
            
            return `
                <button 
                    class="date-btn w-full text-left px-3 py-2.5 rounded-lg text-sm font-medium transition-colors flex justify-between items-center ${
                        isSelected 
                            ? 'bg-primary text-slate-900 shadow-lg shadow-primary/20' 
                            : 'text-text-secondary-dark hover:bg-slate-800 hover:text-text-primary-dark'
                    }"
                    data-date="${date}"
                >
                    <span>${dayName}, ${dayNum}</span>
                    ${isToday ? `<span class="${isSelected ? 'bg-slate-900/20 text-slate-900' : 'bg-primary/20 text-primary'} text-[10px] px-1.5 py-0.5 rounded font-bold">Today</span>` : ''}
                </button>
            `;
        }).join('');
        
        // Attach click listeners to date buttons
        this.elements.dateList.querySelectorAll('.date-btn').forEach(btn => {
            btn.addEventListener('click', () => this.setDate(btn.dataset.date));
        });
    }
    
    getLast7Days() {
        const dates = [];
        const today = new Date();
        for (let i = 0; i < 7; i++) {
            const date = new Date(today);
            date.setDate(date.getDate() - i);
            dates.push(date.toISOString().split('T')[0]);
        }
        return dates;
    }
    
    async loadBulletins() {
        this.showLoading();
        this.allArticles = [];
        
        const regions = ['usa', 'india', 'world'];
        const loadPromises = regions.map(region => this.loadRegionBulletin(region));
        
        try {
            await Promise.allSettled(loadPromises);
            
            if (this.allArticles.length === 0) {
                this.showError('No bulletins available for this date and period.');
                return;
            }
            
            // Sort articles by timestamp (newest first)
            this.allArticles.sort((a, b) => {
                const timeA = a.source?.published_at || a.generated_at;
                const timeB = b.source?.published_at || b.generated_at;
                return new Date(timeB) - new Date(timeA);
            });
            
            this.updateDisplayDate();
            this.filterAndRenderArticles();
            this.hideLoading();
            this.hideError();
            
        } catch (error) {
            console.error('Error loading bulletins:', error);
            this.showError('Failed to load bulletins. Please try again.');
        }
    }
    
    async loadRegionBulletin(region) {
        try {
            const data = await this.loader.loadBulletin(region, this.currentDate, this.currentPeriod);
            const bulletin = data.bulletin;
            
            // Add region info to each article
            bulletin.articles.forEach(article => {
                article._region = region;
                article._generated_at = bulletin.generated_at;
            });
            
            this.allArticles.push(...bulletin.articles);
        } catch (error) {
            console.log(`No bulletin for ${region} on ${this.currentDate} (${this.currentPeriod})`);
        }
    }
    
    updateDisplayDate() {
        const dateObj = new Date(this.currentDate + 'T12:00:00');
        const formatted = dateObj.toLocaleDateString('en-US', { 
            weekday: 'long', 
            month: 'long', 
            day: 'numeric' 
        });
        this.elements.displayDate.textContent = formatted;
    }
    
    filterAndRenderArticles() {
        let articles = this.allArticles;
        
        // Filter by region
        if (this.currentRegion !== 'all') {
            articles = articles.filter(a => a._region === this.currentRegion);
        }
        
        // Filter by search query
        if (this.searchQuery) {
            articles = articles.filter(a => 
                a.title.toLowerCase().includes(this.searchQuery) ||
                a.summary.toLowerCase().includes(this.searchQuery) ||
                a.category.toLowerCase().includes(this.searchQuery)
            );
        }
        
        this.filteredArticles = articles;
        this.elements.articleCount.textContent = `Showing ${articles.length} AI-summarized updates`;
        this.renderArticles();
    }
    
    renderArticles() {
        if (this.filteredArticles.length === 0) {
            this.elements.articlesContainer.innerHTML = `
                <div class="text-center py-12">
                    <span class="material-symbols-outlined text-4xl text-text-secondary-dark mb-4">search_off</span>
                    <p class="text-text-secondary-dark">No articles match your filters.</p>
                </div>
            `;
            return;
        }
        
        this.elements.articlesContainer.innerHTML = this.filteredArticles.map((article, index) => 
            this.createArticleCard(article, index)
        ).join('');
    }
    
    createArticleCard(article, index) {
        const category = (article.category || 'news').toLowerCase();
        const categoryClass = `category-${category}`;
        const timeAgo = this.formatTimeAgo(article.source?.published_at || article._generated_at);
        const regionLabel = this.getRegionLabel(article._region);
        
        // Handle citations - can be array of objects or strings
        const citationsHtml = this.renderCitations(article.citations);
        
        // Handle source
        const sourceHtml = article.source?.name 
            ? `<span class="text-xs text-text-secondary-dark italic">Source: ${this.escapeHtml(article.source.name)}</span>`
            : '';
        
        return `
            <article class="group relative flex flex-col gap-3 py-6 border-b border-border-dark ${index === 0 ? 'first:pt-0' : ''}">
                <div class="flex items-center gap-3 text-xs mb-1 flex-wrap">
                    <span class="font-bold ${categoryClass} px-2 py-0.5 rounded">${this.escapeHtml(article.category)}</span>
                    <span class="text-text-secondary-dark">•</span>
                    <span class="text-text-secondary-dark flex items-center gap-1">
                        <span class="material-symbols-outlined text-[14px]">schedule</span> ${timeAgo}
                    </span>
                    <span class="ml-auto flex items-center gap-1 text-primary font-medium text-[10px] uppercase tracking-wider bg-primary/5 px-2 py-0.5 rounded-full border border-primary/10">
                        <span class="material-symbols-outlined text-[12px]">smart_toy</span> AI Summary
                    </span>
                    ${regionLabel ? `
                        <span class="flex items-center gap-1 text-text-secondary-dark text-[10px] uppercase tracking-wider">
                            <span class="material-symbols-outlined text-[14px]">public</span> ${regionLabel}
                        </span>
                    ` : ''}
                </div>
                <div class="flex-1">
                    <h3 class="text-xl font-bold leading-tight mb-3 text-text-primary-dark group-hover:text-primary transition-colors cursor-pointer">
                        ${this.escapeHtml(article.title)}
                    </h3>
                    <p class="text-sm text-text-secondary-dark leading-relaxed mb-4">
                        ${this.escapeHtml(article.summary)}
                    </p>
                    <div class="flex items-center gap-4 flex-wrap">
                        ${citationsHtml}
                        ${sourceHtml}
                    </div>
                </div>
            </article>
        `;
    }
    
    renderCitations(citations) {
        if (!citations || citations.length === 0) return '';
        
        const links = citations.slice(0, 3).map((citation, idx) => {
            let url, title;
            
            if (typeof citation === 'string') {
                url = citation;
                title = `Source ${idx + 1}`;
            } else {
                url = citation.url;
                title = citation.title || citation.source || `Source ${idx + 1}`;
            }
            
            return `
                <a 
                    href="${this.escapeHtml(url)}" 
                    target="_blank" 
                    rel="noopener noreferrer" 
                    class="inline-flex items-center gap-1 text-xs font-bold text-primary hover:underline"
                >
                    ${idx === 0 ? 'Full Report' : `[${idx + 1}]`} <span class="material-symbols-outlined text-[14px]">open_in_new</span>
                </a>
            `;
        }).join('');
        
        return links;
    }
    
    getRegionLabel(region) {
        const labels = {
            usa: 'USA',
            india: 'India',
            world: 'World'
        };
        return labels[region] || '';
    }
    
    formatTimeAgo(timestamp) {
        if (!timestamp) return 'Recently';
        
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        
        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins} min ago`;
        
        const diffHours = Math.floor(diffMins / 60);
        if (diffHours < 24) return `${diffHours} hrs ago`;
        
        const diffDays = Math.floor(diffHours / 24);
        if (diffDays === 1) return 'Yesterday';
        return `${diffDays} days ago`;
    }
    
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    showLoading() {
        this.elements.loadingState.classList.remove('hidden');
        this.elements.articlesContainer.classList.add('hidden');
        this.elements.errorState.classList.add('hidden');
    }
    
    hideLoading() {
        this.elements.loadingState.classList.add('hidden');
        this.elements.articlesContainer.classList.remove('hidden');
    }
    
    showError(message) {
        this.elements.errorMessage.textContent = message;
        this.elements.errorState.classList.remove('hidden');
        this.elements.loadingState.classList.add('hidden');
        this.elements.articlesContainer.classList.add('hidden');
    }
    
    hideError() {
        this.elements.errorState.classList.add('hidden');
    }
}

// Initialize app
const app = new NewsApp();

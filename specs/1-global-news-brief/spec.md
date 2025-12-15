# Feature Specification: NRI News Brief

**Feature Branch**: `1-global-news-brief`  
**Created**: 2025-12-14  
**Status**: Draft  
**Input**: User description: "Build 'NRI News Brief' - a multi-region news aggregation platform with AI-summarized updates from India, USA, and World sources"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Regional Morning News Catchup (Priority: P1)

A busy professional wants to quickly catch up on important morning news from their region before starting their workday.

**Why this priority**: Core MVP functionality - delivers immediate value by providing AI-summarized regional news. This is the foundation upon which all other features depend.

**Independent Test**: Can be fully tested by visiting the site in the morning (7-11 AM local time), selecting a single region (e.g., USA), and verifying that concise news summaries with citations appear in a responsive card layout. Delivers value as a standalone news reader for one region.

**Acceptance Scenarios**:

1. **Given** it's 8:00 AM EST and I open the platform, **When** I select "USA" region, **Then** I see the morning bulletin with 5-10 AI-summarized news cards from major US sources
2. **Given** I'm viewing morning news cards, **When** I click on a citation link, **Then** I'm taken to the original news source article in a new tab
3. **Given** I'm on a mobile device (320px width), **When** I view the morning bulletin, **Then** cards stack vertically and remain fully readable without horizontal scrolling
4. **Given** the morning bulletin is displayed, **When** I read all summaries, **Then** I can consume all content in approximately 2 minutes

---

### User Story 2 - Evening News Update Across Regions (Priority: P2)

A user wants to catch up on evening news from multiple regions (India, USA, World) before ending their day.

**Why this priority**: Extends P1 by adding multi-region support and evening bulletins. Provides comprehensive global news coverage.

**Independent Test**: Can be tested by visiting the site in the evening (9 PM - 12 AM local time), toggling between India/USA/World regions, and verifying that each region shows distinct evening news summaries with proper timezone handling.

**Acceptance Scenarios**:

1. **Given** it's 9:30 PM IST, **When** I select "India" region, **Then** I see the evening bulletin with India-specific news summaries
2. **Given** I'm viewing India evening news, **When** I switch to "World" region, **Then** the bulletin updates to show global news without page reload
3. **Given** I want comprehensive coverage, **When** I view all three regions (India, USA, World), **Then** each displays distinct, non-overlapping news summaries appropriate to that region
4. **Given** multiple bulletins exist for today, **When** I toggle between "Morning" and "Evening", **Then** I see the appropriate bulletin for each timeframe

---

### User Story 3 - Historical News Browsing with Dark Mode (Priority: P3)

A user wants to review news from previous days and prefers reading in dark mode to reduce eye strain.

**Why this priority**: Quality-of-life enhancement that improves usability for power users. Not essential for core news consumption but significantly improves user experience.

**Independent Test**: Can be tested by selecting a date from the past 7 days in the sidebar, verifying that historical bulletins load correctly, and toggling between light/dark themes to confirm visual consistency.

**Acceptance Scenarios**:

1. **Given** I open the platform, **When** I click on yesterday's date in the sidebar, **Then** I see both morning and evening bulletins from that date
2. **Given** historical bulletins are displayed, **When** I navigate through the past 7 days, **Then** each date shows complete bulletins (or indicates if data is missing)
3. **Given** I prefer dark mode, **When** I toggle to dark theme, **Then** all UI elements (cards, text, sidebar) switch to a dark color scheme with proper contrast
4. **Given** I'm using a device with dark mode system preference, **When** I first visit the site, **Then** the platform automatically loads in dark mode
5. **Given** I'm viewing news from 5 days ago, **When** I try to access news from 8 days ago, **Then** I see a message indicating that content is only retained for 7 days

---

### User Story 4 - Automated Fresh Content Without Manual Work (Priority: P1)

As a platform operator, I want news bulletins to be automatically fetched, summarized, and published without manual intervention.

**Why this priority**: Critical for platform sustainability - without automation, the platform cannot scale or remain current. This is infrastructure but essential for P1 user story delivery.

**Independent Test**: Can be verified by observing GitHub Actions workflow runs at scheduled times (7 AM, 9 PM for each region's timezone), confirming successful execution, and verifying that new JSON files appear in the repository with fresh news data.

**Acceptance Scenarios**:

1. **Given** it's 7:00 AM EST, **When** the USA morning workflow triggers, **Then** new news data is fetched from Perplexity API and stored in `data/usa/YYYY-MM-DD-morning.json`
2. **Given** the India evening workflow runs at 9:00 PM IST, **When** Perplexity API returns categorized news, **Then** the data is stored with proper schema (title, summary, source, url, category, timestamp)
3. **Given** a workflow encounters an API error, **When** the retry logic executes (3 retries with exponential backoff), **Then** the workflow either succeeds on retry or gracefully fails with error logging
4. **Given** a news source fails to return data, **When** the workflow processes remaining sources, **Then** the bulletin is published with available data and logs the missing source
5. **Given** multiple regions trigger workflows simultaneously, **When** all workflows execute, **Then** each region's data is stored independently without conflicts

---

### Edge Cases

- **What happens when Perplexity API is down during scheduled fetch?** System retries 3 times with exponential backoff (1s, 2s, 4s), then logs error and creates GitHub issue. Previous bulletin remains visible to users.
- **How does the system handle duplicate news articles across regions?** Each region's news is independently fetched and categorized by Perplexity API with region-specific prompts. Duplicates may appear but are intentional for regional context.
- **What happens if a user's device time is significantly different from server time?** Bulletin display is based on the bulletin's timestamp, not device time. Morning/evening toggles show bulletins based on their published time (7 AM = morning, 9 PM = evening).
- **How does the platform behave when viewing bulletins on a slow network?** JSON files are optimized (<100KB each); site uses progressive enhancement. If JavaScript fails to load, static HTML shows basic content. Loading states indicate when data is being fetched.
- **What if a user tries to access the 8th or 9th day of history?** Date picker in sidebar only shows the past 7 days; older dates are grayed out. If accessed directly via URL, shows a "Content not available - only 7 days retained" message.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST fetch news data from Perplexity API at scheduled times (7:00 AM and 9:00 PM) for each region's timezone (EST for USA, IST for India, UTC for World)
- **FR-002**: System MUST send region-specific prompts to Perplexity API that instruct it to categorize news by type (politics, technology, business, sports, etc.) and return structured data
- **FR-003**: System MUST store fetched news data as JSON files in the repository with naming convention `data/{region}/{YYYY-MM-DD}-{morning|evening}.json`
- **FR-004**: System MUST display news in a responsive card-based layout that adapts to desktop (1440px), tablet (768px), and mobile (320px) viewports
- **FR-005**: System MUST provide regional filters (India, USA, World) that update the displayed bulletins without page reload
- **FR-006**: System MUST provide morning/evening toggle that switches between 7 AM and 9 PM bulletins for the selected date
- **FR-007**: System MUST display a sidebar with date picker showing the past 7 days, allowing users to browse historical bulletins
- **FR-008**: System MUST retain news data for exactly 7 days; data older than 7 days MUST be automatically deleted by cleanup workflow
- **FR-009**: System MUST provide dark mode and light mode themes that can be toggled manually or detected from system preferences
- **FR-010**: System MUST display each news summary with citation links to original sources, opening in new tabs
- **FR-011**: System MUST ensure page load time is under 3 seconds on 3G connections (target: <500KB total page weight)
- **FR-012**: System MUST use separate GitHub Actions workflows for each region with timezone-appropriate scheduling
- **FR-013**: System MUST implement retry logic with exponential backoff (3 retries: 1s, 2s, 4s delays) for all API calls
- **FR-014**: System MUST log all workflow executions with timestamps, status, and error details
- **FR-015**: System MUST be deployable to GitHub Pages as a static site with no server-side dependencies

### Non-Functional Requirements

- **NFR-001**: Site MUST achieve Lighthouse performance score >90
- **NFR-002**: Site MUST be accessible according to WCAG 2.1 AA standards
- **NFR-003**: All API operations MUST be idempotent (safe to retry without side effects)
- **NFR-004**: JSON data files MUST follow a consistent schema across all regions and bulletins
- **NFR-005**: Site MUST use zero third-party runtime dependencies (vanilla JavaScript only)
- **NFR-006**: Dark mode and light mode MUST maintain minimum 4.5:1 contrast ratio for text

### Key Entities *(include if feature involves data)*

- **Bulletin**: Represents a collection of news summaries for a specific region, date, and time period (morning/evening)
  - Attributes: region (India/USA/World), date (YYYY-MM-DD), period (morning/evening), timestamp, articles[]
  
- **Article**: Represents a single AI-summarized news item
  - Attributes: title, summary (2-3 sentences), category (politics/tech/business/sports/health/etc.), source name, source URL, timestamp, region
  
- **Region**: Represents a geographical news coverage area
  - Values: India (IST timezone), USA (EST timezone), World (UTC timezone)
  - Attributes: name, timezone, scheduled_times (morning, evening)

## Success Criteria *(mandatory)*

The NRI News Brief platform is successful when:

1. **User Engagement**: Users can consume a complete news bulletin (all regions) in under 2 minutes per period (morning or evening)
2. **Performance**: Page loads in under 3 seconds on 3G connections with Lighthouse performance score >90
3. **Automation Reliability**: GitHub Actions workflows successfully fetch and publish bulletins at least 95% of scheduled times (allowing for 5% failure due to API outages)
4. **Multi-Device Usability**: Platform is fully functional and readable on mobile (320px), tablet (768px), and desktop (1440px) viewports without horizontal scrolling
5. **Content Freshness**: Morning bulletins (7 AM) and evening bulletins (9 PM) are published within 15 minutes of scheduled time for each region
6. **Data Retention**: Exactly 7 days of historical bulletins are accessible; older content is automatically removed
7. **Cost Efficiency**: Platform operates at zero infrastructure cost (GitHub Pages hosting, self-hosted runners for CI/CD)
8. **Citation Accuracy**: 100% of article summaries include working citation links to original news sources
9. **Theme Consistency**: Dark mode and light mode maintain WCAG 2.1 AA contrast ratios (4.5:1 for text) across all UI elements
10. **Regional Coverage**: Each region (India, USA, World) displays distinct, non-overlapping news content appropriate to that geographical area

## Assumptions *(mandatory)*

1. **Perplexity API Availability**: Perplexity API has sufficient rate limits and reliability for 6 scheduled requests per day (3 regions × 2 bulletins)
2. **GitHub Actions Reliability**: GitHub Actions scheduled workflows trigger within 5 minutes of cron schedule at least 95% of the time
3. **Self-Hosted Runner**: A GitHub self-hosted runner is available and properly configured with network access to Perplexity API
4. **News Source Stability**: Major news sources maintain stable URLs and accessibility for citation linking
5. **JSON File Size**: Each bulletin's JSON file will be under 100KB (approximately 10-15 articles with summaries)
6. **Browser Support**: Users have browsers supporting ES6+ JavaScript, CSS Grid, and Flexbox (Chrome 60+, Firefox 60+, Safari 12+, Edge 79+)
7. **Repository Size**: 7 days × 3 regions × 2 bulletins/day × 100KB = ~4.2MB of JSON data is acceptable for GitHub repository
8. **Perplexity API Schema**: Perplexity API can be prompted to return structured data that includes title, summary, category, source, and URL
9. **Timezone Handling**: GitHub Actions runners can be configured with appropriate timezones or use UTC with offset calculations
10. **Network Conditions**: Users on 3G connections have minimum 750 Kbps download speed for the <3 second page load requirement

## Dependencies

- **External APIs**: Perplexity AI API for news fetching and summarization (requires API key)
- **Infrastructure**: GitHub (repository hosting, Actions, Pages, self-hosted runner)
- **Browser APIs**: localStorage (theme preference), fetch API (JSON data loading), matchMedia (system theme detection)

## Out of Scope

Explicitly excluded from this feature:

- **User Authentication**: No login, user accounts, or personalized feeds
- **User Personalization**: No custom region selection saving or topic preferences
- **Comments/Social Features**: No commenting system, likes, shares, or social media integration
- **Push Notifications**: No real-time alerts or notification system
- **Real-Time Updates**: No WebSocket or live refresh; updates only at scheduled times
- **Search Functionality**: No search bar or filtering by keyword
- **Long-Term Archival**: No access to bulletins older than 7 days
- **Custom News Sources**: Users cannot add their own news sources or RSS feeds
- **Mobile Native Apps**: Web-only; no iOS/Android native applications
- **Internationalization Beyond 3 Regions**: Only India, USA, and World; no additional regions
- **Content Moderation**: No filtering of sensitive content or editorial review beyond AI summarization
- **Analytics Tracking**: No user behavior tracking or analytics integration

# Family Dashboard - TODO List

## 🚀 High Priority (Core Functionality)

### Chores Module
- [ ] **Edit Chore Modal** - Create modal for editing existing chores
  - Currently the edit button triggers `isEditing = true` but no modal exists
  - Similar to AddChoreModal but pre-populated with existing data
  - Location: `frontend/src/lib/components/chores/`

- [ ] **Automated Weekly/Monthly Resets**
  - Set up scheduled tasks (cron job) for automatic point resets
  - Currently requires manual API calls to `/admin/reset-weekly` and `/admin/reset-monthly`
  - Should run every Monday for weekly and 1st of month for monthly
  - Location: Backend scheduled task

### Weather Module
- [ ] **Geolocation Support** - Auto-detect user location
- [ ] **Air Quality Index (AQI)** - Show air quality data
- [ ] **Better Error Handling** - Improved error messages for weather API failures
- [ ] **Expand/Collapse** - Collapsible forecast details

---

## 🎨 Medium Priority (UX Improvements)

### Chores Module
- [ ] **Photo Upload for Completions**
  - Backend storage already has `photo_url` field
  - Need file upload UI in CompleteChoreModal
  - Need backend file storage (local or S3)

- [ ] **Chore Templates**
  - Pre-defined common chores for quick creation
  - Save custom chores as templates
  - Template library with categories

- [ ] **Completion History View**
  - Dedicated page/modal showing all completions
  - Filter by member, date range, chore type
  - Export to CSV option

- [ ] **Dashboard Analytics**
  - Charts showing points trends over time
  - Weekly/monthly comparison graphs
  - Member performance insights
  - Completion rate metrics

### General UI/UX
- [ ] **Loading Skeletons** - Replace spinners with skeleton screens
- [ ] **Optimistic Updates** - Update UI immediately, rollback on error
- [ ] **Keyboard Shortcuts** - Quick actions for power users (e.g., 'A' to add chore)
- [ ] **Toast Notifications** - Better success/error feedback instead of alerts
- [ ] **Dark Mode Toggle** - User preference for dark/light theme
- [ ] **Mobile App** - React Native or Flutter version

---

## 📊 Low Priority (Nice to Have)

### Chores Module
- [ ] **Leaderboards**
  - Weekly top performers
  - Monthly rankings
  - All-time points leaders
  - Friendly competition display

- [ ] **Achievements & Badges**
  - Milestone badges (100 points, 500 points, etc.)
  - Streak achievements (7 days, 30 days)
  - Special awards (most helpful, fastest completer)
  - Badge display on member cards

- [ ] **Allowance Calculator**
  - Configure point-to-money conversion rate
  - Automatic allowance calculation from monthly points
  - Payment tracking (paid/unpaid)
  - Export allowance reports

- [ ] **Chore Trading/Swapping**
  - Kids can offer to trade chores
  - Parent approval required
  - Negotiation system

- [ ] **Quality Ratings**
  - Parents rate completion quality (1-5 stars)
  - Bonus points for high-quality work
  - Quality history tracking

- [ ] **Auto-Assignment**
  - Smart assignment based on member availability
  - Fair distribution algorithm
  - Load balancing across members

- [ ] **Recurring Chore Improvements**
  - More flexible recurrence patterns (every other day, specific weekdays)
  - Seasonal chores (summer only, winter only)
  - Skip/postpone options

### Notifications
- [ ] **Email Notifications**
  - Weekly summary emails
  - Due date reminders
  - Weekly cap warnings
  - Monthly allowance reports

- [ ] **Push Notifications** (if mobile app built)
  - Chore due soon
  - New chore assigned
  - Points earned notification

### Analytics & Reporting
- [ ] **Advanced Analytics Dashboard**
  - Time-to-complete trends
  - Category breakdown charts
  - Efficiency metrics
  - Predictive analytics

- [ ] **Export Capabilities**
  - Export chores to CSV/Excel
  - Export completions history
  - Export points summary
  - PDF reports

### Integration
- [ ] **Calendar Integration**
  - Show due chores in Google Calendar
  - Sync completed chores as events
  - Due date reminders

- [ ] **Reward System Integration**
  - Connect to gift card APIs
  - Automatic reward redemption
  - Points-to-rewards catalog

---

## 🔧 Technical Improvements

### Backend
- [ ] **API Rate Limiting** - Better rate limiting per user
- [ ] **Caching Layer** - Redis for frequently accessed data
- [ ] **Database Optimization** - Add indexes, optimize queries
- [ ] **API Versioning** - Version the API for future changes
- [ ] **Webhook Support** - Webhooks for external integrations
- [ ] **Backup System** - Automated database backups
- [ ] **Multi-tenant Support** - Support multiple families/households

### Frontend
- [ ] **Error Boundary Components** - Graceful error handling
- [ ] **Service Worker** - Offline support and PWA features
- [ ] **Code Splitting** - Lazy load components for faster initial load
- [ ] **Performance Monitoring** - Track and optimize performance
- [ ] **Accessibility Audit** - Ensure WCAG compliance
- [ ] **Internationalization (i18n)** - Multi-language support
- [ ] **Unit Tests** - Add Jest/Vitest tests for components
- [ ] **E2E Tests** - Playwright or Cypress tests

### DevOps
- [ ] **CI/CD Pipeline** - Automated testing and deployment
- [ ] **Docker Compose** - Containerize the entire stack
- [ ] **Environment Management** - Better dev/staging/prod separation
- [ ] **Monitoring & Logging** - Better log aggregation and monitoring
- [ ] **Health Checks** - Comprehensive health check endpoints

---

## 🐛 Known Issues / Bugs

- [ ] **Activate/Deactivate Button Issue** - Removed from UI, API-only now (RESOLVED: Feature removed)
- [ ] **Recurring Chore Logic** - Fixed to properly check for `recurrence_type != "none"` (RESOLVED)
- [ ] **Completed Chores Not Showing** - Fixed status update logic (RESOLVED)
- [ ] **API Endpoint Paths** - Fixed double `/chores` in endpoints (RESOLVED)

---

## ✅ Recently Completed

- [x] Chores module frontend (6 components + store)
- [x] Chores module backend (models, schemas, API endpoints)
- [x] Points tracking with weekly caps
- [x] Family member management UI
- [x] Horizontal scrolling member cards
- [x] Removed buggy activate/deactivate UI feature
- [x] Fixed recurring chore completion logic
- [x] Fixed completed chore status updates
- [x] Added list chores endpoint
- [x] Fixed API routing issues
- [x] Comprehensive documentation (5 docs)
- [x] Seed script for initial data
- [x] Dashboard integration (2x2 grid)

---

## 📝 Future Considerations

### Phase 2 Features (3-6 months)
- Chore scheduling calendar view
- Parent dashboard with approval workflow
- Sibling collaboration chores
- Time tracking improvements
- Advanced filtering and search

### Phase 3 Features (6-12 months)
- Mobile native apps (iOS/Android)
- Voice assistant integration (Alexa/Google Home)
- Smart home integration (IoT devices)
- Social features (family leaderboard sharing)
- Gamification enhancements

---

## 🎯 Next Sprint Recommendations

Based on current functionality, here are the top priorities for your next development session:

### Must-Have (High Impact, Low Effort)
1. **Edit Chore Modal** - Users can't currently edit chores, only delete/recreate
2. **Toast Notifications** - Replace alert() with better UI feedback
3. **Automated Point Resets** - Set up cron jobs for Monday/monthly resets

### Should-Have (High Impact, Medium Effort)
4. **Photo Upload** - Visual proof of chore completion
5. **Chore Templates** - Faster chore creation
6. **Completion History View** - See all past completions

### Nice-to-Have (Medium Impact, Low Effort)
7. **Loading Skeletons** - Better loading states
8. **Keyboard Shortcuts** - Power user features
9. **Analytics Charts** - Visual progress tracking

---

## 📞 How to Contribute

1. Pick an item from this TODO list
2. Check if it requires backend, frontend, or both
3. Follow the existing code patterns
4. Update this file when completed
5. Document new features in the appropriate README

---

**Last Updated:** October 25, 2025
**Status:** Chores module v1.0 complete and production-ready! 🎉

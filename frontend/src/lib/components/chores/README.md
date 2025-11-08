# Chores Module

A comprehensive family chores management system with points tracking, weekly caps, and allowance calculation.

## Features

### Core Functionality
- **Chore Management**: Create, edit, delete, and complete chores
- **Points System**: Earn points (1-10) for completing chores
- **Weekly Caps**: Configurable weekly point limits by age group
- **Monthly Tracking**: Track monthly points for allowance calculation
- **Recurring Chores**: Support for daily, weekly, bi-weekly, and monthly recurring tasks
- **Priority Levels**: Low, medium, and high priority chores
- **Categories**: Organizing chores by type (cleaning, cooking, dishes, etc.)

### Family Management
- **Multiple Family Members**: Track points for each family member
- **Age Groups**: Predefined age groups with default weekly caps
  - Young (5-10): 25 points/week
  - Teen (11-15): 27 points/week
  - Older Teen (16-17): 30 points/week
  - Adult (18+): 30 points/week
- **Progress Tracking**: Visual weekly progress bars
- **Custom Caps**: Override default caps per member

### Dashboard Views
- **Compact Mode**: Quick overview with stats and top performers
- **Full Mode**: Detailed view with all chores and member cards
- **Real-time Updates**: Auto-refresh every 5 minutes
- **Filtering**: Filter chores by status and assigned member

## Components

### Frontend Components

#### `ChoresDashboard.svelte`
Main dashboard component displaying family members and active chores.

**Props:**
- `compact`: boolean - Display in compact or full mode

**Features:**
- Stats cards (pending, completed today, etc.)
- Family member cards with progress bars
- Active chores list
- Auto-refresh functionality

#### `MemberCard.svelte`
Displays individual family member's points and progress.

**Features:**
- Weekly progress bar with color coding
- Monthly and all-time points
- Weekly cap warnings
- Age group display

#### `ChoresList.svelte`
List of chores with filtering and actions.

**Features:**
- Status filtering (pending, in progress, overdue, completed)
- Member filtering
- Grouped display by status
- Add chore button

#### `ChoreCard.svelte`
Individual chore display with metadata and actions.

**Features:**
- Category and priority badges
- Points display
- Due date with overdue detection
- Assigned member info
- Complete, edit, and delete actions
- Recurring chore indicator

#### `CompleteChoreModal.svelte`
Modal for marking chores as complete.

**Features:**
- Select who completed the chore
- Track actual time spent
- Add completion notes
- Points preview
- Weekly cap validation

#### `AddChoreModal.svelte`
Modal for creating new chores.

**Features:**
- Full chore details (title, description, points)
- Category and priority selection
- Assignment to family members
- Due date and time estimate
- Recurrence configuration
- Notes field

### Store (State Management)

#### `stores/chores.ts`
Svelte store managing all chores-related state.

**Key Functions:**
- `loadDashboard()`: Load dashboard summary
- `loadChores(filters)`: Load chores with optional filtering
- `createChore(chore)`: Create a new chore
- `updateChore(id, updates)`: Update existing chore
- `deleteChore(id)`: Delete a chore
- `completeChore(completion)`: Mark chore as complete
- `loadMembers()`: Load family members
- `loadAgeGroups()`: Load age groups
- `loadCompletions(filters)`: Load completion history

**Derived Stores:**
- `pendingChores`: Filter for pending chores
- `completedChores`: Filter for completed chores
- `overdueChores`: Filter for overdue chores
- `highPriorityChores`: Filter for high priority pending chores

## Backend API

### Endpoints

#### Chores
- `GET /api/chores` - List all chores
- `POST /api/chores` - Create new chore
- `GET /api/chores/{id}` - Get specific chore
- `PUT /api/chores/{id}` - Update chore
- `DELETE /api/chores/{id}` - Delete chore

#### Family Members
- `GET /api/chores/members` - List all family members
- `POST /api/chores/members` - Create new member
- `GET /api/chores/members/{id}` - Get specific member
- `PUT /api/chores/members/{id}` - Update member
- `DELETE /api/chores/members/{id}` - Delete member

#### Age Groups
- `GET /api/chores/age-groups` - List all age groups
- `POST /api/chores/age-groups` - Create age group
- `GET /api/chores/age-groups/{id}` - Get specific age group
- `PUT /api/chores/age-groups/{id}` - Update age group
- `DELETE /api/chores/age-groups/{id}` - Delete age group

#### Completions
- `GET /api/chores/completions` - List completion history
- `POST /api/chores/completions` - Complete a chore

#### Dashboard
- `GET /api/chores/dashboard` - Get dashboard summary

#### Admin
- `POST /api/chores/admin/reset-weekly` - Manually reset weekly points
- `POST /api/chores/admin/reset-monthly` - Manually reset monthly points

## Database Models

### `Chore`
- Title, description, notes
- Points (1-10)
- Category, priority, status
- Assignment and creation info
- Due dates and recurrence
- Time estimate

### `FamilyMember`
- Name, age, age group
- Total, weekly, and monthly points
- Weekly points cap
- Reset tracking
- Active status

### `AgeGroup`
- Name (e.g., "Teen (11-15)")
- Age range (min/max)
- Default weekly cap

### `ChoreCompletion`
- Chore snapshot data
- Points earned
- Completion timestamp
- Optional notes and photo
- Actual time spent

### `WeeklyPointsArchive`
- Historical weekly points data
- Used for analytics and history

### `MonthlyPointsArchive`
- Historical monthly points data
- Used for allowance tracking

## Usage Examples

### Initialize Data
```bash
# From backend directory
python -m backend.seed_chores
```

### Add a Chore
1. Click "Add Chore" button in the ChoresList
2. Fill in chore details:
   - Title (required)
   - Description, category, priority
   - Points value (1-10)
   - Assign to family member
   - Set due date
   - Configure recurrence if needed
3. Click "Create Chore"

### Complete a Chore
1. Click "Complete" button on a ChoreCard
2. Select who completed it
3. Optionally add time spent and notes
4. Click "Mark Complete"
5. Points are automatically awarded and weekly/monthly totals updated

### View Dashboard
The dashboard displays:
- Pending chores count
- Completed today count
- Total completed chores
- Number of active family members
- Each family member's weekly progress
- List of all active chores with filters

### Filtering Chores
- **By Status**: Select "Pending", "In Progress", "Overdue", or "Completed"
- **By Member**: Select a specific family member or "All"
- Filters can be combined

## Points System Rules

### Weekly Caps
- Each age group has a default weekly cap
- Individual members can have custom caps (overrides age group default)
- Once a member reaches their cap, they cannot earn more points that week
- Warnings appear when members are near their cap (80%+)

### Points Calculation
- **Total Points**: Lifetime accumulated points
- **Weekly Points**: Points earned in current week (resets Monday)
- **Monthly Points**: Points earned in current month (used for allowance)

### Recurrence Logic
- When a recurring chore is completed:
  - It's marked complete for the current occurrence
  - Status automatically resets to "Pending" for next occurrence
  - Due date advances based on recurrence pattern
  - Next due date is calculated and stored

### Overdue Detection
- Chores with a due date in the past show as "Overdue"
- Overdue chores are displayed at the top of the list
- Visual indicators (red badges) highlight overdue status

## Color Coding

### Priority Colors
- **Low**: Green
- **Medium**: Yellow
- **High**: Red

### Category Colors
- **Cleaning**: Blue
- **Cooking**: Orange
- **Dishes**: Cyan
- **Laundry**: Purple
- **Trash**: Gray
- **Pets**: Green
- **Yard**: Lime
- **Maintenance**: Yellow
- **Organizing**: Pink
- **Other**: Slate

### Status Colors
- **Pending**: Blue
- **In Progress**: Yellow
- **Completed**: Green
- **Overdue**: Red

### Weekly Progress Colors
- **0-70%**: Green (on track)
- **70-90%**: Yellow (getting close)
- **90-100%**: Red (at or near cap)

## Future Enhancements

### Planned Features
1. **Photo Attachments**: Add before/after photos to chore completions
2. **Chore Templates**: Predefined chore templates for common tasks
3. **Allowance Calculator**: Automatic allowance calculation based on monthly points
4. **Leaderboards**: Weekly/monthly leaderboards for gamification
5. **Achievements**: Badges and achievements for milestones
6. **Push Notifications**: Reminders for due chores
7. **Mobile App**: Native mobile experience
8. **Chore History**: Detailed analytics and history view
9. **Export Data**: Export points/completion data to CSV
10. **Multi-Family**: Support for multiple families/households

### Enhancement Ideas
- **Chore Swapping**: Allow kids to trade chores
- **Bonus Points**: Special events with bonus point opportunities
- **Chore Bundles**: Group related chores together
- **Time Tracking**: Better time estimation based on history
- **Quality Ratings**: Parents can rate chore completion quality
- **Auto-Assignment**: Smart assignment based on availability and fairness
- **Collaborative Chores**: Chores that require multiple people

## Development

### Adding a New Category
1. Add to `ChoreCategory` type in `stores/chores.ts`
2. Add color mapping in `categoryColors`
3. Add label in `categoryLabels`
4. Update backend enum in `models/chores.py` and `schemas/chores.py`

### Adding a New Priority Level
Similar to categories - update types, colors, and labels in both frontend and backend.

### Customizing Weekly Caps
Edit age groups via the API or directly in database:
```sql
UPDATE age_groups SET default_weekly_cap = 30 WHERE name = 'Teen (11-15)';
```

Or override for specific member:
```sql
UPDATE family_members SET weekly_points_cap = 35 WHERE id = 1;
```

## Troubleshooting

### Points Not Updating
- Check that the chore completion was successful (check browser console)
- Verify the family member hasn't reached their weekly cap
- Refresh the dashboard to see latest data

### Chores Not Appearing
- Check filter settings (status and member filters)
- Verify chores were created successfully
- Check browser console for errors

### Weekly Reset Issues
- Weekly resets should happen automatically (scheduled task)
- Manual reset: `POST /api/chores/admin/reset-weekly`
- Check that the backend scheduled task is running

## Integration

The chores module is integrated into the main Family Dashboard as the bottom-right quadrant:

```svelte
<ChoresDashboard compact={selectedQuadrant !== 'chores'} />
```

- **Compact Mode**: Shows quick stats and top 3 members when not focused
- **Expanded Mode**: Shows full dashboard when quadrant is clicked
- **Auto-refresh**: Updates every 5 minutes automatically

## Testing

### Manual Testing Checklist
- [ ] Create a chore
- [ ] Edit a chore
- [ ] Delete a chore
- [ ] Complete a chore
- [ ] Verify points are awarded correctly
- [ ] Test weekly cap enforcement
- [ ] Test recurring chore behavior
- [ ] Filter chores by status
- [ ] Filter chores by member
- [ ] View dashboard statistics
- [ ] Check member progress bars
- [ ] Test overdue detection

### API Testing
Use the backend tests:
```bash
cd backend
pytest tests/test_chores_api.py -v
```

## License
Part of the Family Dashboard project.

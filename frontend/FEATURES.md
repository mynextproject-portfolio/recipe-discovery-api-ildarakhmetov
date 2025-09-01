# Recipe Discovery Frontend Features

## Recipe Source Management

### Internal Recipes (Editable)
- **Source**: `"internal"` 
- **Visual**: Standard white background with normal borders
- **Actions**: Full CRUD - View, Edit, Update
- **Badge**: None (default state)
- **Example**: Classic Chocolate Chip Cookies, Spaghetti Carbonara

### External Recipes (Read-Only)
- **Source**: `"mealdb"` or other external APIs
- **Visual**: Blue left border + source badge
- **Actions**: View only - Edit buttons hidden/disabled  
- **Badge**: Blue "MEALDB" badge + amber "Read Only" indicator
- **Example**: Mediterranean Pasta Salad (ID: 52777)

## Protection Mechanisms

### UI Level Protection
1. **Recipe Cards**: Edit button replaced with "Read Only" badge
2. **Detail View**: Edit button replaced with lock icon + explanation
3. **Visual Distinction**: Blue left border on external recipe cards

### Route Level Protection  
1. **Edit Routes**: `/recipes/{id}/edit` redirects to recipe detail for external recipes
2. **Server-side Check**: Validates recipe source before allowing edit access
3. **Redirect Logic**: 307 redirect preserves the original request method

## Visual Design System

### Color Coding
- **Blue**: External source indicators (`bg-blue-*`, `border-blue-*`)
- **Amber**: Read-only warnings (`bg-amber-*`, `text-amber-*`)
- **Gray**: Disabled states (`bg-gray-*`, `text-gray-*`)

### Badge System
- **Source Badge**: `🌐 MEALDB` (blue, uppercase)
- **Status Badge**: `External Recipe - Read Only` (amber)
- **Action Badge**: `Read Only` (gray, disabled state)

## API Integration

### Data Flow
```
MealDB API → FastAPI Backend → SvelteKit Frontend
    ↓              ↓                    ↓
External       Cached +           Read-Only
Recipes        Combined           Display
```

### Search Behavior
- Searches both internal database AND MealDB simultaneously
- Results combined and displayed with appropriate source indicators
- External recipes properly marked and protected from editing

## Development Notes

- All MealDB recipes have IDs > 50,000 (API convention)
- Internal recipes use sequential IDs starting from 1
- Source field is the authoritative indicator for edit permissions
- Server-side data loading ensures fast initial page renders

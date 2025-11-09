# Sneat Design System Documentation

## Overview

This project uses a custom design system inspired by the Sneat Bootstrap Admin Template. The design system provides a modern, professional, and consistent look across all pages of the HR Interview Platform.

## Architecture

### CSS Files

The design system is split into three main CSS files:

1. **`sneat-design-tokens.css`** - Contains all design tokens (CSS variables)
2. **`sneat-components.css`** - Reusable component classes
3. **`sneat-layouts.css`** - Page layout structures

### Base Template

All templates extend from `base.html` which includes:
- Google Fonts: Public Sans (300, 400, 500, 600, 700)
- All three design system CSS files
- Responsive meta tag

## Design Tokens

### Color Palette

#### Primary Colors
- **Primary**: `#696cff` - Main brand color
- **Primary Hover**: `#5f61e6`
- **Primary Light**: `rgba(105, 108, 255, 0.08)`

#### Semantic Colors
- **Success**: `#71dd37` (green)
- **Info**: `#03c3ec` (blue)
- **Warning**: `#ffab00` (orange)
- **Danger**: `#ff3e1d` (red)
- **Secondary**: `#8592a3` (gray)

#### Grayscale
- Gray 50 to Gray 900 (10 shades)
- Background: `#f5f5f9`
- Card Background: `#ffffff`

### Typography

#### Font Family
```css
--font-family-base: 'Public Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
```

#### Font Sizes
- XS: 0.75rem (12px)
- SM: 0.8125rem (13px)
- Base: 0.9375rem (15px)
- LG: 1rem (16px)
- XL: 1.125rem (18px)
- 2XL: 1.25rem (20px)
- 3XL: 1.5rem (24px)
- 4XL: 2rem (32px)
- 5XL: 2.5rem (40px)

#### Font Weights
- Light: 300
- Normal: 400
- Medium: 500
- Semibold: 600
- Bold: 700

### Spacing

Uses a consistent 8-point grid system:
- 1: 0.25rem (4px)
- 2: 0.5rem (8px)
- 3: 0.75rem (12px)
- 4: 1rem (16px)
- 5: 1.25rem (20px)
- 6: 1.5rem (24px)
- 8: 2rem (32px)
- 10: 2.5rem (40px)
- 12: 3rem (48px)
- 16: 4rem (64px)
- 20: 5rem (80px)

### Border Radius
- XS: 0.125rem (2px)
- SM: 0.25rem (4px)
- MD: 0.375rem (6px)
- LG: 0.5rem (8px)
- XL: 0.75rem (12px)
- 2XL: 1rem (16px)
- Pill: 50rem
- Circle: 50%

### Shadows
Six shadow levels from XS to 2XL, each progressively more prominent.

## Component Classes

### Buttons

#### Base Button
```html
<button class="btn">Button</button>
```

#### Variants
- `btn-primary` - Primary action (purple)
- `btn-secondary` - Secondary action (gray)
- `btn-success` - Success action (green)
- `btn-danger` - Danger/delete action (red)
- `btn-warning` - Warning action (orange)
- `btn-info` - Info action (blue)

#### Outline Buttons
```html
<button class="btn btn-outline-primary">Outline</button>
```

#### Label Buttons (lighter background)
```html
<button class="btn btn-label-primary">Label</button>
```

#### Sizes
- `btn-sm` - Small button
- Default - Standard size
- `btn-lg` - Large button

#### Utilities
- `btn-icon` - Square button for icons
- `w-100` - Full width button

### Cards

```html
<div class="card">
    <div class="card-header">
        <h3 class="card-title">Card Title</h3>
    </div>
    <div class="card-body">
        Content goes here
    </div>
    <div class="card-footer">
        Footer content
    </div>
</div>
```

### Forms

```html
<div class="form-group">
    <label for="input" class="form-label">Label</label>
    <input type="text" id="input" class="form-control" placeholder="Placeholder">
</div>
```

Form components:
- `form-control` - Text inputs, textareas
- `form-select` - Select dropdowns
- `form-label` - Labels

### Alerts

```html
<div class="alert alert-success">Success message</div>
<div class="alert alert-danger">Error message</div>
<div class="alert alert-warning">Warning message</div>
<div class="alert alert-info">Info message</div>
```

### Tables

```html
<table class="table">
    <thead>
        <tr>
            <th>Header</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Data</td>
        </tr>
    </tbody>
</table>
```

### Badges

```html
<span class="badge badge-primary">Badge</span>
<span class="badge badge-success">Success</span>
```

### Status Badges

Special badges for status indicators:
```html
<span class="status-badge status-active">Active</span>
<span class="status-badge status-pending">Pending</span>
<span class="status-badge status-inactive">Inactive</span>
```

## Layout Components

### Admin Layout with Sidebar

The admin dashboard uses a fixed sidebar layout:

```html
<div class="layout-wrapper">
    <aside class="layout-sidebar">
        <!-- Sidebar content -->
    </aside>
    <div class="layout-content with-sidebar">
        <nav class="layout-navbar with-sidebar">
            <!-- Navbar content -->
        </nav>
        <div class="content-wrapper">
            <!-- Main content -->
        </div>
    </div>
</div>
```

Components:
- `layout-sidebar` - Fixed left sidebar (260px width)
- `layout-navbar` - Top navigation bar (62px height)
- `layout-content` - Main content area
- `content-wrapper` - Container for page content (max-width: 1440px)

### Menu Items

```html
<a href="#" class="menu-item active">
    <span class="menu-icon">📊</span>
    Dashboard
</a>
```

### Stats Grid

Display key metrics:

```html
<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-header">
            <h3 class="stat-title">Title</h3>
            <div class="stat-icon primary">💼</div>
        </div>
        <div class="stat-value">42</div>
    </div>
</div>
```

Icon variants: `primary`, `success`, `warning`, `info`

### Public Layout

#### Hero Section

```html
<div class="hero-section">
    <div class="hero-nav">
        <!-- Navigation buttons -->
    </div>
    <div class="hero-content">
        <h1 class="hero-title">Title</h1>
        <p class="hero-subtitle">Subtitle</p>
    </div>
</div>
```

#### Features Grid

```html
<div class="features-section">
    <div class="features-grid">
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <h3 class="feature-title">Feature</h3>
            <p class="feature-description">Description</p>
        </div>
    </div>
</div>
```

### Page Header

Standard page header for admin pages:

```html
<div class="page-header">
    <div class="page-header-content">
        <div>
            <h1 class="page-title">Page Title</h1>
            <p class="page-subtitle">Subtitle</p>
        </div>
        <div class="page-actions">
            <button class="btn btn-primary">Action</button>
        </div>
    </div>
</div>
```

### Table Container

Wrapper for tables with consistent styling:

```html
<div class="table-container">
    <div class="table-header">
        <h2 class="table-title">Table Title</h2>
        <div class="table-actions">
            <!-- Action buttons -->
        </div>
    </div>
    <table class="table">
        <!-- Table content -->
    </table>
</div>
```

## Utility Classes

### Spacing
- `mb-0` to `mb-5` - Margin bottom
- `mt-0` to `mt-5` - Margin top
- `gap-2`, `gap-3` - Gap for flexbox

### Display
- `d-flex` - Display flex
- `d-block` - Display block
- `d-inline-block` - Display inline-block
- `d-none` - Display none

### Flex Utilities
- `align-items-center` - Center items vertically
- `justify-content-between` - Space between items
- `justify-content-center` - Center items

### Text
- `text-center` - Center text
- `text-right` - Right align text
- `text-muted` - Muted gray text
- `text-primary`, `text-success`, `text-danger` - Colored text

### Width
- `w-100` - 100% width

## Responsive Design

### Breakpoints

- Mobile: < 768px
- Tablet: 768px - 991px
- Desktop: > 991px

### Mobile Behavior

- Sidebar collapses on screens < 991px
- Tables scroll horizontally
- Stats grid becomes single column on mobile
- Features grid becomes single column on mobile

## Usage Examples

### Creating a New Admin Page

1. Extend `base.html`
2. Import the admin layout macro
3. Call the macro with appropriate content

```html
{% extends 'base.html' %}

{% block title %}Page Title{% endblock %}

{% block content %}
{% from 'org_admin/_layout.html' import admin_layout %}
{% call admin_layout('page-name', current_user) %}
    <div class="page-header">
        <div class="page-header-content">
            <h1 class="page-title">Title</h1>
        </div>
    </div>
    
    <!-- Your content here -->
{% endcall %}
{% endblock %}
```

### Creating a Form Page

```html
<div class="card">
    <div class="card-body">
        <h2 class="card-title">Form Title</h2>
        
        <form method="POST">
            <div class="form-group">
                <label for="field" class="form-label">Field Name</label>
                <input type="text" id="field" name="field" class="form-control" required>
            </div>
            
            <button type="submit" class="btn btn-primary">Submit</button>
        </form>
    </div>
</div>
```

### Creating a Data Table

```html
<div class="table-container">
    <div class="table-header">
        <h2 class="table-title">Data Table</h2>
        <div class="table-actions">
            <a href="#" class="btn btn-primary">+ Add New</a>
        </div>
    </div>
    
    <table class="table">
        <thead>
            <tr>
                <th>Column 1</th>
                <th>Column 2</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for item in items %}
            <tr>
                <td>{{ item.name }}</td>
                <td>{{ item.value }}</td>
                <td>
                    <a href="#" class="btn btn-sm btn-secondary">Edit</a>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
```

## Best Practices

1. **Always use design tokens** - Use CSS variables instead of hardcoded values
2. **Consistent spacing** - Use the spacing scale (8-point grid)
3. **Semantic colors** - Use appropriate color variants (primary, success, danger, etc.)
4. **Responsive first** - Test on mobile, tablet, and desktop
5. **Accessibility** - Include proper labels, ARIA attributes, and focus states
6. **Component reuse** - Use existing components before creating new ones

## Dark Mode Support

The design system includes dark mode variables (currently not active). To enable dark mode, add `data-theme="dark"` to the `<html>` tag.

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Future Enhancements

1. Icon library integration (BoxIcons or similar)
2. Animation utilities
3. More utility classes
4. Custom form elements (checkboxes, radio buttons, switches)
5. Modal/dialog components
6. Toast notifications
7. Loading states
8. Skeleton screens


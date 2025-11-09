# Sneat Design System - Quick Start Guide

## 🚀 Getting Started

Your HR Interview Platform now uses a professional Sneat-inspired design system. Here's everything you need to know to start using it.

## 📁 Files Overview

```
app/static/css/
├── sneat-design-tokens.css    # Colors, spacing, typography (CSS variables)
├── sneat-components.css        # Buttons, cards, forms, tables
└── sneat-layouts.css           # Page layouts, grids, admin dashboard

app/templates/
└── base.html                   # Base template (loads all CSS + fonts)
```

## 🎨 Quick Reference

### Colors (Use these CSS variables)

```css
var(--primary)      /* #696cff - Purple */
var(--success)      /* #71dd37 - Green */
var(--info)         /* #03c3ec - Cyan */
var(--warning)      /* #ffab00 - Orange */
var(--danger)       /* #ff3e1d - Red */
var(--secondary)    /* #8592a3 - Gray */
```

### Common Components

#### Button
```html
<button class="btn btn-primary">Primary Button</button>
<button class="btn btn-secondary">Secondary Button</button>
<button class="btn btn-success">Success Button</button>
<button class="btn btn-sm">Small Button</button>
```

#### Card
```html
<div class="card">
    <div class="card-body">
        <h3 class="card-title">Card Title</h3>
        <p>Card content here</p>
    </div>
</div>
```

#### Form
```html
<div class="form-group">
    <label for="email" class="form-label">Email</label>
    <input type="email" id="email" class="form-control">
</div>
```

#### Alert
```html
<div class="alert alert-success">Success message!</div>
<div class="alert alert-danger">Error message!</div>
```

#### Badge
```html
<span class="badge badge-primary">Primary</span>
<span class="status-badge status-active">Active</span>
```

#### Table
```html
<table class="table">
    <thead>
        <tr><th>Name</th><th>Value</th></tr>
    </thead>
    <tbody>
        <tr><td>John</td><td>100</td></tr>
    </tbody>
</table>
```

### Spacing Utilities

```html
<div class="mb-4">Margin bottom (16px)</div>
<div class="mt-5">Margin top (20px)</div>
<div class="gap-3">Gap for flex (12px)</div>
```

### Layout Utilities

```html
<div class="d-flex justify-content-between align-items-center">
    <div>Left content</div>
    <div>Right content</div>
</div>

<div class="text-center">Centered text</div>
<button class="btn w-100">Full width button</button>
```

## 📄 Creating a New Admin Page

```html
{% extends 'base.html' %}

{% block title %}My Page{% endblock %}

{% block extra_css %}
<style>
body {
    margin: 0;
    padding: 0;
}
</style>
{% endblock %}

{% block content %}
{% from 'org_admin/_layout.html' import admin_layout %}
{% call admin_layout('page-id', current_user) %}
    <div class="page-header">
        <div class="page-header-content">
            <div>
                <h1 class="page-title">My Page Title</h1>
                <p class="page-subtitle">Page description</p>
            </div>
            <div class="page-actions">
                <a href="#" class="btn btn-primary">+ Add New</a>
            </div>
        </div>
    </div>
    
    <!-- Your content here -->
    <div class="card">
        <div class="card-body">
            <p>Page content</p>
        </div>
    </div>
{% endcall %}
{% endblock %}
```

## 📄 Creating a New Public Page

```html
{% extends 'base.html' %}

{% block title %}My Public Page{% endblock %}

{% block content %}
<div class="container" style="padding-top: var(--spacing-8);">
    <div class="page-header">
        <h1 class="page-title">Welcome</h1>
    </div>
    
    <div class="card">
        <div class="card-body">
            <p>Your content here</p>
        </div>
    </div>
</div>
{% endblock %}
```

## 🎯 Common Patterns

### Stats Dashboard

```html
<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-header">
            <h3 class="stat-title">Total Users</h3>
            <div class="stat-icon primary">👥</div>
        </div>
        <div class="stat-value">1,234</div>
    </div>
</div>
```

### Data Table with Actions

```html
<div class="table-container">
    <div class="table-header">
        <h2 class="table-title">Users</h2>
        <div class="table-actions">
            <a href="#" class="btn btn-primary">+ Add User</a>
        </div>
    </div>
    <table class="table">
        <thead>
            <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Status</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>John Doe</strong></td>
                <td>john@example.com</td>
                <td><span class="status-badge status-active">Active</span></td>
                <td>
                    <a href="#" class="btn btn-sm btn-secondary">Edit</a>
                    <a href="#" class="btn btn-sm btn-danger">Delete</a>
                </td>
            </tr>
        </tbody>
    </table>
</div>
```

### Form Page

```html
<div class="card">
    <div class="card-body">
        <h2 class="card-title">Create New Item</h2>
        
        <form method="POST">
            <div class="form-group">
                <label for="name" class="form-label">Name *</label>
                <input type="text" id="name" name="name" class="form-control" required>
            </div>
            
            <div class="form-group">
                <label for="description" class="form-label">Description</label>
                <textarea id="description" name="description" class="form-control" rows="4"></textarea>
            </div>
            
            <div class="form-group">
                <label for="status" class="form-label">Status</label>
                <select id="status" name="status" class="form-select">
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                </select>
            </div>
            
            <div class="d-flex gap-3">
                <button type="submit" class="btn btn-primary">Save</button>
                <a href="#" class="btn btn-secondary">Cancel</a>
            </div>
        </form>
    </div>
</div>
```

## 📱 Responsive Design

The design system is mobile-first and fully responsive:

- **Mobile**: < 768px (single column)
- **Tablet**: 768px - 991px (adapted layout)
- **Desktop**: > 991px (full layout with sidebar)

No extra work needed - just use the components!

## 🎨 Color Usage Guide

**When to use each color:**

- **Primary** (`btn-primary`): Main actions (Create, Save, Submit)
- **Secondary** (`btn-secondary`): Secondary actions (Cancel, Edit, Back)
- **Success** (`btn-success`): Positive actions (Approve, Activate, Confirm)
- **Danger** (`btn-danger`): Destructive actions (Delete, Remove, Deactivate)
- **Warning** (`btn-warning`): Warning actions (Reset, Archive)
- **Info** (`btn-info`): Information actions (Details, View More)

## 💡 Pro Tips

1. **Always use design tokens** (CSS variables) instead of hardcoded colors
2. **Use spacing utilities** (`mb-4`, `mt-5`) for consistent spacing
3. **Wrap tables** in `table-container` for better styling
4. **Use status badges** for workflow states (active, pending, etc.)
5. **Add page headers** for consistency across admin pages
6. **Use the layout macro** for admin pages to maintain consistency

## 🔍 Need More Details?

- **Full Documentation**: See `SNEAT_DESIGN_SYSTEM.md`
- **Implementation Summary**: See `DESIGN_IMPLEMENTATION_SUMMARY.md`
- **Component Examples**: Check existing templates in `app/templates/`

## 🐛 Common Issues

### CSS not loading?
Make sure `base.html` has the three CSS files:
```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/sneat-design-tokens.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/sneat-components.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/sneat-layouts.css') }}">
```

### Fonts not showing?
Public Sans is loaded from Google Fonts in `base.html`:
```html
<link href="https://fonts.googleapis.com/css2?family=Public+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
```

### Layout not working?
For admin pages, make sure you're using the layout macro:
```html
{% from 'org_admin/_layout.html' import admin_layout %}
{% call admin_layout('page-name', current_user) %}
    <!-- content -->
{% endcall %}
```

## ✅ Quick Checklist for New Pages

- [ ] Extends `base.html`
- [ ] Has a proper `{% block title %}`
- [ ] Uses design system components (buttons, cards, forms)
- [ ] Uses spacing utilities instead of custom CSS
- [ ] Uses CSS variables for colors
- [ ] Includes flash message handling
- [ ] Is responsive (test on mobile)
- [ ] Has consistent page header (for admin pages)

## 🎉 You're Ready!

Start building with the Sneat design system. All the hard work is done - just use the components and enjoy the professional look!

**Questions?** Check the full documentation in `SNEAT_DESIGN_SYSTEM.md`

---

**Happy coding! 🚀**


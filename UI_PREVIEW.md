# React UI Preview

## Modern Research RAG Assistant Interface

The new React interface provides a professional, intuitive experience designed for PhD researchers.

## Main Interface

```
┌────────────────────────────────────────────────────────────────────┐
│                    📚 Research RAG Assistant                        │
│            AI-powered research paper query and analysis            │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────┬──────────────────────────┐   │
│  │  CHAT AREA                      │  SETTINGS                │   │
│  │                                 │                          │   │
│  │  ┌───────────────────────────┐ │  ⚙️ Settings             │   │
│  │  │ ☑ 🔍 Force Retrieval      │ │  ┌──────────────────┐   │   │
│  │  │                            │ │  │ 🤖 Model         │   │   │
│  │  │ ✓ ON: Searching documents │ │  │ llama-70b  ▼    │   │   │
│  │  │ with citations             │ │  └──────────────────┘   │   │
│  │  └───────────────────────────┘ │                          │   │
│  │                                 │  📄 Documents: 5         │   │
│  │  ┌───────────────────────────┐ │  ├────●──────────────┤  │   │
│  │  │ User:                      │ │  1                  20   │   │
│  │  │ What are the latest        │ │                          │   │
│  │  │ approaches to SLAM?        │ │  🎯 Relevance: 75%      │   │
│  │  └───────────────────────────┘ │  ├───────●───────────┤  │   │
│  │                                 │  50                 100   │   │
│  │  ┌───────────────────────────┐ │                          │   │
│  │  │ Assistant:                 │ │  ─────────────────────   │   │
│  │  │ Based on your papers:      │ │                          │   │
│  │  │                            │ │  📊 System Status        │   │
│  │  │ Recent SLAM approaches     │ │  LM Studio: connected ✅│   │
│  │  │ focus on... [Smith 2024]   │ │  PDFs: 127              │   │
│  │  │                            │ │  Indexed: 100           │   │
│  │  │ 📚 Sources (3):            │ │  Chunks: 12,458         │   │
│  │  │ [1] Lightweight SLAM       │ │  Pending: 27            │   │
│  │  │     (Smith, 2024) - 0.89   │ │                          │   │
│  │  │ [2] Visual SLAM            │ │  ─────────────────────   │   │
│  │  │     (Jones, 2023) - 0.85   │ │                          │   │
│  │  │ [3] Neural SLAM            │ │  📥 Indexing             │   │
│  │  │     (Brown, 2024) - 0.82   │ │  [Start Indexing]       │   │
│  │  └───────────────────────────┘ │                          │   │
│  │                                 │                          │   │
│  │  ┌───────────────────────────┐ │                          │   │
│  │  │ Ask a question... [Send]  │ │                          │   │
│  │  └───────────────────────────┘ │                          │   │
│  └─────────────────────────────────┴──────────────────────────┘   │
└────────────────────────────────────────────────────────────────────┘
```

## Color Scheme

The interface uses a modern gradient design:

- **Background**: Purple gradient (667eea → 764ba2)
- **Cards**: White with subtle shadows
- **Primary Actions**: Gradient buttons matching theme
- **User Messages**: Purple gradient bubbles
- **Assistant Messages**: Light gray bubbles
- **Status Badges**: Green (connected) / Red (disconnected)

## Key UI Elements

### 1. Force Retrieval Toggle
```
┌─────────────────────────────────┐
│ ☑ 🔍 Force Retrieval            │
│                                  │
│ ✓ ON: Searching documents with  │
│ citations (slower but            │
│ comprehensive)                   │
└─────────────────────────────────┘
```

**When OFF:**
```
┌─────────────────────────────────┐
│ ☐ 🔍 Force Retrieval            │
│                                  │
│ ✗ OFF: Simple LLM chat          │
│ (faster, no document search)     │
└─────────────────────────────────┘
```

### 2. Settings Panel
```
┌──────────────────────────────┐
│ ⚙️ Settings                  │
│                              │
│ 🤖 Model                     │
│ ┌──────────────────────────┐│
│ │ llama-70b-chat        ▼ ││
│ └──────────────────────────┘│
│                              │
│ 📄 Documents: 5              │
│ ├────●──────────────────┤   │
│ 1                       20   │
│                              │
│ 🎯 Relevance: 75%            │
│ ├───────●───────────────┤   │
│ 50                     100   │
└──────────────────────────────┘
```

### 3. System Status
```
┌──────────────────────────────┐
│ 📊 System Status             │
│                              │
│ LM Studio: [connected] ✅    │
│ PDFs: 127                    │
│ Indexed: 100                 │
│ Chunks: 12,458               │
│ Pending: 27                  │
└──────────────────────────────┘
```

### 4. Message Display
```
User Message:
┌─────────────────────────────┐
│ What are the latest SLAM    │
│ approaches in constrained   │
│ hardware?                   │
└─────────────────────────────┘
```

```
Assistant Message with Sources:
┌─────────────────────────────────────┐
│ Based on your research papers:      │
│                                      │
│ Recent approaches focus on three    │
│ main strategies: [Smith et al.]...  │
│                                      │
│ 📚 Sources (3 documents):           │
│                                      │
│ [1] Lightweight SLAM for Embedded   │
│     Smith et al. (2024) - Score: 0.89│
│                                      │
│ [2] Resource-Efficient Visual SLAM  │
│     Jones & Lee (2023) - Score: 0.85 │
│                                      │
│ [3] Neural SLAM on Edge Devices     │
│     Brown et al. (2024) - Score: 0.82│
└─────────────────────────────────────┘
```

## Responsive Design

### Desktop (1600px+)
- Two-column layout
- Settings panel always visible
- Optimal for research work

### Tablet (768px - 1024px)
- Still two columns but narrower
- Settings panel condensed

### Mobile (<768px)
- Single column
- Settings panel on top
- Chat below
- Fully functional

## Animations

### Page Load
- Smooth fade-in
- Staggered element appearance

### Messages
- Slide up animation
- Smooth scroll to new messages

### Buttons
- Hover: Slight lift effect
- Click: Ripple effect
- Disabled: Fade opacity

### Status Updates
- Pulse animation for "in progress"
- Color transitions for state changes

## Accessibility

- ✅ Keyboard navigation
- ✅ ARIA labels
- ✅ Screen reader compatible
- ✅ High contrast mode support
- ✅ Focus indicators
- ✅ Semantic HTML

## Dark Mode (Future)

The CSS is structured to easily support dark mode:
```css
:root {
  --bg-primary: white;
  --text-primary: #2c3e50;
  /* ... */
}

[data-theme="dark"] {
  --bg-primary: #1a1a1a;
  --text-primary: #ecf0f1;
  /* ... */
}
```

## Browser Support

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## Performance

- **First Contentful Paint**: < 1s
- **Time to Interactive**: < 2s
- **Smooth 60fps animations**
- **Lazy loading for images**
- **Code splitting for routes**

## User Feedback

Visual feedback for all actions:

### Loading States
```
┌─────────────────────┐
│ Thinking...         │
│ ●●●                 │
└─────────────────────┘
```

### Success States
```
✅ Indexing Complete!
Processed 27 documents
```

### Error States
```
❌ Error: Could not connect
Please check LM Studio
```

## Summary

The React interface provides:

✅ **Professional Appearance**: Modern gradient design
✅ **Intuitive Layout**: Everything in logical places
✅ **Clear Feedback**: Always know what's happening
✅ **Responsive**: Works on all devices
✅ **Fast**: Smooth interactions
✅ **Accessible**: Works for everyone

Perfect for PhD research work! 🎓

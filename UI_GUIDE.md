# Research RAG UI - Visual Guide

## Main Interface Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  Research RAG Assistant                                    [≡]   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐                                          │
│  │ 🤖 Select Model: │                                          │
│  │ ▼ llama-70b-chat │                                          │
│  └──────────────────┘                                          │
│                                                                 │
│  📚 Research RAG Assistant                                      │
│  AI-powered research paper query and analysis system           │
│  for PhD researchers.                                           │
│                                                                 │
│  ✅ LM Studio Server Connected                                  │
│  Available models:                                              │
│    • llama-70b-chat                                             │
│    • mistral-7b-instruct                                        │
│    • qwen-14b                                                   │
│                                                                 │
│  You can select a model using the dropdown at the top left.    │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ 🔧 Retrieval Settings                                   │   │
│  │                                                          │   │
│  │ Number of Documents:  [━━━━━━━●━━━━━━━━━━] 5            │   │
│  │                                                          │   │
│  │ Relevance Threshold:  [━━━━━━━━━━━━━●━━━━] 75%          │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                 │
│  📊 Library Status                                              │
│  - PDFs in folder: 127                                         │
│  - Already indexed: 100                                        │
│  - Chunks in vector store: 12,458                             │
│  - PDF folder: `data/pdfs`                                     │
│                                                                 │
│  📥 27 New PDFs Found                                          │
│    - paper_1.pdf                                               │
│    - paper_2.pdf                                               │
│    ... and 25 more                                             │
│                                                                 │
│  [✅ Index Now]  [⏭️ Skip for Now]                              │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  💬 Type your research question...                       [→]   │
└─────────────────────────────────────────────────────────────────┘
```

## During Indexing

```
┌─────────────────────────────────────────────────────────────────┐
│  🔄 PDF Indexing in Progress • You can still search indexed docs│
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  🔄 Indexing in Progress                                        │
│                                                                 │
│  Extracted 3,456 chunks from 27 documents.                     │
│                                                                 │
│  Now generating metadata with LLM...                           │
│  (Processing 15/27 papers)                                     │
│                                                                 │
│  You can still query existing documents.                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Query Example

### User Query
```
┌─────────────────────────────────────────────────────────────────┐
│  👤 User                                                        │
│                                                                 │
│  What are the main approaches to SLAM in resource-constrained  │
│  hardware? Focus on papers from 2023-2025.                     │
└─────────────────────────────────────────────────────────────────┘
```

### Assistant Response
```
┌─────────────────────────────────────────────────────────────────┐
│  🤖 Research RAG Assistant                                      │
│                                                                 │
│  Based on the recent literature in your collection, there are  │
│  three main approaches to SLAM in resource-constrained         │
│  hardware:                                                      │
│                                                                 │
│  1. **Feature-Based Methods** [Smith et al., 2024] propose a  │
│     lightweight ORB-SLAM variant that reduces memory usage by  │
│     40% through selective keyframe management...               │
│                                                                 │
│  2. **Direct Methods** [Johnson & Lee, 2023] demonstrate that  │
│     direct photometric alignment can achieve real-time         │
│     performance on embedded ARM processors...                  │
│                                                                 │
│  3. **Learned Features** [Zhang et al., 2024] introduce a      │
│     neural feature extractor optimized for edge devices...     │
│                                                                 │
│  Filtered to 5 documents meeting 75% relevance threshold      │
│  (from 5 retrieved)                                            │
│                                                                 │
│  ─────────────────────────────────────────────────────────────│
│                                                                 │
│  📚 Sources:                                                    │
│  - [1] Lightweight ORB-SLAM for Embedded Systems... (Smith,   │
│    2024) - Score: 0.89                                         │
│  - [2] Direct Visual SLAM on ARM Processors... (Johnson,       │
│    2023) - Score: 0.86                                         │
│  - [3] Neural SLAM for Edge Computing... (Zhang, 2024) -       │
│    Score: 0.84                                                 │
│  - [4] Survey of Resource-Efficient SLAM... (Brown, 2023) -    │
│    Score: 0.81                                                 │
│  - [5] Hardware Acceleration for Visual SLAM... (Davis, 2024)  │
│    Score: 0.78                                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Source Details Panel (Side Panel)

```
┌───────────────────────────────────┐
│ [1] Lightweight ORB-SLAM for...  │
├───────────────────────────────────┤
│                                   │
│ **Lightweight ORB-SLAM for       │
│ Embedded Systems**                │
│                                   │
│ *Smith, J. et al.* (2024)         │
│                                   │
│ **Relevance Score:** 0.894        │
│ **Page:** 3                       │
│                                   │
│ **Summary:** This paper presents │
│ a novel variant of ORB-SLAM      │
│ optimized for embedded systems   │
│ with limited memory...            │
│                                   │
│ **Methodology:** The authors     │
│ implement selective keyframe     │
│ management and adaptive feature  │
│ tracking...                       │
│                                   │
│ **Results:** Achieves 40%        │
│ reduction in memory usage while  │
│ maintaining 95% accuracy...       │
│                                   │
│ **Relevant Excerpt:**             │
│ "Our approach leverages a        │
│ hierarchical keyframe selection  │
│ strategy that prioritizes frames │
│ with high information content... │
│ (800 more characters)             │
│                                   │
└───────────────────────────────────┘
```

## Settings Panel Detail

```
┌─────────────────────────────────────────────┐
│ ⚙️ Settings                                 │
├─────────────────────────────────────────────┤
│                                             │
│ 🤖 Model                                    │
│ ┌─────────────────────────────────────┐   │
│ │ llama-70b-chat                   ▼  │   │
│ └─────────────────────────────────────┘   │
│ Select the LLM model to use for          │
│ generation                                │
│                                             │
│ 📊 Number of Documents         [5]         │
│ ├─────●─────────────────────────┤         │
│ 1                               20         │
│ Number of documents to retrieve           │
│                                             │
│ 🎯 Relevance Threshold (%)    [75]        │
│ ├──────────────●────────────────┤         │
│ 50                             100         │
│ Minimum relevance score for results       │
│                                             │
└─────────────────────────────────────────────┘
```

## Visual Design Features

### Color Scheme
- **Primary**: Deep blue (#2c3e50) - Professional, academic
- **Secondary**: Bright blue (#3498db) - Interactive elements
- **Accent**: Coral red (#e74c3c) - Important actions
- **Success**: Green (#27ae60) - Confirmations
- **Warning**: Orange (#f39c12) - Progress indicators

### Typography
- **Headers**: Segoe UI Bold, 1.2-1.5rem
- **Body**: Segoe UI, 1rem
- **Code/Paths**: Monospace, 0.9rem
- **Labels**: Segoe UI Semibold, 0.95rem

### Components

#### Model Selector (Top Left)
- Fixed position overlay
- White background with shadow
- Rounded corners (8px)
- Hover effect on dropdown
- Focus ring for accessibility

#### Settings Panel
- Integrated Chainlit settings
- Sliders with custom styling
- Real-time value display
- Tooltip support
- Responsive layout

#### Progress Indicator
- Fixed top banner
- Gradient background (warning colors)
- Animated spinner
- Pulse animation
- Dismissible after completion

#### Source Citations
- Sidebar elements
- Collapsible panels
- Metadata rich display
- Syntax highlighted excerpts
- Score visualization

### Animations
- Slider thumb scale on hover
- Button lift on hover
- Progress indicator pulse
- Smooth color transitions
- Fade in/out for messages

### Responsive Design
- Desktop: Side-by-side layout
- Tablet: Stacked layout
- Mobile: Single column, collapsed panels
- Model selector repositions to top on mobile

## Accessibility Features
- WCAG 2.1 AA compliant colors
- Keyboard navigation support
- Screen reader friendly labels
- Focus indicators on all interactive elements
- Sufficient color contrast (4.5:1 minimum)

## Browser Compatibility
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Dark Mode
- Automatic detection via `prefers-color-scheme`
- Inverted color scheme
- Maintained contrast ratios
- Smooth transitions between modes

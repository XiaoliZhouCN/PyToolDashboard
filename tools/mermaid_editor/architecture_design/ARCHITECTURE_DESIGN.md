# Mermaid Editor Architecture Design

## 1. Current Goal

Build and maintain a Mermaid note/editor tool in Python at:

- `/d:/Repositories/pytools/mermaid_editor`

Initial reference input:

- `/d:/Repositories/NexusRenderer/workflow.md`

Core capabilities for the first milestone:

1. Read Mermaid source from Markdown files and render diagrams.
2. Support manual layout editing instead of relying only on Mermaid auto-layout.
3. Support manually adding subgraphs and nodes.
4. Support editing node identifiers and display text.

Product positioning clarification:

- local knowledge base tool
- single-user / personal use
- local-first, not collaboration-first

## 2. Form Choice: Web App vs Window App

### Option A: Frontend/Backend Web App

#### Advantages

- Cross-platform delivery is convenient; browser is the runtime.
- UI technology for graph editing is mature:
  - `React`
  - `Vue`
  - `Svelte`
  - `Konva`
  - `SVG`
  - `Canvas`
  - `D3`
- Future collaboration features are easier to extend:
  - shared editing
  - remote storage
  - account system
  - publishing/sharing
- Frontend iteration speed is high for interactive diagram editing.

#### Disadvantages

- For a local note tool, backend is often unnecessary overhead.
- Local file access, drag-drop desktop behavior, and offline packaging are more cumbersome.
- If implemented as “Python backend + browser frontend”, the interaction core still largely lives in JavaScript; Python value is reduced to file service/API orchestration.
- Desktop-style editing experience may need extra packaging later, such as Electron/Tauri/PWA.

#### Best Fit

- Multi-user collaboration is a priority.
- Future target includes cloud sync and browser access.
- The team is comfortable treating the editor as a web product first.

### Option B: Native Window Program

#### Advantages

- Better match for a local engineering tool / note tool workflow.
- Natural local file access:
  - open Markdown
  - save Markdown
  - import/export assets
  - manage local project folders
- Easier offline usage and distribution as a single desktop app.
- More suitable for future editor-class features:
  - split panes
  - dock widgets
  - outline tree
  - local history
  - shortcut-heavy editing
- Python can directly own application orchestration, parsing, persistence, and plugin management.

#### Disadvantages

- If fully native-drawn UI is chosen, graph editing UI development cost rises sharply.
- If later collaboration/cloud becomes core, a pure desktop-first architecture has more migration work.
- Cross-platform UI consistency depends on the desktop framework.

#### Best Fit

- Local-first Mermaid editing is the main target.
- Manual layout editing is a core requirement.
- The product is closer to an IDE/editor than a shared web whiteboard.

## 3. Recommendation

### Recommended Direction

Choose a **window program**, but use a **hybrid architecture**:

- **Desktop shell**: `PySide6`
- **Interactive editor surface**: HTML/CSS/JavaScript inside `QWebEngineView`
- **Python side**:
  - file IO
  - Markdown / Mermaid parsing
  - project state
  - persistence
  - export pipeline
- **Web side**:
  - canvas/SVG interaction
  - drag layout
  - selection
  - node/subgraph editing
  - visual feedback

This is the most balanced solution for the current target.

Because the product is explicitly for **personal local knowledge management**, the desktop-first choice is no longer just a preference; it is the primary product fit.

## 4. Why This Recommendation Fits Best

The requested tool is not just a Mermaid viewer. It is becoming a **diagram editor** with:

- manual positioning
- structural editing
- local Markdown integration
- future note/tooling expansion

That combination is closer to:

- a lightweight IDE
- a desktop diagram editor

than to a traditional browser webpage.

At the same time, the editing surface itself is highly interactive and is best implemented with web rendering technology rather than trying to draw everything in pure Qt widgets.

So the recommended architecture is:

**Desktop application outside, web editor inside.**

This keeps:

- Python as the main language and orchestration layer
- high UI productivity for the graph editor
- a clean future path for expansion

## 5. Extensibility Comparison

### Web App Extensibility

Strong in:

- collaboration
- cloud storage
- share links
- online publishing
- team workflows

Weaker in:

- deep local integration
- local-first engineering workflows
- desktop-grade file/project operations

### Window App Extensibility

Strong in:

- local note/database integration
- project-based workflows
- plugin systems
- keyboard-driven editor features
- file watching
- export/import tools

Weaker in:

- instant browser access
- zero-install usage
- real-time collaboration out of the box

## 6. Final Architecture Decision

### Decision

For `mermaid_editor`, the preferred implementation is:

**Python desktop application based on `PySide6`, with an embedded web editor for the diagram canvas.**

### Decision Rationale

1. Better fit for local Markdown note editing.
2. Better fit for manual graph layout interactions.
3. Better long-term path for becoming a serious editor tool.
4. Keeps Python as the primary project language.
5. Allows future extraction of the editor surface into a standalone web frontend if needed.
6. Avoids unnecessary backend and collaboration complexity for a single-user product.

## 7. Suggested Technical Direction

### Desktop Layer

- `PySide6`
- `QMainWindow`
- `QSplitter`
- `QTreeWidget` or `QListWidget`
- `QPlainTextEdit`
- `QWebEngineView`

### Python Core

- Mermaid block extraction from Markdown
- document model
- graph model
- manual layout persistence
- import/export
- autosave / project save

### Web Editor Layer

- SVG-based or Canvas-based node rendering
- drag-and-drop positioning
- subgraph box editing
- node text editing
- selection / hover / context menu

### Persistence Strategy

Recommended to store:

1. original Mermaid text
2. editor metadata for manual layout

Example direction:

- keep Mermaid source in Markdown
- store manual layout metadata in sidecar JSON, or
- embed editor metadata in fenced comment blocks

This prevents manual layout data from being lost when Mermaid syntax is reloaded.

For this project, persistence should be optimized for local personal workflows:

- fast local open/save
- robust autosave
- recoverable history
- no mandatory remote dependency
- optional future export/sync, but not a core requirement

## 8. Milestone Suggestion

### M1

- open Markdown file
- extract Mermaid blocks
- render current diagram

### M2

- select node
- drag node position
- save manual layout metadata

### M3

- add/delete node
- rename node id
- edit node display text
- add/delete subgraph

### M4

- bidirectional sync:
  - visual edits -> Mermaid text
  - Mermaid text edits -> visual model

### M5

- export SVG/PNG
- multi-diagram document support
- outline / diagram navigator

## 9. Immediate Next Step

Proceed with a desktop-first implementation skeleton:

1. create project structure
2. build a PySide6 main window
3. load `/d:/Repositories/NexusRenderer/workflow.md`
4. extract Mermaid code blocks
5. render them in an embedded web view
6. design manual layout data model

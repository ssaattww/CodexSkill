# Example Document Layout for Multiple Projects

## When to Consult This Guidance

- Before creating a new project's initial documents, when deciding where to place them
- When deciding where to place a new document whose location has not yet been established. This includes design documents, phase or task status documents, reports, and other new documents, including missing documents added to an existing project

Do not repeat this placement check for routine generation or updates at paths that have already been established.

## Example for Large Repositories with Multiple Projects

This hierarchy is not required for a single-project repository. For a large repository containing multiple projects, consider the following entry points and grouping.

```text
<repository>/
├── <solution-file>
├── README.md                 # Links to the overall basic design and each project
├── docs/                     # Example folder for repository-wide documents
│   ├── basic-design.md
│   ├── phases-status.md
│   ├── tasks-status.md
│   └── reports/              # Example, if allowed by existing rules
└── projects/
    ├── alpha/
    │   ├── README.md         # Links to the project-specific design
    │   └── docs/
    │       └── alpha-design.md
    └── beta/
        ├── README.md
        └── docs/
            └── beta-design.md
```

The names illustrate the layout; choose names that follow the repository's existing conventions.

| Scope | Documents and entry points |
| --- | --- |
| Repository-wide | Put the solution and README at the repository root. Group the basic design, phase status, task status, and entry point for repository-wide reports in the overall documentation folder. |
| Each project | Link from the README directly inside each project to that project's document folder and project-specific design. |
| Navigation | Link from the root README to the overall design and each project. Link from each project README to its project-specific design. |

## Align with Existing Rules

- `<overall-docs>`, `<project-docs>`, and file names are examples; do not require the same names in every repository. Before adopting them, check repository instructions, existing document names, scripts, CI, and reserved paths, then use consistent names within that repository.
- Place and name reports according to `report-output-manager` and the target repository's rules. For example, if an existing rule reserves `<repo-root>/reports/`, use it and do not apply the `<overall-docs>/reports/` example. Do not retroactively change existing reserved paths when adopting a new layout.
- Do not move or change existing documents, reports, links, diagrams, CI, or automation in bulk. If a migration is needed, handle it as separate work after checking its impact on references and automation.

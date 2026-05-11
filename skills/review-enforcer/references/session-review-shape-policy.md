# Source Layout And Documentation Policy

Open this when a review must check whether code changes keep file naming,
folder placement, partial type layout, XML documentation, and test comments in a
consistent source shape.

This reference defines the shape rules the reviewer should apply. It does not
replace repository-specific design documents; when a design document gives a
stricter rule, use the design document as the source of truth.

## File Naming Rules

Allow dotted file names only when the framework or toolchain owns that shape.

Allowed examples:

- `.csproj`
- `.sln`
- `.razor.cs`
- `.razor.css`
- `.g.cs`
- `.Designer.cs`
- `.AssemblyInfo.cs`

Do not use dotted names as hand-written responsibility markers.

Avoid:

- `TrackerEngine.FrameCommit.cs`
- `TrackerEngine.BallTracking.cs`
- `TypeName.Responsibility.cs`

Prefer:

- `TrackerEngine/FrameCommit.cs`
- `TrackerEngine/BallTracking.cs`
- `TypeName/Responsibility.cs`

Do not pack the type name and responsibility into one hand-written file name
when a type-owned folder can express the same structure.

Avoid:

- `TrackerCoordinatorDiagnostics.cs`
- `TrackerCoordinatorDispatch.cs`

Prefer:

- `TrackerCoordinator/Diagnostics.cs`
- `TrackerCoordinator/Dispatch.cs`

## Folder Placement Rules

Use one top-level type per file as the default.

Multiple top-level types may share one file only when they are read and changed
as one unit, such as:

- parent/child DTOs
- a small enum or support type that is not useful alone
- one external configuration schema group
- one serialization schema group

Use type-owned folders for large partial types.

The folder name owns the type identity. The file name owns the responsibility.

Preferred shape:

```text
TrackerEngine/
  TrackerEngine.cs
  FrameCommit.cs
  BallTracking.cs
  RobotTracking.cs
  Geometry.cs
  Settings.cs
```

Do not change namespaces or public contracts just because files move into a
folder.

Keep meaningful domain folders such as `Configuration`, `Model`, and `Proto`
when they describe the source boundary better than a type-owned folder.

## Partial Type Rules

Use `partial` only when splitting one large type makes the type easier to read by
responsibility.

The main file should contain:

- fields
- constructors
- top-level orchestration methods
- the public or internal entry points that define the type's main role

Responsibility files should contain one coherent behavior area.

Examples:

- `FrameCommit.cs`
- `ProfileSwitch.cs`
- `Diagnostics.cs`
- `Dispatch.cs`

Every hand-written partial class declaration should have an XML summary that
states the responsibility of that file.

Example:

```csharp
/// <summary>
/// Coordinates engine event dispatch, snapshot updates, packet publishing, and observer notification order.
/// </summary>
public sealed partial class TrackerCoordinator
```

## Production XML Documentation Rules

Write XML summaries for public, protected, and internal API surface.

This includes:

- classes
- records
- interfaces
- enums
- public/protected/internal properties
- public/protected/internal methods
- configuration schema properties
- DTO properties
- UI state properties
- serialization schema properties

Private methods usually do not need XML documentation.

Add XML documentation to private methods when they are a boundary or ordering
point that future edits can easily break, such as:

- dispatch ordering
- flush ordering
- profile switch application
- diagnostics schema construction
- capture file or replay schema handling
- schema conversion
- Kalman or identity-assignment boundaries

A good summary should describe the contract a maintainer must preserve, not only
repeat the method name.

Prefer:

```csharp
/// <summary>
/// Applies the active profile only after the engine emits ProfileSwitched, then keeps publisher and snapshot state aligned.
/// </summary>
```

Avoid:

```csharp
/// <summary>
/// Handles profile switching.
/// </summary>
```

When a property represents an external setting, include the operational meaning
of null, zero, empty string, units, or default values when that meaning matters.

## Test Documentation Rules

Every `[Fact]` and `[Theory]` test method should have an XML summary immediately
above the attribute.

Use this shape:

```csharp
/// <summary>
/// Verifies that a profile switch request resolves the named profile and applies it through the coordinator.
/// </summary>
[Fact]
public void RequestProfileSwitch_ResolvesNamedProfileAndAppliesItThroughCoordinator()
```

The summary should say what behavior the test proves. It should not merely
repeat the method name with spaces.

Test classes should have XML summaries when they group a meaningful contract or
behavior area.

Shared fixtures, helper classes, and test doubles should have XML summaries when
multiple tests depend on them.

Do not use a normal comment as the primary explanation for a test method.

Avoid:

```csharp
// Verifies that missing active profiles fail with the profile name.
[Fact]
public void Resolve_WithMissingActiveProfile_Throws()
```

Prefer:

```csharp
/// <summary>
/// Verifies that resolving a missing active profile fails with the missing profile name.
/// </summary>
[Fact]
public void Resolve_WithMissingActiveProfile_Throws()
```

Normal comments inside a test method are acceptable for assertion groups, test
data setup, or local reasoning that is not the method's main contract.

## Inline Comment Rules

Use XML documentation for type, member, and test-method contracts.

Use `//` comments only for local explanations inside a method body.

Good uses of `//`:

- explaining why an order must be preserved
- marking assertion groups
- clarifying non-obvious test data
- documenting an invariant directly next to the code that relies on it

Avoid comments that merely restate the code.

Avoid comments that promise future behavior not implemented by the current code.

If a normal comment sits directly above a type, property, method, `[Fact]`, or
`[Theory]`, convert it to XML documentation unless it is intentionally a local
implementation note.

## Review Blocking Rules

Treat these as blocking findings:

- a hand-written `Type.Responsibility.cs` file remains where a type-owned folder
  should be used
- a hand-written `TypeResponsibility.cs` partial file remains where
  `Type/Responsibility.cs` should be used
- a design document names a file path that no longer matches the real source
  layout
- a public, protected, or internal API lacks required XML documentation
- a configuration schema or DTO property lacks required XML documentation
- a `[Fact]` or `[Theory]` does not have an XML summary immediately above it
- a test method still uses a normal comment as its primary "what this verifies"
  explanation
- a partial class responsibility file lacks a class-level XML summary

Treat these as non-blocking concerns unless the repository has a stricter local
rule:

- missing XML documentation on tiny private helpers
- missing comments on obvious arithmetic helpers
- wording that could be clearer but already preserves the correct contract
- inline comments that are slightly inconsistent but not misleading

Treat these as user-confirmation-required gaps:

- the repository has no authoritative coding standard and two plausible shapes
  conflict
- a file may be generated or framework-owned, but the reviewer cannot confirm it
  from the workspace
- enforcing the rule would require changing public API shape rather than only
  source layout or documentation

## Minimal Checklist

Before closing a review that touches source layout or comments, check:

- Dotted names are framework/toolchain owned only.
- Large partial types use `TypeName/Responsibility.cs`.
- Namespaces and public contracts did not change due to file moves.
- Public, protected, and internal API surface has XML summaries.
- Configuration schema and DTO properties have XML summaries.
- Important private boundary methods have XML summaries.
- Every `[Fact]` and `[Theory]` has an XML summary immediately above it.
- Normal comments are local implementation notes, not member contracts.

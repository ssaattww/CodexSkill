import path from 'node:path';
import { spawnSync } from 'node:child_process';

const POWERSHELL = String.raw`
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = 'Stop'
$response = $null

function Stop-Check([string] $message) {
  throw [System.InvalidOperationException]::new($message)
}

function Get-DriveRoot([string] $itemPath) {
  $full = [System.IO.Path]::GetFullPath($itemPath)
  $driveRoot = [System.IO.Path]::GetPathRoot($full)
  if ($driveRoot -notmatch '^[A-Za-z]:\\$') {
    Stop-Check "Path is not on a local drive: $full"
  }
  $drive = [System.IO.DriveInfo]::new($driveRoot)
  if (-not $drive.IsReady -or $drive.DriveType -ne [System.IO.DriveType]::Fixed
      -or $drive.DriveFormat -ne 'NTFS') {
    Stop-Check "Drive is not a ready fixed NTFS volume: $driveRoot"
  }
  return $driveRoot.ToUpperInvariant()
}

function Assert-Directory([string] $itemPath, [bool] $privateRoot, [string] $userSid, [hashtable] $tokenSids) {
  $full = [System.IO.Path]::GetFullPath($itemPath)
  $item = Get-Item -LiteralPath $full -Force
  if (-not $item.PSIsContainer
      -or (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0)) {
    Stop-Check "Path is not a plain directory: $full"
  }

  $acl = Get-Acl -LiteralPath $full -ErrorAction Stop
  if (-not $acl.AreAccessRulesCanonical) {
    Stop-Check "ACL order cannot be evaluated: $full"
  }

  $owner = $acl.GetOwner([System.Security.Principal.SecurityIdentifier]).Value
  $trustedOwners = @($userSid, 'S-1-5-18', 'S-1-5-32-544')
  if ($privateRoot) {
    if ($owner -ne $userSid) { Stop-Check "Private directory owner is not the current user: $full" }
  } elseif ($owner -notin $trustedOwners) {
    Stop-Check "Ancestor owner is unrecognized: $full"
  }

  # FileSystemRights write/control bits. Unknown or non-filesystem rules fail closed.
  $writeMask = [int64]0x000D0156
  $createMask = [int64]0x00000006
  $trustedWriters = @($userSid, 'S-1-5-18', 'S-1-5-32-544')
  $userCreateRights = [int64]0

  foreach ($rule in @($acl.GetAccessRules($true, $true, [System.Security.Principal.SecurityIdentifier]))) {
    if ($rule -isnot [System.Security.AccessControl.FileSystemAccessRule]) {
      Stop-Check "Unsupported ACL rule type: $full"
    }

    $sid = $rule.IdentityReference.Value
    $rights = [int64]$rule.FileSystemRights
    $writeRights = $rights -band $writeMask
    if ($writeRights -eq 0) { continue }

    if ($rule.AccessControlType -eq [System.Security.AccessControl.AccessControlType]::Deny) {
      if ($tokenSids.ContainsKey($sid)) {
        Stop-Check "A deny rule applies to the current token's write access: $full"
      }
      continue
    }

    if ($rule.AccessControlType -ne [System.Security.AccessControl.AccessControlType]::Allow) {
      Stop-Check "Unsupported ACL access type: $full"
    }
    if ($sid -notin $trustedWriters) {
      Stop-Check "An untrusted principal can write: $full"
    }
    if ($sid -eq $userSid) {
      $userCreateRights = $userCreateRights -bor ($rights -band $createMask)
    }
  }

  if ($privateRoot -and ($userCreateRights -band $createMask) -ne $createMask) {
    Stop-Check "Current user lacks explicit file and directory creation rights: $full"
  }
}

try {
  $requestJson = [Console]::In.ReadToEnd()
  $request = ConvertFrom-Json -InputObject $requestJson
  $currentIdentity = [System.Security.Principal.WindowsIdentity]::GetCurrent()
  $principal = [System.Security.Principal.WindowsPrincipal]::new($currentIdentity)
  if ($principal.IsInRole([System.Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Stop-Check 'Installation requires the ordinary user session.'
  }
  $currentSid = $currentIdentity.User.Value
  $tokenSids = @{}
  $tokenSids[$currentSid] = $true
  foreach ($group in [System.Security.Principal.WindowsIdentity]::GetCurrent().Groups) {
    $tokenSids[$group.Value] = $true
  }

  $parent = [System.IO.Path]::GetFullPath([string]$request.parent)
  $source = [System.IO.Path]::GetFullPath([string]$request.sourceRoot)
  $parentDrive = Get-DriveRoot $parent
  [void](Get-DriveRoot $source)

  $ancestorPaths = @($request.ancestors)
  if ($ancestorPaths.Count -eq 0) { Stop-Check 'Ancestor list is missing.' }
  if (-not ($ancestorPaths | Where-Object {
    [System.StringComparer]::OrdinalIgnoreCase.Equals(
      [System.IO.Path]::GetFullPath([string]$_), $parent
    )
  })) {
    Stop-Check 'Verified ancestors do not include the temporary parent.'
  }

  foreach ($ancestor in $ancestorPaths) {
    $fullAncestor = [System.IO.Path]::GetFullPath([string]$ancestor)
    if ((Get-DriveRoot $fullAncestor) -ne $parentDrive) {
      Stop-Check 'Ancestor is not on the temporary area drive.'
    }
    Assert-Directory $fullAncestor $false $currentSid $tokenSids
  }

  Assert-Directory $parent $true $currentSid $tokenSids
  Assert-Directory $source $false $currentSid $tokenSids

  if ($null -ne $request.root -and [string]$request.root -ne '') {
    $root = [System.IO.Path]::GetFullPath([string]$request.root)
    if (-not [System.StringComparer]::OrdinalIgnoreCase.Equals(
      [System.IO.Directory]::GetParent($root).FullName, $parent
    )) {
      Stop-Check 'Created area is not a direct child of the verified parent.'
    }
    if ((Get-DriveRoot $root) -ne $parentDrive) {
      Stop-Check 'Created area drive differs from its verified parent.'
    }
    Assert-Directory $root $true $currentSid $tokenSids
  }

  $response = @{ ok = $true }
} catch {
  $response = @{ ok = $false; reason = $_.Exception.Message }
}

[Console]::Out.WriteLine((ConvertTo-Json -InputObject $response -Compress))
`;

function refuse(reason) {
  return { ok: false, reason };
}

export function inspectLocalAreaAttributes(input) {
  if (process.platform !== 'win32') {
    return refuse('Windows attribute inspection is unavailable on this platform.');
  }

  const systemRoot = process.env.SystemRoot;
  if (!systemRoot) return refuse('SystemRoot is unavailable.');

  const executable = path.join(
    systemRoot,
    'System32',
    'WindowsPowerShell',
    'v1.0',
    'powershell.exe',
  );
  const encodedScript = Buffer.from(POWERSHELL, 'utf16le').toString('base64');

  const run = spawnSync(
    executable,
    ['-NoLogo', '-NoProfile', '-NonInteractive', '-EncodedCommand', encodedScript],
    {
      input: Buffer.from(JSON.stringify(input), 'utf8'),
      encoding: 'utf8',
      windowsHide: true,
      timeout: 5000,
      maxBuffer: 64 * 1024,
    },
  );

  if (run.error || run.status !== 0) {
    return refuse(run.error?.message || run.stderr?.trim() || 'PowerShell attribute inspection failed.');
  }

  try {
    const result = JSON.parse(run.stdout.trim());
    return result?.ok === true
      ? { ok: true }
      : refuse(result?.reason || 'Windows attributes could not be verified.');
  } catch (error) {
    return refuse(`PowerShell returned unreadable JSON: ${error.message}`);
  }
}

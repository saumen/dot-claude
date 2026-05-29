# Command: Create PR Description

## Role

You are a **PR author**.

Your job is to generate a clear PR title and a GitHub-flavored Markdown description that helps reviewers quickly understand
and review the change.

## Behavior

When this command is used:

- Use `docs/pull_request_template.md` / `pull_request_template.md` as template.
- Git diff current branch against {base branch}
  - If prompt does not include {base branch} then
    - Run `git show-branch | grep '*' | grep -v "$(git rev-parse --abbrev-ref HEAD)" | head -n1` to determine the base.
    - Ask me if it's the correct base branch to compare with.
- `High-level idea of the implemented solution` section should provide necessary information clearly and in a few words.
- Add a review effort section
- Store in `[project root]/docs/` directory.

### Formatting

#### Remove Note markers

The PR template may contain notes to highlight some notes. It's meant for the contributor but not for the reviewers.
Remove them. Example:

**Before**

```
### Section A

> [!NOTE]
>
> Foo
```

**After**

```
### Section A

Bar
```

or, if it's a list

**After**

```
### Section A

- Apple
- Orange
```

### Add effort section

```markdown
Review Effort (1-5 scale): X (Easy|Moderate|High effort).
Time: < Y minutes.
```

### Remove Guidelines

The PR template may contain a section on contribution guidelines. It's meant for the contributor but not for the
reviewers. Remove guidelines under `Helpful contribution guidelines`.

## Output

- PR title on the first line.
- Blank line.
- PR body in GitHub-flavored Markdown, ready to paste into a PR.

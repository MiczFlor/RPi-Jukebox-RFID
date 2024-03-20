# Documentation with Markdown

We use markdown for documentation. Please add/update documentation in `documentation`.

## Linting

To ensure a consistent documentation we lint markdown files.

We use [markdownlint-cli2](https://github.com/DavidAnson/markdownlint-cli2) for linting.

`.markdownlint-cli2.yaml` configures linting consistently for the Github Action, the pre-commit hook, manual linting and the [markdownlint extension](https://github.com/DavidAnson/vscode-markdownlint) for Visual Studio Code.

You can start a manual check, if you call `run_markdownlint.sh`.

If markdown files are changed and the pre-commit hook is enabled, `run_markdownlint.sh` is triggered on commits.

After creating a PR or pushing to the repo a Github Action triggers the linter, if markdown files are changed (see `.github/workflows/markdown_v3.yml`).

### Disabling Rules

> [!NOTE]
> Please use disabling rules with caution and always try to fix the violation first.

A few rules are globally disabled in `.markdownlint-cli2.yaml` (see section `config`).

If you want to disable a rule for a specific section of a markdown file you can use

```markdown
<!-- markdownlint-disable MD010 -->
section where MD010 should be ignored 
<!-- markdownlint-restore -->
```

### References

* <https://github.com/DavidAnson/markdownlint-cli2>
* Rules:
  * <https://github.com/DavidAnson/markdownlint/blob/main/doc/Rules.md>
  * <https://github.com/DavidAnson/markdownlint/blob/main/README.md#rules--aliases>

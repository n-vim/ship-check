# ShipCheck Commands

This file gives a quick reference for the main ShipCheck commands.

## Status

```bash
shipcheck status .
shipcheck status . --profile python
shipcheck status . --format markdown --output SHIPCHECK_REPORT.md
shipcheck status . --format json --output shipcheck-report.json
```

## Doctor

```bash
shipcheck doctor .
shipcheck doctor . --profile library
```

## Analyze

```bash
shipcheck analyze .
shipcheck analyze . --format json
```

## Release Notes

```bash
shipcheck notes .
shipcheck notes . --github
shipcheck release-notes . --output RELEASE.md
```

## Changelog

```bash
shipcheck changelog . --dry-run
shipcheck changelog . --force
shipcheck changelog . --version 1.2.0 --force
```

## Version Bump

```bash
shipcheck bump patch .
shipcheck bump minor .
shipcheck bump major .
shipcheck bump prerelease . --tag beta
shipcheck bump patch . --dry-run
shipcheck bump patch . --set 1.4.0
```

## Checklist

```bash
shipcheck checklist .
shipcheck checklist . --output RELEASE_CHECKLIST.md
```

## Profiles

```bash
shipcheck profiles
shipcheck profile python
shipcheck profile library
```

## Config

```bash
shipcheck init .
shipcheck config .
```

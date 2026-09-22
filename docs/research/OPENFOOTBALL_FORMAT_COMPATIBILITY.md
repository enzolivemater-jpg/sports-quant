# OpenFootball Parser — Format Compatibility

Date: 2026-09-22

Status: RESEARCH_TOOLING

Direct source inspection found two EPL Football.TXT line formats relevant to the free historical baseline.

## Legacy format

Verified examples:
- EPL 2000/01
- 2009/10
- 2010/11
- 2014/15
- 2018/19
- 2020/21
- 2022/23
- 2023/24

Shape:

`home  score (half-time)  away`

Older files may also:
- omit indentation on date lines;
- omit the year on individual date lines;
- rely on the season date-range header plus chronological month rollover.

## Modern format

Verified:
- EPL 2024/25

Shape:

`home v away score (half-time)`

## Parser policy

The research parser now:
- accepts both line formats;
- reads the season start year from `# Date ...` when present;
- increments the year on chronological month rollover when a date line omits its year;
- still honors explicit years when supplied;
- preserves inherited kickoff-time behavior;
- records `source_line_format` per parsed match;
- assigns neither canonical IDs nor canonical `known_at`.

## Why this matters

A naive single-format parser would report zero matches for older seasons and falsely make the free historical source look incomplete.

Format compatibility is a research tooling requirement before multi-season baseline sizing.

It does not make OpenFootball a production provider and does not authorize F4/F5.

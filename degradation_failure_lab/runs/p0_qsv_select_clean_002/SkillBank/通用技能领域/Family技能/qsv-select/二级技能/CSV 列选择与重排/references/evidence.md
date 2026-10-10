# CSV 列选择与重排 Evidence

- family: qsv-select
- skill_id: 3aab94b4-5f80-54ee-89cd-136656f9e5d6
- support_count: 1

## Evidence 1

- support_id: 69a12244-23ce-507b-96b6-a3cd30c9c606
- relation_type: support
- document: select.md
- doc_id: 83df504e-ec88-5282-8168-b2b1e35829c7
- source_file: D:\Baseline-anthing2skill\AutoSkill-main\degradation_failure_lab\data\sources\qsv\257ae7b38738688138dc430c2ccb4eef8766f3fc\select.md
- section: # select
- span: 9:2716
- confidence: 0.90
- quote: > Select, re-order, reverse, duplicate or drop columns.

**[Table of Contents](TableOfContents.md)** | **Source: [src/cmd/select.rs](https://github.com/dathere/qsv/blob/master/src/cmd/select.rs)** | [👆](TableOfContents.md#legend "has powerful column selector support. See `select` for syntax.")

<a name="nav"></a>
[Description](#description) | [Examples](#examples) | [Usage](#usage) | [Arguments](#arguments) | [Select Options](#select-options) | [Common Options](#common-options)

<a name="description"></a>

## Description [↩](#nav)
Select columns from CSV data efficiently.

<a name="examples"></a>

## Examples [↩](#nav)
> Select the first and fourth columns

```console
qsv select 1,4
```

> Select the first 4 columns (by index)

```console
qsv select 1-4
```

> Select the first 4 columns (by name)

```console
qsv select Header1-Header4
```

> Ignore the first 2 columns (by range)

```console
qsv select 3-
```

> Ignore the first 2 columns (by index)

```console
qsv select '!1-2'
```

> Select the third column named 'Foo':

```console
qsv select 'Foo[2]'
```

> Select the first and last columns, _ is a special character for the last column:

```console
qsv select 1,_
```

> Reverse the order of columns:

```console
qsv select _-1
```

> select columns starting with 'a' (regex)

```console
qsv select /^a/
```

> select columns with a digit (regex)

```console
qsv select '/^.*\d.*$/'
```

> remove SSN, account_no and password columns (regex)

```console
qsv select '!/SSN|account_no|password/'
```

> Sort the columns lexicographically (i.e. by their byte values)

```console
qsv select 1- --sort
```

> Select some columns and then sort them

```console
qsv select 1,4,5-7 --sort
```

> Randomly shuffle the columns:

```console
qsv select 1- --random
```

> Randomly shuffle the columns with a seed

```console
qsv select 1- --random --seed 42
```

> Select some columns and then shuffle them with a seed:

```console
qsv select 1,4,5-7 --random --seed 42
```

> Re-order and duplicate columns arbitrarily using different types of selectors

```console
qsv select 3-1,Header3-Header1,Header1,Foo[2],Header1
```

> Quote column names that conflict with selector syntax:

```console
qsv select '\"Date - Opening\",\"Date - Actual Closing\"'
```

For more examples, see [tests](https://github.com/dathere/qsv/blob/master/tests/test_select.rs).
